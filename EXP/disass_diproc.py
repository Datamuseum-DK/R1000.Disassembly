#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2021 Poul-Henning Kamp <phk@phk.freebsd.dk>
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

import os
import sys

from pyreveng import mem, code, data, listing, instree
import pyreveng.cpu.mcs51 as mcs51

import exp_disass

MYDIR = os.path.split(__file__)[0]
FILENAME1 = os.path.join(MYDIR, "P8052AH_9028.bin")
FILENAME2 = "/home/phk/Proj/PHK110_R1000_DIAG/Take2_Analysis/mem32_diproc.bin"

class ExpDisass():
    ''' Provide disassembled EXP instructions '''
    def __init__(self):
        self.disass = dict()
        exp_tree = instree.InsTree(8)
        exp_tree.load_string(exp_disass.R1K_EXP)
        for ins in range(0, 1<<16):
            def getmore(_adr, vec):
                vec += [ins >> 8, ins & 0xff, 0, 0, 0, 0]
            idx = (ins >> 8) & 0xfe
            if idx not in self.disass:
                self.disass[idx] = set()
            for inst in exp_tree.find(0x20, getmore):
                if "FAIL" in inst.assy[0]:
                    break
                txt = inst.assy[0].ljust(12)
                txt += inst.assy[1].ljust(24)
                txt += inst.pil.raw_bits
                self.disass[idx].add(txt)
                break

    def __getitem__(self, ins):
        yield from self.disass[ins]

class DiprocDisass():

    def __init__(self, octets, output_file="/tmp/_", **kwargs):
        self.exp_ins = ExpDisass()
        m = mem.ByteMem(0, len(octets))
        for adr, octet in enumerate(octets):
            m[adr] = octet
        self.cx = mcs51.I8032()
        self.cx.m.map(m, 0)
        self.cx.vectors(
            (
                "RESET",
                "RI_TI",
            )
        )

        self.common()

        self.distinct()

        code.lcmt_flows(self.cx.m)

        listing.Listing(
            self.cx.m,
            fn=output_file,
            align_blank=True,
            align_xxx=True,
            ncol=4,
            **kwargs
        )

    def common(self):

        for adr, lbl in (
            (0x00003, "diag_address"),
            (0x00004, "diag_status"),
            (0x00005, "diag_loop_cnt"),
            (0x00006, "diag_loop_top"),
            (0x00010, "exp_PC"),
            (0x00011, "R1_"),
            (0x00012, "R2_"),
            (0x00013, "R3_"),
            (0x00014, "R4_"),
            (0x00015, "R5_"),
            (0x00016, "R6_"),
            (0x00017, "R7_"),
        ):
            self.cx.as_data.set_label(adr, lbl)

        for i in self.cx.m:
            if i.mne == "ACALL":
                self.cx.m.set_label(i.dstadr, "SET_DIAG_ADDR()")
                break

        uart_vector = list(self.cx.m.find(0x23))[0].dstadr

        for offset, lbl in (
            (0x00, "SERIAL_INTERRUPT()"),
            (0x4d, "DIAG_DO_CMD_R0"),
            (0x4e, "DIAG_DO_CMD_A"),
            (0x53, "DIAG_CMD_6"),
            (0x5d, "DIAG_CMD_0_STATUS"),
            (0x71, "DIAG_CMD_A_DOWNLOAD"),
            (0xa3, "DIAG_CMD_2_UPLOAD"),
            (0xc1, "DIAG_CMD_C"),
            (0xce, "DIAG_CMD_E"),
            (0xdb, "DIAG_CMD_4"),
            (0xdf, "DIAG_CMD_8"),
        ):
            self.cx.m.set_label(uart_vector + offset, lbl)

        rxadr = list(self.cx.m.find(uart_vector + 0xa3))[0].dstadr
        self.cx.m.set_label(rxadr, "SERIAL_RX_BYTE()")
        for i in sorted(self.cx.m.find(lo = rxadr, hi = uart_vector)):
            if i.mne == "RET":
                self.cx.m.set_label(i.hi, "SERIAL_TX_BYTE()")
                break

    def distinct(self):
        return

    def engine(self, execute):
        self.cx.disass(execute)
        self.cx.m.set_label(execute, "EXECUTE")
        bcmt = dict()
        for off, item, _tbl in self.switch(execute + 0x07, execute + 266):
            for cmt in sorted(self.exp_ins[off]):
                cmts = bcmt.get(item.dstadr, set())
                if cmt in cmts:
                    continue
                self.cx.m.set_block_comment(item.dstadr, cmt)
                cmts.add(cmt)
                bcmt[item.dstadr] = cmts

    def switch(self, adr, end):
        setup = self.cx.disass(adr)
        dispatch = self.cx.disass(setup.hi)
        dispatch.flow_out = []
        tbl = setup.dstadr
        for off in range(0, end - tbl, 2):
            dispatch += code.Jump(cond="A=0x%02x" % off, to=tbl + off)
            item = self.cx.disass(tbl + off)
            yield off, item, tbl

    def switch_labeled(self, adr, end):
        for off, item, tbl in self.switch(adr, end):
            if len(list(self.cx.m.get_labels(item.dstadr))) == 0:
                self.cx.m.set_label(item.dstadr, "SUB_%04x_%02x" % (tbl, off))


