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
from .pops import *

class FunctionCall():
    ''' A call to a function '''

    def __init__(self, ins, dst, sp):
        self.ins = ins
        self.dst = dst
        self.sp = sp
        if dst == 0x102c4:
           self.f102c4()
        elif dst == 0x102d0:
           self.f102d0()
        elif dst == 0x102d4:
           self.f102d4()
        elif dst == 0x102e8:
           self.f102e8()
        elif False:
           print("FCALL", hex(ins.lo), hex(dst), ins.txt)

    def f102c4(self):
        print(
            "MakeString",
            hex(self.ins.lo),
            str(self.sp.get(4, 4)),
            str(self.sp.get(2, 2)),
            str(self.sp.get(0, 2)),
        )
        arg0 = self.sp.get(4, 4)
        arg1 = self.sp.get(2, 2)
        arg2 = self.sp.get(0, 2)
        print("   ", type(arg0), arg0, arg1, arg2)
        if arg0 and isinstance(arg0, StackItemBackReference):
            arg0 = arg0.resolve()
        else:
            self.sp.put(8, StackItemString())
            return
        if arg0 and isinstance(arg0, StackItemBlob) and arg0.blob:
            txt = ""
            for i in range(arg2.val):
                try:
                    txt += "%c" % arg0[i]
                except IndexError:
                    txt += "…"
            self.sp.put(8, StackItemString(txt))
        else:
            self.sp.put(8, StackItemString())

    def f102d0(self):
        print(
            "StringCat2",
            hex(self.ins.lo),
            str(self.sp.get(4, 4)),
            str(self.sp.get(0, 4)),
        )
        self.sp.put(8, StackItemString())

    def f102d4(self):
        print(
            "StringCat3",
            hex(self.ins.lo),
            str(self.sp.get(8, 4)),
            str(self.sp.get(4, 4)),
            str(self.sp.get(0, 4)),
        )
        self.sp.put(12, StackItemString())

    def f102e8(self):
        print(
            "LONG2HEXSTR",
            hex(self.ins.lo),
            str(self.sp.get(4, 4)),
            str(self.sp.get(0, 4)),
        )
        self.sp.put(8, StackItemString())
