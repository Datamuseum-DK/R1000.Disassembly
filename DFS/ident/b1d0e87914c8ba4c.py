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
   IOC first quareter/b1d0e87914c8ba4c
   -----------------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    y = data.Txt(cx.m, 0x8000015b)
    y = data.Txt(cx.m, 0x80000156, y.lo)

    for a in (
        0x80000072,
        0x800001c4,
        0x80000314,
        0x80000374,
    ):
        data.Txt(cx.m, a, splitnl=True)

    for a in (
        0x800001c2,
        0x80001b96,
    ):
        data.Const(cx.m, a, a+2)
        cx.m.set_line_comment(a, "NB: odd address jump")

    cx.m.set_block_comment(0x80000222, 'CONSOLE_UART Test Mode registers')
    cx.m.set_block_comment(0x8000025c, 'CONSOLE_UART Local Loopback')
    cx.m.set_line_comment(0x80000266, '16x N81')
    cx.m.set_line_comment(0x8000026c, '1X,BKDET,async 9600')
    cx.m.set_line_comment(0x80000272, 'Local Loopback -RTS RxEN +DTR TxEN')
    cx.m.set_block_comment(0x800002c4, 'CONSOLE_UART')
    cx.m.set_block_comment(0x80000314, 'IOC SELFTEST')
    cx.m.set_block_comment(0x80000b90, 'SelfTest: PIT')
    cx.m.set_line_comment(0x80000ba8, 'BRG=1, Counter, IP2 = PITCLK')
    cx.m.set_line_comment(0x80000ba8, 'PITCLK IOCp76 = 100ns * 256 = 25.6us')
    cx.m.set_block_comment(0x80000bf8, 'SelfTest: Modem DUART channel')
    cx.m.set_block_comment(0x80000d26, 'SelfTest: Diagnostic DUART channel')
    cx.m.set_block_comment(0x80000ddc, 'SelfTest: Clock / Calendar SELFTEST')
    cx.m.set_block_comment(0x80000eca, 'SelfTest: Checking for RESHA board')
    cx.m.set_block_comment(0x80000f7a, 'SelfTest: RESHA EEProm Interface')
    cx.m.set_block_comment(0x800011a0, 'SelfTest: Local interrupts')
    cx.m.set_block_comment(0x800011dc, 'SelfTest: Local interrupts 0x50')
    cx.m.set_block_comment(0x80001202, 'SelfTest: Local interrupts 0x42 RX_BREAK')
    cx.m.set_line_comment(0x80001202, 'Local Loopbac')
    cx.m.set_line_comment(0x80001208, 'Local Loopback +TX-break')
    cx.m.set_line_comment(0x80001226, 'Local Loopback -TX-break')
    cx.m.set_line_comment(0x8000122c, 'Wait for txhold empty')
    cx.m.set_line_comment(0x80001238, 'Wait for txshift non-empty')
    cx.m.set_line_comment(0x80001240, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001248, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001250, 'Wait for txhold empty')
    cx.m.set_block_comment(0x80001280, 'SelfTest: Local interrupts 0x51')
    cx.m.set_block_comment(0x8000129e, 'SelfTest: Local interrupts 0x46')
    cx.m.set_block_comment(0x800012cc, 'SelfTest: Local interrupts 0x45 - CONSOLE_RXRDY')
    cx.m.set_line_comment(0x800012d2, 'Wait for txhold empty')
    cx.m.set_line_comment(0x800012de, 'Wait for rxhold full')
    cx.m.set_line_comment(0x800012f2, 'Wait for txshift empty')
    cx.m.set_line_comment(0x800012fa, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001302, 'Wait for txshift empty')
    cx.m.set_block_comment(0x8000132a, 'SelfTest: Local interrupts 0x44')
    cx.m.set_block_comment(0x8000135c, 'SelfTest: Local interrupts 0x52')
    cx.m.set_block_comment(0x8000137a, 'SelfTest: Local interrupts 0x4f')
    cx.m.set_block_comment(0x800013a8, 'SelfTest: Local interrupts 0x4d')
    cx.m.set_block_comment(0x800013d6, 'SelfTest: Local interrupts 0x4e')
    cx.m.set_block_comment(0x80001408, 'SelfTest: Local interrupts 0x4b')
    cx.m.set_block_comment(0x80001436, 'SelfTest: Local interrupts 0x4a')
    cx.m.set_block_comment(0x80001470, 'SelfTest: Local interrupts 0x49')
    cx.m.set_block_comment(0x800014a8, 'SelfTest: Local interrupts 0x48')
    cx.m.set_block_comment(0x800014d6, 'SelfTest: Illegal reference protection')
    cx.m.set_block_comment(0x800015d4, 'SelfTest: I/O bus parity')
    cx.m.set_block_comment(0x80001672, 'SelfTest: I/O bus spurious interrupts')
    cx.m.set_block_comment(0x800016e4, 'SelfTest: Temperature sensors')
    cx.m.set_block_comment(0x8000174c, 'SelfTest: IOC diagnostic processor')
    cx.m.set_block_comment(0x800017fe, 'SelfTest: Power margining')
    cx.m.set_block_comment(0x80001862, 'SelfTest: Clock margining')

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we alrady found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
