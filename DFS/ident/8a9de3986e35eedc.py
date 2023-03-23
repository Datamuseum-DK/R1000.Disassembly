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
   RUN_UDIAG.M200 / 8a9de3986e35eedc.html
   --------------------------------------
'''

from pyreveng import data

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    data.Txt(cx.m, 0x2014c, 0x20170)
    data.Txt(cx.m, 0x20170, 0x20198)
    data.Txt(cx.m, 0x2019a, 0x201a0)
    data.Txt(cx.m, 0x201a0, 0x201ae)

def round_1(cx):
    ''' Let the disassembler loose '''

def round_2(cx):
    ''' Spelunking in what we already found '''
    for a, b in (
        (0x203ce, None),
        (0x20406, None),
    ):
        cx.disass(a)
        if b:
            cx.m.set_label(a, b)
        cx.m.set_line_comment(a, "MANUAL")

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''

    for a, b in (
        (0x2077a, "START_ALL_BOARDS()"),
        (0x20bd6, "RUN_UNTIL_STOP()"),
        (0x2130e, "exp_SET_HIT.MEM()"),		# 0002061c
        (0x213cc, "exp_RESET_MEM.MEM()"),	# 00020834
        (0x21476, "exp_RUN_CHECK.MEM()"),	# 00020796
        (0x21608, "exp_FILL_MEMORY.MEM()"),	# 00020d02
        (0x21882, "exp_CLEAR_HITS.MEM()"),	# 00020622
    ):
        cx.m.set_label(a, b)
