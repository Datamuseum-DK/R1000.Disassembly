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
   FS/ae518f62f41ffb95
   -------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    cx.m.set_label(0x116ca, 'months')
    for a in range(0x116ca, 0x116ee, 0x3):
        data.Txt(cx.m, a, a + 0x3, label=False)

    cx.m.set_label(0x12f12, 'disk_error_messages')
    for a in range(0x12f12, 0x130f2, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x1312a, 'disk_error2_messages')
    for a in range(0x1312a, 0x1330a, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x14824, 'push_error_messages')
    for a in range(0x14824, 0x149e6, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x149e6, 'exp_error_messages')
    for a in range(0x149e6, 0x14ba8, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x15ca8, 'tape_error_messages')
    for a in range(0x15ca8, 0x15e4c, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x15eb2, 'tape_error2_messages')
    for a in range(0x15eb2, 0x16056, 0x1e):
        data.Txt(cx.m, a, a + 0x1e, label=False)

    cx.m.set_label(0x1a2aa, 'config_strings')
    for a in range(0x1a2aa, 0x1a43a, 0x14):
        data.Txt(cx.m, a, a + 0x14, label=False)

    cx.m.set_label(0x18479, "ExpDestinations[16]")
    for a in range(0x18479, 0x18519, 10):
        data.Txt(cx.m, a, a + 10, label=False)

    cx.m.set_label(0x18519, "ExpStatus[10]")
    for a in range(0x18519, 0x1857d, 10):
        data.Txt(cx.m, a, a + 10, label=False)


def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we alrady found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
