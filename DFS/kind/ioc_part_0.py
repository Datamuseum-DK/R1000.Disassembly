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

import ioc_eeprom_exports

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

def round_1(cx):
    ''' Let the disassembler loose '''
    cx.codeptr(0x80000004)

    for i in ioc_eeprom_exports.IOC_EEPROM_PART0_EXPORTS:
        cx.disass(i)

    for a, b in (
        (0x80000020, "IOC_20_XXX"),
        (0x80000088, "_TEST_FAILED"),
        (0x800000d8, "OUTSTR_PRESERVE_D0(A0)"),
        (0x800000f8, "OUTSTR_SMASH_D0(A0)"),
        (0x80000142, "OUTSTR_OK()"),
        (0x8000014c, "OUTSTR_CRNL()"),
        (0x8000015e, "DELAY(D0)"),
        (0x8000016c, "CHECKSUM_FUNC"),
        (0x800001e4, "CHECKSUM_EEPROM"),
        (0x800001f6, None),
        (0x80000208, None),
        (0x8000021a, None),
        (0x80001524, None),
        (0x80001566, None),
        (0x800015a8, None),
        (0x800015d4, None),
        (0x80001628, None),
        (0x80001672, None),
        (0x800016a2, None),
        (0x800016c2, None),
    ):
        cx.disass(a)
        cx.m.set_line_comment(a, "Manual")
        if b:
            cx.m.set_label(a, b)

def round_2(cx):
    ''' Spelunking in what we alrady found '''
    ioc_eeprom_exports.add_exports(
        cx.m,
        ioc_eeprom_exports.IOC_EEPROM_PART0_EXPORTS
    )

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
