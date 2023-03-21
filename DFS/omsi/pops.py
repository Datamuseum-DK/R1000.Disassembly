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

from pyreveng import code, pil, mem, assy, data

from .stack import *
from .function_call import *

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
        sp = Stack()
        if self.stack_level and self.stack_level < 0:
            sp.push(StackItem(-self.stack_level, None))
        for i in self.ins:
            j = list(i.render(pfx + "    "))
            if self.kind == "Naked":
                i.update_stack(sp)
                if len(j) > 1:
                    yield from j
                    j = [""]
                j = j[0]
                while len(j.expandtabs()) < 80:
                    j += "\t"
                yield j.expandtabs() + sp.render()
            else:
                yield from j

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

    def update_stack(self, stack):
        return

class PopBody(Pop):
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

    def update_stack(self, sp):
        if "ADDQ.L" in self.txt and ",A7" in self.txt:
            i = self.txt.split()[-1].split(",")[0]
            assert i[:3] == "#0x"
            sp.pop(int(i[1:], 16))
        elif "ADDA.W" in self.txt and ",A7" in self.txt:
            i = self.txt.split()[-1].split(",")[0]
            assert i[:3] == "#0x"
            sp.pop(int(i[1:], 16))
        elif "SUBQ.L" in self.txt and ",A7" in self.txt:
            i = self.txt.split()[-1].split(",")[0]
            assert i[:3] == "#0x"
            sp.push(StackItem(int(i[1:], 16), None))
        elif "SUBA.W" in self.txt and ",A7" in self.txt:
            i = self.txt.split()[-1].split(",")[0]
            assert i[:3] == "#0x"
            sp.push(StackItem(int(i[1:], 16), None))
        elif "PEA.L" in self.txt:
            arg = self.txt.split()[1]
            if "(A7+0x" in arg:
                offset = int(arg[3:-1], 16)
                sp.push(StackItemBackReference(offset))
            else:
                sp.push(StackItem(4, "^" + arg))
        elif ",-(A7)" in self.txt:
            width = self.stack_width()
            if "MOVE" in self.txt:
                arg = self.txt.split()[1].split(",")[0]
                if arg[:3] == "#0x" and "MOVE.W" in self.txt:
                    sp.push(StackItemInt(int(arg[3:], 16)))
                elif arg[:3] == "#0x" and "MOVE.L" in self.txt:
                    sp.push(StackItemLong(int(arg[3:], 16)))
                else:
                    sp.push(StackItem(width, arg))
            else:
                sp.push(StackItem(width, "something"))
        elif "(A7)+," in self.txt:
            sp.pop(self.stack_width())
        elif "JSR" in self.txt:
            oper = self.ins.oper[0]
            arg = self.txt.split()[1]
            if isinstance(oper, assy.Arg_dst):
                FunctionCall(self, oper.dst, sp)
            elif arg[:2] == "0x":
                FunctionCall(self, int(arg, 16), sp)
            else:
                print("JSR", self, arg)

class PopPrologue(Pop):
    ''' Pseudo-Op for function Prologue '''
    kind = "Prologue"

class PopEpilogue(Pop):
    ''' Pseudo-Op for function Epilogue '''
    kind = "Epilogue"

class PopStackPush(Pop):
    ''' Pseudo-Op for copying things onto stack '''
    kind = "StackPush"

    def __init__(self):
        super().__init__()
        self.string = ""
        self.srcadr = None
        self.srclen = None

    def render(self, pfx=""):
        txt = pfx + "<STACKPUSH +0x%x> " % self.srclen
        if self.string:
            yield txt + " \"%s\"" % self.string.txt
        else:
            yield txt + " " + str(type(self.srcadr)) + " " + str(self.srcadr.render())
        # yield from super().render(pfx)

    def point(self, cx, srcadr, srclen):
        self.srcadr = srcadr
        self.srclen = srclen
        if isinstance(srcadr, assy.Arg_dst):
            self.ptr = srcadr.dst
            self.string = data.Txt(cx.m, self.ptr, self.ptr + self.srclen)
            self.string.compact = False

    def update_stack(self, sp):
        if self.string:
           sp.push(StackItemStringLiteral(self.srclen, self.string.txt))
        else:
           sp.push(StackItem(self.srclen, '"…"'))

         

class PopStackPop(Pop):
    ''' Pseudo-Op for copying things from stack '''
    kind = "StackPop"

class PopTextPush(Pop):
    ''' Pseudo-Op for pushing string literal on stack '''
    kind = "TextPush"

    def __init__(self):
        super().__init__()
        self.string = ""
        self.srcadr = None
        self.srclen = None

    def render(self, pfx=""):
        txt = pfx + "<TEXTPUSH +0x%x> " % self.srclen
        if self.string:
            yield txt + " \"%s\"" % self.string.txt
        else:
            yield txt + " " + str(type(self.srcadr)) + " " + str(self.srcadr.render())
        # yield from super().render(pfx)

    def point(self, cx, srcadr, srclen):
        self.srcadr = srcadr
        self.srclen = srclen
        if isinstance(srcadr, assy.Arg_dst):
            self.ptr = srcadr.dst - self.srclen
            try:
                self.string = data.Txt(cx.m, self.ptr, self.ptr + self.srclen)
                self.string.compact = False
            except mem.MemError:
                print("TP fail", hex(self.ptr), hex(self.srclen))
                pass

    def update_stack(self, sp):
        if self.string:
           sp.push(StackItemStringLiteral(self.srclen, self.string.txt))
        else:
           sp.push(StackItem(self.srclen, '"…"'))


class PopBailout(Pop):
    ''' Pseudo-Op for bailing out of context'''
    kind = "Bailout"

class PopLimitCheck(Pop):
    ''' Pseudo-Op for limit checks'''
    kind = "LimitCheck"

class PopRegCacheLoad(Pop):
    ''' Pseudo-Op for loading register caches'''
    kind = "RegCacheLoad"
