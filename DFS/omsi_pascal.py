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

from pyreveng import code, data, mem, pil, assy

PseudoCode = code.Decoder("pseudo")

class MatchHit():

    def __init__(self, stmt, idx, mins):
        self.stmt = stmt
        self.idx = idx
        self.mins = mins
        self.lo = mins[0].lo

    def __iter__(self):
        yield from self.mins

    def __len__(self):
        return len(self.mins)

    def __getitem__(self, idx):
        return self.mins[idx]

    def replace(self, cls):
        pop = cls(self.lo)
        for i in self.mins:
            self.stmt.del_ins(i)
            pop.add_ins(i)
        self.stmt.ins.insert(self.idx, pop)
        return pop

    def render(self, file=sys.stdout):
        file.write("HIT\n")
        for i in self.mins:
            file.write("   " + str(i) + "\n")

class Pop():

    ''' Pseudo-Op base class '''

    kind = "Naked"

    def __init__(self, lo):
        self.lo = lo
        self.hi = lo
        self.ins = []
        self.txt = ""
        self.come_from = []
        self.go_to = []
        self.stack_delta = 0
        self.stack_adj = False

    def __iter__(self):
        yield from self.ins

    def __len__(self):
        return len(self.ins)

    def __getitem__(self, idx):
        return self.ins[idx]

    def render(self, pfx=""):
        hdr = pfx + str(self) + " d%+d" % self.stack_delta
        for src in self.come_from:
            hdr += "  <-" + hex(src.lo)
        for dst in self.go_to:
            hdr += "  ->" + hex(dst.lo)
        yield hdr
        for i in self.ins:
            yield from i.render(pfx + "    ")

    def add_ins(self, ins):
        assert isinstance(ins, Pop)
        assert ins.lo >= self.hi
        ins.pop = self
        self.ins.append(ins)
        self.hi = ins.hi

    def del_ins(self, ins):
        assert isinstance(ins, Pop)
        i = self.ins.index(ins)
        self.ins.remove(ins)

    def __repr__(self):
        return "<POP %05x-%05x %s>" % (self.lo, self.hi, self.kind)

    def match(self, pattern):
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
        super().__init__(ins.lo)
        self.ins = ins
        self.hi = ins.hi
        self.txt = ins.render()
        self.pop = None

    def __repr__(self):
        txt = "<MI %05x d%+d" % (self.lo, self.stack_delta)
        if self.stack_adj:
            txt += "."
        return txt + " " + self.txt + ">"

    def render(self, pfx):
        yield pfx + str(self)

class PopPrologue(Pop):

    ''' Pseudo-Op for function Prologue '''

    kind = "Prologue"

class PopEpilogue(Pop):

    ''' Pseudo-Op for function Epilogue '''

    kind = "Epilogue"

class PopMemCpy(Pop):

    ''' Pseudo-Op for memcpy(3) style copy '''

    kind = "MemCpy"

class PopTextPush(Pop):

    ''' Pseudo-Op for pushing string literal on stack '''

    kind = "TextPush"

class PopLimitCheck(Pop):

    ''' Pseudo-Op for limit checks'''

    kind = "LimitCheck"

class PopRegCacheLoad(Pop):

    ''' Pseudo-Op for loading register caches'''

    kind = "RegCacheLoad"

