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
   DBUSLOAD / ae92d5b29.html
   -------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    for a in (
        0x201ec,
        0x20212,
        0x20226,
    ):
        data.Txt(cx.m, a, a + 1);

    cx.m.set_label(0x20298, "board_id_list")
    data.Const(cx.m, 0x20298, 0x2029e)

    for a in (
        0x201b2,
        0x201ba,
        0x201c2,
        0x201ca,
        0x201d2,
    ):
        data.Txt(cx.m, a, a + 8)
    for a, b in (
        (0x20924, "Load_RegFile_Only()"),
        (0x20b7a, "Load_RegFile_Dispatch()"),
        (0x2102a, "Load_Control_Store()"),
    ):
        cx.m.set_label(a, b)
        cx.m.set_block_comment(a, b)
    
    cx.m.set_block_comment(0x2115a, "idx=0, adr=6, TYP")
    cx.m.set_block_comment(0x211a6, "idx=1, adr=7, VAL")
    cx.m.set_block_comment(0x211f4, "idx=2, adr=3, FIU")
    cx.m.set_block_comment(0x21242, "idx=4, adr=4, IOC")
    cx.m.set_block_comment(0x21300, "idx=3, adr=2, SEQ")
    

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we alrady found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
