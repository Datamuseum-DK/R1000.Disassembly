#!/usr/bin/env python
#
# Copyright (c) 2023 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

'''
   OMSI PASCAL unwrangling
   =======================
'''

import sys

from pyreveng import code, pil, mem, assy

PseudoCode = code.Decoder("pseudo")

class MatchHit():

    ''' Pop.match returns one of these to describe the hit '''

    def __init__(self, stmt, idx, mins):
        self.stmt = stmt
        self.idx = idx
        self.mins = mins

    def __iter__(self):
        yield from self.mins

    def __len__(self):
        return len(self.mins)

    def __getitem__(self, idx):
        return self.mins[idx]

    def replace(self, cls):
        ''' Peplace the hit with a pseudo-op of the given class '''
        pop = cls()
        for i in self.mins:
            self.stmt.del_ins(i)
            pop.append_ins(i)
        self.stmt.insert_ins(self.idx, pop)
        return pop

    def render(self, file=sys.stdout):
        ''' Render the hit usably '''
        file.write("HIT\n")
        for i in self.mins:
            file.write("   " + str(i) + "\n")

class Pop():

    ''' Pseudo-Op base class '''

    kind = "Naked"

    def __init__(self):
        self.lo = -1
        self.hi = -1
        self.ins = []
        self.txt = ""
        self.come_from = []
        self.go_to = []
        self.stack_delta = 0
        self.stack_adj = False
        self.stack_level = None

    def __iter__(self):
        yield from self.ins

    def __len__(self):
        return len(self.ins)

    def __lt__(self, other):
        return self.lo < other.lo

    def __getitem__(self, idx):
        return self.ins[idx]

    def render(self, pfx=""):
        ''' Render recursively '''
        hdr = pfx + str(self) + " d%+d" % self.stack_delta + " [" + str(self.stack_level) + "]"
        for src in self.come_from:
            hdr += "  <-" + hex(src.lo)
        for dst in self.go_to:
            hdr += "  ->" + hex(dst.lo)
        yield hdr
        for i in self.ins:
            yield from i.render(pfx + "    ")

    def append_ins(self, ins):
        ''' Append an instruction '''
        assert isinstance(ins, Pop)
        assert ins.lo >= self.hi
        ins.pop = self
        self.ins.append(ins)
        self.lo = self.ins[0].lo
        self.hi = self.ins[-1].hi
        self.stack_delta += ins.stack_delta

    def insert_ins(self, idx, ins):
        ''' Insert an instruction '''
        assert isinstance(ins, Pop)
        ins.pop = self
        self.ins.insert(idx, ins)
        self.lo = self.ins[0].lo
        self.hi = self.ins[-1].hi
        self.stack_delta += ins.stack_delta

    def del_ins(self, ins):
        ''' Delete an instruction '''
        assert isinstance(ins, Pop)
        i = self.ins.index(ins)
        assert i >= 0
        self.ins.remove(ins)
        self.lo = self.ins[0].lo
        self.hi = self.ins[-1].hi
        self.stack_delta -= ins.stack_delta

    def __repr__(self):
        return "<POP %05x-%05x %s>" % (self.lo, self.hi, self.kind)

    def match(self, pattern):
        ''' look for particular pattern '''
        if self.kind != "Naked":
            return
        idx = 0
        while idx < len(self):
            match = []
            for off, hits in enumerate(pattern):
                if idx + off >= len(self):
                    break
                ins = self[idx + off]
                good = True
                for hit in hits:
                    if not hit in ins.txt:
                        good = False
                        break
                if not good:
                    break
                match.append(ins)
            if match:
                yield MatchHit(self, idx, match)
            idx += 1

    def reg_writes(self, reg):
        ''' Use PIL to find out how many times a register is written '''
        count = 0
        for ins in self.ins:
            pill = getattr(ins.ins, "pil", None)
            if not pill:
                continue
            for pils in pill:
                if not isinstance(pils, pil.PIL_Stmt_Assign):
                    continue
                dst = pils.spec[0]
                if dst.nam != "%" + reg:
                    continue
                count += 1
        return count

