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
    DFS FS calls
    ============
'''

from .base import DfsFsCall

DfsFsCall(0x10284, "?string_lit2something")
DfsFsCall(0x1028c, "?muls_d3_d4_to_d3")        # ref: FS.0 0x107ea
DfsFsCall(0x10290, "?mulu_d3_d4_to_d3")        # ref: FS.0 0x107f4
DfsFsCall(0x10294, "?divs_d3_d4")              # ref: FS.0 0x1080a
DfsFsCall(0x10298, "?divu_d3_d4")              # ref: FS.0 0x10816
DfsFsCall(0x1029c, "?malloc(LONG)")            # ref: FS.0 0x10816
DfsFsCall(0x102a8, "?free(LONG, PTR)")
DfsFsCall(0x102b8, "?alloc_str()")
DfsFsCall(0x102c4, "?fill_str(WORD, WORD, PTR)")
DfsFsCall(0x102d0, "?strcat(STR, STR)")
DfsFsCall(0x102f0, "ToUpper(str *)")
DfsFsCall(0x10384, "?read_from_file")          # ref: DBUSULOAD.M200
DfsFsCall(0x103b0, "?exec_command()")
DfsFsCall(0x103d0, "?wr_console_c(CHAR)")
DfsFsCall(0x103d8, "?wr_console_s(STR)")
DfsFsCall(0x1047e, "?exp_xmit(EXP.L,NODE.B)")
DfsFsCall(0x10496, "?experiment_close")        # ref: FS.0 0x18f4e
DfsFsCall(0x1056e, "?open_file")               # ref: BOOTINFO.M200
DfsFsCall(0x105a4, "Read_fc0c(word *)")
DfsFsCall(0x105aa, "Read_fc00(byte *)")
DfsFsCall(0x105da, "Write_fc01(byte)")
DfsFsCall(0x105e0, "Read_fc01(byte *)")
DfsFsCall(0x105e6, "Set_fc04_to_01()")

_fs = 0
