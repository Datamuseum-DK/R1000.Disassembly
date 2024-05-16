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
   IOC EEPROMs
   -----------
'''

from pyreveng import data
import ioc_hardware
import ioc_eeprom_exports

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    ioc_hardware.add_symbols(cx.m)
    ioc_eeprom_exports.add_symbols(cx.m)
    ioc_eeprom_exports.add_flow_check(cx)

    for adr in (
        0x80001ffa,
        0x80003ffa,
        0x80005ffa,
        0x80007dfa,
    ):
        ioc_hardware.eeprom_checksum(cx.m, adr)

    data.Txt(cx.m, 0x8000240c, label=False)
    data.Txt(cx.m, 0x8000254e, label=False)
    data.Txt(cx.m, 0x80002873, label=False)
    data.Txt(cx.m, 0x8000288d, label=False)
    data.Txt(cx.m, 0x80002d0d, label=False)
    data.Txt(cx.m, 0x800033ce, label=False)

    for a in range(0x800043aa, 0x80004488, 4):
        data.Const(cx.m, a, a + 4, fmt="%02x")

def round_1(cx):
    ''' Let the disassembler loose '''
    # cx.disass(0x800043aa + 0x27)

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
