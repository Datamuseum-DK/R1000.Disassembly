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
   Top-level class for working with r1k microcode
   ==============================================
'''

import r1k_ucode_m200_file as m200_file
import r1k_ucode_explain
import r1k_ucode_decoded as decoded

class Uins(decoded.Ucode):
    ''' subclass '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.macro_ins = []

    explainer = r1k_ucode_explain.Explain()

    def explain(self):
        ''' Explain this micro instruction on stdout '''
        print("%04x" % self.adr)
        for j in sorted(self.macro_ins):
            print("  macro_ins: %04x" % j)
        for txt in self.explainer.decode_text(self):
            print("   ", txt)

class Ucode():
    ''' Decoded, ready to play with microcode '''

    def __init__(self, iterable=None):

        self.uins = [Uins(i) for i in range(1<<14)]

        ucode = m200_file.R1kM200UcodeFile(iterable)

        for mult, ucodes in (
            (1, ucode.dispatch_ram_low()),
            (64, ucode.dispatch_ram_high()),
        ):
            for n, i in enumerate(ucodes):
                j = Uins(0)
                j.load_dispatch_uword(i)
                self.uins[j.dispatch_uadr].load_dispatch_uword(i)
                self.uins[j.dispatch_uadr].macro_ins.append(n * mult)

        for uins, fiu, ioc, seq, typ, val in zip(
            self.uins[0x100:],
            ucode.fiu_ucode(),
            ucode.ioc_ucode(),
            ucode.seq_ucode(),
            ucode.typ_ucode(),
            ucode.val_ucode(),
        ):
            uins.load_fiu_uword(fiu)
            uins.load_ioc_uword(ioc)
            uins.load_seq_uword(seq)
            uins.load_typ_uword(typ)
            uins.load_val_uword(val)

    def __getitem__(self, idx):
        return self.uins.__getitem__(idx)

    def __iter__(self):
        yield from self.uins[0x100:]

def main():
    ''' ... '''
    i = Ucode()
    for j in i:
        j.explain()

if __name__ == "__main__":
    main()
