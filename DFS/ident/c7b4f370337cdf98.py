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
   @(#)200 IOP KERNEL 0_8_11,92/09/15,09:00:00
   -------------------------------------------
'''

from pyreveng import assy, data

from kind import kernel_subr as ks

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    data.Txt(cx.m, 0x41a)
    data.Txt(cx.m, 0x44d)
    y = data.Txt(cx.m, 0x6090, splitnl=True)
    y = data.Txt(cx.m, y.hi, splitnl=True)
    ks.month_table(cx, 0x5cb4)

def round_1(cx):
    ''' Let the disassembler loose '''

    ks.Dispatch_Table(cx, 0x5c10,  8, "R1K_OP", R1K_OPS, "(A0=mailbox)")
    ks.Dispatch_Table(cx, 0x25f2,  3, "R1K_OP_01", {}, "(A0=mailbox)", kind=True)
    ks.Dispatch_Table(cx, 0x5d24, 19, "R1K_OP_02_DISK", R1K_OPS_DISK, "(A0=mailbox)")
    ks.Dispatch_Table(cx, 0x5ce2, 10, "R1K_OP_06_VME", {}, "(A0=mailbox)")
    ks.Dispatch_Table(cx, 0xa11a,  5, "R1K_OP_06_VME_01", {}, "(A0=mailbox)")
    ks.Dispatch_Table(cx, 0x654c,  6, "R1K_OP_07", {}, "(A0=mailbox)")
    ks.Dispatch_Table(cx, 0x58f4,  6, "R1K_OP_07_MEM", {}, "(A0=mailbox)")

    ks.Dispatch_Table(cx, 0x62a0, 14, "MODEM_TIMEOUT")

    ks.menu_dispatch(cx, 0x603e)

    for a, b in (
        (0x490, "ReturnMailbox_0()"),
        (0x498, "ReturnMailbox_1()"),
        (0x75a, "GET_SECTOR_BUFFER([A0+0x13].B => A1)"),
        (0x89a, "Assert_612_still_booting()"),
        (0xfe2, "ConvertGeometry(A0=CHAN)"),
        (0x23ec, "MODEM_GET_CHAR(D0)"),
        (0x23fc, "TEXT_TO_MODEM(A2=ptr, D1=len, D2, D3)"),
	(0x2446, "_KC09_MODEM(D0.W)"),
	(0x24b0, "_KC07_READ_CONSOLECHAR(D0<=port, D0=>char)"),
	(0x252c, "TEXT_TO_CONSOLE(A2=ptr,D1=len, D3)"),
	(0x25b4, "kc08_meat(D3=W, D0=B)"),
	(0x28fe, "TRANSFER_FIFO(A2=port_fifo)"),
	(0x2b6c, "GET_PORT_DESC(D0=port.W)"),
	(0x3c6c, "MODEM_FSM_ADVANCE(D0=tmo, D1=nxt)"),
        (0x5006, "DiagBusResponse(D2)"),
        (0x511e, "DO_KC_15_DiagBus(D0=cmd,A0=ptr)"),
        (0x528e, "INIT_KERNEL"),
        (0x53e4, "Timeout_Stop_PIT(A1)"),
        (0x5404, "Timeout_Start_PIT()"),
        (0x543a, "Timeout_Arm(D0=ticks,A2=entry)"),
        (0x5472, "Timeout_Cancel(A2=entry)"),
        (0x54d2, "AwaitInterrupt()"),
        (0x6ad6, "live0_boot1"),
        (0x6090, "BREAK_MENU"),
        (0x74bc, "port_event_mailbox"),
        (0x74c8, "port_event_buffer"),
        (0x74cc, "port_event_ptr"),
        (0x74d0, "port_event_space"),
        (0x773c, "MODEM_TXBUF"),
        (0x775c, "modem_timeout"),
        (0x7768, "modem_fsm_next"),
        (0x778a, "MODEM_EXPECT"),
        (0x778e, "MODEM_STATE"),
        (0x77b7, "diagbus_rxsum"),
        (0x77bc, "diagbus_rxwant"),
        (0x77e8, "diagbus_inbuf"),
        (0x79b8, "Timeout_chain"),
        (0x9000, "INIT_KERNEL_03_FIFO()"),
        (0x9084, "VME_LONGJMP2"),
        (0x9efe, "INIT_KERNEL_10_VME()"),
        (0xb8ca, "INIT_KERNEL_05_UARTS()"),
        (0xbc82, "Timeout_Init()"),
        (0xe006, "CONSOLE_N_DESC"),
        (0x9303fc12, "IO_VME_STD_REGISTER"),
    ):
        cx.m.set_label(a, b)

    cx.disass(0x000027e4)
    cx.disass(0x00003c8c)
    cx.disass(0x000054e4)

    ks.port_fifos(cx, 0x704c)
    ks.fsm_vectors(cx, 0x7740)
    ks.fsm_funcs(cx, "XE1201", (0x376c, 0x3a74, 0x3a90, 0x3aaa, 0x3ac6, 0x3d7e,))
    ks.fsm_funcs(cx, "DUART", (0x377a, 0x3a82, 0x3a9e, 0x3ab8, 0x3ad4, 0x3d8a,))
    ks.Dispatch_Table(cx, 0x37a2, 4, "duart_vec1", kind="JSR")
  
    ks.Dispatch_Table(cx, 0x64ee, 8, "KC15_BoardCmds") 

    ks.Dispatch_Table(cx, 0x5e4c, 32, "tape1") 
    ks.Dispatch_Table(cx, 0x5ecc, 32, "tape2") 
    ks.Dispatch_Table(cx, 0x5fee, 16, "0x5fee") 
    ks.Dispatch_Table(cx, 0x6372, 18, "MODEM_FSM_1") 
    ks.Dispatch_Table(cx, 0x63ba, 44, "MODEM_FSM_2") 
    ks.Dispatch_Table(cx, 0x646c,  7, "0x646c") 
    ks.Dispatch_Table(cx, 0x6402,  4, "MODEM_FSM_3") 

    data.Txt(cx.m, 0x624a, 0x6272)

    ks.reg_save(cx, 0x6510)

    cx.m.set_label(0x5d0c, "disk_unibus_adr")
    for i in range(4):
        adr = 0x5d0c + i * 4
        data.Const(cx.m, adr, adr + 4, "0x%08x", cx.m.bu32, 4)

    ks.drive_table(cx, 0x6b24, 0x6b68)

    for a, b in (
    ):
        cx.disass(a)
        cx.m.set_block_comment(a, b)


def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''

R1K_OPS = {
    0x01: "PORT",
    0x02: "DISK",
    0x03: "TAPE",
    #0x05: "NOP",
    #0x06: "VME",
    0x07: "MEM",
}

R1K_OPS_DISK = {
    # 0x02: "PROBE",
}

