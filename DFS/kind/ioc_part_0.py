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
   First quarter of IOC EEPROM
   ---------------------------
'''

from pyreveng import assy, data

import ioc_eeprom_exports

#                                    . . . . . . . . . . . . . . . .       . . . . . . . .|. . . . . . . .|
call_a1 = 'call_a1      |43|F9|80|00| aa            | bb            |60|00| cc            | dd            |'

class call_a1_ins(assy.Instree_ins):

    def __init__(self, lim, lang):
        super().__init__(lim, lang)
        lang.m.set_line_comment(self.lo, "CALL_A1")
        # print("CALL_A1", self['aa'], self['bb'], self['cc'], self['dd'])
        adr = 0x80000000
        adr |= self['aa'] << 8
        adr |= self['bb']
        self.lang.disass(adr)
        raise assy.Invalid()

#                                    . . . . . . . . . . . . . . . .          . . . . . . . .
dir_uart = 'dir_uart	|43|F9|80|00| aa            | bb            |10|19|67| cc            |'

class dir_uart_ins(assy.Instree_ins):

    def __init__(self, lim, lang):
        super().__init__(lim, lang)
        lang.m.set_line_comment(self.lo, "DIR_UART")
        # print("DIR_UART", self['aa'], self['bb'], self['cc'])
        adr = 0x80000000
        adr |= self['aa'] << 8
        adr |= self['bb']
        y = data.Txt(self.lang.m, adr)
        raise assy.Invalid()

#
switch_1 = 'switch_1	|4E|F0|05|B1|\n'
switch_1 += 'switch_1	|4E|F0|75|B1|\n'

class switch_1_ins(assy.Instree_ins):

    def __init__(self, lim, lang):
        super().__init__(lim, lang)
        lang.m.set_line_comment(self.lo, "SWITCH1")
        # print("SWITCH1 %08x" % self.lo)
        n = {
            0x05: 5,
            0x75: 8,
        }[self.lang.m[self.lo + 2]]
        for i in range(n):
            y = self.lang.codeptr(self.lo + 8 + 4 * i)
            self.lang.m.set_label(y.dst, "SWITCH_%08x_%d" % (self.lo, i))
        raise assy.Invalid()

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    cx.add_ins(call_a1, call_a1_ins)
    cx.add_ins(dir_uart, dir_uart_ins)
    cx.add_ins(switch_1, switch_1_ins)

def round_1(cx):
    ''' Let the disassembler loose '''
    cx.codeptr(0x80000004)

    for i in ioc_eeprom_exports.IOC_EEPROM_PART0_EXPORTS:
        cx.disass(i)


    for a, b in (
        (0x80000020, "IOC_20_XXX"),
        (0x80000088, "_TEST_FAILED"),
    ):
        cx.disass(a)
        cx.m.set_line_comment(a, "Manual")
        if b:
            cx.m.set_label(a, b)
    return

def round_2(cx):
    ''' Spelunking in what we already found '''
    ioc_eeprom_exports.add_exports(
        cx.m,
        ioc_eeprom_exports.IOC_EEPROM_PART0_EXPORTS
    )

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