class OmsiFunction():
    ''' A single function '''

    def __init__(self, up, lo):
        self.up = up
        self.lo = lo
        self.stmts = {lo: Pop(lo)}

    def __iter__(self):
        for _lo, stmt in sorted(self.stmts.items()):
            yield from stmt

    def render(self, file=sys.stdout):
        ''' Render to text '''
        file.write("OF %05x\n" % self.lo)
        for _lo, stmt in sorted(self.stmts.items()):
            for i in stmt.render(pfx="    "):
                file.write(i + "\n")

    def add_code_ins(self, ins):
        ''' Add another M68K instruction '''
        self.stmts[self.lo].add_ins(PopMIns(ins))

    def analyze(self):
        ''' Analyze '''
        if not self.find_prologue():
            return
        self.find_epilogue()
        self.prune_switch()
        self.uncache_registers()
        self.assign_stack_delta()
        self.find_memcpy()
        self.find_textpush()
        self.find_limit_check_1()
        self.find_limit_check_2()
        self.find_limit_check_3()
        self.find_limit_check_4()
        self.partition()

    def find_prologue(self):
        for stmt in self.stmts.values():
            for hit in stmt.match(
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
                    pop = hit.replace(PopPrologue)
                    return True
        for stmt in self.stmts.values():
            for hit in stmt.match(
                (
                    ("LINK.W",),
                    ("MOVEM.L",),
                    ("CMPA.L", "(A5),A7",),
                    ("tRAPV",),
                )
            ):
                if len(hit) == 4:
                    pop = hit.replace(PopPrologue)
                    return True

    def find_epilogue(self):
        for stmt in self.stmts.values():
            for hit in stmt.match(
                (
                    ("MOVEM.L", "(A7)+",),
                    ("UNLK",),
                )
            ):
                if len(hit) == 2:
                    pop = hit.replace(PopEpilogue)
                    return

    def prune_switch(self):
        for stmt in self.stmts.values():
            for hit in stmt.match(
                (
                    ("SWITCH", ),
                    ("CONST", ),
                )
            ):
                if len(hit) < 2:
                    continue
                while True:
                    ins = stmt[hit.idx + 1]
                    if not isinstance(ins.ins, data.Const):
                        break
                    stmt.ins.pop(hit.idx + 1)

    def assign_stack_delta(self):
        for stmt in self.stmts.values():
            for ins in stmt:
                if "PEA.L" in ins.txt:
                    ins.stack_delta = -4
                elif "-(A7)" in ins.txt:
                    opsz = ins.ins.mne.split(".")[-1]
                    ins.stack_delta = {
                        "B": -2,
                        "W": -2,
                        "L": -4,
                    }[opsz]
                elif "(A7)+" in ins.txt:
                    opsz = ins.ins.mne.split(".")[-1]
                    ins.stack_delta = {
                        "B": 2,
                        "W": 2,
                        "L": 4,
                    }[opsz]
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
                        ins.stack_delta = -int(oper[1:], 16)
                    elif "ADDA.W" in ins.txt:
                        ins.stack_adj = True
                        oper = ins.txt.split()[1].split(",")[0]
                        assert oper[0] == "#"
                        ins.stack_delta = -int(oper[1:], 16)
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

    def find_memcpy(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
                (
                    ("SUBA.W",),
                    ("MOVEA.L",),
                    ("LEA.L",),
                    ("MOVEQ.L",),
                    ("MOVE.B",),
                    ("DBF",),
                )
            ):
                if len(hit) < 6:
                    continue
                src = str(hit[2].ins.oper[0])
                srcreg = str(hit[2].ins.oper[1])
                cnt = hit[3].ins.oper[0]
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
                pop = hit.replace(PopMemCpy)
                pop.stack_delta = pop.ins[0].stack_delta

    def find_textpush(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
                (
                    ("LEA.L",),
                    ("MOVEQ.L",),
                    ("MOVE.",),
                    ("DBF",),
                )
            ):
                if len(hit) < 4:
                    continue
                src = str(hit[0].ins.oper[0])
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
                pop.stack_delta = - (int(cnt[1:], 16))
                opsz = hit[2].ins.mne.split(".")[-1]
                if opsz == "W":
                    pop.stack_delta *= 2
                elif opsz == "L":
                    pop.stack_delta *= 4

    def find_limit_check_1(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
                (
                    ("CMP",),
                    ("BLS",),
                    ("TRAP",),
                )
            ):
                if len(hit) < 3:
                    continue

                if hit[1].ins.flow_out[0].to != hit[2].ins.hi:
                    continue

                if "#15" not in hit[2].txt and "#14" not in hit[2].txt:
                    continue

                hit.replace(PopLimitCheck)

    def find_limit_check_2(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
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

    def find_limit_check_3(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
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

    def find_limit_check_4(self):
        for stmt in list(self.stmts.values()):
            for hit in stmt.match(
                (
                    ("cHK.W",),
                )
            ):
                if len(hit) < 1:
                    continue
                hit.replace(PopLimitCheck)

    def uncache_registers(self):
        pop = None
        leal = True
        for stmt in list(self.stmts.values()):
            idx = 1
            while idx < len(stmt):
                ins = stmt[idx]
                if "LEA.L" not in ins.txt:
                    break
                reg = str(ins.ins.oper[-1])
                writes = stmt.reg_writes(reg)
                # print("UCR", writes, ins)
                if writes != 1:
                    break
                if not pop:
                    pop = PopRegCacheLoad(ins.lo)
                stmt.del_ins(ins)
                pop.add_ins(ins)
            while idx < len(stmt):
                ins = stmt[idx]
                if "MOVEQ" not in ins.txt:
                    break
                reg = str(ins.ins.oper[-1])
                writes = stmt.reg_writes(reg)
                if writes != 1:
                    break
                if not pop:
                    pop = PopRegCacheLoad(ins.lo)
                stmt.del_ins(ins)
                pop.add_ins(ins)
            break
        if not pop:
            return
        # We know there is a prologue
        stmt.ins.insert(1, pop)
        for ins in pop.ins:
            src = str(ins.ins.oper[1])
            dst = ins.ins.oper[0]
            if isinstance(dst, assy.Arg_verbatim):
                dst = str(dst)
            elif isinstance(dst, assy.Arg_dst):
                dst = "0x%x" % dst.dst
            else:
                print("RCL unknown arg", ins, type(dst), dst)
                continue
            if src[0] == "A":
                src = "(" + src + ")"
            for rins in stmt.ins:
                if not isinstance(rins, PopMIns):
                    continue
                if src not in rins.txt:
                    continue
                rins.txt = rins.txt.replace(src, dst)

    def partition(self):
        starts = set()
        for stmt in list(self.stmts.values()):
            for ins in stmt:
                if not starts and isinstance(ins, PopMIns):
                    starts.add(ins.lo)
                flow_out = getattr(ins.ins, "flow_out", [])
                for flow in flow_out:
                    if flow.typ in ("C", "N"):
                        continue
                    starts.add(flow.to)
        pop = None
        pops = []
        for stmt in list(self.stmts.values()):
            idx = 1
            while not isinstance(stmt[idx], PopMIns):
                idx += 1
            while idx < len(stmt):
                ins = stmt[idx]
                if isinstance(ins, PopEpilogue):
                    break
                if ins.lo in starts:
                    pop = Pop(ins.lo)
                    pops.append(pop)
                    stmt.ins.insert(idx, pop)
                    self.stmts[pop.lo] = pop
                    idx += 1
                stmt.del_ins(ins)
                pop.add_ins(ins)
        for pop in pops:
            ins = pop[-1]
            flow_out = getattr(ins.ins, "flow_out", [])
            for flow in flow_out:
                if flow.typ in ("C",):
                    continue
                stmt2 = self.stmts.get(flow.to)
                if stmt2:
                    pop.go_to.append(stmt2)
                    stmt2.come_from.append(pop)
                else:
                    print("S2?.st?", hex(flow.to))
            

class OmsiPascal():

    def __init__(self, cx):
        self.cx = cx
        self.functions = {}

        while True:
            if not self.hunt_functions():
                break
            continue
            targets = []
            for adr, func in sorted(self.functions.items()):
                targets += list(func.hunt_reg_calls())
            targets = set(targets)
            for adr in sorted(targets):
                try:
                    i = cx.m[adr]
                except mem.MemError:
                    continue
                cx.disass(adr)

        for _lo, func in sorted(self.functions.items()):
            func.analyze()

        for _lo, func in sorted(self.functions.items()):
            func.render()

    def hunt_functions(self):
        did = False
        cur_func = None
        for i in self.cx.m:
            mne = getattr(i, "mne", None)
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
                cur_func.add_code_ins(i)
        return did
