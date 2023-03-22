
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

from pyreveng import mem, assy

from omsi import pops

class OmsiFunction():
    ''' A PASCAL function '''

    def __init__(self, up, lo):
        self.up = up
        self.lo = lo
        self.body = pops.PopBody()
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
        self.body.append_ins(pops.PopMIns(ins))

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
        self.find_stack_adj()

        prev = ""
        for ins in self.body:
            if ins.kind == "Naked" and "DB" in ins.txt and "A7" in prev:
                print("NB: unspotted stack loop", prev, ins.txt)
            prev = ins.txt

        self.assign_stack_delta()
        self.find_limit_checks()
        self.find_block_moves()
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
                hit.replace(pops.PopPrologue())
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
                hit.replace(pops.PopPrologue())
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
                hit.replace(pops.PopEpilogue())
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
                pop = pops.PopRegCacheLoad()
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
                pop = pops.PopRegCacheLoad()
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
                if not isinstance(rins, pops.PopMIns):
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
            src = hit[2].ins.oper[0]
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
            pop = hit.replace(pops.PopStackPush())
            cnt = hit[0].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpush", cnt)
                hit.render()
                exit(2)
            pop.stack_delta = - int(cnt[3:], 16)
            pop.stack_delta *= hit[4].data_width()
            pop.point(self.up.cx, src, -pop.stack_delta)

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
            src = hit[2].ins.oper[0]
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
            pop = hit.replace(pops.PopStackPush())
            cnt = hit[1].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpush", cnt)
                hit.render()
                exit(2)
            pop.stack_delta = - int(cnt[3:], 16)
            pop.stack_delta *= hit[2].data_width()
            pop.point(self.up.cx, src, -pop.stack_delta)

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
            pop = hit.replace(pops.PopStackPop())
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
            src = hit[0].ins.oper[0]
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
            pop = hit.replace(pops.PopTextPush())
            cnt = 1 + int(cnt[1:], 16)
            pop.stack_delta = -cnt * hit[2].data_width()
            pop.point(self.up.cx, src, - pop.stack_delta)

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
            hit.replace(pops.PopBailout())

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
                    hit.replace(pops.PopLimitCheck())

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

                hit.replace(pops.PopLimitCheck())


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

                hit.replace(pops.PopLimitCheck())

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
            hit.replace(pops.PopLimitCheck())

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
            hit.replace(pops.PopLimitCheck())

        for hit in self.body.match(
            (
                ("cHK.W",),
            )
        ):
            if len(hit) < 1:
                continue
            hit.replace(pops.PopLimitCheck())

    def find_stack_adj(self):
        ''' Find limit checks '''

        for idx in range(len(self.body)):
            ins = self.body[idx]
            if not ",A7" in ins.txt:
                continue
            for mne, sign in (
                ("ADDQ.L", 1),
                ("SUBQ.L", -1),
                ("ADDA.W", 1),
                ("SUBA.W", -1),
            ):
                if mne not in ins.txt:
                    continue
                i = ins.txt.split()[-1].split(",")[0]
                assert i[:3] == "#0x"
                pop = pops.PopStackAdj(sign * int(i[1:], 16))
                self.body.del_ins(ins)
                pop.append_ins(ins)
                self.body.insert_ins(idx, pop)

    def find_block_moves(self):
        ''' Find block move loops '''

        def looks_good(hit):
            cntreg = hit[-3][1]
            if hit[-1][0] != cntreg:
                print("Bad BlockMove cntreg", hit[-1][0], hit[-2][1])
                hit.render()
                return False
            cnt = hit[-3][0]
            if cnt[:3] != "#0x":
                print("Bad BlockMove cnt", cnt)
                hit.render()
                return False
            cnt = int(cnt[1:], 16) * hit[-2].data_width()
            for i in (hit[-2][0], hit[-2][1]):
                if len(i) != 5 or i[:2] != "(A" or i[-2:] != ")+":
                    print("Bad BlockMove reg", i)
                    hit.render()
                    return False
            return cnt, hit[-2][0][1:3], hit[-2][1][1:3]

        for hit in self.body.match(
            (
                ("MOVEQ.L",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 3:
                continue
            i = looks_good(hit)
            if i:
                cnt, srcreg, dstreg = i
                hit.replace(pops.PopBlockMove(srcreg, dstreg, cnt))

        for hit in self.body.match(
            (
                ("MOVE.W",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 3:
                continue
            i = looks_good(hit)
            if i:
                cnt, srcreg, dstreg = i
                hit.replace(pops.PopBlockMove(srcreg, dstreg, cnt))

    def partition(self):
        ''' partition into basic blocks '''

        # Collect the start-address of all basic blocks
        starts = set()
        starts.add(self.body[0].lo)
        for ins in self.body:
            if not starts and isinstance(ins, pops.PopMIns):
                starts.add(ins.lo)
            for typ, where in ins.flow_to():
                if typ not in ("C", "N"):
                    assert hex(where)
                    starts.add(where)
        starts.add(self.body[-1].lo)
        # print("Q", [hex(x) for x in sorted(starts)])

        # Collect (psudo-)instructions into basic blocks
        pop = None
        allpops = {}
        idx = 0
        while idx < len(self.body):
            ins = self.body[idx]
            if ins.overhead:
                allpops[ins.lo] = ins
                idx += 1
                continue
            if ins.lo in starts or not pop:
                pop = pops.Pop()
                allpops[ins.lo] = pop
                self.body.insert_ins(idx, pop)
                idx += 1
            self.body.del_ins(ins)
            pop.append_ins(ins)

        # Tie basic blocks together
        for pop in allpops.values():
            if isinstance(pop, pops.PopEpilogue):
                continue
            ins = pop[-1]
            for typ, where in ins.flow_to():
                if typ in ("C",):
                    continue
                dst = allpops.get(where)
                if dst is None:
                    print("BLIND dst (switch to trap?)", ins, typ, hex(where))
                else:
                    pop.go_to.append(dst)
                    dst.come_from.append(pop)

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

        self.debug = False

        while True:
            sofar = len(self.discovered)
            if not self.hunt_functions():
                break
            for _lo, func in sorted(self.functions.items()):
                if self.debug:
                    try:
                        func.analyze()
                    except Exception as err:
                        print("ERROR", err)
                else:
                    func.analyze()
            if sofar == len(self.discovered):
                break

    def discover(self, where):
        ''' More code to disassemble '''
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
        ''' Render what we have found out '''
        for _lo, func in sorted(self.functions.items()):
            if self.debug:
                try:
                    func.render(file)
                except Exception as err:
                    file.write("\n\nEXCEPTION: %s\n\n" % str(err))
                    print("EXCEPTION in", func, err)
            else:
                func.render(file)

    def dot_file(self, file):
        ''' Emit dot(1) sources '''
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
