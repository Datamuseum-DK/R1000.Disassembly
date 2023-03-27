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
   Disassemble .M200 files
   -----------------------
'''

import os
import sys
import html
import importlib
import hashlib
import dotplot

from pyreveng import listing
import pyreveng.cpu.m68020 as m68020

import load_dfs_file

class DisassM200File():
    ''' Disassemble a single M200 file '''

    def __init__(self, input_file):
        self.input_file = input_file
        self.cx = m68020.m68020()
        self.cx.omsi = None

        try:
            self.ident, self.low, self.high = load_dfs_file.load_dfs_file(self.cx.m, input_file)
        except load_dfs_file.LoadError as err:
            print(".M200 LoadError", input_file, err)
            return

        self.identify()

        for turnus in range(5):
            i = "round_%d" % turnus
            for j in self.contrib:
                k = getattr(j, i, None)
                if k:
                    k(self.cx)

    def identify(self):

        self.tryout = ["all"]

        self.kind = {
            0x00000000: "kernel",
            0x00010000: "fs",
            0x00020000: "program",
            0x00054000: "bootblock",
            0x00070000: "resha",
            0x80000000: "ioc",
            0xe0004000: "enp100",
        }.get(self.low)
        print("IDENT", self.input_file, "0x%x" % self.low, self.kind, self.ident)

        self.tryout.append("kind." + self.kind)

        self.tryout.append("ident." + self.ident)

        if self.kind == "ioc":
            # IOC consists of four quite individual parts
            for a in range(4):
                self.tryout.append("kind.ioc_part_%d" % a)
                b = 0x80000000 + 0x2000 * a
                # One of the last 8 bytes varies between otherwise identical
                # sources of the IOC EEPROM
                i = hashlib.sha256(cx.m.bytearray(b, 0x1ff8)).hexdigest()[:16]
                self.tryout.append("ident." + i)

        self.contrib = []
        self.cx.m.set_block_comment(self.low, "R1000.Disassembly modules:")
        for i in self.tryout:
            try:
                self.contrib.append(importlib.import_module(i))
            except ModuleNotFoundError as err:
                self.cx.m.set_block_comment(self.low, "  no " + i)
                if 1 or not "No module named" in str(err):
                    print("  no", i)
                    print(err)
                continue
            # print("  import", i)
            self.cx.m.set_block_comment(self.low, "  import " + i)

    def listing(self, file, **kwargs):
        listing.Listing(
            self.cx.m,
            fo=file,
            align_blank=True,
            align_xxx=True,
            ncol=8,
            lo=self.low,
            hi=self.high,
            **kwargs
        )

    def autoarchaelogist_listing(self, filename):
        pfx = filename.rsplit(".", 2)[0]
        print("PFX", pfx)
        ut8file = pfx + ".utf8"
        with open(ut8file, "w") as file:
            self.listing(file)

        with open(filename, "w") as file:
            if self.cx.omsi:
                self.cx.omsi.aarender(file, pfx)

            file.write("<H4>Raw from R1000.Disassembly/DFS</H4>\n")
            file.write("<pre>\n")
            for i in open(ut8file, "r"):
                file.write(html.escape(i))
            file.write("</pre>\n")
            os.remove(ut8file)

def main():
    ''' Standard __main__ function '''

    if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
        print("PyReveng3/R1000.Disassembly", os.path.basename(__file__), sys.argv[3], sys.argv[4])
        djob = DisassM200File(sys.argv[3])
        djob.autoarchaelogist_listing(sys.argv[4])
       
    elif len(sys.argv) > 1:
        assert "-AutoArchaeologist" not in sys.argv
        for i in sys.argv[1:]:
            j = i.split("/")[-1]
            djob = DisassM200File(i)
            djob.listing(open("/tmp/_" + j, "w"))
            djob.autoarchaelogist_listing("/tmp/_AA_")
    else:
        print("Specify input files")

if __name__ == '__main__':
    main()
