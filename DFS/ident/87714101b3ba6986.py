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
   RDIAG / 26adbd2fa5860e7d.html
   -------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''

    for a, b, n in (
        (0x201b4, 0x2022c, 10),
        (0x2025e, 0x202f4, 10),
        (0x202f8, 0x2036c, 10),
        (0x203ac, 0x20438, 10),
        (0x204f0, 0x20540, 10),
        (0x205de, 0x20638, 10),
        (0x2095c, 0x20c5e, 10),
        (0x2276e, 0x2291c, 10),
        (0x22b66, 0x22d10, 10),
    ):
        for i in range(a, b, n):
            data.Txt(cx.m, i, i + n, label=False)

    cx.m.set_label(0x20bb4, "TXTTBL_POWER_MARGINS")
    cx.m.set_label(0x20bdc, "TXTTBL_CLOCK_MARGINS")
    cx.m.set_label(0x20c04, "TXTTBL_CMDS")
    cx.m.set_label(0x20a74, "TXTTBL__ALL_COND_SYS_VAL...")
    cx.m.set_label(0x22b5c, "TBL_something")

    cx.m.set_label(0x23272, "CHECK_ARG_CNT(Int)")
    cx.m.set_label(0x23b98, "POP_ARG(?)")
    cx.m.set_label(0x23c90, "PUSH_ARG(?)")
    cx.m.set_label(0x279a8, "variables")
    cx.m.set_label(0x27982, "eval_buffer?")
    cx.m.set_label(0x23fd0, "FIND_VAR(?)")
    cx.m.set_label(0x225dc, "DISPATCH_CMDS(?)")
    cx.m.set_label(0x22472, "MATCH_CMDS(?)")
    cx.m.set_label(0x221f8, "MATCH_CLOCK_MARGINS(?)")
    cx.m.set_label(0x22168, "MATCH_POWER_MARGINS(?)")
    cx.m.set_label(0x25516, "TRY_SCRIPT_FILE(?)")
    for adr, prim in (
         (0x23cee, "WRITE"),
         (0x23ecc, "ABORT"),
         (0x241f2, "SET"),
         (0x24364, "VAR"),
         (0x24452, "VARS"),
         (0x2484e, "EQ"),
         (0x248c6, "NE"),
         (0x2493e, "CASE"),
         (0x2496a, "INSERT"),
         (0x24a6a, "EXTRACT"),
         (0x24b50, "#CASE"),
         (0x24b7c, "#EQ"),
         (0x24bc8, "#NE"),
         (0x24c14, "#LT"),
         (0x24c60, "#GT"),
         (0x24cac, "#LE"),
         (0x24cf8, "#GE"),
         (0x24d44, "ADD"),
         (0x24d8e, "SUB"),
         (0x24dd8, "MUL"),
         (0x24e22, "DIV"),
         (0x24e6c, "MOD"),
         (0x24eb6, "OR"),
         (0x24f00, "AND"),
         (0x24f4a, "XOR"),
         (0x24f94, "LSHIFT"),
         (0x24fd8, "RSHIFT"),
         (0x2501e, "NOT"),
         (0x25054, "#INSERT"),
         (0x250e4, "#EXTRACT"),
         (0x25156, "READ"),
         (0x244b4, "KILL"),
         (0x2451e, "PUSH"),
         (0x244f0, "LEVEL"),
         (0x251c8, "CONVERT"),
         (0x2534a, "COUNT_ONES"),
         (0x252ca, "REPEAT"),
         (0x2538e, "MODEL"),
         (0x253ae, "ASCII"),
    ):
        cx.m.set_label(adr, "PRIM_" + prim + "(?)")

    for adr, cmd in (
         (0x21746, "TEST"),
         (0x21ae2, "RUN"),
         (0x21ea4, "ERRMESS"),
         (0x2150e, "INIT_STATE"),
         (0x22096, "ISOLATE"),
         (0x220dc, "TRACE"),
         (0x22122, "ULOAD"),
         (0x22288, "MARGIN"),
         (0x22518, "POWERDOWN"),
    ):
        cx.m.set_label(adr, "CMD_" + cmd + "(?)")

def round_1(cx):
    ''' Let the disassembler loose '''

    cx.disass(0x20df0)
    cx.disass(0x20e4e)
    cx.disass(0x22e60)
    cx.disass(0x22e68)
    cx.disass(0x232fe)

def round_2(cx):
    ''' Spelunking in what we alrady found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
