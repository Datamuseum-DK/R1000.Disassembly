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
    DFS KERNEL calls
    ================
'''

from .base import DfsKernCall

DfsKernCall(
    0x01,
    "KC01_DumpOn",
)
DfsKernCall(
    0x02,
    "KC02_Start_Disk_IO",
    bcmt='''
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
'''
    )

DfsKernCall(0x03, "KC03_Wait_Disk_IO")
DfsKernCall(0x05, "KC05_Write_Console_String")
DfsKernCall(0x06, "KC06_Write_Console_Char")
DfsKernCall(0x07, "KC07_Read_Console_Char")
DfsKernCall(0x0f, "KC0f_ReInit")
DfsKernCall(0x10, "KC10_Panic")
DfsKernCall(0x13, "KC13_RTC")
DfsKernCall(0x15, "KC15_Diag_Bus")
DfsKernCall(0x16, "KC16_Clock_Margin")
DfsKernCall(0x17, "KC17_Power_Margin")
DfsKernCall(0x1c, "KC1c_ProtCopy(src.P, dst.P, len.W)")
DfsKernCall(0x1e, "KC1e_Fifo_Response(chan.W, ptr.P)")

_x = 0
