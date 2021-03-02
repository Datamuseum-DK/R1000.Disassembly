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

DfsFsCall(0x102f0, "ToUpper(str *)")
DfsFsCall(0x105a4, "Read_fc0c(word *)")
DfsFsCall(0x105aa, "Read_fc00(byte *)")
DfsFsCall(0x105da, "Write_fc01(byte)")
DfsFsCall(0x105e0, "Read_fc01(byte *)")
DfsFsCall(0x105e6, "Set_fc04_to_01()")

#######################################################################

def fs_call_doc(asp):

    asp.set_block_comment(0x10204,'''DISK-I/O
========

D1 = 2 -> READ
D1 = 3 -> WRITE
(Other registers may be significant too)

STACK+a: LWORD desc pointer
STACK+6: LWORD src/dst pointer
STACK+4: WORD (zero)

Desc+00:        0x0100
Desc+02:        0x0000
Desc+04:        0x0002
Desc+06:        0x0000
Desc+08:        0x0080
Desc+0a:        0x0002
Desc+0c:        0x____ cylinder
Desc+0e:        0x__ head
Desc+0f:        0x__ sector

CHS is 512 byte sectors
''')

_fs = 0
