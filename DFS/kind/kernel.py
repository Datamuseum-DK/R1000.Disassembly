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
   KERNEL generic stuff
   --------------------
'''

from pyreveng import assy, data
import pyreveng.cpu.m68020 as m68020

import ioc_hardware
import ioc_eeprom_exports
import dfs_syscalls

#######################################################################

KERNEL_DESC = '''
PANIC.W         tvect,>R        |0 1 0 1|0 0 0 0|1 1 1 1|1 0 1 0| w                             |
'''

class KernelIns(m68020.m68020_ins):
    ''' Kernel specific (pseudo-)instructions'''

    def assy_tvect(self):
        ''' vector number/message '''
        self.lang.m.set_label(self.lo, "PANIC_0x%x" % self['w'])
        return assy.Arg_imm(self['w'])

#######################################################################

def vector_line_a(cx):
    ''' Follow the LINE_A vector to find KERNCALL entrypoints '''
    a = cx.m.bu32(0x28)
    for i, j in (
        (0x00, 0x48), (0x01, 0xe7), (0x02, 0x80), (0x03, 0x04),
        (0x1a, 0x4e), (0x1b, 0xb0), (0x1c, 0x05),
    ):
        if cx.m[a + i] != j:
            print("Line_a mismatch", "0x%x" % i, "0x%x" % j, "0x%x" % cx.m[a+i])
            return
    if cx.m[a + 0x1d] == 0xa1:
        tbl = cx.m.bu16(a + 0x1e)
    elif cx.m[a + 0x1d] == 0xb1:
        tbl = cx.m.bu32(a + 0x1e)
    else:
        print("Line_a mismatch", "0x1d", "(0xa1/0xb1)", "0x%x" % cx.m[a+0x1d])
        return

    cx.m.set_label(tbl, "KERNCALL_VECTORS")
    for sc in range(33):
        i = tbl + sc * 4
        y = cx.codeptr(i)
        syscall = cx.dfs_syscalls[sc * 2 + 0x10200]
        syscall.set_block_comment(cx, y.dst)
        cx.m.set_block_comment(y.dst, "(From PTR @ 0x%x)" % (i))
        cx.m.set_label(y.dst, syscall.name)

#######################################################################

def hunt_vectors(cx):
    ''' hunt code pointed to by dynamic assignment to vectors '''
    cand = set()
    cands = -1
    while len(cand) != cands:
        cands = len(cand)
        for node in cx.m:
            if cx.m.bu16(node.lo) != 0x21fc:
                continue
            src = cx.m.bu32(node.lo + 2)
            dst = cx.m.bu16(node.lo + 6)
            if dst & 0x8000:
                continue
            if dst > 0x400 or dst & 3:
                continue
            cx.disass(src)
            cand.add((src, dst))
    for i, j in cand:
        dst = cx.m.bu32(j) 
        lbl = list(cx.m.get_labels(dst))
        cx.m.set_line_comment(i, "Via " + lbl[0])

#######################################################################

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    ioc_hardware.add_symbols(cx.m)
    ioc_eeprom_exports.add_symbols(cx.m)
    cx.it.load_string(KERNEL_DESC, KernelIns)
    cx.dfs_syscalls = dfs_syscalls.DfsSysCalls()
    ioc_eeprom_exports.add_flow_check(cx)

    cx.m.set_block_comment(0x400, "Microcode Information Block")

    y = data.Const(cx.m, 0x400, 0x404, "0x%08x", cx.m.bu32, 4)
    cx.m.set_line_comment(y.lo, "?Number of slots")

    y = data.Const(cx.m, 0x404, 0x406, "0x%04x", cx.m.bu16, 2)
    cx.m.set_line_comment(y.lo, "?Buffer size")

    y = data.Const(cx.m, 0x406, 0x408, "0x%04x", cx.m.bu16, 2)
    cx.m.set_line_comment(y.lo, "?Mailbox size")

    y = cx.dataptr(0x408)
    cx.m.set_line_comment(y.lo, "?Mailbox Base Address")

    y = cx.dataptr(0x40c)
    cx.m.set_line_comment(y.lo, "?Buffer Base Address")

    y = data.Const(cx.m, 0x410, 0x416, "%d", cx.m.bu16, 2)
    cx.m.set_line_comment(y.lo, "Version number")

    
    y = data.Const(cx.m, 0x77a, 0x77c, "0x%04x", cx.m.bu16, 2)
    cx.m.set_label(y.lo, "live0_boot1")

    cx.dataptr(0x416)

def round_1(cx):
    ''' Let the disassembler loose '''
    for vec, lbl in ioc_hardware.INTERRUPT_VECTORS.items():
        d = cx.m.bu32(vec * 4)
        cx.m.set_label(d, "VECTOR_" + lbl)
    cx.vectors(0x400)
    vector_line_a(cx)

def round_2(cx):
    ''' Spelunking in what we already found '''
    hunt_vectors(cx)

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''
