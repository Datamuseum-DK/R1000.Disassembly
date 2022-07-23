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
        0x80001ffb,
        0x80003ffb,
        0x80005ffb,
        0x80007dfb,
    ):
        y = data.Const(cx.m, adr, adr + 3, fmt="%02x")
        y.typ = ".REV"
        cx.m.set_block_comment(adr, "Revision and checksum")
        y = data.Const(cx.m, adr + 3, adr + 5, fmt="0x%02x")
        y.typ = ".SUM"
        

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
