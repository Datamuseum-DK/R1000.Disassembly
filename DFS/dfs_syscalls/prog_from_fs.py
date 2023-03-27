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
    Data locations in programs
    ==========================
'''

from pyreveng import data

DFS_LABELS = {
    0x20000: "stack.top",
    0x2000c: "heap.top",
    0x20010: "code.end",
    0x20018: "programfailurehandler",
    0x2001c: "experimentfailurehandler",
    0x20024: "exp_init_done",
    0x200f0: "is_open_ERROR_LOG",
    0x200f1: "write_error_ERROR_LOG",
    0x200fc: "file_ERROR_LOG",
    0x20108: "somekindoffsflag",
}

def prog_from_fs(cx, mapped):
    ''' Add labels for data FS knows about in programs '''

    for adr, lbl in DFS_LABELS.items():
        cx.m.set_label(adr, lbl)

    if mapped:
        # Comment: adr in FS_0
        data.Const(cx.m, 0x20014, 0x20018, size=4, fmt="0x%08x", func=cx.m.bu32) # 10696
        data.Const(cx.m, 0x20020, 0x20024, size=4, fmt="0x%08x", func=cx.m.bu32) # 14e72
        data.Const(cx.m, 0x20024, 0x20025, size=1, fmt="0x%02x"                ) # 
        data.Const(cx.m, 0x20025, 0x20026, size=1, fmt="0x%02x"                ) # 19624
        data.Const(cx.m, 0x20026, 0x20028, size=2, fmt="0x%04x", func=cx.m.bu16) # 1878e
        data.Const(cx.m, 0x20028, 0x2002a, size=2, fmt="0x%04x", func=cx.m.bu16) # 196b8
        data.Const(cx.m, 0x2002c, 0x2002e, size=2, fmt="0x%04x", func=cx.m.bu16) # 187b4
        data.Const(cx.m, 0x2002e, 0x20030, size=2, fmt="0x%04x", func=cx.m.bu16) # 18f2c
        data.Const(cx.m, 0x20030, 0x20032, size=2, fmt="0x%04x", func=cx.m.bu16) # 18814
        cx.dataptr(0x200ec)
        data.Const(cx.m, 0x200f0, 0x200f1)
        data.Const(cx.m, 0x200f1, 0x200f2)
        data.Const(cx.m, 0x200f2, 0x200f6, size=4, fmt="0x%08x", func=cx.m.bu32) # 18050
        data.Const(cx.m, 0x200f6, 0x200fa, size=4, fmt="0x%08x", func=cx.m.bu32) # 180fa
        data.Const(cx.m, 0x200fa, 0x200fb, size=1, fmt="0x%02x"                ) # 1804a
        data.Const(cx.m, 0x200fb, 0x200fc, size=1, fmt="0x%02x"                ) # 18098
        data.Const(cx.m, 0x200fc, 0x20100, size=4, fmt="0x%08x", func=cx.m.bu32) # 17d70
        data.Const(cx.m, 0x20100, 0x20104, size=4, fmt="0x%08x", func=cx.m.bu32) # 17d0c
        data.Const(cx.m, 0x20104, 0x20106, size=2, fmt="0x%04x", func=cx.m.bu16) # 17cae
        data.Const(cx.m, 0x20106, 0x20108, size=2, fmt="0x%04x", func=cx.m.bu16) # 17d84
        data.Const(cx.m, 0x20108, 0x20109, size=1, fmt="0x%02x"                ) # 15734
        data.Const(cx.m, 0x20109, 0x2010a, size=1, fmt="0x%02x"                ) # align

