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
REPEAT		imm			|0 0 0 0 0 0 0|m| imm		|
REPEAT		imm			|0 0 0|   imm   |
UNTIL		-			|0 0 0 1 0 1 1|m|
CALL		subr,>C			|0 0 0 1 1 0| x |
CALL_PT1	subr,>CC		|0 0 0 1 1 1| x |
CALL_PX1	subr,>CC		|0 0 1 0 0 0| x |
CALL_PT0	subr,>CC		|0 0 1 0 0 1| x |
CALL_PX0	subr,>CC		|0 0 1 0 1 0| x |
RET		>R 			|0 0 1 0 1 1 0|m|
RET_PT1		>RC			|0 0 1 0 1 1 1|m|
RET_PX1		>RC			|0 0 1 1 0 0 0|m|
RET_PT0		>RC			|0 0 1 1 0 0 1|m|
RET_PX0		>RC			|0 0 1 1 0 1 0|m|
JMP		dst,>J			|0 0 1 1 0 1 1|m| dst 		|
JMP_PT1		dst,>JC			|0 0 1 1 1 0 0|m| dst 		|
JMP_PX1		dst,>JC			|0 0 1 1 1 0 1|m| dst 		|
JMP_PT0		dst,>JC			|0 0 1 1 1 1 0|m| dst		|
JMP_PX0		dst,>JC			|0 0 1 1 1 1 1|m| dst 		|
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
END		>R 			|0 1 0 1 1 1 0|m|
LOOPE		imm,dst,>JC		|0 1 0 1 1 1 1 0| imm		| dst		|
x5F		-			|0 1 0 1 1 1 1 1|
FAIL3		-			|0 1 1 0 0 0 0|m|
x62		imm			|0 1 1 0 0 0 1 0| imm		|
y63		-			|0 1 1 0 0 0 1 1|
PT1		-			|0 1 1 0 0 1 0|m|
PX1		-			|0 1 1 0 0 1 1|m|
PT0		-			|0 1 1 0 1 0 0|m|
PX0		-			|0 1 1 0 1 0 1|m|
PTINV		-			|0 1 1 0 1 1 0|m|
PXINV		-			|0 1 1 0 1 1 1|m|
LD		R2,var			|0 1 1 1 0 0 0|m| var		|
LD		R3,var			|0 1 1 1 0 0 1|m| var		|
INC		R2			|0 1 1 1 0 1 0|m|
INC		R3			|0 1 1 1 0 1 1|m|
DEC		R2			|0 1 1 1 1 0 0|m|
DEC		R3			|0 1 1 1 1 0 1|m|
ADD		R2,imm			|0 1 1 1 1 1 0|m| imm		|
ADD		R3,imm			|0 1 1 1 1 1 1|m| imm		|
XHG		R2,R3			|1 0 0 0 0 0 0|m|
INC		var			|1 0 0 0 0 0 1|m| var		|
x84		var			|1 0 0 0 0 1 0 0| var		|
x85		-			|1 0 0 0 0 1 0 1|
DEC		var			|1 0 0 0 0 1 1|m| var		|
x88		imm			|1 0 0 0 1 0 0 0| imm		|
INV		var			|1 0 0 0 1 0 1|m| var		|
x8C		var			|1 0 0 0 1 1 0 0| var		|
COPY		var,var2		|1 0 0 0 1 1 1 0| var		| var2		|
STORE		imm,var			|1 0 0 0 1 1 1 1| imm		| var		|
x90		var,var2		|1 0 0 1 0 0 0 0| var		| var2		|
x91		imm,imm2,var		|1 0 0 1 0 0 0 1| imm		| imm2		| var		|
ADD		var,var2		|1 0 0 1 0 0 1 0| var		| var2		|
ADD		imm,var			|1 0 0 1 0 0 1 1| imm		| var		|
x95		imm,imm2,var		|1 0 0 1 0 1 0 1| imm		| imm2		| var		|
AND		var,var2		|1 0 0 1 0 1 1 0| var		| var2		|
AND		imm,var			|1 0 0 1 0 1 1 1| imm		| var		|
x98		var			|1 0 0 1 1 0 0 0| var		|
x99		imm,imm2,var		|1 0 0 1 1 0 0 1| imm		| imm2		| var		|
OR		var,var2		|1 0 0 1 1 0 1 0| var		| var2		|
OR		imm,var2		|1 0 0 1 1 0 1 1| imm		| var2		|
x9D		imm,imm2,var		|1 0 0 1 1 1 0 1| imm		| imm2		| var		|
XOR		var,var2		|1 0 0 1 1 1 1 0| var		| var2		|
XOR		imm,var			|1 0 0 1 1 1 1 1| imm		| var		|
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
xB2		var,imm,imm2		|1 0 1 1 0 0 1|m| var		| imm		| imm2		|
xB4		var,var2		|1 0 1 1 0 1 0|m| var		| var2		|
xB6		imm,var,imm2		|1 0 1 1 0 1 1 0| imm		| var		| imm2		|
xB7		imm,var,var2		|1 0 1 1 0 1 1 1| imm		| var		| var2		|
xB8		var			|1 0 1 1 1 0 0|m| var		|
xBA		var,var2		|1 0 1 1 1 0 1 0| var		| var2		|
FSM		fsm			|1 0 1 1 1 1 0|m| fsm		|
WP1_FSM		var,fsm			|1 0 1 1 1 1 1 0| var		| fsm		|
WP1_FSM		R2,fsm			|1 0 1 1 1 1 1 1| fsm		|
WP2_FSM		var,fsm			|1 1 0 0 0 0 0 0| var		| fsm		|
WP2_FSM		R2,fsm			|1 1 0 0 0 0 0 1| fsm		|
WP12_FSM	var,fsm			|1 1 0 0 0 0 1 0| var		| fsm		|
WP12_FSM	R2,fsm			|1 1 0 0 0 0 1 1| fsm		|
WP1_FSM		imm,fsm			|1 1 0 0 0 1 0|m| imm		| fsm		|
WP2_FSM		imm,fsm			|1 1 0 0 0 1 1|m| imm		| fsm		|
WP12_FSM	imm,imm2,fsm		|1 1 0 0 1 0 0|m| imm		| imm2		| fsm		|
FSM_RP1		fsm,var			|1 1 0 0 1 0 1 0| fsm		| var		|
FSM_RP1		fsm,R3			|1 1 0 0 1 0 1 1| fsm		|
FSM_RP2		fsm,var			|1 1 0 0 1 1 0 0| fsm		| var		|
FSM_RP2		fsm,R3			|1 1 0 0 1 1 0 1| fsm		|
FSM_RP12	fsm,var			|1 1 0 0 1 1 1 0| fsm		| var		|
FSM_RP12	fsm,R3			|1 1 0 0 1 1 1 1| fsm		|
xD0		var,imm			|1 1 0 1 0 0 0 0| var		| imm		|
xD2		imm,imm2		|1 1 0 1 0 0 1 0| imm		| imm2		|
xD4		imm,imm2,var		|1 1 0 1 0 1 0 0| imm		| imm2		| var		|
xD5		imm,var,var2		|1 1 0 1 0 1 0 1| imm		| var		| var2		|
FSM8		-			|1 1 0 1 0 1 1|m|
FSM2		-			|1 1 0 1 1 0 0|m|

# XXX: Implement DA as (variable length) prefix ?
#xDA_R5		R3			|1 1 0 1 1 0 1 0| x	      |1|
#xDA_R5		R2			|1 1 0 1 1 0 1 0| x	  |1|0|1|
#xDA_R5		imm			|1 1 0 1 1 0 1 0| x	      |0| imm		|

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
FAIL4		>R			|1 1 0 1|1 1| m |
FAIL4		>R			|1 1 1 0| m     |
FAIL4		>R			|1 1 1 1| m     |
'''

class R1kExpIns(assy.Instree_ins):
    ''' Experiment Instructions '''

    def assy_dax(self):
        ''' ... '''
        return assy.Arg_imm(self['dax'] | 0x80)

    def assy_imm(self):
        ''' ... '''
        return assy.Arg_imm(self['imm'])

    def assy_fsm(self):
        ''' ... '''
        return assy.Arg_verbatim("/0x%02x/" % self['fsm'])

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
        self.verbatim += ("R2",)
        self.verbatim += ("R3",)
