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
        0x800001c4,
    ):
        data.Txt(cx.m, a, splitnl=True)

    for a in (
        0x800001c2,
        0x80001b96,
    ):
        data.Const(cx.m, a, a+2)
        cx.m.set_line_comment(a, "NB: odd address jump")

    for a, b in (
        (0x80000222, "Self-Test: CONSOLE_UART Test Mode registers"),
        (0x8000025c, "Self-Test: CONSOLE_UART Local Loopback"),
        (0x800002c4, "Self-Test: CONSOLE_UART"),
        (0x800003a4, "Self-Test: 512 KB memory ..."),
        (0x800003de, "Self-Test"),
        (0x80000408, "Self-Test"),
        (0x80000434, "Self-Test"),
        (0x8000045e, "Self-Test"),
        (0x800004f8, "Self-Test"),
        (0x80000568, "Self-Test: Memory parity ... (GOOD PARITY)"),
        (0x80000596, "Self-Test: CLEAR_BERR"),
        (0x800005b2, "Self-Test: Parity generators"),
        (0x80000604, "Self-Test: Byte parities"),
        (0x800006b0, "Self-Test"),
        (0x80000702, "Self-Test"),
        (0x800007f4, "Self-Test: I/O bus control ..."),
        (0x80000886, "Self-Test: I/O bus map ..."),
        (0x800008d0, "Self-Test"),
        (0x80000924, "Self-Test"),
        (0x800009da, "Self-Test: I/O bus map parity ..."),
        (0x800009fc, "Self-Test"),
        (0x80000a40, "Self-Test"),
        (0x80000a74, "Self-Test: I/O bus transactions ..."),
        (0x80000ab6, "Self-Test"),
        (0x80000b22, "Self-Test"),
        (0x80000ba2, "Self-Test: PIT ..."),
        (0x80000c1a, "Self-Test: Modem DUART channel ..."),
        (0x80000c98, "Self-Test"),
        (0x80000d4e, "Self-Test: Diagnostic DUART channel ..."),
        (0x80000dfc, "Self-Test: Clock / Calendar ..."),
        (0x80000e32, "Self-Test"),
        (0x80000e54, "Self-Test"),
        (0x80000fa0, "Self-Test: RESHA EEProm Interface ..."),
        (0x800011c0, "Self-Test: Local interrupts ..."),
        (0x800011d6, "Self-Test: Local interrupts 0x50"),
        (0x800011fc, "Self-Test: Local interrupts 0x42 RX_BREAK"),
        (0x8000127a, "Self-Test: Local interrupts 0x51"),
        (0x80001298, "Self-Test: Local interrupts 0x46"),
        (0x800012c6, "Self-Test: Local interrupts 0x45 - CONSOLE_RXRDY"),
        (0x80001324, "Self-Test: Local interrupts 0x44"),
        (0x80001352, "Self-Test: Local interrupts 0x52"),
        (0x80001374, "Self-Test: Local interrupts 0x4f"),
        (0x800013a2, "Self-Test: Local interrupts 0x4d"),
        (0x800013d0, "Self-Test: Local interrupts 0x4e"),
        (0x80001402, "Self-Test: Local interrupts 0x4b"),
        (0x80001430, "Self-Test: Local interrupts 0x4a"),
        (0x8000146a, "Self-Test: Local interrupts 0x49"),
        (0x800014a2, "Self-Test: Local interrupts 0x48"),
        (0x80001502, "Self-Test: Illegal reference protection ..."),
        (0x8000154a, "Self-Test"),
        (0x8000158c, "Self-Test"),
        (0x800015f2, "Self-Test: I/O bus parity ..."),
        (0x8000169c, "Self-Test: I/O bus spurious interrupts ..."),
        (0x80001700, "Self-Test: Temperature sensors ..."),
        (0x80001774, "Self-Test: IOC diagnostic processor ..."),
        (0x8000181c, "Self-Test: Power margining ..."),
        (0x80001880, "Self-Test: Clock margining ..."),
        (0x8000189e, "Self-Test"),
        (0x800018d6, "Self-Test"),
        (0x8000191e, "Self-Test"),
        #? (0x80001934, "Self-Test"),
    ):
        cx.m.set_block_comment(a, b)

    cx.m.set_line_comment(0x80000266, '16x N81')
    cx.m.set_line_comment(0x8000026c, '1X,BKDET,async 9600')
    cx.m.set_line_comment(0x80000272, 'Local Loopback -RTS RxEN +DTR TxEN')
    cx.m.set_block_comment(0x80000314, 'IOC SELFTEST')
    cx.m.set_line_comment(0x80000ba8, 'BRG=1, Counter, IP2 = PITCLK')
    cx.m.set_line_comment(0x80000ba8, 'PITCLK IOCp76 = 100ns * 256 = 25.6us')
    cx.m.set_block_comment(0x80000eca, 'SelfTest: Checking for RESHA board')
    cx.m.set_line_comment(0x80001202, 'Local Loopbac')
    cx.m.set_line_comment(0x80001208, 'Local Loopback +TX-break')
    cx.m.set_line_comment(0x80001226, 'Local Loopback -TX-break')
    cx.m.set_line_comment(0x8000122c, 'Wait for txhold empty')
    cx.m.set_line_comment(0x80001238, 'Wait for txshift non-empty')
    cx.m.set_line_comment(0x80001240, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001248, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001250, 'Wait for txhold empty')
    cx.m.set_line_comment(0x800012d2, 'Wait for txhold empty')
    cx.m.set_line_comment(0x800012de, 'Wait for rxhold full')
    cx.m.set_line_comment(0x800012f2, 'Wait for txshift empty')
    cx.m.set_line_comment(0x800012fa, 'Wait for txshift empty')
    cx.m.set_line_comment(0x80001302, 'Wait for txshift empty')

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
