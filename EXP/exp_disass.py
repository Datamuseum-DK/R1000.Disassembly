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

from pyreveng import assy

R1K_EXP = '''
x00		imm			|0 0 0 0 0 0 0 0| imm		|
x02		-			|0 0 0 0 0 0 1 0|
x03		-			|0 0 0 0 0 0 1 1|
x04		-			|0 0 0 0 0 1 0 0|
x05		-			|0 0 0 0 0 1 0 1|
x06		-			|0 0 0 0 0 1 1 0|
x07		-			|0 0 0 0 0 1 1 1|
x08		-			|0 0 0 0 1 0 0 0|
x09		-			|0 0 0 0 1 0 0 1|
x0A		-			|0 0 0 0 1 0 1 0|
x0B		-			|0 0 0 0 1 0 1 1|
x0C		-			|0 0 0 0 1 1 0 0|
x0D		-			|0 0 0 0 1 1 0 1|
x0E		-			|0 0 0 0 1 1 1 0|
x0F		-			|0 0 0 0 1 1 1 1|
x10		-			|0 0 0 1 0 0 0 0|
x11		-			|0 0 0 1 0 0 0 1|
x13		-			|0 0 0 1 0 0 1 1|
y14		-			|0 0 0 1 0 1 0 0|
y15		-			|0 0 0 1 0 1 0 1|
y16		-			|0 0 0 1 0 1 1 0|
CALL		subr,>C			|0 0 0 1 1 0| x |
x1C		-			|0 0 0 1 1 1 0 0|
x1D		-			|0 0 0 1 1 1 0 1|
x1F		-			|0 0 0 1 1 1 1 1|
x20		-			|0 0 1 0 0 0 0 0|
x21		-			|0 0 1 0 0 0 0 1|
x22		-			|0 0 1 0 0 0 1 0|
x24		-			|0 0 1 0 0 1 0 0|
x25		-			|0 0 1 0 0 1 0 1|
x26		-			|0 0 1 0 0 1 1 0|
x27		-			|0 0 1 0 0 1 1 1|
x28		imm			|0 0 1 0 1 0 0 0| imm		|
x29		dst,>JC			|0 0 1 0 1 0 0 1| dst		|
x2A		-			|0 0 1 0 1 0 1 0|
x2B		-			|0 0 1 0 1 0 1 1|
RETURN		>R 			|0 0 1 0 1 1 0 0|
x2D		-			|0 0 1 0 1 1 0 1|
x2F		var			|0 0 1 0 1 1 1 1| var		|
x30		var			|0 0 1 1 0 0 0 0| var		|
x31		imm			|0 0 1 1 0 0 0 1| imm		|
x32		imm			|0 0 1 1 0 0 1 0| imm		|
x33		-			|0 0 1 1 0 0 1 1|
x34		-			|0 0 1 1 0 1 0 0|
x36		dst,>JC			|0 0 1 1 0 1 1 0| dst 		|
x38		dst,>JC			|0 0 1 1 1 0 0 0| dst 		|
x39		-			|0 0 1 1 1 0 0 1|
x3A		dst,>JC			|0 0 1 1 1 0 1 0| dst 		|
x3B		-			|0 0 1 1 1 0 1 1|
x3C		dst,>JC			|0 0 1 1 1 1 0 0| dst		|
x3E		dst,>JC			|0 0 1 1 1 1 1 0| dst 		|
x3F		imm			|0 0 1 1 1 1 1 1| imm		|
x40		var,var2,dst,>JC	|0 1 0 0 0 0 0 0| var		| var2		| dst		|
x41		imm,var,dst,>JC		|0 1 0 0 0 0 0 1| imm		| var		| dst		|
x42		imm,var,dst,>JC		|0 1 0 0 0 0 1 0| imm		| var		| dst		|
x43		imm,var,dst,>JC		|0 1 0 0 0 0 1 1| imm		| var		| dst		|
x44		var,dst,>JC		|0 1 0 0 0 1 0 0| var		| dst		|
x45		dst,>JC			|0 1 0 0 0 1 0 1| dst		|
y46		var,dst,>JC		|0 1 0 0 0 1 1 0| var		| dst		|
y47		dst,>JC			|0 1 0 0 0 1 1 1| dst		|
x48		imm,dst,>JC		|0 1 0 0 1 0 0 0| imm		| dst		|
x49		-			|0 1 0 0 1 0 0 1|
x4A		var,dst,>JC		|0 1 0 0 1 0 1 0| var		| dst		|
x4B		-			|0 1 0 0 1 0 1 1|
x4C		var,var2,dst,>JC	|0 1 0 0 1 1 0 0| var		| var2		| dst		|
x4D		imm,var,dst,>JC		|0 1 0 0 1 1 0 1| imm		| var		| dst		|
x4EL		var,var2,dst,>JC	|0 1 0 0 1 1 1 0|0|var		| var2		| dst		|
x4F		imm,var,dst,>JC		|0 1 0 0 1 1 1 1| imm		| var		| dst		|
x50		var,var2		|0 1 0 1 0 0 0 0| var		| var2		|
x51		imm,imm2,var,dst,>JC	|0 1 0 1 0 0 0 1| imm		| imm2		| var		| dst		|
x52		var,var2,dst,>JC	|0 1 0 1 0 0 1 0|0|var		| var2		| dst		|
x53		imm,imm2,var,dst,>JC	|0 1 0 1 0 0 1 1| imm		| imm2		| var		| dst		|
LOOP4		var,dst,>JC		|0 1 0 1 0 1 0 0| var		| dst		|
LOOP6		var,dst,>JC		|0 1 0 1 0 1 1 0| var		| dst		|
x57		-			|0 1 0 1 0 1 1 1|
LOOP8		var,dst,>JC		|0 1 0 1 1 0 0 0| var		| dst		|
x59		-			|0 1 0 1 1 0 0 1|
LOOPA		var,dst,>JC		|0 1 0 1 1 0 1 0| var		| dst		|
x5B		-			|0 1 0 1 1 0 1 1|
END		>R 			|0 1 0 1 1 1 0 0|
x5D		-			|0 1 0 1 1 1 0 1|
LOOPE		imm,dst,>JC		|0 1 0 1 1 1 1 0| imm		| dst		|
x5F		-			|0 1 0 1 1 1 1 1|
x60		-			|0 1 1 0 0 0 0 0|
x61		imm			|0 1 1 0 0 0 0 1| imm		|
x62		imm			|0 1 1 0 0 0 1 0| imm		|
y63		-			|0 1 1 0 0 0 1 1|
y64		-			|0 1 1 0 0 1 0 0|
x66		-			|0 1 1 0 0 1 1 0|
x67		-			|0 1 1 0 0 1 1 1|
x68		-			|0 1 1 0 1 0 0 0|
x6A		-			|0 1 1 0 1 0 1 0|
x6B		-			|0 1 1 0 1 0 1 1|
x6C		-			|0 1 1 0 1 1 0 0|
x6E		-			|0 1 1 0 1 1 1 0|
x70		var			|0 1 1 1 0 0 0 0| var		|
x72		var			|0 1 1 1 0 0 1 0| var		|
x73		-			|0 1 1 1 0 0 1 1|
x74		-			|0 1 1 1 0 1 0 0|
x76		-			|0 1 1 1 0 1 1 0|
x77		-			|0 1 1 1 0 1 1 1|
x78		-			|0 1 1 1 1 0 0 0|
x79		-			|0 1 1 1 1 0 0 1|
x7A		-			|0 1 1 1 1 0 1 0|
x7C		imm			|0 1 1 1 1 1 0 0| imm		|
x7E		imm			|0 1 1 1 1 1 1 0| imm		|
x80		var			|1 0 0 0 0 0 0 0| var		|
x82		var			|1 0 0 0 0 0 1 0| var		|
x83		-			|1 0 0 0 0 0 1 1|
x84		var			|1 0 0 0 0 1 0 0| var		|
x85		-			|1 0 0 0 0 1 0 1|
x86		imm			|1 0 0 0 0 1 1 0| imm		|
x88		imm			|1 0 0 0 1 0 0 0| imm		|
x8A		var			|1 0 0 0 1 0 1 0| var		|
x8C		var			|1 0 0 0 1 1 0 0| var		|
COPY		var,var2		|1 0 0 0 1 1 1 0| var		| var2		|
STORE		imm,var			|1 0 0 0 1 1 1 1| imm		| var		|
x90		var,var2		|1 0 0 1 0 0 0 0| var		| var2		|
x91		imm,imm2,var		|1 0 0 1 0 0 0 1| imm		| imm2		| var		|
x92		var,var2		|1 0 0 1 0 0 1 0| var		| var2		|
y93_add		imm,var			|1 0 0 1 0 0 1 1| imm		| var		|
x95		imm,imm2,var		|1 0 0 1 0 1 0 1| imm		| imm2		| var		|
x96		var,var2		|1 0 0 1 0 1 1 0| var		| var2		|
AND		imm,var			|1 0 0 1 0 1 1 1| imm		| var		|
x98		var			|1 0 0 1 1 0 0 0| var		|
x99		imm,imm2,var		|1 0 0 1 1 0 0 1| imm		| imm2		| var		|
y9A_or		var,var2		|1 0 0 1 1 0 1 0| var		| var2		|
x9B		imm,var2		|1 0 0 1 1 0 1 1| imm		| var2		|
x9D		imm,imm2,var		|1 0 0 1 1 1 0 1| imm		| imm2		| var		|
y9E		var,var2		|1 0 0 1 1 1 1 0| var		| var2		|
y9F		imm,var			|1 0 0 1 1 1 1 1| imm		| var		|
xA0		var,var2		|1 0 1 0 0 0 0 0| var		| var2		|
xA1		imm,imm2,var		|1 0 1 0 0 0 0 1| imm		| imm2		| var		|
xA2		-			|1 0 1 0 0 0 1 0|
xA4		imm,imm2,var		|1 0 1 0 0 1 0 0| imm		| imm2		| var		|
xA5L		var,dst,>JC		|1 0 1 0 0 1 0 1|0|var		| dst		|
yA6		imm,var			|1 0 1 0 0 1 1 0| imm		| var		|
xA7		imm			|1 0 1 0 0 1 1 1| imm		|
xA9		imm			|1 0 1 0 1 0 0 1| imm		|
xA8		imm,var			|1 0 1 0 1 0 0 0| imm		| var		|
xAA		imm,var			|1 0 1 0 1 0 1 0| imm		| var		|
xAB		imm,var			|1 0 1 0 1 0 1 1| imm		| var		|
xAC		imm,var			|1 0 1 0 1 1 0 0| imm		| var		|
xAEL		imm,var,imm2		|1 0 1 0 1 1 1 0|0 0| imm	| var		|imm2		|
xAEH		imm,var			|1 0 1 0 1 1 1 0| imm		| var		|
xAFL		imm,dst,>JC		|1 0 1 0 1 1 1 1|0| imm		| dst		|
xAFH		imm			|1 0 1 0 1 1 1 1| imm		|
xB0		imm,var,var2,dst,>JC	|1 0 1 1 0 0 0 0| imm		| var		| var2		| dst		|
xB0M		imm,var,var2		|1 0 1 1 0 0 0 0|0 1| imm	| var		| var2		|
xB0H		imm,var,var2		|1 0 1 1 0 0 0 0|1| imm		| var		| var2		|
xB1L		var,dst,>JC		|1 0 1 1 0 0 0 1|0 0| var	| dst		|
xB1		imm			|1 0 1 1 0 0 0 1| imm		|
xB2		var,imm,imm2		|1 0 1 1 0 0 1 0| var		| imm		| imm2		|
xB4		var,var2		|1 0 1 1 0 1 0 0| var		| var2		|
xB6		imm,var,imm2		|1 0 1 1 0 1 1 0| imm		| var		| imm2		|
xB7		imm,var,var2		|1 0 1 1 0 1 1 1| imm		| var		| var2		|
xB8		var			|1 0 1 1 1 0 0 0| var		|
xBA		var,var2		|1 0 1 1 1 0 1 0| var		| var2		|
yBC		imm			|1 0 1 1 1 1 0 0| imm		|
xBE		var,imm			|1 0 1 1 1 1 1 0| var		| imm		|
xBF		imm			|1 0 1 1 1 1 1 1| imm		|
yC0		var,imm			|1 1 0 0 0 0 0 0| var		| imm		|
xC1		imm			|1 1 0 0 0 0 0 1| imm		|
xC2		var,imm			|1 1 0 0 0 0 1 0| var		| imm		|
xC3		imm			|1 1 0 0 0 0 1 1| imm		|
xC4		imm,imm2		|1 1 0 0 0 1 0 0| imm		| imm2		|
xC6		imm,imm2		|1 1 0 0 0 1 1 0| imm		| imm2		|
xC8		imm,imm2		|1 1 0 0 1 0 0 0| imm		| imm2		|
xC9		var,var2		|1 1 0 0 1 0 0 1| var		| var2		|
xCA		imm,imm2		|1 1 0 0 1 0 1 0| imm		| imm2		|
xCB		imm			|1 1 0 0 1 0 1 1| imm		|
xCC		imm,imm2		|1 1 0 0 1 1 0 0| imm		| imm2		|
xCD		imm			|1 1 0 0 1 1 0 1| imm		|
xCE		imm,var			|1 1 0 0 1 1 1 0| imm		| var		|
xCF		imm			|1 1 0 0 1 1 1 1| imm		|
xD0		var,imm			|1 1 0 1 0 0 0 0| var		| imm		|
xD2		imm,imm2		|1 1 0 1 0 0 1 0| imm		| imm2		|
xD4		imm,imm2,var		|1 1 0 1 0 1 0 0| imm		| imm2		| var		|
xD5		imm,var,var2		|1 1 0 1 0 1 0 1| imm		| var		| var2		|
xD6		-			|1 1 0 1 0 1 1 0|
yD8		-			|1 1 0 1 1 0 0 0|
yDC		var			|1 1 0 1 1 1 0 0| var		|
yDE		var			|1 1 0 1 1 1 1 0| var		|
xDA30		imm,imm2		|1 1 0 1 1 0 1 0|0 0 1 1 0 0 0 0| imm		| imm2		|
xDA33		imm			|1 1 0 1 1 0 1 0|0 0 1 1 0 0 1 1| imm		|
xDA93		imm			|1 1 0 1 1 0 1 0|1 0 0 1 0 0 1 1| imm		|
xDA5B		-			|1 1 0 1 1 0 1 0|0 1 0 1 1 0 1 1|
xDA40		imm,imm2		|1 1 0 1 1 0 1 0|0 1 0 0 0 0 0 0| imm		| imm2		|
xDA42		imm,imm2		|1 1 0 1 1 0 1 0|0 1 0 0 0 0 1 0| imm		| imm2		|
xDA52		var,imm			|1 1 0 1 1 0 1 0|0 1 0 1 0 0 1 0| var		| imm		|
xDA60		imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 0 0 0 0 0| imm		| imm2		|
xDA62		imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 0 0 0 1 0| imm		| imm2		|
xDA66		var,imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 0 0 1 1 0| var		| imm		| imm2		|
xDA70		imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 1 0 0 0 0| imm		| imm2		|
xDA72		imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 1 0 0 1 0| imm		| imm2		|
xDA76		imm,imm2		|1 1 0 1 1 0 1 0|0 1 1 1 0 1 1 0| imm		| imm2		|
xDA80		dax,imm,imm2		|1 1 0 1 1 0 1 0|1| dax		| imm		| imm2		|
xDA86		imm,imm2,dst,>JC	|1 1 0 1 1 0 1 0|1 0 0 0 0 1 1 0| imm		| imm2		| dst		|
xDAA1		imm			|1 1 0 1 1 0 1 0|1 0 1 0 0 0 0 1| imm		|
xDAL		imm,var			|1 1 0 1 1 0 1 0| imm		| var		|
xE0		imm,var			|1 1 1 0 0 0 0 0| imm		| var		|
yE1		imm,imm2		|1 1 1 0 0 0 0 1| imm		| imm2		|
yE2		imm,var			|1 1 1 0 0 0 1 0| imm		| var		|
xF0		dst,>JC			|1 1 1 1 0 0 0 0| dst		|
xF2		dst,>JC			|1 1 1 1 0 0 1 0| dst		|
'''

