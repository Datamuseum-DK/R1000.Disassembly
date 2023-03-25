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

    def replace(self, pop):
        ''' Peplace the hit with a pseudo-op of the given class '''
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
    overhead = False

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
        assert isinstance(pop, Pop)
        return self.ins.index(pop)

    def render(self, pfx="", cx=None):
        ''' Render recursively '''
        hdr = pfx + str(self) + " d%+d" % self.stack_delta + " [" + str(self.stack_level) + "]"
        for src in self.come_from:
            hdr += "  <-" + hex(src.lo)
        for dst in self.go_to:
            hdr += "  ->" + hex(dst.lo)
        yield hdr
        sptr = stack.Stack()
        if self.stack_level and self.stack_level < 0:
            sptr.push(stack.StackItem(-self.stack_level, None))
        for i in self.ins:
            j = list(i.render(pfx + "    ", cx))
            if self.kind == "Naked":
                i.update_stack(sptr)
                if len(j) > 1:
                    yield from j
                    j = [""]
                j = j[0]
                j += "\t"
                while len(j.expandtabs()) < 80:
                    j += "\t"
                yield j.expandtabs() + sptr.render()
            else:
                yield from j

    def flow_to(self):
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

    def __repr__(self):
        txt = "<MI %05x d%+d" % (self.lo, self.stack_delta)
        return txt + " " + self.txt + ">"

    def __getitem__(self, idx):
        return self.txt.split()[1].split(",")[idx]

    def __len__(self):
        ''' Number of arguments '''
        if not ',' in self.txt:
            return 0
        i = self.txt.split()[1].split(",")
        return len(i)

    def get(self, idx, dfl=None):
        ''' Get argument '''
        i = self.txt.split()[1].split(",")
        if idx < len(i):
            return i[idx]
        return dfl

    def render(self, pfx="", cx=None):
        yield pfx + str(self)

    def data_width(self):
        ''' Width of instruction data '''
        return { "B": 1, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

    def stack_width(self):
        ''' Width of instruction data on stack '''
        return { "B": 2, "W": 2, "L": 4, }[self.ins.mne.split(".")[-1]]

    def flow_to(self):
        for i in self.ins.flow_out:
            yield (i.typ, i.to)

    def update_stack(self, sp):
        if "PEA.L" in self.txt:
            arg = self.txt.split()[1]
            if "(A7+0x" in arg:
                offset = int(arg[3:-1], 16)
                sp.push(stack.StackItemBackReference(offset))
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

class PopStackAdj(Pop):
    ''' Adjustments to stack pointer'''
    kind="StackAdj"
    def __init__(self, delta):
        super().__init__()
        self.delta = delta
        self.stack_delta = delta

    def update_stack(self, sp):
        if self.delta < 0:
            sp.push(stack.StackItem(-self.delta, None))
        elif self.delta > 0:
            sp.pop(self.delta)

    def render(self, pfx="", cx=None):
        yield pfx + "<StackAdj %+d>" % self.delta

class PopStackCheck(Pop):
    ''' Stack level check '''
    kind = "StackCheck"
    overhead = True

    def render(self, pfx="", cx=None):
        yield pfx + str(self)

class PopPrologue(Pop):
    ''' Pseudo-Op for function Prologue '''
    kind = "Prologue"
    overhead = True

    def render(self, pfx="", cx=None):
        yield pfx + "<Prologue>"

class PopEpilogue(Pop):
    ''' Pseudo-Op for function Epilogue '''
    kind = "Epilogue"
    overhead = True

    def render(self, pfx="", cx=None):
        yield pfx + "<Epilogue>"

    def flow_to(self):
        if False:
            yield None

class PopBlob(Pop):
    ''' Pseudo-Op for literal bytes '''
    kind = "Blob"

    def __init__(self, blob=None, width=None, src=None):
        super().__init__()
        if blob:
            width = len(blob)
        self.blob = blob
        self.width = width
        self.src = src
        self.stack_delta = - width

    def __repr__(self):
        txt = "<Blob [%d]" % self.width
        if self.blob:
            txt += " @"
        elif isinstance(self.src, int):
            txt += " " + hex(self.src)
        elif self.src:
            txt += " " + str(self.src)
        return txt + ">"

    def render(self, pfx="", cx=None):
        yield pfx + str(self)

    def update_stack(self, sp):
        if self.blob:
            sp.push(stack.StackItemBlob(blob=self.blob))
        else:
            sp.push(stack.StackItemBlob(width=self.width))

class PopStackPop(Pop):
    ''' Pseudo-Op for copying things from stack '''
    kind = "StackPop"

    def _render(self, pfx=""):
        yield pfx + str(self)

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

    def render(self, pfx="", cx=None):
        yield pfx + str(self)

class PopBlockMove(Pop):
    ''' Pseudo-Op for block move loops'''
    kind = "BlockMove"

    def __init__(self, src, dst, length):
        super().__init__()
        self.src = src
        self.dst = dst
        self.length = length

    def __repr__(self):
        return "<BlockMove [%d] %s -> %s>" % (self.length, self.src, self.dst)

    def render(self, pfx="", cx=None):
        yield pfx + str(self)

class PopRegCacheLoad(Pop):
    ''' Pseudo-Op for loading register caches'''
    kind = "RegCacheLoad"
    overhead = True

    def render(self, pfx="", cx=None):
        yield pfx + "<RegCacheLoad>"
