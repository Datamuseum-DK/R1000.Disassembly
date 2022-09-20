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
   P2ABUS.M200 / 4d4298301994e8
   ----------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    # data.Txt(cx.m, 0x201ce, label=False)
    cx.m.set_label(0x2253a, "READ_PARITY_MEMBOARD(adr : Byte; VAR TAGSTORE0_ERROR : Byte; VAR TAGSTORE1_ERROR : Byte; VAR ADDRESS_ERROR : Byte)")
    cx.m.set_block_comment(0x2251a, '''
SomethingMem()
--------------

    A6+0x14: Board address
    A6+0x10: Out param 1, Byte, ?TAGSTORE0_ERROR
    A6+0x0c: Out param 2, Byte, ?TAGSTORE1_ERROR
    A6+0x08: Out param 3, Byte, ?ADDRESS_ERROR
''')

def round_1(cx):
    ''' Let the disassembler loose '''

    for adr in (
        0x204e8,
        0x20590,
        0x205c6,
    ):
        cx.disass(adr)
        cx.m.set_line_comment(adr, "Manual")

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
