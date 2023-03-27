#!/usr/bin/env python3
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

from pyreveng import code, pil

from omsi import stack, function_call

PseudoCode = code.Decoder("pseudo")

class MatchHit():

    ''' Pop.match returns one of these to describe the hit '''

    def __init__(self, pop, idx, mins):
        self.pop = pop
        self.idx = idx
        self.mins = mins

    def __iter__(self):
        yield from self.mins

    def __len__(self):
        return len(self.mins)

    def __getitem__(self, idx):
        return self.mins[idx]

    def getstack(self):
        ''' Get stack image '''
        return self.pop.getstack(self.idx)

    def replace(self, pop):
        ''' Peplace the hit with a pseudo-op of the given class '''
        for i in self.mins:
            self.pop.del_ins(i)
            pop.append_ins(i)
        self.pop.insert_ins(self.idx, pop)
        return pop

    def render(self, file=sys.stdout):
        ''' Render the hit usably '''
        file.write("HIT %s\n" % hex(self.mins[0].lo))
        for i in self.mins:
            file.write("   " + str(i) + "\n")

class Pop():

    ''' Pseudo-Op base class '''

    kind = "Naked"
    overhead = False
    compact = False

    def __init__(self):
        self.lo = -1
        self.hi = -1
        self.ins = []
        self.come_from = []
        self.go_to = []
        self.stack_delta = 0
        self.stack_adj = False
        self.stack_level = None
        self.txt = self.kind

    def __iter__(self):
        yield from self.ins

    def __len__(self):
        return len(self.ins)

    def __lt__(self, other):
        return self.lo < other.lo

    def __getitem__(self, idx):
        return self.ins[idx]

    def index(self, pop):
        ''' Index of element '''
        assert isinstance(pop, Pop)
        return self.ins.index(pop)

    def render(self, pfx="", cx=None):
        ''' Render recursively '''
        hdr = (pfx + str(self)).expandtabs().ljust(60)
        if self.stack_level is not None:
            hdr += " Σ" + str(self.stack_level)
        if self.stack_delta:
            hdr += " Δ%+d" % self.stack_delta
        flow = []
        for dst in self.go_to:
            if dst.lo == self.hi:
                flow.append("↓")
        for dst in self.go_to:
            if dst.lo != self.hi:
                flow.append("→" + hex(dst.lo))
        for src in self.come_from:
            if src.hi != self.lo:
                flow.append("←" + hex(src.lo))
        yield hdr.expandtabs().ljust(72) + " ".join(flow)
        if self.compact:
            return
        sptr = stack.Stack()
        if self.stack_level and self.stack_level < 0:
            sptr.push(stack.StackItem(-self.stack_level, None))
        for i in self.ins:
            j = list(i.render(pfx + "    ", cx))
            if self.kind == "Naked":
                i.update_stack(sptr)
                txt = j[0].expandtabs().ljust(80)
                yield txt + sptr.render()
                if len(j) > 1:
                    yield from j[1:]
            else:
                yield from j

    def getstack(self, idx):
        ''' Get stackimage seen at idx '''
        assert self.kind == "Naked"
        sptr = stack.Stack()
        if self.stack_level and self.stack_level < 0:
            sptr.push(stack.StackItem(-self.stack_level, None))
        for i, j in enumerate(self.ins):
            if i == idx:
                return sptr
            j.update_stack(sptr)
        return None

    def flow_to(self):
        ''' Where next ? '''
        yield ('N', self.hi)

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
        if self.kind not in ("Body", "Naked"):
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

    def update_stack(self, _sp):
        ''' Updated stack image '''
        return

class PopBody(Pop):
    ''' The body of a function '''
    kind = "Body"

