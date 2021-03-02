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

from pyreveng import listing
import pyreveng.cpu.m68020 as m68020

import load_dfs_file

MYDIR = os.path.split(__file__)[0]

FILENAME = os.path.join(MYDIR, "FS_0.M200")

def disassemble_file(input_file, output_file="/tmp/_", verbose=True):
    ''' Disassemble a single file '''
    cx = m68020.m68020()
    try:
        ident = load_dfs_file.load_dfs_file(cx.m, input_file)
    except load_dfs_file.LoadError as err:
        if verbose:
            print(input_file, err)
        return
    first_adr = None
    for first_adr,_j  in cx.m.gaps():
        break
    kind = {
        0x00000000: "kernel",
        0x00010000: "fs",
        0x00020000: "program",
        0x00054000: "bootblock",
        0x00070000: "resha",
        0x80000000: "ioc",
        0xe0004000: "enp100",
    }.get(first_adr)
    print(input_file, "0x%x" % first_adr, kind, ident)

    contrib = []
    for i in (
        "all",
        "kind." + kind,
        "ident." + ident,
    ):
        if not os.path.isfile(i.replace(".", "/") + ".py"):
            continue
        contrib.append(importlib.import_module(i))
        print("  import", i)

    for turnus in range(4):
        i = "round_%d" % turnus
        for j in contrib:
            k = getattr(j, i, None)
            if k:
                k(cx)

    listing.Listing(cx.m, fn=output_file)

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
        disassemble_file(FILENAME)

if __name__ == '__main__':
    main()