class DiprocStd(DiprocDisass):

    def distinct(self):
        for adr, lbl in (
            (0x170, "BAD_INS"),
            (0x13d8, "PERMUTE_BITS"),
            (0x1393, "R6 = PICK_BITS()"),
        ):
            self.cx.m.set_label(adr, lbl)

        self.engine(0x51c)
        self.switch_labeled(0x39e, 0x3b2)
        self.switch_labeled(0x3c7, 0x3db)
        self.switch_labeled(0x101e, 0x1115)

        self.cx.m.set_label(0x46f, "fsm_imm")
        self.cx.m.set_label(0x1000, "ins_da")

        self.cx.m.set_label(0x117c, "da_set_1")
        self.cx.m.set_label(0x1194, "da_set_2")
        self.cx.m.set_label(0x1222, "da_set_3")
        self.cx.m.set_label(0x1246, "da_set_4")
        self.cx.m.set_label(0x12c2, "da_set_5")
        self.cx.m.set_label(0x12e1, "da_set_6")
        self.cx.m.set_label(0x133a, "da_set_a")
        self.cx.m.set_label(0x135c, "da_set_c")

        self.cx.m.set_block_comment(0xed5, '''
SEQ.SEQCHAIN
============
DIAG.D7:        BHREG0  8.2 8.1 8.0 7.0 BHREG1  7.1 7.2 7.4 7.3 MEVNT0  4.7 4.6 4.5 4.4 MEVNT1  4.3 4.2 4.1 4.0
DIAG.D6:        UEVENT0 5.0 2.2 3.3 2.3 UEVNT1  3.4 3.5 3.6 3.7 UEVNT2  2.0 2.1 3.0 3.1 UEVNT3  3.2 2.4 2.5 2.6
DIAG.D5:        UADR0   6.6 6.5 0.5 0.4 UADR1   0.3 0.2 0.1 0.0 UADR2   1.7 1.6 1.5 1.4 UADR3   1.3 1.2 1.1 1.0
DIAG.D4:        RESTRG  7.7 --- 7.6 7.5 TSVLD   6.0 8.4 8.5 8.3 PAREG   5.4 5.3 5.2 5.1 LTCHRG  6.1 6.2 6.3 6.4
''')

        for adr, rows, cols  in (
            (0x07b3, 0x0d, 8),
            (0x0809, 0x09, 8),
            (0x085b, 0x09, 8),
            (0x0a60, 0x15, 9),
            (0x0bdf, 0x15, 9),
            (0x0c85, 0x0d, 9),
            (0x0cb7, 0x05, 9),
            (0x0d97, 0x09, 9),
            (0x0e7a, 0x09, 9),
            (0x0ecc, 0x09, 9),
        ):
            if rows:
                self.cx.m.set_label(adr, "TABLE_%04x[0x%02x]" % (adr, rows))
                end = adr + rows
                for i in range(adr, end, cols):
                    j = min(i + cols, end)
                    data.Const(self.cx.m, adr, j, fmt="0x%02x")
                    adr = j
            else:
                self.cx.m.set_label(adr, "TABLE_%04x" % adr)

        self.cx.m.set_block_comment(0x746, '''
This table is used by `READ_RF_A.TYP` and seens to
unpermute the bits between the serial scan-chain and
some "canonical" format.
''')
        for adr, lbl  in (
            (0x0746, "BITSPEC_TYP_RF"),
            (0x07c0, None),
            (0x0812, None),
            (0x0864, None),
            (0x08ad, None),
            (0x08f6, None),
            (0x09ab, None),
            (0x0a75, None),
            (0x0b2a, None),
            (0x0bf4, None),
            (0x0c92, None),
            (0x0cbc, None),
            (0x0d05, "BITSPEC_FIU_MDREG"),
            (0x0d4e, "BITSPEC_FIU_UIR"),
            (0x0da0, None),
            (0x0e31, None),
            (0x0e83, None),
            (0x0ed5, "BITSPEC_SEQ_SEQCHAIN"),
        ):
            if lbl:
                self.cx.m.set_label(adr, lbl)
            else:
                self.cx.m.set_label(adr, "BITSPEC_%04x" % adr)
            while self.cx.m[adr] != 0xff:
                item = data.Data(self.cx.m, adr, adr + 9)
                tbl = []
                for _j in range(8):
                    j = self.cx.m[adr]
                    adr += 1
                    if j != 0x1f:
                        tbl.append("+0x%02x.%d" % (j & 0x1f, 7 - (j >> 5)))
                    else:
                        tbl.append("NOP    ")
                tbl.append("0x%02x" % self.cx.m[adr])
                adr += 1
                item.rendered = ".BITPOS\t" + ", ".join(tbl)
                item.compact = True
            data.Const(self.cx.m, adr, adr + 1)

