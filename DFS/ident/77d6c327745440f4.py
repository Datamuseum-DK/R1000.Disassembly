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
   @(#)400S IOP KERNEL,4_2_18,92/08/06,16:15:00
   --------------------------------------------
'''

from pyreveng import assy, data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    cx.m.set_label(0x55a, "req_fifo_ready_flag")
    data.Const(cx.m, 0x55a, 0x55b)
    cx.m.set_label(0x28d8, "PANIC_0x824")
    for a in (
        0x0000800c,
        0x0000a46a,
        0x0000a518,
        0x0000a53b,
    ):
        data.Txt(cx.m, a, splitnl=True)

    for a in range(0x0000a9a4, 0x0000a9e0, 4):
        cx.m.set_label(a, "REG_SAVE_%X" % cx.m[a])
        data.Const(cx.m, a, a + 4)

    for a in (
        0xa560,
        0xa569,
        0xa571,
        0xa580,
        0xa585,
        0xa58f,
        0xa59c,
        0xa5a6,
    ):
        data.Txt(cx.m, a, splitnl=True, term=(255,))

    a = 0xa24e
    cx.m.set_label(a, "BREAK_MENU")
    while a < 0xa35d:
        y = data.Txt(cx.m, a, term=(0x00, 0x02, 0x03,), splitnl=True, label=False)
        a = y.hi

    for a in range(0x0000a3c8, 0x0000a3d8, 4):
        y = cx.dataptr(a)
        data.Txt(cx.m, y.dst, term=(0x01,))

    y = data.Const(cx.m, 0x8de, 0x8de + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "CYL_PER_DRV[4]")

    y = data.Const(cx.m, 0x8e6, 0x8e6 + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "CYL_MSB_PER_DRV[4]")

    y = data.Const(cx.m, 0x8ee, 0x8ee + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "CYL_LSB_PER_DRV[4]")

    y = data.Const(cx.m, 0x8f6, 0x8f6 + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "LSEC_PER_TRK[4]")

    y = data.Const(cx.m, 0x8fe, 0x8fe + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "HD_PER_CYL[4]")

    y = data.Const(cx.m, 0x906, 0x906 + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "LSEC_PER_CYL[4]")

    y = data.Const(cx.m, 0x90e, 0x90e + 8, "%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "BYTE_PER_PSEC[4]")

    def drive_desc(a):
        z = data.Const(cx.m, a, a + 0x14)
        cx.dataptr(a + 0x14)
        z = data.Const(cx.m, a + 0x18)
        cx.m.set_line_comment(z.lo, "Drive number")
        z = data.Const(cx.m, a + 0x2b, a + 0x2b + 4)
        cx.m.set_line_comment(z.lo, ".lba")
        z = data.Const(cx.m, a + 0x19, a + 0x1f)
        z = data.Const(cx.m, a + 0x20, a + 0x2b)
        z = data.Const(cx.m, a + 0x2f)
        z = data.Const(cx.m, a + 0x30, a + 0x3f)
        z = data.Const(cx.m, a + 0x40, a + 0x4f)
        z = data.Const(cx.m, a + 0x50, a + 0x5c)

    cx.m.set_label(0x92e, "DRIVE_TABLE")
    for d in range(4):
        y = cx.dataptr(0x92e + 4*d)
        cx.m.set_label(0x954 + d * 0x5c, "DRIVE_DESC[%d]" % d)
        drive_desc(0x954 + d * 0x5c)

    cx.m.set_label(0x944, "SCSI_D_DESC")

class Dispatch_Table():

    def __init__(self, cx, lo, length, pfx = None, funcs = {}, sfx="", kind=None, width=4):
        if pfx is None:
            pfx = "AT_%x" % lo
        self.cx = cx
        self.lo = lo
        self.length = length
        self.pfx = pfx
        self.funcs = funcs
        self.sfx = sfx
        self.kind = kind
        self.width = width

        self.proc()

    def proc(self):
        self.cx.m.set_label(self.lo, self.pfx.lower() + "_dispatch")
        for n in range(self.length):
            adr = self.lo + self.width * n
            what = self.funcs.get(n)
            lbl = self.pfx + "_%02x" % n
            if what:
                lbl += "_" + what
            lbl += self.sfx
            if self.kind is None:
                if self.width == 4:
                    dst = self.cx.m.bu32(adr)
                else:
                    dst = self.cx.m.bu16(adr)
                y = data.Codeptr(self.cx.m, adr, adr + self.width, dst)
                if dst == 0:
                    continue
                self.cx.disass(dst)
                self.cx.m.set_first_label(dst, lbl)
            else:
                y = self.cx.disass(adr)
                if y.dstadr:
                    self.cx.m.set_first_label(y.dstadr, lbl)
                else:
                    self.cx.m.set_first_label(adr, lbl)

R1K_OPS = {
    0x02: "DISK",
    0x03: "TAPE",
    0x05: "NOP",
    0x06: "VME",
    0x07: "MEM",
}

R1K_OPS_DISK = {
    0x02: "PROBE",
}

MODEM_FSM_1 = {
}

MODEM_FSM_2 = {
    0x01: "Expect_COM",
    0x0b: "Expect_Online",
    0x0e: "Expect_CRNLCRNL",
    0x05: "Expect_password",
    0x07: "Expect_1200_BAUD",
    0x09: "Expect_to_call",
    0x00: "Expect_SERVICE",
}

MODEM_FSM_3 = {
    0x00: "Expect_COM",
    0x04: "Expect_password",
    0x06: "Expect_1200_BAUD",
    0x08: "Expect_to_call",
    0x0a: "Expect_Online",
    0x0d: "Expect_CRNL",
}

SCSI_OP = {
    0x02: "READ_6",
    0x03: "WRITE_6",
    0x04: "READ_6_1024",
    0x09: "REQUEST_SENSE",
    0x0a: "READ_DEFECT_DATA_10",
    0x0d: "FORMAT_UNIT",
    0x12: "SEEK_6",
    0x13: "MODE_SELECT_6",
    0x14: "MODE_SENSE_6",
    0x15: "WRITE_SAME_512",
    0x16: "VENDOR_0x06",
    0x17: "SEND_DIAGNOSTIC",
    0x18: "RECEIVE_DIAGNOSTIC",
    0x19: "READ_BUFFER",
    0x1b: "READ_LONG_10",
    0x1a: "WRITE_BUFFER",
    0x1c: "WRITE_LONG_10",
    0x1d: "VENDOR_0xda",
    0x1e: "VENDOR_0xd8",
    0x1f: "VENDOR_0xd2",
    0x20: "VENDOR_0xd1",
}

def round_1(cx):
    ''' Let the disassembler loose '''

    Dispatch_Table(cx, 0x3b82, 4, "MODEM_VEC1_DUART", kind="JSR")
    Dispatch_Table(cx, 0x42e6, 6, kind="JSR", width=2)

    Dispatch_Table(cx, 0xa494, 8, "KC15_BoardCmds")

    Dispatch_Table(cx, 0xa8a0,  8, "R1K_OP", R1K_OPS, "(A0=mailbox)")
    Dispatch_Table(cx, 0x2448,  3, "R1K_OP_01", {}, "(A0=mailbox)", "JSR")
    Dispatch_Table(cx, 0xa68c, 33, "R1K_OP_02_DISK", R1K_OPS_DISK, "(A0=mailbox)")
    Dispatch_Table(cx, 0xa19c,  6, "R1K_OP_04", {}, "(A0=mailbox)", "JSR")
    Dispatch_Table(cx, 0xa79c, 10, "R1K_OP_06_VME", {}, "(A0=mailbox)")
    Dispatch_Table(cx, 0x8188,  6, "R1K_OP_07", {}, "(A0=mailbox)")
    Dispatch_Table(cx, 0xa8c0, 32, "R1K_OP_03_TAPE", {}, "(A0=mailbox)")
    Dispatch_Table(cx, 0x695e,  5, "R1K_OP_06_VME_01", {}, "(A0=mailbox)")
    Dispatch_Table(cx, 0x8234,  6, "R1K_OP_07_MEM", {}, "(A0=mailbox)")

    for i in range(16):
        adr = 0xa1fc + i * 2
        val = cx.m.bu16(adr)
        data.Dataptr(cx.m, adr, adr + 2, dst = val)
        if val:
            Dispatch_Table(cx, val, 21, width=2, pfx="0xa1fc[0x%x]" % i)

    Dispatch_Table(cx, 0xa3b7, 7, width=2)

    Dispatch_Table(cx, 0xa5b1, 18, "MODEM_FSM_1", MODEM_FSM_1)
    Dispatch_Table(cx, 0xa5f9, 18, "MODEM_FSM_2", MODEM_FSM_2)
    Dispatch_Table(cx, 0xa641, 18, "MODEM_FSM_3", MODEM_FSM_3)
    Dispatch_Table(cx, 0xa4e0, 14, "MODEM_TIMEOUT")
    cx.m.set_label(0x1454, "modem_timeout")
    cx.m.set_label(0x1460, "modem_fsm_next")
    cx.m.set_label(0x40e2, "MODEM_FSM_ADVANCE(D0=tmo, D1=nxt)")

    Dispatch_Table(cx, 0x6720,  5)
    Dispatch_Table(cx, 0x7890,  8)
    Dispatch_Table(cx, 0x7e1e,  7)
    Dispatch_Table(cx, 0x7b5c,  4)
    Dispatch_Table(cx, 0xa42c,  21, width=2)
    Dispatch_Table(cx, 0xa710,  33, "SCSI_OP", SCSI_OP)

    cx.codeptr(0xa7c4)

    Dispatch_Table(cx, 0xa954,  16, None, {})

    for a, b in (
        (0x0d1c, "console_desc { B=wptr, B=rdptr, W=nbuf, L=buffer }"),
        (0x2602, "see 0x2612"),
        (0x2602, "via 0x09c4()"),
        (0x263e, "via 0x118"),
        (0x2694, "via 0x128"),
        (0x2e04, "See 00002bb6"),
        (0x2f02, "via 0x147d"),
        (0x3180, "via 0x09c4()"),
        (0x31c4, "via 0x12c"),
        (0x36aa, "via 0x09c4()"),
        (0x3b3e, "via 0x130"),
        (0x3b4a, "via 0x1438"),
        (0x3b58, "See 0000354e"),
        (0x3ed2, "via 0x143c"),
        (0x3ee0, "via 0x143c"),
        (0x3eee, "via 0x1440"),
        (0x3efc, "via 0x1440"),
        (0x3f08, "via 0x1444"),
        (0x3f16, "via 0x1444"),
        (0x3f24, "via 0x1448"),
        (0x3f32, "via 0x1448"),
        (0x4104, "via 0x09c4()"),
        (0x4120, "via 0x11c"),
        (0x4208, "via 0x144c"),
        (0x4214, "via 0x144c"),
        (0x4226, "via 0x09c4()"),
        (0x440e, "via 0x09c4()"),
        (0x4544, "via 0x147d"),
        (0x4548, "via 0x147d"),
        (0x46a0, "MANUAL"),
        (0x46aa, "via 0x147d"),
        (0x46c8, "MANUAL"),
        (0x49ba, "via 0x128"),
        (0x50b8, "MANUAL"),
        (0x5b52, "MANUAL"),
        (0x6246, "via VME_LONGJMP2"),
        (0x6312, "via 0x520"),
        (0x6734, "MANUAL"),
        (0x6738, "MANUAL"),
        (0x6940, "via 0x09c4()"),
        (0x6a0e, "via 0x520"),
        (0x6b8e, "via 0x09c4()"),
        (0x7fd4, "via VME_LONGJMP2"),
        (0x8208, "via 0x520"),
        (0x82bc, "Via 0x8"),
        (0x842a, "MANUAL"),
        (0x8480, "via 0x09c4()"),
        (0x8d72, "MANUAL"),
        (0x9cb8, "via 0x520"),
        (0x9cc0, "MANUAL"),
        (0x9e88, "Wake after stop"),
        (0x9f0e, "via 0x09c4()"),
        (0x62c6, "via 0xa7c4"),
        (0x9756, "MANUAL"),
    ):
        cx.disass(a)
        cx.m.set_block_comment(a, b)

    for a, b in (
        (0x04eb, "kc12_sleep_callout_flag"),
        (0x0784, "kc12_sleep_callout"),
        (0x0d1c, "CONSOLE_RXFIFO"),
        (0x0d22, "CONSOLE_RXFIFO.ptr"),
        (0x0d24, "MODEM_RXFIFO"),
        (0x0d2a, "MODEM_RXFIFO.ptr"),
        (0x0d2c, "IMODEM_RXFIFO"),
        (0x0d32, "IMODEM_RXFIFO.ptr"),
        (0x0d3c, "CONSOLE_RXBUF"),
        (0x0e3c, "MODEM_RXBUF"),
        (0x0f3c, "IMODEM_RXBUF"),
        (0x1429, "XE1201_CTRL_COPY"),
        (0x1434, "MODEM_TXBUF"),
        (0x1438, "MODEM_VEC_1_SEND_BYTE"),
        (0x143c, "MODEM_VEC_2_ENABLE_TX"),
        (0x1440, "MODEM_VEC_3_DISABLE_TX"),
        (0x1444, "MODEM_VEC_4_RAISE_DTR"),
        (0x1448, "MODEM_VEC_5_LOWER_DTR"),
        (0x144c, "MODEM_VEC_6"),
        (0x1481, "MODEM_EXPECT"),
        (0x1485, "MODEM_STATE"),
        (0x14dd, "diagbus_rxsum"),
        (0x14e0, "diagbus_rxwant"),
        (0x14e4, "diagbus_rxptr"),
        (0x150c, "diagbus_inbuf"),
        (0x160c, "diagbus_callout_flag"),
        (0x160e, "diagbus_callout"),
        (0x163c, "Timeout_chain"),
        (0x2204, "D0=MODEM_GET_CHAR(D0)"),
        (0x2244, "TEXT_TO_MODEM(A2=ptr, D1=len, D2, D3)"),
        (0x2288, "_KC09_MODEM(D0.W)"),
        (0x22f4, "_KC07_READ_CONSOLECHAR(D0<=port, D0=>char)"),
        (0x2374, "TEXT_TO_CONSOLE(A2=ptr,D1=len, D3)"),
        (0x2410, "kc08_meat(D3=W, D0=B)"),
        (0x2978, "GET_CONSOLE_DESC(D0=port.W)"),
        (0x3112, "START_MODEM(void)"),
        (0x32f4, "INIT_KERNEL_05_UARTS"),
        (0x3486, "SETUP_IMODEM"),
        (0x34e4, "SETUP_XMODEM"),
        (0x362c, "DiagBusResponse(D2)"),
        (0x36aa, "DiagBusTimeoutCallback()"),
        (0x374c, "DO_KC_15_DiagBus(D0=cmd,A0=ptr)"),
        (0x3970, "INT_MODEM_RESET"),
        (0x3b4a, "MODEM_VEC_1_XE1201_SEND_BYTE"),
        (0x3b58, "MODEM_VEC_1_DUART_SEND_BYTE"),
        (0x3e96, "MODEM_IS_X"),
        (0x3ed2, "MODEM_VEC_2_XE1201_ENABLE_TX"),
        (0x3ee0, "MODEM_VEC_2_DUART_ENABLE_TX"),
        (0x3eee, "MODEM_VEC_3_XE1201_DISABLE_TX"),
        (0x3efc, "MODEM_VEC_3_DUART_DISABLE_TX"),
        (0x3f08, "MODEM_VEC_4_XE1201_RAISE_DTR"),
        (0x3f16, "MODEM_VEC_4_DUART_RAISE_DTR"),
        (0x3f24, "MODEM_VEC_5_XE1201_LOWER_DTR"),
        (0x3f32, "MODEM_VEC_5_DUART_LOWER_DTR"),
        (0x4208, "MODEM_VEC_6_XE1201"),
        (0x4214, "MODEM_VEC_6_DUART"),
        (0x4b20, "CHS512_TO_LBA1024(A0=CHAN)"),
        (0x4cdc, "SCSI_OPERATION(A0=mailbox)"),
        (0x520c, "SCSI_D_REQ_SENSE(scsi_id=D2)"),
        (0x5b98, "INIT_KERNEL_06_DISKS"),
        (0x5d14, "DELAY_LOOP(D1)"),
        (0x5d28, "PROBE_DISK_GEOMETRY(D2)"),
        (0x5db0, "SCSI_D_MODE_SENSE_3(scsi_id=D2)"),
        (0x5dca, "SCSI_D_MODE_SENSE_4(scsi_id=D2)"),
        (0x5e6a, "SCSI_D_WAIT_STATUS(timeout=D2)"),
        (0x5e8a, "SCSI_D_WAIT_COMPLETE(timeout=D2)"),
        (0x5f16, "SCSI_D_TEST_UNIT_READY()"),
        (0x5f74, "INIT_KERNEL_11"),
        (0x5f7a, "SAVECORE()"),
        (0x6072, "SCSI_D_WRITE_10_SOMETHING(scsi_id=D0,src=D4,blockno=D6)"),
        (0x66a8, "INIT_KERNEL_10_VME"),
        (0x8398, "BOUNCE_TO_FS"),
        (0x8420, "Assert_612_still_booting"),
        (0x8480, "KC12_Sleep_CallBack"),
        (0x8acc, "INIT_KERNEL_04"),
        (0x8ae8, "ReturnMailbox_0()"),
        (0x8af0, "ReturnMailbox_1()"),
        (0x8bec, "Stuff_Response_Fifo(A1)"),
        (0x8df0, "GET_SECTOR_BUFFER([A0+0x13].B => A1)"),
        (0x8e12, "CONFIG_IO_MAP()"),
        (0x8eb4, "INIT_KERNEL_03_FIFO"),
        (0x9ad0, "INIT_KERNEL_07"),
        (0x9c40, "INIT_KERNEL"),
        (0x9cee, "INIT_KERNEL_01"),
        (0x9d6e, "Timeout_Stop_PIT(A1)"),
        (0x9d8e, "Timeout_Start_PIT()"),
        (0x9dc4, "Timeout_Arm(D0=ticks,A2=entry)"),
        (0x9e00, "Timeout_Cancel(A2=entry)"),
        (0x9e6a, "Timeout_Init()"),
        (0x9e74, "AwaitInterrupt()"),
        (0x9f0e, "INIT_KERNEL_08"),
        (0x9fde, "INIT_KERNEL_09"),
        (0xe000, "CONSOLE_N_DESC"),
        (0xe00e, "CONSOLE_XON_CHAR"),
        (0xe00f, "CONSOLE_XOFF_CHAR"),
    ):
        cx.m.set_label(a, b)

    for a, b in (
        (0x4b2a, "chan.drive"),
        (0x4b2e, "chan.cyl"),
        (0x4b32, "must be <= n_cyl"),
        (0x4b3a, "multiply by n_heads"),
        (0x4b40, "chan.head"),
        (0x4b44, "must be <= n_heads"),
        (0x4b5e, "multiply by n_sect.512"),
        (0x4b64, "chan.sect"),
        (0x4b68, "must be <= n_sect.512"),
        (0x4b72, "sect.512 -> sect.1024"),
        (0x4b78, "drive_desc.lba"),
        (0x1a120, "A1 = return address"),
        (0x1a12a, "length of exp name"),
        (0x1a130, "A1 now after string"),
        (0x1a14a, "1st byte after string"),
        (0x1a14c, "2nd byte after string"),
        (0x1a15a, "3rd byte after string"),
        (0x1a15c, "4th byte after string"),
    ):
        cx.m.set_line_comment(a, b)

    cx.m.set_label(0xa878, "Month_Table")
    for a in range(0xa878, 0x0a8a0, 2):
        data.Const(cx.m, a, a + 2)

    cx.m.set_block_comment(0x3970, "Reset INT_MODEM by writing 3 zeros to cmd reg")

    cx.codeptr(0x51c)
    cx.m.set_label(0x51c, "IO_TIMEOUT_TMP")
    cx.codeptr(0x520)
    cx.m.set_label(0x520, "IO_TIMEOUT")

    cx.codeptr(0x1778)
    cx.m.set_label(0x1778, "VME_LONGJMP1")
    cx.codeptr(0x177c)
    cx.m.set_label(0x177c, "VME_LONGJMP2")


    y = data.Const(cx.m, 0xa7e4, 0xa7f4)
    cx.m.set_label(y.lo, "stack_adjust")


def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''

'''
00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
                                                                                             -- 0x00...0x56 even numbers
                                                                                             S@512
                                                                                          --    0x00...0x0e
                                                                                          HD
                                                                                    -----[-- --] 0x0000...0x0031
                                                                                    CYL
                                                                                 --             0x02/0x03
                                                                              --                0x00
                                                                              DRIVE
                                                                           --                   0x80/0x84/0x86
00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
                                                               --                               0x02
                                                            -----------                         0x??0200000 ?? even
                                                   -----------                                  pointer
                                                -----------                                     ????????
                                                --                                              ??
00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
                                          --                                                    0x81,0xa1,0xc1
                        -----------                                                             0x00000000...0x00020000
                        LENGTH

            -----------                                                                         0x954,0x9303fc00
            DRIVEDESC/SCSI CDB ?

-----------                                                                                     0x00004d{58,60,92,a2}

0       0       4       2
0       0       8       4
13      3       52      0x22e8
13      12      58      0x2480
'''

