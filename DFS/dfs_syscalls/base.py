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

SYSCALLS = {}

class DfsSysCall():
    ''' Base class for system-calls'''

    def __init__(self, adr, name):
        self.adr = adr
        self.name = name

    def round_0(self, cx):
        cx.m.set_label(self.adr, self.name)

    def round_1(self, cx):
        try:
            _v = cx.m[self.adr]
        except mem.MemError:
            return
        cx.disass(self.adr)
        cx.m.set_block_comment(self.adr, self.__doc__)

    def round_2(self, cx):
        y = list(cx.m.find(self.adr))
        if len(y) == 1:
            ins = y[0]
            if len(ins.flow_out) == 1:
                f = ins.flow_out[0]
                if isinstance(f.to, int):
                    cx.m.set_label(f.to, "_" + self.name)
                    cx.m.set_block_comment(f.to, self.__doc__)

class DfsKernCall(DfsSysCall):
    ''' KERNEL system-call '''
    def __init__(self, number, name=None):
        SYSCALLS[number] = self
        adr = 0x10200 + 2 * number
        if name is None:
            name = "KC_%02x" % number
        super().__init__(adr, name)

class DfsFsCall(DfsSysCall):
    ''' FS system-call '''

    def __init__(self, adr, name=None):
        if name is None:
            name = "FSCALL_%x" % adr
        SYSCALLS[adr] = self
        super().__init__(adr, name)

class DfsSysCalls():
    ''' ... '''

    def __init__(self, hi=0x1061c):
        self.hi = hi
        for number in range(0x40):
            adr = 0x10200 + number + 2
            if number not in SYSCALLS:
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

    def __getitem__(self, adr):
        return SYSCALLS[adr]

    def __iter__(self):
        yield from sorted(SYSCALLS.items())