class R1kExpIns(assy.Instree_ins):
    ''' Experiment Instructions '''

    def assy_dax(self):
        ''' ... '''
        return assy.Arg_imm(self['dax'] | 0x80)

    def assy_imm(self):
        ''' ... '''
        return assy.Arg_imm(self['imm'])

    def assy_imm2(self):
        ''' ... '''
        return assy.Arg_imm(self['imm2'])

    def assy_var(self):
        ''' ... '''
        a  = self['var']
        if a >= self.lang.code_base:
            self.lang.m.set_attr(a, 1)
        return assy.Arg_dst(self.lang.m, a)

    def assy_var2(self):
        ''' ... '''
        a  = self['var2']
        if a >= self.lang.code_base:
            self.lang.m.set_attr(a, 1)
        return assy.Arg_dst(self.lang.m, a)

    def assy_dst(self):
        ''' ... '''
        self.dstadr = self['dst']
        return assy.Arg_dst(self.lang.m, self.dstadr)

    def assy_subr(self):
        ''' ... '''
        a = self.lang.m[self.lo]
        self.dst_adr = self.lang.m[a]
        if not self.dst_adr:
            raise assy.Invalid()
        self.lang.codeptr(a)
        self.lang.subrs.add(self.dst_adr)
        return assy.Arg_dst(self.lang.m, self.dst_adr)

class R1kExp(assy.Instree_disass):
    ''' Experiment "CPU" '''
    def __init__(self, lang="R1KEXP"):
        super().__init__(
            lang,
            ins_word=8,
            mem_word=8,
            abits=8,
        )
        self.add_ins(R1K_EXP, R1kExpIns)
