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
   R1000 microcode disassembler
   ----------------------------

   We want to use some of the high-level facilities in PyReveng3, but rather
   than actually give pyreveng3 the full 272 bit wide microcode words, we
   just pretend the "instructions" are identical to the address, and then
   the disassembler grabs into a stashed copy of `r1k_ucode` and uses
   `r1k_ucode_explain` to "disassemble" the instructions.

'''

import os
import importlib

from pyreveng import mem, assy, data, listing

import r1k_ucode_explain
import macro_disass

import r1k_ucode

R1K_UCODE = '''
A       a       | uadr			    |
'''

class R1kUcodeIns(assy.Instree_ins):
    ''' Ucode Instructions '''

    def assy_a(self):
        self.mne = ""
        uins = self.lang.ucode[self.lo]
        uins.dstadr = None
        retval = list(uins.explainer.decode_text(uins))
        if uins.dstadr is not None:
            self.dstadr = uins.dstadr
            retval += list("==> " + str(x) for x in self.lang.m.get_labels(self.dstadr))
 
        return "\n\t" + "\n\t".join(retval)

class R1kUcode(assy.Instree_disass):
    ''' Ucode "CPU" '''
    def __init__(self, lang="R1KUCODE"):
        super().__init__(
            lang,
            ins_word=14,
            mem_word=14,
            abits=14,
        )
        self.add_ins(R1K_UCODE, R1kUcodeIns)

def r1k_microcode(fn=None):
    ''' Disassemble an ucode file '''
    cx = R1kUcode()
    cx.ucode = r1k_ucode.Ucode(source=fn)
    for u in reversed(cx.ucode):
        if not u.explainer.isdefault(u):
            break
    m = mem.WordMem(0x100, u.adr + 2, bits=14)
    cx.m = m

    detail_module = "details_" + cx.ucode.hash[:6]
    try:
        details = importlib.import_module(detail_module)
        details.Details(cx)
    except ModuleNotFoundError as err:
        cx.m.set_block_comment(cx.m.lo, "  no " + detail_module)

    print("CX", cx, "CX.M", cx.m)

    for n, uins in enumerate(cx.ucode):
        adr = n + 0x100
        if adr >= m.hi:
            break
        m[adr] = adr
        j = set()
        for i in uins.macro_ins:
            x = macro_disass.disassemble(i)
            if "QQ" in x:
                continue
            if x not in j:
                cx.m.set_block_comment(adr, "0x%04x " % i + x)
                j.add(x)
            cx.m.set_label(adr, "MACRO_%04x" % i)

    cx.disass(0x100)
    explain = r1k_ucode_explain.Explain()
    cx.m.set_block_comment(0x100, "Defaults not shown:")
    cx.m.set_block_comment(0x100, "===================")
    for i in explain.defaults_text():
        cx.m.set_block_comment(0x100, " " * 4 + i)

    cx.m.set_block_comment(0x100, " ")

    for i, j in (
        ("Early macro", explain.early_macro_events),
        ("Late macro", explain.late_macro_events),
        ("Micro", explain.micro_events),
    ):
        for x, y in j.items():
            cx.m.set_block_comment(x, i + " event: " + y)
            cx.m.set_label(x, y)

    return cx

#######################################################################

if __name__ == '__main__':
    import sys

    import glob

    #if len(sys.argv) == 5 and sys.argv[1] == "-AutoArchaeologist":
    #    cx = r1k_experiment(sys.argv[3], sys.argv[2])
    #    listing.Listing(cx.m, fn=sys.argv[4], ncol=1)
    #    exit(0)

    cx = r1k_microcode(sys.argv[1])
    listing.Listing(cx.m, fn="/tmp/_ucode", ncol=1, charset=False)