class PopMIns(Pop):
    ''' Machine Instruction '''
    kind = "MIns"

    def __init__(self, ins):
        super().__init__()
        self.ins = ins
        self.lo = ins.lo
        self.hi = ins.hi
        self.txt = ins.render()
        self.pop = None
        self.compact = True

    def __repr__(self):
        txt = "<MI %05x " % self.lo
        return txt + " " + self.txt + ">"

    def __getitem__(self, idx):
        return self.txt.split()[1].split(",")[idx]

    def __len__(self):
        ''' Number of arguments '''
        if ',' not in self.txt:
            return 0
        i = self.txt.split()[1].split(",")
        return len(i)

    def get(self, idx, dfl=None):
        ''' Get argument '''
        i = self.txt.split()[1].split(",")
        if idx < len(i):
            return i[idx]
        return dfl

    def data_width(self):
        ''' Width of instruction data '''
        return { "B": 1, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

    def stack_width(self):
        ''' Width of instruction data on stack '''
        return { "B": 2, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

    def flow_to(self):
        for i in self.ins.flow_out:
            yield (i.typ, i.to)

    def set_stack_delta(self):
        ''' set the stack delta for this instruction '''
        if "PEA.L" in self.txt:
            self.stack_delta = -4
        elif "-(A7)" in self.txt:
            self.stack_delta = - self.stack_width()
        elif "(A7)+" in self.txt:
            self.stack_delta = self.stack_width()
        elif "A7" in self.txt:
            if "(A7)" in self.txt:
                return
            if "A7+0x" in self.txt:
                return
            if "MOVE" in self.txt and "A7," in self.txt:
                return
            if "ADDQ.L" in self.txt:
                oper = self[0]
                assert oper[0] == "#"
                self.stack_delta = int(oper[1:], 16)
            elif "ADDA.W" in self.txt and self[0][0] == "#":
                oper = self[0]
                assert oper[0] == "#"
                self.stack_delta = int(oper[1:], 16)
            elif "SUBQ.L" in self.txt and self[0][0] == "#":
                oper = self[0]
                assert oper[0] == "#"
                self.stack_delta = -int(oper[1:], 16)
            elif "SUBA.W" in self.txt and self[0][0] == "#":
                oper = self[0]
                assert oper[0] == "#"
                self.stack_delta = -int(oper[1:], 16)
            elif self[0] == "(A5+0x8)" and self[1] == "A7":
                # Part of bailout
                pass
            else:
                print("SD A7", self)


    def update_stack(self, sp):
        if "PEA.L" in self.txt:
            arg = self.txt.split()[1]
            if "(A7+0x" in arg:
                offset = int(arg[3:-1], 16)
                sp.push(stack.StackItemReference(offset))
            else:
                sp.push(stack.StackItem(4, "^" + arg))
        elif "-(A7)" in self.txt:
            width = self.stack_width()
            if "MOVE" in self.txt:
                arg = self.txt.split()[1].split(",")[0]
                if arg[:3] == "#0x" and "MOVE.W" in self.txt:
                    sp.push(stack.StackItemInt(int(arg[3:], 16)))
                elif arg[:3] == "#0x" and "MOVE.L" in self.txt:
                    sp.push(stack.StackItemLong(int(arg[3:], 16)))
                else:
                    sp.push(stack.StackItem(width, arg))
            elif "CLR.W" in self.txt:
                sp.push(stack.StackItemInt(0))
            elif "CLR.B" in self.txt:
                sp.push(stack.StackItemInt(0))
            elif "CLR.W" in self.txt:
                sp.push(stack.StackItemInt(0))
            else:
                sp.push(stack.StackItem(width, "something"))
        elif "(A7)+" in self.txt:
            sp.pop(self.stack_width())
        elif ",(A7)" in self.txt:
            width = self.stack_width()
            if "MOVE" in self.txt:
                sp.pop(width)
                arg = self.txt.split()[1].split(",")[0]
                if arg[:3] == "#0x" and "MOVE.W" in self.txt:
                    sp.push(stack.StackItemInt(int(arg[3:], 16)))
                elif arg[:3] == "#0x" and "MOVE.L" in self.txt:
                    sp.push(stack.StackItemLong(int(arg[3:], 16)))
                elif "MOVE.B" in self.txt:
                    sp.push(stack.StackItem(width, None))
                else:
                    sp.push(stack.StackItem(width, arg))
            else:
                sp.pop(width)
                sp.push(stack.StackItem(width, None))
                # print("SM", self)

class PopConst(Pop):
    ''' Constant pushes '''
    kind = "Const"
    compact = True

    def __init__(self, width, val, push):
        super().__init__()
        if 0 and not push:
            self.stack_delta = width
        self.width = width
        self.val = val
        self.push = push

    def __str__(self):
        txt = "<Const %d.%d" % (self.val, self.width)
        if self.push:
            txt += " push"
        else:
            txt += " replace"
        return txt + ">"

    def update_stack(self, sp):
        if not self.push:
            sp.pop(self.width)
        if self.width == 4:
            sp.push(stack.StackItemLong(self.val))
        elif self.width == 2:
            sp.push(stack.StackItemInt(self.val))

class PopStackPointer(Pop):
    ''' Stack relative pointer pushes '''
    kind = "Pointer.sp"
    compact = True

    def __init__(self, offset):
        super().__init__()
        self.offset = offset

    def __str__(self):
        return "<Pointer.sp %s %d>" % (hex(self.lo), self.offset)

    def update_stack(self, sp):
        sp.push(stack.StackItemReference(self.offset))

class PopFramePointer(Pop):
    ''' Frame relative pointer pushes '''
    kind = "Pointer.fp"
    compact = True

    def __init__(self, offset, lvar=None):
        super().__init__()
        self.offset = offset
        self.lvar = lvar

    def __str__(self):
        if self.lvar:
            return "<Pointer.fp %s %s>" % (hex(self.lo), str(self.lvar))
        return "<Pointer.fp %s %d>" % (hex(self.lo), self.offset)

    def update_stack(self, sp):
        sp.push(stack.FrameItemReference(self.offset))

class PopStackAdj(Pop):
    ''' Adjustments to stack pointer'''
    kind = "StackAdj"
    compact = True

    def __init__(self, delta):
        super().__init__()
        self.stack_delta = delta

    def update_stack(self, sp):
        if self.stack_delta < 0:
            sp.push(stack.StackItem(-self.stack_delta, None))
        elif self.stack_delta > 0:
            sp.pop(self.stack_delta)

class PopStackCheck(Pop):
    ''' Stack level check '''
    kind = "StackCheck"
    overhead = True
    compact = True

class PopPrologue(Pop):
    ''' Pseudo-Op for function Prologue '''
    kind = "Prologue"
    overhead = True
    compact = True

class PopEpilogue(Pop):
    ''' Pseudo-Op for function Epilogue '''
    kind = "Epilogue"
    overhead = True
    compact = True

    def flow_to(self):
        if False:
            yield None

class PopBlob(Pop):
    ''' Pseudo-Op for literal bytes '''
    kind = "Blob"
    compact = True

    def __init__(self, blob=None, width=None, src=None, push=True):
        super().__init__()
        if blob:
            width = len(blob)
        self.blob = blob
        self.width = width
        self.src = src
        self.push = push
        #if not push:
        #    self.stack_delta = width

    def __repr__(self):
        txt = "<Blob %s [%d]" % (hex(self.lo), self.width)
        if self.blob:
            txt += " @"
        elif isinstance(self.src, int):
            txt += " " + hex(self.src)
        elif self.src:
            txt += " " + str(self.src)
        return txt + ">"

    def update_stack(self, sp):
        if not self.push:
            sp.pop(self.width)
        if self.blob:
            sp.push(stack.StackItemBlob(blob=self.blob))
        else:
            sp.push(stack.StackItemBlob(width=self.width))

class PopStackPop(Pop):
    ''' Pseudo-Op for copying things from stack '''
    kind = "StackPop"

class PopBailout(Pop):
    ''' Pseudo-Op for bailing out of context'''
    kind = "Bailout"

    def flow_to(self):
        if False:
            yield None

class PopCall(Pop):
    ''' Pseudo-Op for function calls '''
    kind = "Call"

    def __init__(self, dst, lbl=None):
        super().__init__()
        self.dst = dst
        self.lbl = lbl

    def __repr__(self):
        return "<Call 0x%05x 0x%05x>" % (self.lo, self.dst)

    def render(self, pfx="", cx=None):
        yield pfx + str(self)
        if self.lbl:
            yield pfx + "    " + self.lbl
        elif cx:
            lbls = list(cx.m.get_labels(self.dst))
            if lbls:
                yield pfx + "    " + lbls[0]

    def flow_to(self):
        yield ("N", self.hi)

    def update_stack(self, sp):
        function_call.FunctionCall(self, sp)

class PopLimitCheck(Pop):
    ''' Pseudo-Op for limit checks'''
    kind = "LimitCheck"
    compact = True

class PopMallocCheck(Pop):
    ''' Pseudo-Op for malloc'ed pointer '''
    kind = "MallocCheck"
    compact = True

    def __init__(self, areg):
        super().__init__()
        self.areg = areg

    def __repr__(self):
        return "<MallocCheck %s %s>" % (hex(self.lo), self.areg)

class PopBlockMove(Pop):
    ''' Pseudo-Op for block move loops'''
    kind = "BlockMove"
    compact = True

    def __init__(self, src, dst, length):
        super().__init__()
        self.src = src
        self.dst = dst
        self.length = length

    def __repr__(self):
        return "<BlockMove %d,%s,%s>" % (self.length, self.src, self.dst)

    def update_stack(self, sp):
        if self.src != "A7" and self.dst != "A7":
            return
        if self.length > 0:
            sp.pop(self.length)
        else:
            sp.push(stack.StackItemBlob(width=-self.length))

class PopRegCacheLoad(Pop):
    ''' Pseudo-Op for loading register caches'''
    kind = "RegCacheLoad"
    overhead = True
    compact = True

class PopStringLit(Pop):
    ''' Push string literal '''
    kind = "StringLit"

    def __init__(self, txt=None):
        super().__init__()
        self.txt = txt
        self.stack_delta = 0
        if self.txt:
            self.compact = True

    def __str__(self):
        if self.txt:
            return "<Lit %s %d>" % (hex(self.lo), len(self.txt))
        return "<Lit %s>" % hex(self.lo)

    def update_stack(self, sp):
        sp.put(0, stack.StackItemString(self.txt))
