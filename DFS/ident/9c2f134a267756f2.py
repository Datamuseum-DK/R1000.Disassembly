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
   NOVRAM.M200 / 2fd4534b0.html
   ----------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    for a in range(0x2012c, 0x20150, 4):
        data.Txt(cx.m, a, a + 4, label=True)
    data.Txt(cx.m, 0x20156, 0x2015a, label=True)

    cx.m.set_block_comment(0x20aa6, " does READ_NOVRAM_DATA.*")

    cx.m.set_label(0x206be, "GetBoardName(&String, Byte)")
    cx.m.set_label(0x214e6, "ReEnterBoard(?)")
    cx.m.set_label(0x22582, "TestRamBoard(?)")

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we alrady found '''
    cx.disass(0x207fc)
    cx.disass(0x20928)
    cx.disass(0x20aa6)
    cx.disass(0x20cb6)
    cx.disass(0x20f26)
    cx.disass(0x21944)
    cx.disass(0x21cda)
    cx.disass(0x2201c)
    cx.disass(0x220ea)

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
