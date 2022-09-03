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
   ENP100.M200
   -----------
'''

from pyreveng import data

import pascal

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    cx.m.set_label(0x22534, "cmdtable")
    a0 = 0x2f532
    a2 = a0
    for adr in range(0x22534, 0x22804, 12):
        y = data.Txt(cx.m, adr, adr+12, label=False)
        off = cx.m.bu16(a2)
        a3 = a0 + off
        cx.m.set_label(a3, "CASE_" + y.txt)
        a2 += 2

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''

    pascal.PascalFunction(cx, 0x26990, "WriteConsoleHex(val : Long)")
    for a, b in (
        ( 0x22c5e, "CMD_RESPONSE"),
        ( 0x22f5a, "CMD_VERIFY"),
        ( 0x234de, "CMD_FILL_HUGE"),
        ( 0x25014, "CMD_DUMP_ENP_RAM"),
        ( 0x268b2, "CMD_DEBUG"),
        #( 0x26990, "WriteConsoleHex(val : Long)"),
        ( 0x26ab6, "CMD_TERMINATE"),
        ( 0x26cd6, "CMD_SET_VMEGEN"),
        ( 0x26e00, "CMD_SET_RAM"),
        ( 0x27014, "CMD_COMPARE"),
        ( 0x270ce, "CMD_R1K_RESET"),
        ( 0x276cc, "CMD_R1K_RAMTEST"),
        ( 0x27d36, "CMD_HARD_RST"),
        ( 0x27dfc, "CMD_ASSERT_RST"),
        ( 0x27e6a, "CMD_LP_RAM_RD"),
        ( 0x2806e, "CMD_LP_RAM_WRT"),
        ( 0x2822e, "CMD_READ_256"),
        ( 0x2832c, "CMD_WRITE_256"),
        ( 0x28440, "CMD_SHOW_ADDRS"),
        ( 0x28642, "CMD_WRITE_RAM"),
        ( 0x2885c, "CMD_TEST_RAM"),
        ( 0x29160, "CMD_SHOW_EPA"),
        ( 0x29644, "CMD_DOWNLOAD"),
        ( 0x29d32, "CMD_CONFIGURE"),
        ( 0x2a4e0, "CMD_GET_TCP_CHAN"),
        ( 0x2a6da, "CMD_RESERVE_TCP"),
        ( 0x2a856, "CMD_BIND_TCP"),
        ( 0x2aa6c, "CMD_PO_TCP"),
        ( 0x2acaa, "CMD_CONNECT_TCP"),
        ( 0x2ae6e, "CMD_ACCEPT_TCP"),
        ( 0x2b076, "CMD_GET_UDP_CHAN"),
        ( 0x2b274, "CMD_RESERVE_UDP"),
        ( 0x2b3f0, "CMD_BIND_UDP"),
        ( 0x2b74a, "CMD_GET_ETH_CHAN"),
        ( 0x2b95a, "CMD_RESERVE_ETH"),
        ( 0x2bae0, "CMD_BIND_ETH"),
        ( 0x2bde6, "CMD_OPEN_ETH"),
        ( 0x2bfc8, "CMD_RECEIVE"),
        ( 0x2c13c, "CMD_RECEIVE_CP"),
        ( 0x2c4ea, "CMD_CANCEL_RX"),
        ( 0x2c618, "CMD_SHOW_CHANNEL"),
        ( 0x2c7f6, "CMD_TRANSMIT_UDP"),
        ( 0x2c9d4, "CMD_ENP_ABORT"),
        ( 0x2cb06, "CMD_XMIT_TCP"),
        ( 0x2cc72, "CMD_TX_FULL_TCP"),
        ( 0x2ce0c, "CMD_TX_HUGE_TCP"),
        ( 0x2d0b8, "CMD_TX_HUGE_ETH"),
        ( 0x2d37a, "CMD_CLOSE"),
        ( 0x2d6ae, "CMD_CP_SERVER"),
        ( 0x2d814, "CMD_CP_CLIENT"),
        ( 0x2dcd2, "CMD_LP_CP_CLIENT"),
        ( 0x2e522, "CMD_GET_SC_OPT"),
        ( 0x2e6b8, "CMD_DELAY"),
        ( 0x2e842, "CMD_TEST_VME_CTL"),
        ( 0x2ecda, "CMD_TEST_VME_ADR"),
        ( 0x2f1d0, "CMD_TEST_ALL"),
        ( 0x2f22c, "CMD_POUND"),
        ( 0x2f5e6, "CMD_DUMP_IOP_RAM"),
        ( 0x2f82c, "CMD_ECHO_ON_OFF"),
        ( 0x33b1c, "CMD_MASK"),
        ( 0x358e4, "ptr_0x9303e00c"),
        ( 0x358e8, "ptr_0x9303e102"),
        ( 0x358ec, "ptr_0x9303e10a"),
        ( 0x358f0, "ptr_0x9303e008"),
        ( 0x358f4, "ptr_0x9303e106"),
        ( 0x358f8, "ptr_0x9303e202"),
        ( 0x35900, "ptr_0x9303f800"),
        ( 0x35904, "ptr_0x9303f400"),
        ( 0x35908, "ptr_0x9303f000"),
    ):
        cx.m.set_label(a, b)
