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
   Second quarter of IOC EEPROM
   ----------------------------
'''

from pyreveng import mem, data, assy
import pyreveng.cpu.m68020 as m68020

import ioc_eeprom_exports

BASE = 0x80002000
SIZE = 0x2000

#######################################################################

IOC_PART2_SPEC = '''
OUTTEXT         outtxt,>J       | 4E | 96 |
'''

class IocPart2Ins(m68020.m68020_ins):
    ''' Pseudo-instructions '''

    def assy_outtxt(self):
        ''' inline text '''
        if self.lo < BASE or self.hi > BASE + SIZE:
            raise assy.Invalid()
        y = data.Txt(self.lang.m, self.hi, align=2, label=False, splitnl=True)
        self.dstadr = y.hi

#######################################################################


def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    cx.add_ins(IOC_PART2_SPEC, IocPart2Ins)

def round_1(cx):
    ''' Let the disassembler loose '''
    for i in ioc_eeprom_exports.IOC_EEPROM_PART1_EXPORTS:
        cx.disass(i)

def round_2(cx):
    ''' Spelunking in what we alrady found '''
    ioc_eeprom_exports.add_exports(
        cx.m,
        ioc_eeprom_exports.IOC_EEPROM_PART1_EXPORTS
    )

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