class DiprocMem32(DiprocDisass):

    def distinct(self):
        for adr, lbl in (
            (0x190, "BAD_INS"),
            (0x117b, "PERMUTE_BITS"),
            (0x1136, "R6 = PICK_BITS()"),
        ):
            self.cx.m.set_label(adr, lbl)
        self.engine(0x56e)
        self.switch_labeled(0x3be, 0x3d2)
        self.switch_labeled(0x3e7, 0x3fb)
        self.switch_labeled(0x1023, 0x105a)
        for adr in (
            0x800,
            0x86d,
            0x8da,
            0x9b3,
            0xa8c,
            0xb65,
            0xbf6,
            0xc0f,
        ):
            self.cx.m.set_label(adr, "L_%04x" % adr)

def disassemble_file(input_file, *args, **kwargs):
    ''' Disassemble a single file '''

    octets = open(input_file, "rb").read()
    assert len(octets) == 8192
    csum = "%04x" % (sum(octets) & 0xffff)
    cls = {
        "c036": DiprocStd,
        "0184": DiprocMem32,
    }[csum]
    return cls(octets, *args, **kwargs).cx

def main():
    ''' Standard __main__ function '''

    if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
        print("PyReveng3/R1000.Disassembly", os.path.basename(__file__))
        disassemble_file(sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 1:
        assert "-AutoArchaeologist" not in sys.argv
        for i in sys.argv[1:]:
            disassemble_file(i)
    else:
        disassemble_file(FILENAME1, output_file="/tmp/_diproc1", pil=False)
        disassemble_file(FILENAME2, output_file="/tmp/_diproc2", pil=False)

if __name__ == '__main__':
    main()
