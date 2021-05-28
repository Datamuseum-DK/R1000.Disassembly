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

from pyreveng import mem, code, data, listing
import pyreveng.cpu.mcs51 as mcs51

MYDIR = os.path.split(__file__)[0]
FILENAME = os.path.join(MYDIR, "P8052AH_9028.bin")

def disassemble_file(input_file, output_file="/tmp/_", verbose=True, **kwargs):
    ''' Disassemble a single file '''

    m = mem.Stackup((input_file,))

    cx = mcs51.I8032()
    cx.m.map(m, 0)

    cx.vectors(
        (
            "RESET",
            "IE1",
            "TF1",
            "RI_TI",
        )
    )

    for a, b, c in (
         (0x03a2, 0x03b2, 0x03a1),
         (0x03cd, 0x03db, 0x03ca),
         (0x0526, 0x0626, 0x0525),
         (0x1025, 0x1115, 0x1021),
    ):
        d = cx.disass(c)
        d.flow_out = []
        for n, i in enumerate(range(a, b, 2)):
            d += code.Jump(cond="A=0x%02x" % (i - a), to=i)
            y = cx.disass(i)
            cx.m.set_label(y.dstadr, "SUB_%04x_%02x" % (a, n))

    for a, b,c  in (
        (0x0746, 0x6d, 8),
        (0x07b3, 0x0d, 8),
        (0x07c0, 0x49, 8),
        (0x0809, 0x09, 8),
        (0x0812, 0x49, 8),
        (0x085b, 0x09, 8),
        (0x0864, 0x49, 8),
        (0x08ad, 0x49, 8),
        (0x08f6, 0xb5, 8),
        (0x09ab, 0xb5, 8),
        (0x0a60, 0x15, 8),
        (0x0a75, 0xb5, 8),
        (0x0b2a, 0xb5, 8),
        (0x0bdf, 0x15, 8),
        (0x0bf4, 0x91, 8),
        (0x0c85, 0x0d, 8),
        (0x0c92, 0x25, 8),
        (0x0cb7, 0x05, 8),
        (0x0cbc, 0x49, 8),
        (0x0d05, 0x49, 8),
        (0x0d4e, 0x49, 8),
        (0x0d97, 0x09, 8),
        (0x0da0, 0x91, 8),
        (0x0e31, 0x49, 8),
        (0x0e7a, 0x09, 8),
        (0x0e83, 0x49, 8),
        (0x0ecc, 0x09, 8),
        (0x0ed5, 0x91, 8),
    ):
        if b:
            cx.m.set_label(a, "TABLE_%04x[0x%02x]" % (a, b))
            e = a + b
            for i in range(a, a + b, c):
                j = min(i + c, e)
                data.Const(cx.m, a, j, fmt="0x%02x")
                a = j
        else:
            cx.m.set_label(a, "TABLE_%04x" % a)

    code.lcmt_flows(cx.m)

    listing.Listing(
        cx.m,
        fn=output_file,
        align_blank=True,
        align_xxx=True,
        ncol=8,
        **kwargs
    )

    return cx

def main():
    ''' Standard __main__ function '''

    if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
        print("PyReveng3/R1000.Disassembly", os.path.basename(__file__))
        disassemble_file(sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 1:
        assert "-AutoArchaeologist" not in sys.argv
        for i in sys.argv[1:]:
            cx = disassemble_file(i)
    else:
        cx = disassemble_file(FILENAME, pil=True)

if __name__ == '__main__':
    main()
