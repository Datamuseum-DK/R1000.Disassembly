#!/usr/bin/env python
#
# Copyright (c) 2021-2021 Poul-Henning Kamp <phk@phk.freebsd.dk>
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

'''
   R1000 DIAG Experiment disassembler
   ----------------------------------
'''

import os

from pyreveng import mem, assy, data, listing

from exp_disass import R1kExp

FILENAME = os.path.join(os.path.split(__file__)[0], "READ_NOVRAM.M32")

class ExpMem(mem.ByteMem):
    '''
       Subclass with "volatile" attributes
       We use two attribute bits to mark
       locations which are part of paramters
       and locations modified at run-time.
    '''

    def dfmt(self, adr):
        ''' Mark bytes with attribute-bits set '''
        try:
            d = self[adr]
        except:
            return self.undef
        return "%02x" % d + [' ', "'", '"', '+'][self.get_attr(adr)]

def r1k_experiment(fn, ident=None):
    ''' Disassemble an experiment file '''
    cx = R1kExp()
    cx.ident = ident
    m = ExpMem(0, 0xff, attr=2)
    cx.m.map(m, 0)
    adr = 0x10
    params = []
    b = open(fn, "rb").read().rstrip(b'\x00')
    for i in b.split(b'\x0a'):
        i = i.decode("ASCII")
        i = i.rstrip()
        if not i:
            continue
        if i[0] == "P":
            params.append(i)
        else:
            j = i.split()
            m[adr] = int(j[0], 16)
            adr += 1
    cx.hi_adr = adr

    cx.subrs = set()
    cx.code_base = cx.m[0x10]
    y = cx.codeptr(0x10)
    cx.m.set_label(y.dst, "EXPERIMENT")

    cx.m.set_label(0x10, "PC_")
    for i in range(1, 8):
        cx.m.set_label(0x10 + i, "R%d_" % i)

    for i in params:
        a = int(i[1:3], 16)
        b = int(i[5:6], 16)
        if a+b <= cx.code_base:
            cx.m.set_line_comment(a, i)
            for j in range(a, a + b):
                cx.m.set_attr(j, 2)
            if b:
                y = data.Const(cx.m, a, a + b)
                y.typ = ".PARAM"
        else:
            for j in range(a, a + b):
                cx.m.set_attr(j, 2)
            j = list(cx.m.find(lo=a, hi=a+b))
            print(j, "A 0x%x" % a)
            if len(j) > 0:
                cx.m.set_line_comment(j[0].lo, i)
            else:
                cx.m.set_line_comment(a, i)

    for i in cx.subrs:
        cx.m.set_block_comment(i, "Subroutine")

    for i, j in cx.m.gaps():
        if i < 0x10:
            continue
        if j > cx.code_base:
            continue
        while i < j:
            y = data.Const(cx.m, i)
            y.typ = ".DATA"
            i += 1

    # code.lcmt_flows(cx.m)
    return cx

#######################################################################

if __name__ == '__main__':
    import sys

    import glob

    if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
        cx = r1k_experiment(sys.argv[3], sys.argv[2])
        listing.Listing(
	    cx.m,
	    fn=sys.argv[4],
	    ncol=6,
	    lo=0x10,
	    hi=cx.hi_adr,
	    charset=False,
        )
        exit(0)

    for ext in (
        ".M32",
        ".FIU",
        ".SEQ",
        ".VAL",
        ".TYP",
        ".IOC",
        # ".MEM"
    ):
        for fn in sorted(glob.glob("/critter/DDHF/R1000/hack/X/*NOVRAM*" + ext)):
            bfn = os.path.basename(fn)
            print(bfn)
            try:
                cx = r1k_experiment(fn, bfn)
                listing.Listing(
                    cx.m,
                    fn="/tmp/_." + bfn + ".EXP",
                    ncol=4,
                    lo=0x10,
                    hi=cx.hi_adr,
                    charset=False,
                )
            except mem.MemError as err:
                print("FAIL", fn, err)
