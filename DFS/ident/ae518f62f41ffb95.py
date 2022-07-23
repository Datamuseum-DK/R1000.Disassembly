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
   FS_0.M200/ae518f62f41ffb95
   --------------------------
'''

from pyreveng import data

def text_table(cx, lo, label, cnt, length, *args, **kwargs):
    if label is None:
        label = "texttable_0x%x" % lo
    cx.m.set_label(lo, label)
    for i in range(cnt):
        y = data.Txt(cx.m, lo, lo + length, label=False, *args, **kwargs)
        lo = y.hi

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    text_table(cx, 0x116ca, 'months', 12, 3)
    text_table(cx, 0x12f12, 'error_messages', 16, 0x1e)
    text_table(cx, 0x1312a, 'error_messages2', 16, 0x1e)
    text_table(cx, 0x14368, None, 17, 6)
    text_table(cx, 0x143f2, None, 17, 6)
    text_table(cx, 0x14824, 'push_error_messages', 15, 0x1e)
    text_table(cx, 0x149e6, 'exp_error_messages', 15, 0x1e)
    text_table(cx, 0x15ca8, 'tape_error_messages', 14, 0x1e)
    text_table(cx, 0x15eb2, 'tape2_error_messages', 14, 0x1e)
    text_table(cx, 0x18282, 'board_names', 16, 10)
    text_table(cx, 0x1832e, 'status_names', 10, 10)

    for adr in (
        0x18322,
    ):
        for i in range(3):
            data.Txt(cx.m, adr + i, adr + i + 1)

    cx.m.set_label(0x1a2aa, 'config_strings')
    for a in range(0x1a2aa, 0x1a43a, 0x14):
        data.Txt(cx.m, a, a + 0x14, label=False)

    cx.m.set_label(0x18479, "ExpDestinations[16]")
    for a in range(0x18479, 0x18519, 10):
        data.Txt(cx.m, a, a + 10, label=False)

    cx.m.set_label(0x18519, "ExpStatus[10]")
    for a in range(0x18519, 0x1857d, 10):
        data.Txt(cx.m, a, a + 10, label=False)

    cx.m.set_label(0x11a36, "Str2Int(String, &LongInt, Long, Long, &Byte)")
    cx.m.set_label(0x11ab4, "Month(String, &LongInt, &Void)")

    cx.m.set_label(0x130f2, "Legal_Filename_BitMap")
    cx.m.set_block_comment(0x130f2, "Legal characters in filename:  $.0-9?A-Z[\]_")
    data.Const(cx.m, 0x130f2, 0x13112)

    cx.m.set_label(0x1330a, "ReportError(Byte error, Byte mode, String)")

    cx.m.set_label(0x1346a, "CheckFilename()")
    cx.m.set_line_comment(0x13544, "Filename hashing")

    cx.m.set_label(0x13718, "NameI(Char*, &void)")

    cx.m.set_label(0x1aa5e, "_Write_fc0c(word *)")

    cx.m.set_label(0x1b0b8, "cur_push_level")

    for i in range(9, 16):
        adr = 0x1a0d8 + 4 * i
        data.Const(cx.m, adr, adr + 4, fmt="0x%02x")
        cx.m.set_line_comment(adr, "Param Type 0x%x" % i)

    cx.m.set_line_comment(0x0001a11c, "Return PC")
    cx.m.set_line_comment(0x0001a122, "Stack Delta")
    cx.m.set_line_comment(0x0001a12a, "Name Length")
    cx.m.set_line_comment(0x0001a15a, "D1 => number of O_params")
    cx.m.set_line_comment(0x0001a15c, "D0 => number of I_params")
    cx.m.set_line_comment(0x0001a1a2, "I_Param: length - 1")
    cx.m.set_line_comment(0x0001a196, "I_Param: 8 (flag)")
    cx.m.set_line_comment(0x0001a1c6, "D1 => number of O_params")
    cx.m.set_line_comment(0x0001a20c, "O_Param: length - 1")
    cx.m.set_line_comment(0x0001a200, "O_Param: 8 (flag)")

    cx.m.set_label(0x18458, "diproc_adr_valid")
    data.Const(cx.m, 0x18458, 0x18458+0x10)
    cx.m.set_label(0x18474, "diproc_adr_table[TVISF]")
    data.Const(cx.m, 0x18474, 0x18474+0x5)



def round_1(cx):
    ''' Let the disassembler loose '''
    cx.disass(0x11a36)
    cx.m.set_label(0x10704, "Program.Program_Failure()")
    cx.disass(0x10704)
    cx.m.set_label(0x1070c, "Program.Experiment_Failure()")
    cx.disass(0x1070c)

    cx.disass(0x118a2)

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
