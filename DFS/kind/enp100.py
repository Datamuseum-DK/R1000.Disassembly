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
   ENP100 TCP/IP code
   ------------------
'''

from pyreveng import data, discover

#######################################################################

def flow_check(asp, ins):
    for f in ins.flow_out:
        if f.to in (
            0xe001706c,
        ):
            if asp.bu16(ins.lo - 6) == 0x4879:  # PEA.L
                 i = asp.bu32(ins.lo - 4)
                 y = data.Txt(asp, i, align=1, splitnl=True)

#######################################################################

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    cx.flow_check.append(flow_check)

def round_1(cx):
    ''' Let the disassembler loose '''
    cx.disass(0xe0004000)
    cx.disass(0xe0004010)
    for a in range(0xe001c92c, 0xe001c9d0, 4):
        cx.codeptr(a)

def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
    for a, b in cx.m.gaps():
        for i in range(a, b, 4):
            if not cx.m[i] == 0xe0:
                continue
            j = cx.m.bu32(i)
            if a <= j < b:
                if cx.m.bu16(j) == 0x4e56:
                    cx.disass(j)
    discover.Discover(cx)
