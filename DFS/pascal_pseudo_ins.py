#!/usr/bin/env python
#
# Copyright (c) 2012-2014 Poul-Henning Kamp <phk@phk.freebsd.dk>
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

'''
   PASCAL pseudo-instructions
   ==========================
'''

from pyreveng import assy, data, code
import pyreveng.cpu.m68020 as m68020

#######################################################################

PASCAL_DESC = '''
STACKCHECK	-		| BF | D5 | &
				| 62 | 06 | &
				| 44 | FC | 00 | 02 | &
				| 4E | 76 | {
}
CHKSTR		areg		|1 0 1 1| a   |1|1 1 1 0|1| b   | FF | FC | &
				| 67 | 02 | &
				| 4E | 4D | {
}
CHKSTRLEN	dreg		| 0C8 |0| d   | 00 | 00 | 00 | 7D | &
				| 63 | 02 | &
				| 4E | 4F | {
}
'''

class PascalIns(m68020.m68020_ins):
    ''' PASCAL pseudo instructions '''

    def assy_dreg(self):
        ''' data register '''
        return "D%d" % self['d']

    def assy_areg(self):
        ''' address register '''
        if self['a'] != self['b']:
            raise assy.Invalid()
        return "A%d" % self['a']

#######################################################################
#  Recognize pushing a text-string onto the stack


PASCAL_PUSHTXT_DESC = '''

+PTA		-		|0 0 1 0|sreg |0|0 1 0 0|1 1 1 1|
+PTB		-		|0 1 0 0|areg |1|1 1 1 1|1 0 1 0|x				|
+PTC		-		|0 1 1 1|dreg |0|0| y		|
+PTDB+		-		|0 0 0 1|sreg |0|1 1 0 1|1|areg |
+PTDW-		-		|0 0 1 1|sreg |1|0 0 1 0|0|areg |
+PTDL-		-		|0 0 1 0|sreg |1|0 0 1 0|0|areg |
PUSHTXT		pushtxt		|0 1 0 1|0 0 0 1|1 1 0 0 1|dreg | FF | FC |
'''

class PascalPushtxtIns(m68020.m68020_ins):
    ''' pushtxt pseudo-instructions '''

    def assy_areg(self):
        ''' address register '''
        if self['a'] != self['b']:
            raise assy.Invalid()
        return "A%d" % self['a']

    def assy_pushtxt(self):
        ''' XXX: Use PIL instead ? '''
        if len(self.lim) == 5 and self.lim[0].assy[0] == "+PTA":
            sreg = self.lim[0]['sreg']
            lim = self.lim[-4:]
            off = self.lo + 4
        elif len(self.lim) == 4:
            sreg = 7
            lim = self.lim
            off = self.lo + 2
        else:
            raise assy.Invalid()
        for i, j in zip(lim, ("+PTB", "+PTC", "+PTD", "PUSH")):
            if i.assy[0][:4] != j:
                raise assy.Invalid()
        if lim[0]['areg'] != lim[2]['areg']:
            raise assy.Invalid()
        if lim[1]['dreg'] != self['dreg']:
            raise assy.Invalid()
        if lim[2]['sreg'] != sreg:
            raise assy.Invalid()
        adr = off + lim[0]['x'] - (1<<16)
        length = lim[1]['y'] + 1
        length *= {
            'B': 1,
            'W': 2,
            'L': 4,
        }[lim[2].assy[0][4]]
        if lim[2].assy[0][-1] == '-':
            adr -= length
        elif lim[2].assy[0][-1] != '+':
            raise assy.Invalid()
        for i in range(adr, adr+length):
            j = self.lang.m[i]
            if 32 <= j <= 126:
                pass
            elif j in (9, 10, 13):
                pass
            else:
                print("BAD char 0x%02x" % j)
                raise assy.Invalid()
        y = data.Txt(self.lang.m, adr, adr+length, label=False)
        return '"' + y.txt + '"'

#######################################################################

PASCAL_SWITCH_DESC = '''
SWITCH		sw		|0 0 1 1|dreg1|0| 3B |0|dreg2|0 0 0 0| 06 | &
				| 4E | FB |0|dreg3|0 0 0 0| 02 |
'''

class PascalSwitchIns(m68020.m68020_ins):
    ''' PASCAL switch pseudo instructions '''

    def assy_sw(self):
        ''' Decode switch table '''
        dreg = self['dreg1']
        if dreg != self['dreg2']:
            raise assy.Invalid()
        if dreg != self['dreg3']:
            raise assy.Invalid()
        ptr = self.hi
        fin = self.lang.m.bu16(self.hi) + self.hi
        n = 0
        while ptr < fin:
            i = self.lang.m.bs16(ptr)
            d = self.hi + i
            if i > 0:
                fin = min(fin, d)
            self += code.Jump(cond="0x%x" % n, to=d)
            data.Const(
                self.lang.m,
                ptr,
                ptr + 2,
                size=2,
                func=self.lang.m.bu16
            )
            self.lang.m.set_line_comment(ptr, "[0x%x] -> 0x%x" % (n, d))
            self.lang.m.set_label(d, "switch@0x%x[0x%x]" % (self.lo, n))
            ptr += 2
            n += 1
        return "D%d.W" % dreg

#######################################################################

def add_pascal_pseudo_ins(cx):
    ''' Augment disassembler with PASCAL pseudo instructions '''
    cx.add_ins(PASCAL_DESC, PascalIns)
    cx.add_ins(PASCAL_PUSHTXT_DESC, PascalPushtxtIns)
    cx.add_ins(PASCAL_SWITCH_DESC, PascalSwitchIns)
