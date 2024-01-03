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
   Kernel Subroutines
   ------------------
'''

from pyreveng import assy, data

def month_table(cx, adr):
    cx.m.set_label(adr, "Month_Table")
    for a in range(adr, adr + 0x13 * 2, 2):
        data.Const(cx.m, a, a + 2)

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

def port_fifos(cx, adr):
    for port, name in enumerate(("CONSOLE", "MODEM", "IMODEM", "PORT3")):
        base = adr + 8 * port
        cx.m.set_label(base, name + "_RXFIFO.0")
        cx.m.set_label(base + 1, name + "_RXFIFO.1")
        cx.m.set_label(base + 2, name + "_RXFIFO.cnt")
        cx.m.set_label(base + 4, name + "_RXFIFO.ptr_l")
        cx.m.set_label(base + 6, name + "_RXFIFO.ptr_w")
        fifo = adr + 0x20 + 0x100 * port
        cx.m.set_label(fifo, name + "_RXBUF")
        y = data.Data(cx.m, fifo, fifo + 0x100)
        y.compact = True
        ptr = base + 6
        y = data.Const(cx.m, ptr, ptr + 2, "0x%04x", cx.m.bu16, 2)
        cx.m.set_line_comment(ptr, "=> " + name + "_RXBUF")

def menu_dispatch(cx, base):
    cx.m.set_label(base, "MENU_DISPATCH")
    for i in range(16):
        adr = base + i * 2
        val = cx.m.bu16(adr)
        data.Dataptr(cx.m, adr, adr + 2, dst = val)
        if val:
            Dispatch_Table(cx, val, 21, width=2, pfx="menu_dispatch[0x%x]" % i)

FSM_VEC = [
    "VEC_1_SEND_BYTE",
    "VEC_2_ENABLE_TX",
    "VEC_3_DISABLE_TX",
    "VEC_4_RAISE_DTR",
    "VEC_5_LOWER_DTR",
    "VEC_6_ENABLE_RX",
]

def fsm_vectors(cx, base):
    for i in FSM_VEC:
        cx.m.set_label(base, "FSM_" + i)
        base += 4

def fsm_funcs(cx, pfx, funcs):
    for i, j in zip(funcs, FSM_VEC):
        if i is not None:
            cx.m.set_label(i, pfx + "_" + j)
            cx.disass(i)

def reg_save(cx, adr):
    for a in range(adr, adr + 0x3c, 4):
        cx.m.set_label(a, "REG_SAVE_%X" % cx.m[a])
        data.Const(cx.m, a, a + 4)

def drive_desc(cx, a):
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


def drive_table(cx, tbl, descs, ndrive=4):
    cx.m.set_label(tbl, "DRIVE_TABLE")
    for d in range(ndrive):
        y = cx.dataptr(tbl + 4*d)
        desc = descs + d * 0x5c
        cx.m.set_label(desc, "DRIVE_DESC[%d]" % d)
        drive_desc(cx, desc)

