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
   IOC second quarter/e2df11e2533ad8c4 
   -----------------------------------
'''

from pyreveng import data

def boot_reason(cx, a):
    ''' Coded string table '''
    data.Const(cx.m, a, a+1)
    b = cx.m[a]
    assert b & 0x80
    i = 1
    while True:
        j = cx.m[a+i]
        if not j or j & 0x80:
            break
        i += 1
    y = data.Txt(cx.m, a+1, a+i, label=False)
    return y.hi

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    for a in (
        0x8000221c,
        0x80002232,
        0x8000223d,
        0x80002481,
        0x8000256e,
        0x8000257d,
        0x8000258c,
        0x800027ee,
        0x8000287b,
        0x8000289f,
        0x80002a24,
        0x80002a2c,
        0x80002c14,
        0x80003690,

    ):
        data.Txt(cx.m, a, splitnl=True)

    a = 0x8000228f
    while cx.m[a] & 0x80:
        a = boot_reason(cx, a)
    data.Const(cx.m, a, a + 1)
    data.Txt(cx.m, a+1, label=False)

    a = 0x80002d2d
    while a < 0x80002dff:
        y = data.Txt(cx.m, a, label=False)
        a =y.hi

    for a in range(0x800036e8, 0x800036fc, 4):
        y = cx.dataptr(a)
        data.Txt(cx.m, y.dst, label=False)

def round_1(cx):
    ''' Let the disassembler loose '''

    for a, b in (
        (0x80002790, None),
        (0x800027a8, None),
        (0x80002bc4, None),
    ):
        cx.disass(a)
        cx.m.set_line_comment(a, "MANUAL")
        if b:
            cx.m.set_label(a, b)


    # EEprom writing trampoline
    data.Const(cx.m, 0x80003a2a, 0x80003a2c)
    cx.disass(0x80003a2c)

    for a, b in (
        (0x800024a8, "out_hex_digits(n=D1,val=D2)"),
        (0x800024b6, "report_boot_reason_code()"),
        (0x800025ce, "ask_which_boot_device"),
        (0x80002634, "boot_L"),
        (0x80002642, "boot_tape"),
        (0x800026a2, "boot_disk"),
        (0x800026d6, "boot_400S"),
        (0x8000271a, "boot_default_device"),
        (0x80002e22, "show_boot_menu"),
        (0x80002f2c, "menu_change_boot_crash_maint"),
        (0x80002f58, "menu_change_iop_config"),
        (0x80002e8c, "menu_enable_manual_crash_debugging"),
        (0x80002e84, "menu_boot_iop_ask_media"),
        (0x80003344, "REPORT_BOOT_IP_TAPE_CONFIG"),
        (0x80003526, "REPORT_TAPE_DRIVES"),
        (0x8000366e, "OUTPUT_IP_NUMBER(A1)"),
        (0x800036e8, "machine_type_table"),
        (0x8000386c, "whine_on_duarts"),
        (0x800038b0, "duart_loop"),
        (0x800038ee, "duart_step_a"),
        (0x80003914, "duart_step_b"),
        (0x8000394c, "duart_step_c"),
        (0x80003950, "duart_step_d"),
        (0x8000396c, "duart_modem_rxchar(->D0)"),
        (0x8000397a, "duart_modem_txchar(D0)"),
        (0x80003988, "duart_diag_rxchar(->D0)"),
        (0x80003996, "duart_diag_tx_mode_1b_char(D0)"),
        (0x800039b0, "duart_diag_tx_mode_1f_char(D0)"),
        (0x80003a2a, "eeprom_trampoline_magic"),
        (0x80003a2c, "eeprom_write_trampoline"),
    ):
        cx.m.set_label(a, b)

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
