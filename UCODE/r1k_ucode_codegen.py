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
   Codegenerator for r1k_ucode_decoded.py
   ======================================

   The mapping from the microword bytes sent down on the diagbus
   to the individual fields in the microcode word involves a 90°
   turn because the i8052 diag-processor uses serial access to
   the microword registers.

   To keep this manageable, we record the layout of the serial-in/
   parallel-out registers in `r1k_ucode_diag_chains.py` from which
   this creates `r1k_ucode_decoded.py`.

   When we get there, this program will also write a similar set
   of functions as C-source for the emulator.
'''

import r1k_ucode_diag_chains as diag_chains

DOCCMT = "''' Machine Generated file, see r1k_ucode_codegen.p '''"

class Chain():
    ''' One serial-parallel register chain '''

    def __init__(self, chaindef):
        self.chaindef = chaindef
        self.nbytes = len(chaindef[0])

    def __iter__(self):
        for i in range(0, self.nbytes):
            idx = self.nbytes - (1 + i)
            for n, j in enumerate(self.chaindef):
                yield i, 7-n, j[idx]

    def xor(self):
        ''' The bits in the register which are inverted '''
        retval = bytearray([0]) * self.nbytes
        for idx, bit, field in self:
            if field[3]:
                retval[idx] |= 1 << bit
        return retval

def main():
    ''' ... '''

    chains = {
        "dispatch": Chain(diag_chains.SEQ_DECODER_SCAN),
        "seq": Chain(diag_chains.SEQ_UIR_SCAN_CHAIN),
        "fiu": Chain(diag_chains.FIU_MICRO_INSTRUCTION_REGISTER),
        "typ": Chain(diag_chains.TYP_WRITE_DATA_REGISTER),
        "val": Chain(diag_chains.VAL_WRITE_DATA_REGISTER),
        "ioc": Chain(diag_chains.IOC_DIAG_CHAIN),
    }

    fo = open("r1k_ucode_decoded.py", "w")
    fo.write('#!/usr/bin/env python3\n')
    fo.write('\n')
    fo.write(DOCCMT + "\n")
    fo.write('\n')

    fields = {}

    for name, chain in chains.items():
        for idx, bit, field in chain:
            if field[1][0] == 'x':
                continue
            fname = name + "_" + field[1]
            t = fields.get(fname, 1)
            t = max(t, field[2])
            fields[fname] = t

    fo.write('class Ucode():')
    fo.write('\n')
    fo.write('    ' + DOCCMT + "\n")
    fo.write('\n')
    fo.write('    def __init__(self, adr):\n')
    fo.write('        self.adr = adr\n')
    for name in chains:
        fo.write('        self.%s_uword = None\n' % name)
    fo.write('        self.dispatch_macro_ins = []\n')
    for i in sorted(fields):
        fo.write('        self.%s = None\n' % i)

    fo.write("\n")
    fo.write("    fields = {\n")
    for i, j in sorted(fields.items()):
        fo.write('        "%s": %d,\n' % (i, j))
    fo.write("    }\n")

    fo.write("\n")
    fo.write("    def __iter__(self):\n")
    fo.write("        for i in self.fields:\n")
    fo.write("            yield i, getattr(self, i)\n")

    for name, chain in chains.items():
        fo.write("\n")
        fo.write("    def load_%s_uword(self, uword):\n" % name)
        fo.write('        ' + DOCCMT + "\n")
        fo.write('\n')
        xor = chain.xor()
        idxo = -1
        fo.write("        self.%s_uword = bytes(uword)\n" % name)
        xmask = 0
        seen_fld = set()
        for idx, bit, field in chain:
            fname = name + "_" + field[1]
            if idxo != idx:
                if xmask:
                    fo.write(" " * 8 + "assert not a & 0x%02x\n" % xmask)
                    xmask = 0
                fo.write("\n")
                if xor[idx]:
                    fo.write("        a = uword[%d] ^ 0x%02x\n" % (idx, xor[idx]))
                else:
                    fo.write("        a = uword[%d]\n" % idx)
                idxo = idx
            if field[1][0] == 'x':
                xmask |= 1 << bit
                continue
            t = "self.%s " % fname
            if fname in seen_fld:
                t += "|="
            else:
                t += "="
                seen_fld.add(fname)
            t += " (a & 0x%02x)" % (1 << bit)
            t = " " * 8 + t
            if bit == field[2]:
                fo.write(t + "\n")
            elif bit < field[2]:
                fo.write("%s << %d\n" % (t, field[2] - bit))
            else:
                fo.write("%s >> %d\n" % (t, bit - field[2]))
        if xmask:
            fo.write(" " * 8 + "assert not a & 0x%02x\n" % xmask)

if __name__ == "__main__":
    main()
