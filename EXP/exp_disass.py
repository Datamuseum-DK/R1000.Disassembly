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
REPEAT_L	imm			|0 0 0 0 0 0 0|m| imm		|
REPEAT		imm			|0 0 0|   imm   |
UNTIL		-			|0 0 0 1 0 1 1|m|
CALL		subr,>C			|0 0 0 1 1 0| x |
CALL_PT		subr,>CC		|0 0 0 1 1 1| x |
CALL_PX		subr,>CC		|0 0 1 0 0 0| x |
CALL_NPT	subr,>CC		|0 0 1 0 0 1| x |
CALL_NPX	subr,>CC		|0 0 1 0 1 0| x |
RET		>R 			|0 0 1 0 1 1 0|m|
RET_PT		>RC			|0 0 1 0 1 1 1|m|
RET_PX		>RC			|0 0 1 1 0 0 0|m|
RET_NPT		>RC			|0 0 1 1 0 0 1|m|
RET_NPX		>RC			|0 0 1 1 0 1 0|m|
JMP		dst,>J			|0 0 1 1 0 1 1|m| dst 		|
JMP_PT		dst,>JC			|0 0 1 1 1 0 0|m| dst 		|
JMP_PX		dst,>JC			|0 0 1 1 1 0 1|m| dst 		|
JMP_NPT		dst,>JC			|0 0 1 1 1 1 0|m| dst		|
JMP_NPX		dst,>JC			|0 0 1 1 1 1 1|m| dst 		|
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

# Compare two bytes
CMP2_BNE	var,var2,dst,>JC	|0 1 0 1 0 0 1 0|0|var		| var2		| dst		|
CMP2_BNE	imm,imm2,var,dst,>JC	|0 1 0 1 0 0 1 1| imm		| imm2		| var		| dst		|

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
SET_PT		-			|0 1 1 0 0 1 0|m|
SET_PX		-			|0 1 1 0 0 1 1|m|
CLR_PT		-			|0 1 1 0 1 0 0|m|
CLR_PX		-			|0 1 1 0 1 0 1|m|
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
INC2		var			|1 0 0 0 0 1 0|m| var		|
DEC		var			|1 0 0 0 0 1 1|m| var		|
x88		imm			|1 0 0 0 1 0 0 0| imm		|
INV		var			|1 0 0 0 1 0 1|m| var		|

CPL2		var			|1 0 0 0 1 1 0|m| var		|

COPY		var,var2		|1 0 0 0 1 1 1 0| var		| var2		|
STORE		imm,var			|1 0 0 0 1 1 1 1| imm		| var		|

# Copy two bytes from @var -> @var2
COPY2		var,var2		|1 0 0 1 0 0 0 0| var		| var2		|

# Store two immediate bytes
STORE2		imm,imm2,var		|1 0 0 1 0 0 0 1| imm		| imm2		| var		|

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

# A6,A7,AA,AB Vector right shift/rotate ?  imm = nshift-1, imm2 = nbytes
V_RIGHT.0	imm,imm2,var		|1 0 1 0 0 1 1 0| imm | imm2	| var		|
V_RIGHT.0	imm,imm2,R3		|1 0 1 0 0 1 1 1| imm | imm2	|
V_RIGHT.1	imm,imm2,var		|1 0 1 0 1 0 1 0| imm | imm2	| var		|
V_RIGHT.1	imm,imm2,R3		|1 0 1 0 1 0 1 1| imm | imm2	|

# A8,A9,AC,AD Vector left shift/rotate ?  imm = nshift-1, imm2 = nbytes
V_LEFT.0	imm,imm2,var		|1 0 1 0 1 0 0 0| imm | imm2	| var		|
V_LEFT.0	imm,imm2,R3		|1 0 1 0 1 0 0 1| imm | imm2	|
V_LEFT.1	imm,imm2,var		|1 0 1 0 1 1 0 0| imm | imm2	| var		|
V_LEFT.1	imm,imm2,R3		|1 0 1 0 1 1 0 0| imm | imm2	|

# Vector operations, acts on #imm location starting at var/R3
V_INV		imm,var			|1 0 1 0 1 1 1|0|1 0 0|imm	| var		|
V_INV		imm,R3			|1 0 1 0 1 1 1|1|1 0 0|imm	|
V_oper		var,imm,imm2		|1 0 1 0 1 1 1|0|imm2 |imm	| var		|
V_oper		R3,imm,imm2		|1 0 1 0 1 1 1|1|imm2 |imm	|
xAE		dst,>JC			|1 0 1 0 1 1 1 0|0 0 0 0 1 0 0 0|0 0 0 1 1 0 1 0| dst		|

# Vector operations, acts on #imm locations, at var+var2/R2+R3
#    example: TEST_RDR_SCAN.IOC
V_CMP_BNE	imm,var,var2,>JC	|1 0 1 1 0 0 0 0|0 0 1| imm	| var		| var2		| dst		|
V_CMP_BNE	imm,R2,R3,>JC		|1 0 1 1 0 0 0 1|0 0 1| imm	| dst		|
V_XOR		imm,var,var2		|1 0 1 1 0 0 0 0|1 1 0| imm	| var		| var2		|
V_XOR		imm,R2,R3		|1 0 1 1 0 0 0 1|1 1 0| imm	|

xB0_?		imm,imm2,var,var2	|1 0 1 1 0 0 0 0| imm | imm2	| var		| var2		|
xB1_?		imm,imm2,R2,R3		|1 0 1 1 0 0 0 1| imm | imm2	|

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
FSM_W16		var,fsm			|1 1 0 1 0 0 0 0| var		| fsm		|
FSM_W16		imm,fsm			|1 1 0 1 0 0 1|m| imm		| fsm		|
xD4		imm,imm2,var		|1 1 0 1 0 1 0 0| imm		| imm2		| var		|
xD5		imm,var,var2		|1 1 0 1 0 1 0 1| imm		| var		| var2		|
FSM8		-			|1 1 0 1 0 1 1|m|
FSM2		-			|1 1 0 1 1 0 0|m|

# imm2 is FSM command
xDA_12		var,imm2		|1 1 0 1 1 0 1|m| col   |0 0 0|0| var		| imm2		|
xDA_12		R2,imm2			|1 1 0 1 1 0 1|m| col   |0 0 0|1| imm2		|

xDA_34		var,imm2		|1 1 0 1 1 0 1|m| col   |0 0 1|0| var		| imm2		|
xDA_34		R2,imm2			|1 1 0 1 1 0 1|m| col   |0 0 1|1| imm2		|

# XXX: Not sure about these lengths
xDA_56		var,imm2,>R		|1 1 0 1 1 0 1|m| col   |0 1|x|0| var		| imm2		|
xDA_56		R2,imm2,>R		|1 1 0 1 1 0 1|m| col   |0 1|x|1| imm2		|

# XXX: Not sure about these lengths
xDA_ac		var,imm2,>R		|1 1 0 1 1 0 1|m| col   |1|  x|0| var		| imm2		|
xDA_ac		R2,imm2,>R		|1 1 0 1 1 0 1|m| col   |1|  x|1| imm2		|

FAIL4		>R			|1 1 0 1 1 0 1|m|0 0 0 0 1 0 0 0|

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
        return assy.Arg_verbatim("{%02x}" % self['fsm'])

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