class PopMIns(Pop):
    ''' Machine Instruction '''

    def __init__(self, ins):
        super().__init__()
        self.ins = ins
        self.lo = ins.lo
        self.hi = ins.hi
        self.txt = ins.render()
        self.pop = None

    def __repr__(self):
        txt = "<MI %05x d%+d" % (self.lo, self.stack_delta)
        if self.stack_adj:
            txt += "."
        return txt + " " + self.txt + ">"

    def render(self, pfx=""):
        yield pfx + str(self)

    def data_width(self):
        ''' Width of instruction data '''
        return { "B": 1, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

    def stack_width(self):
        ''' Width of instruction data on stack '''
        return { "B": 2, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

class PopPrologue(Pop):
    ''' Pseudo-Op for function Prologue '''
    kind = "Prologue"

class PopEpilogue(Pop):
    ''' Pseudo-Op for function Epilogue '''
    kind = "Epilogue"

class PopStackPush(Pop):
    ''' Pseudo-Op for copying things onto stack '''
    kind = "StackPush"

class PopStackPop(Pop):
    ''' Pseudo-Op for copying things from stack '''
    kind = "StackPop"

class PopTextPush(Pop):
    ''' Pseudo-Op for pushing string literal on stack '''
    kind = "TextPush"

class PopBailout(Pop):
    ''' Pseudo-Op for bailing out of context'''
    kind = "Bailout"

class PopLimitCheck(Pop):
    ''' Pseudo-Op for limit checks'''
    kind = "LimitCheck"

class PopRegCacheLoad(Pop):
    ''' Pseudo-Op for loading register caches'''
    kind = "RegCacheLoad"

class OmsiFunction():
    ''' A PASCAL function '''

    def __init__(self, up, lo):
        self.up = up
        self.lo = lo
        self.body = Pop()
        self.calls = set()
        self.traps = {}

    def __iter__(self):
        yield from self.body

    def __repr__(self):
        return "<OMSI function 0x%05x>" % self.lo

    def render(self, file=sys.stdout):
        ''' Render to text '''
        file.write("OF %05x\n" % self.lo)
        for i in self.body.render(pfx="    "):
            file.write(i + "\n")

    def dot_file(self, file):
        ''' Produce a dot(1) input file '''
        file.write("digraph {\n")
        for i in sorted(self.body):
            file.write("P%05x [label=\"%05x" % (i.lo, i.lo))
            try:
                file.write("\\n%d + %d" % (i.stack_level, i.stack_delta))
                file.write(" = %d" % (i.stack_level + i.stack_delta))
            except TypeError:
                pass
            file.write("\"]\n")
            for j in i.go_to:
                file.write("P%05x -> P%05x\n" % (i.lo, j.lo))
        file.write("}\n")


    def append_code_ins(self, ins):
        ''' Add another M68K instruction '''
        self.body.append_ins(PopMIns(ins))

    def analyze(self):
        ''' Progressively raise the level of abstraction '''
        if not self.find_prologue():
            return

        for ins in self.body:
            if "TRAP" in ins.txt and ("#15" in ins.txt or "#14" in ins.txt):
                self.traps[ins.lo] = ins

        self.find_epilogue()
        self.uncache_registers()
        self.find_stackpush()
        self.find_stackpop()
        self.find_textpush()
        self.find_bailout()

        prev = ""
        for ins in self.body:
            if ins.kind == "Naked" and "DB" in ins.txt and "A7" in prev:
                print("NB: unspotted stack loop", prev, ins.txt)
            prev = ins.txt

        self.assign_stack_delta()
        self.find_limit_checks()
        self.partition()
        self.set_stack_levels()

    def find_prologue(self):
        ''' There are two variants of function prologues '''
        for hit in self.body.match(
            (
                ("LINK.W",),
                ("CMPA.L", "(A5),A7",),
                ("BHI",),
                ("MOVE.W", "#0x2,CCR"),
                ("tRAPV",),
                ("ADDA.W",),
                ("MOVEM.L",),
            )
        ):
            if len(hit) == 7:
                hit.replace(PopPrologue)
                return True

        for hit in self.body.match(
            (
                ("LINK.W",),
                ("MOVEM.L",),
                ("CMPA.L", "(A5),A7",),
                ("tRAPV",),
            )
        ):
            if len(hit) == 4:
                hit.replace(PopPrologue)
                return True
        return False

    def find_epilogue(self):
        ''' Only one kind of epilogue so far '''
        for hit in self.body.match(
            (
                ("MOVEM.L", "(A7)+",),
                ("UNLK",),
            )
        ):
            if len(hit) == 2:
                hit.replace(PopEpilogue)
                return

    def uncache_registers(self):
        ''' Values used multiple times are cached in vacant registers '''
        pop = None

        dsts = set()
        for ins in self.body:
            flow_out = getattr(ins.ins, "flow_out", [])
            for flow in flow_out:
                if flow.typ != "N":
                    dsts.add(flow.to)

        # Must follow Prologue
        idx = 1

        while idx < len(self.body):
            ins = self.body[idx]
            if ins.lo in dsts:
                break
            if "LEA.L" not in ins.txt:
                break
            reg = str(ins.ins.oper[-1])
            writes = self.body.reg_writes(reg)
            # print("UCR", writes, ins)
            if writes != 1:
                break
            if not pop:
                pop = PopRegCacheLoad()
            self.body.del_ins(ins)
            pop.append_ins(ins)
        while idx < len(self.body):
            ins = self.body[idx]
            if ins.lo in dsts:
                break
            if "MOVE" not in ins.txt:
                break
            reg = str(ins.ins.oper[-1])
            if reg[0] != "D":
                break
            writes = self.body.reg_writes(reg)
            if writes != 1:
                break
            if not pop:
                pop = PopRegCacheLoad()
            self.body.del_ins(ins)
            pop.append_ins(ins)

        if not pop:
            return

        self.body.insert_ins(1, pop)

        for ins in pop.ins:
            reg = str(ins.ins.oper[1])
            if reg[0] == "A":
                pat = "(" + reg + ")"
            else:
                pat = reg
            rpl = ins.ins.oper[0]
            if isinstance(rpl, assy.Arg_verbatim):
                rpl = str(rpl)
            elif isinstance(rpl, assy.Arg_dst):
                rpl = "0x%x" % rpl.dst
            else:
                print("RCL unknown arg", ins, type(rpl), rpl)
                continue
            for rins in self.body:
                if not isinstance(rins, PopMIns):
                    continue
                if pat in rins.txt:
                    rins.txt = rins.txt.replace(pat, rpl)
                    if "JSR" in rins.txt:
                        self.up.discover(rpl)
                if reg[0] == 'A' and reg + "," in rins.txt and "MOVEA.L" in rins.txt:
                    dst = rins.txt.split(",")[-1]
                    rins.txt = "LEA.L   " + rpl + "," + dst

    def assign_stack_delta(self):
        ''' Assign stack increment/decrement to each instruction '''
        for ins in self.body:
            if "PEA.L" in ins.txt:
                ins.stack_delta = -4
            elif "-(A7)" in ins.txt:
                ins.stack_delta = - ins.stack_width()
            elif "(A7)+" in ins.txt:
                ins.stack_delta = ins.stack_width()
            elif "A7" in ins.txt:
                if "(A7)" in ins.txt:
                    pass
                elif "A7+0x" in ins.txt:
                    pass
                elif "MOVE" in ins.txt and "A7," in ins.txt:
                    pass
                elif "ADDQ.L" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = int(oper[1:], 16)
                elif "ADDA.W" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = int(oper[1:], 16)
                elif "SUBQ.L" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = -int(oper[1:], 16)
                elif "SUBA.W" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = -int(oper[1:], 16)
                else:
                    print("SD A7", ins)

    def find_stackpush(self):
        ''' Find loops which push things on stack '''
        for hit in self.body.match(
            (
                ("SUBA.W", ",A7"),
                ("MOVEA.L", "A7,"),
                ("LEA.L",),
                ("MOVEQ.L",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 6:
                continue
            _src = str(hit[2].ins.oper[0])
            srcreg = str(hit[2].ins.oper[1])
            cntreg = str(hit[3].ins.oper[1])
            fmreg = str(hit[4].ins.oper[0])
            toreg = str(hit[4].ins.oper[1])
            if hit[5].ins.flow_out[0].to != hit[4].lo:
                continue
            if cntreg != str(hit[5].ins.oper[0]):
                continue
            if "(" + srcreg + ")+" != fmreg:
                continue
            if toreg[0] != "(" or toreg[-2:] != ")+":
                continue
            toreg = toreg[1:-2]
            pop = hit.replace(PopStackPush)
            cnt = hit[0].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpush", cnt)
                hit.render()
                return
            pop.stack_delta = - int(cnt[3:], 16)
            pop.stack_delta *= hit[4].data_width()

        for hit in self.body.match(
            (
                ("MOVEA.L",),
                ("MOVEQ.L",),
                ("MOVE.", "-(A7)"),
                ("DBF",),
            )
        ):
            if len(hit) < 4:
                continue
            #_src = str(hit[2].ins.oper[0])
            #srcreg = str(hit[2].ins.oper[1])
            cntreg = str(hit[1].ins.oper[1])
            #fmreg = str(hit[4].ins.oper[0])
            #toreg = str(hit[4].ins.oper[1])
            if hit[3].ins.flow_out[0].to != hit[2].lo:
                continue
            if cntreg != str(hit[3].ins.oper[0]):
                continue
            #if "(" + srcreg + ")+" != fmreg:
            #    continue
            #if toreg[0] != "(" or toreg[-2:] != ")+":
            #    continue
            #toreg = toreg[1:-2]
            pop = hit.replace(PopStackPush)
            cnt = hit[1].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpush", cnt)
                hit.render()
                return
            pop.stack_delta = - int(cnt[3:], 16)
            pop.stack_delta *= hit[2].data_width()

    def find_stackpop(self):
        ''' Find loops which push things on stack '''
        for hit in self.body.match(
            (
                ("MOVEQ.L",),
                ("MOVE.", "(A7)+"),
                ("DBF",),
            )
        ):
            if len(hit) < 3:
                continue
            cntreg = str(hit[0].ins.oper[1])
            if hit[2].ins.flow_out[0].to != hit[1].lo:
                continue
            if cntreg != str(hit[2].ins.oper[0]):
                continue
            pop = hit.replace(PopStackPop)
            cnt = hit[0].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpop", cnt)
                hit.render()
                return
            pop.stack_delta = int(cnt[3:], 16)
            pop.stack_delta *= hit[1].data_width()

    def find_textpush(self):
        ''' Find loops which push string literals on stack '''
        for hit in self.body.match(
            (
                ("LEA.L",),
                ("MOVEQ.L",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 4:
                continue
            _src = str(hit[0].ins.oper[0])
            srcreg = str(hit[0].ins.oper[1])
            cnt = str(hit[1].ins.oper[0])
            cntreg = str(hit[1].ins.oper[1])
            fmreg = str(hit[2].ins.oper[0])
            toreg = str(hit[2].ins.oper[1])
            if hit[3].ins.flow_out[0].to != hit[2].lo:
                continue
            if cntreg != str(hit[3].ins.oper[0]):
                continue
            if "-(" + srcreg + ")" != fmreg:
                continue
            if toreg != "-(A7)":
                continue
            toreg = toreg[1:-2]
            pop = hit.replace(PopTextPush)
            pop.stack_delta = - (1 + int(cnt[1:], 16))
            pop.stack_delta *= hit[2].data_width()

    def find_bailout(self):
        ''' Find jumps out of context'''
        for hit in self.body.match(
            (
                ("MOVEA.L", "(A5+0x8),A7"),
                ("MOVE",),
                ("JMP",),
            )
        ):
            if len(hit) < 3:
                continue
            hit.replace(PopBailout)

    def find_limit_checks(self):
        ''' Find limit checks '''

        conds = ("BLS", "BLT", "BLE", "BGE", "BGT",)

        for cond in conds:
            for hit in self.body.match(
                (
                    ("CMP",),
                    (cond,),
                )
            ):
                if len(hit) < 2:
                    continue

                if hit[1].ins.flow_out[0].to in self.traps:
                    hit.replace(PopLimitCheck)

        for cond in conds:
            for hit in self.body.match(
                (
                    ("SUB.L",),
                    (cond,),
                    ("TRAP",),
                )
            ):
                if len(hit) < 3:
                    continue

                if hit[1].ins.flow_out[0].to != hit[2].ins.hi:
                    continue

                if hit[2].lo not in self.traps:
                    continue

                hit.replace(PopLimitCheck)


        for cond in conds:
            for hit in self.body.match(
                (
                    ("CMP",),
                    (cond,),
                    ("TRAP",),
                )
            ):
                if len(hit) < 3:
                    continue

                if hit[1].ins.flow_out[0].to != hit[2].ins.hi:
                    continue

                if hit[2].lo not in self.traps:
                    continue

                hit.replace(PopLimitCheck)

        for hit in self.body.match(
            (
                ("ADDQ.W", "#0x1,"),
                ("SUBQ.W", "#0x1,"),
                ("cHK.W",),
            )
        ):
            if len(hit) < 3:
                continue
            treg = str(hit[0].ins.oper[-1])
            if treg != str(hit[1].ins.oper[-1]):
                continue
            if treg != str(hit[2].ins.oper[-1]):
                continue
            hit.replace(PopLimitCheck)

        for hit in self.body.match(
            (
                ("EXTB.W", ),
                ("cHK.W",),
            )
        ):
            if len(hit) < 2:
                continue
            treg = str(hit[0].ins.oper[-1])
            if treg != str(hit[1].ins.oper[-1]):
                continue
            hit.replace(PopLimitCheck)

        for hit in self.body.match(
            (
                ("cHK.W",),
            )
        ):
            if len(hit) < 1:
                continue
            hit.replace(PopLimitCheck)

    def partition(self):
        ''' partition into basic blocks '''
        starts = set()
        for ins in self.body:
            if not starts and isinstance(ins, PopMIns):
                starts.add(ins.lo)
            flow_out = getattr(ins.ins, "flow_out", [])
            for flow in flow_out:
                if flow.typ not in ("C", "N"):
                    starts.add(flow.to)
        # print("QQQ", self, ["%x" % x for x in sorted(starts)])
        pop = None
        pops = {}
        idx = 1
        while self.body[idx].lo not in starts:
            idx += 1
        while idx < len(self.body):
            ins = self.body[idx]
            if isinstance(ins, PopEpilogue):
                break
            if ins.lo in starts:
                pop = Pop()
                pops[ins.lo] = pop
                self.body.insert_ins(idx, pop)
                idx += 1
            self.body.del_ins(ins)
            pop.append_ins(ins)

        for idx, ins in enumerate(self.body[:-1]):
            if ins.kind != "Naked":
                nxt = self.body[idx + 1]
                if nxt:
                    ins.go_to.append(nxt)
                    nxt.come_from.append(ins)
                else:
                    print("MISSING NXT", ins)

        for pop in pops.values():
            ins = pop[-1]
            flow_out = getattr(ins.ins, "flow_out", None)
            if flow_out is None:
                next = pops.get(ins.hi)
                if next is not None:
                    pop.go_to.append(next)
                    next.come_from.append(pop)
                elif not isinstance(ins, PopBailout):
                    print("MISSING NEXT", pop, ins, next)
                continue
            for flow in flow_out:
                if flow.typ in ("C",):
                    continue
                stmt2 = pops.get(flow.to)
                if stmt2:
                    pop.go_to.append(stmt2)
                    stmt2.come_from.append(pop)
                elif flow.to in self.traps:
                    pass
                elif flow.to == self.body[-1].lo:
                    stmt2 = self.body[-1]
                    if stmt2:
                        pop.go_to.append(stmt2)
                        stmt2.come_from.append(pop)
                    else:
                        print("MISSING EPILOG", pop, ins, flow, stmt2)
                else:
                    print("S2?.st?", ins, flow_out, flow.to, self.body[-1].lo)
                    print(self.body[-1])

    def set_stack_levels(self):
        ''' Assign stack level to each basic block '''
        for ins in self.body:
            if not ins.come_from:
                ins.stack_level = 0
        for ins in self.body:
            if ins.stack_level is None:
                continue
            leave = ins.stack_level + ins.stack_delta
            for dst in ins.go_to:
                if dst.stack_level is None:
                    dst.stack_level = leave
                elif dst.stack_level != leave:
                    print("STACK SKEW", ins, leave, "->", dst, dst.stack_level)

class OmsiPascal():

    ''' Identify and analyse PASCAL functions '''

    def __init__(self, cx):
        self.cx = cx
        self.functions = {}
        self.discovered = set()

        while True:
            sofar = len(self.discovered)
            if not self.hunt_functions():
                break
            for _lo, func in sorted(self.functions.items()):
                if True:
                    try:
                        func.analyze()
                    except Exception as err:
                        print("ERROR", err)
                else:
                    func.analyze()
            if sofar == len(self.discovered):
                break

    def discover(self, where):
        if where in self.discovered:
            return
        self.discovered.add(where)
        adr = int(where, 16)
        try:
            self.cx.m[adr]
        except mem.MemError:
            return
        # print("OMSI Discover", where)
        self.cx.disass(adr)

    def render(self, file=sys.stdout):
        for _lo, func in sorted(self.functions.items()):
            func.render(file)

    def dot_file(self, file):
        for _lo, func in sorted(self.functions.items()):
            func.dot_file(file)

    def hunt_functions(self):
        ''' Hunt for more yet undiscovered functions '''
        did = False
        cur_func = None
        is_switch = False
        for i in self.cx.m:
            mne = getattr(i, "mne", None)
            if not mne and is_switch:
                continue
            if not mne:
                cur_func = None
                continue
            is_switch = i.mne == "SWITCH"
            if mne == "LINK.W" and cur_func:
                cur_func = None
            if mne == "LINK.W" and i.lo not in self.functions:
                cur_func = OmsiFunction(self, i.lo)
                self.functions[i.lo] = cur_func
                did = True
            elif mne == "RTS" and cur_func:
                cur_func.has_rts = True
                cur_func = None
            if cur_func:
                cur_func.append_code_ins(i)
        return did
