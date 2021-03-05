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
   Function call dot(1) plot
   -------------------------
'''

from pyreveng import assy

def dot_plot(cx, filename="/tmp/_.dot"):
    fo = open(filename, "w")
    fo.write("digraph {\n")
    fo.write('rankdir="LR"\n')
    inside = False
    aregs = {}
    already = set()
    labeled = dict()

    def label(adr):
        if adr in labeled:
            return labeled[adr]
        labeled[adr] = None
        sc = cx.dfs_syscalls.get(adr)
        if sc:
            fo.write('X_%08x [label="%s"]\n' % (adr, sc.name))
            labeled[adr] = sc.name
            return sc.name

        j = list(cx.m.get_labels(adr))
        if j:
            fo.write('X_%08x [label="%s"]\n' % (adr, j[0]))
            labeled[adr] = j[0]
            return j[0]

    def arrow(fm,to):
        if (fm,to) not in already:
            lbl = label(to)
            j = "X_%08x" % to
            for i in (
                "StringCat",
                "Malloc",
                "Free",
                "Panic",
                "AppendChar",
                "Console",
                "LeftPad",
                "NewString",
                "StringDup",
                "StringEqual",
                "Word2String",
                "FsErrMsgStr",
                "PopProgram",
                "Open",
                "Disk_IO",
                "KC1c_ProtCopy",
                "free",
                "muls",
                "divs",
                "fill_str",
            ):
                if lbl and i in lbl:
                    j = "X_%08x_" % fm + i
                    fo.write(j + '[shape=plaintext, label="%s()"]\n' % i)
                    break
            fo.write("X_%08x" % fm + " -> " + j + '\n')
            already.add((fm,to))

    for i in cx.m: 
        if not isinstance(i, assy.Assy):
            continue
        if i.mne == "LINK.W":
            label(i.lo)
            inside = i
            aregs = {}
        elif i.mne == "RTS":
            inside = None
        elif inside and i.mne == "LEA.L":
            j = cx.m.bu16(i.lo)
            if j & 0xf1ff == 0x41f9:
                aregs[(j >> 9) & 7] = cx.m.bu32(i.lo + 2)
            elif j & 0xf1ff == 0x41fa:
                aregs[(j >> 9) & 7] = cx.m.bs16(i.lo + 2) + i.lo + 2
        elif inside and i.mne in ("JSR", "BSR"):
            if i.dstadr:
                arrow(inside.lo, i.dstadr)
            else:
                j = cx.m.bu16(i.lo)
                k = j & 7
                if j & ~7 == 0x4e90 and k in aregs:
                    arrow(inside.lo, aregs[k])
                else:
                    print("K", i, i.render())
                    fo.write('X_%08x_Q [label="?"]\n' % i.lo)
                    ('X_%08x -> X_%08x_Q\n' % (inside.lo, i.lo))
    fo.write("}\n")
