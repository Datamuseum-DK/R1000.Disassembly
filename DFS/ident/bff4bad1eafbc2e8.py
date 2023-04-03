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
   CLI.M200 bff4bad1eafbc2e8
   -------------------------
'''

from pyreveng import assy, data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    for i, j in (
        (0x20db4, "CMD_TIME()"),
        (0x210a6, "CMD_DIRECTORY()"),
        (0x2048e, "CMD_COPY()"),
        (0x20674, "CMD_DELETE()"),
        (0x20a90, "CMD_TYPE()"),
        (0x20b78, "CMD_CREATE()"),
        (0x20808, "CMD_RENAME()"),
        (0x208ec, "CMD_REMOTE()"),
        (0x209c2, "CMD_LOCAL()"),
        (0x21278, "CMD_PRINTER()"),
    ):
        cx.m.set_label(i, j)

    for i in (
        0x202f2,
        0x2036a,
    ):
        for adr in range(i, i + 10 * 10, 10):
            data.Txt(cx.m, adr, adr + 10, label=False)

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
