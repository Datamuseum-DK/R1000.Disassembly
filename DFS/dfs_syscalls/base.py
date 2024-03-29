#!/usr/bin/env python
#
# Copyright (c) 2012-2021 Poul-Henning Kamp <phk@phk.freebsd.dk>
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
   DFS system-calls
   ================
'''

from pyreveng import mem

import pascal
import rounds

SYSCALLS = {}
KERNCALLS = {}

class DfsSysCall(rounds.Rounds):
    ''' Base class for system-calls'''

    def __init__(self, adr, name, bcmt=None):
        SYSCALLS[adr] = self
        self.adr = adr
        self.name = name
        self.bcmt = bcmt
        if ':' in name:
            self.pascal = pascal.PascalDecl(name)
        elif '(void)' in name:
            self.pascal = pascal.PascalDecl(name)
        else:
            self.pascal = None

    def __repr__(self):
        return "<DfsSysCall 0x%x %s>" % (self.adr, self.name)

    def __lt__(self, other):
        return self.adr < other.adr 

    def set_block_comment(self, cx, adr):
        cx.m.set_block_comment(adr, self.name)
        if self.pascal:
            for i in self.pascal.stack_map():
                cx.m.set_block_comment(adr, i)
        if self.bcmt:
            cx.m.set_block_comment(adr, "=" * len(self.name))
            cx.m.set_block_comment(adr, self.bcmt)

    def flow_check(self, asp, ins):
        return

    def round_0(self, cx):
        cx.m.set_label(self.adr, self.name)
        self.set_block_comment(cx, self.adr)

    def round_1(self, cx):
        try:
            _v = cx.m[self.adr]
        except mem.MemError:
            return
        cx.disass(self.adr)

    def round_2(self, cx):
        y = list(cx.m.find(self.adr))
        if len(y) != 1:
            return
        ins = y[0]
        i = getattr(ins, "flow_out", [])
        if len(i) != 1:
            return
        f = i[0]
        if not isinstance(f.to, int):
            return
        cx.m.set_label(f.to, "_" + self.name)
        self.set_block_comment(cx, f.to)

class DfsKernCall(DfsSysCall):
    ''' KERNEL system-call '''
    def __init__(self, number, name=None, **kwargs):
        adr = 0x10200 + 2 * number
        if name is None:
            name = "KERNCALL_%02x" % number
        super().__init__(adr, name, **kwargs)

class DfsFsCall(DfsSysCall):
    ''' FS system-call '''

    def __init__(self, adr, name=None, dead=False, **kwargs):
        if name is None:
            name = "FSCALL_%x" % adr
        super().__init__(adr, name, **kwargs)
        self.dead = dead

    def flow_check(self, asp, ins):
        if self.dead:
            ins.flow_out.pop(-1)

class DfsSysCalls(rounds.Rounds):
    ''' ... '''

    def __init__(self, hi=0x1061c):
        self.hi = hi
        for number in range(0x40):
            adr = 0x10200 + number * 2
            if number not in KERNCALLS and adr not in SYSCALLS:
                DfsKernCall(number)
        for adr in range(0x10280, 0x10460, 4):
            if adr not in SYSCALLS:
                DfsFsCall(adr)
        for adr in range(0x10460, hi, 6):
            if adr not in SYSCALLS:
                DfsFsCall(adr)

    def round_0(self, cx):
        for sc in SYSCALLS.values():
            sc.round_0(cx)

    def round_1(self, cx):
        for sc in SYSCALLS.values():
            sc.round_1(cx)

    def round_2(self, cx):
        for sc in SYSCALLS.values():
            sc.round_2(cx)

    def round_3(self, cx):
        for sc in SYSCALLS.values():
            sc.round_3(cx)

    def round_4(self, cx):
        print("R4")
        for sc in SYSCALLS.values():
            sc.round_4(cx)

    def __getitem__(self, adr):
        return SYSCALLS[adr]

    def get(self, adr):
        return SYSCALLS.get(adr)

    def __iter__(self):
        yield from SYSCALLS.values()
