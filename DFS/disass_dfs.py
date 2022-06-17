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
   IOC FS_?.M200 - DFS filesystem
   ------------------------------
'''

import os
import sys
import importlib
import hashlib
import dotplot

from pyreveng import listing
import pyreveng.cpu.m68020 as m68020

import load_dfs_file

MYDIR = os.path.split(__file__)[0]

FILENAME = os.path.join(MYDIR, "FS_0.M200")

def disassemble_file(input_file, output_file="/tmp/_", verbose=True, **kwargs):
    ''' Disassemble a single file '''
    cx = m68020.m68020()
    try:
        ident = load_dfs_file.load_dfs_file(cx.m, input_file)
    except load_dfs_file.LoadError as err:
        if verbose:
            print(input_file, err)
        return

    high = 0
    low = 1<<32
    for i, j  in cx.m.gaps():
        high = max(high, j)
        low = min(low, i)

    tryout = []
    tryout.append("all")

    kind = {
        0x00000000: "kernel",
        0x00010000: "fs",
        0x00020000: "program",
        0x00054000: "bootblock",
        0x00070000: "resha",
        0x80000000: "ioc",
        0xe0004000: "enp100",
    }.get(low)
    print(input_file, "0x%x" % low, kind, ident)

    tryout.append("kind." + kind)

    tryout.append("ident." + ident)

    if kind == "ioc":
        # IOC consists of four quite individual parts
        for a in range(4):
            tryout.append("kind.ioc_part_%d" % a)
            b = 0x80000000 + 0x2000 * a
            i = hashlib.sha256(cx.m.bytearray(b, 0x2000)).hexdigest()[:16]
            tryout.append("ident." + i)

    contrib = []
    cx.m.set_block_comment(low, "R1000.Disassembly modules:")
    for i in tryout:
        try:
            contrib.append(importlib.import_module(i))
        except ModuleNotFoundError:
            cx.m.set_block_comment(low, "  no " + i)
            print("  no", i)
            continue
        print("  import", i)
        cx.m.set_block_comment(low, "  import " + i)

    for turnus in range(4):
        i = "round_%d" % turnus
        for j in contrib:
            k = getattr(j, i, None)
            if k:
                k(cx)

    listing.Listing(
        cx.m,
        fn=output_file,
        align_blank=True,
        align_xxx=True,
        ncol=8,
        lo=low,
        hi=high,
        **kwargs
    )
    if False:
        from pyreveng import partition
        partition.Partition(cx.m)
    return cx

def main():
    ''' Standard __main__ function '''

    if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
        print("PyReveng3/R1000.Disassembly", os.path.basename(__file__))
        disassemble_file(sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 1:
        assert "-AutoArchaeologist" not in sys.argv
        for i in sys.argv[1:]:
            j = i.split("/")[-1]
            cx = disassemble_file(i, "/tmp/_" + j)
            dotplot.dot_plot(cx)
    else:
        cx = disassemble_file(FILENAME, pil=True)
        dotplot.dot_plot(cx)

if __name__ == '__main__':
    main()
