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
   FS generic stuff
   ----------------
'''

from pyreveng import assy

import pyreveng.cpu.m68020 as m68020

import pascal_pseudo_ins
import dfs_syscalls

#######################################################################

FS_DESC = '''
KERNCALL        vect,>J         |1 0 1 0 0 0 0 0| vect          |
'''

class FsIns(m68020.m68020_ins):
    ''' Kernel specific (pseudo-)instructions'''

    def assy_vect(self):
        ''' vector number '''
        return assy.Arg_imm(self['vect'])

#######################################################################

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    pascal_pseudo_ins.add_pascal_pseudo_ins(cx)
    cx.it.load_string(FS_DESC, FsIns)
    cx.dfs_syscalls = dfs_syscalls.DfsSysCalls(hi=cx.m.bu32(0x10004))
    cx.dfs_syscalls.round_0(cx)

def round_1(cx):
    ''' Let the disassembler loose '''
    y = cx.codeptr(0x10004)
    cx.m.set_label(y.dst, "START")
    cx.m.set_block_comment(y.dst, "START")
    cx.dfs_syscalls.round_1(cx)

def round_2(cx):
    ''' Spelunking in what we already found '''
    cx.dfs_syscalls.round_2(cx)

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
    for sc in cx.dfs_syscalls:
        i = cx.m.bu16(sc.adr)
        if i == 0x6000:
            j = sc.adr + 2 + cx.m.bs16(sc.adr + 2)
        elif i == 0x4ef9:
            j = cx.m.bu32(sc.adr + 2)
        else:
            continue
        cx.m.set_label(j, "_" + sc.name)
