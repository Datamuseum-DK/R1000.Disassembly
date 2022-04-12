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
CALL		PT,subr,>CC		|0 0 0 1 1 1| x |
CALL		PX,subr,>CC		|0 0 1 0 0 0| x |
CALL		NPT,subr,>CC		|0 0 1 0 0 1| x |
CALL		NPX,subr,>CC		|0 0 1 0 1 0| x |
RET		>R			|0 0 1 0 1 1 0|m|
RET		PT,>RC			|0 0 1 0 1 1 1|m|
RET		PX,>RC			|0 0 1 1 0 0 0|m|
RET		NPT,>RC			|0 0 1 1 0 0 1|m|
RET		NPX,>RC			|0 0 1 1 0 1 0|m|
JMP		dst,>J			|0 0 1 1 0 1 1|m| dst		|
JMP		PT,dst,>JC		|0 0 1 1 1 0 0|m| dst		|
JMP		PX,dst,>JC		|0 0 1 1 1 0 1|m| dst		|
JMP		NPT,dst,>JC		|0 0 1 1 1 1 0|m| dst		|
JMP		NPX,dst,>JC		|0 0 1 1 1 1 1|m| dst		|
JMP		GT,var,var2,dst,>JC	|0 1 0 0 0 0 0 0| var		| var2		| dst		|
JMP		LT,var,var2,dst,>JC	|0 1 0 0 0 0 0 1| var		| var2		| dst		|
TEST		Z,imm,var,dst,>JC	|0 1 0 0 0 0 1 0| imm		| var		| dst		|
TEST		NZ,imm,var,dst,>JC	|0 1 0 0 0 0 1 1| imm		| var		| dst		|
JMP		Z,var,dst,>JC		|0 1 0 0 0 1 0|m| var		| dst		|
JMP		NZ,var,dst,>JC		|0 1 0 0 0 1 1|m| var		| dst		|
JMP.W		Z,var,dst,>JC		|0 1 0 0 1 0 0|m| var		| dst		|
JMP.W		NZ,var,dst,>JC		|0 1 0 0 1 0 1|m| var		| dst		|
JMP		EQ,var,var2,dst,>JC	|0 1 0 0 1 1 0 0| var		| var2		| dst		|
JMP		EQ,imm,var,dst,>JC	|0 1 0 0 1 1 0 1| imm		| var		| dst		|
JMP		NE,var,var2,dst,>JC	|0 1 0 0 1 1 1 0| var		| var2		| dst		|
JMP		NE,imm,var,dst,>JC	|0 1 0 0 1 1 1 1| imm		| var		| dst		|

# Compare two bytes, branch if equal
JMP.W		EQ,var,var2,dst,>JC	|0 1 0 1 0 0 0 0| var		| var2		| dst		|
JMP.W		EQ,wimm,var,dst,>JC	|0 1 0 1 0 0 0 1| imm		| imm2		| var		| dst		|

# Compare two bytes, branch if non equal
JMP.W		NE,var,var2,dst,>JC	|0 1 0 1 0 0 1 0| var		| var2		| dst		|
JMP.W		NE,wimm,var,dst,>JC	|0 1 0 1 0 0 1 1| imm		| imm2		| var		| dst		|

# Decrement, jump not zero
DJNZ		var,dst,>JC		|0 1 0 1 0 1 0|m| var		| dst		|
DJNZ.W		var,dst,>JC		|0 1 0 1 0 1 1|m| var		| dst		|

# Decrement, jump not negative
DJNN		var,dst,>JC		|0 1 0 1 1 0 0|m| var		| dst		|
DJNN.W		var,dst,>JC		|0 1 0 1 1 0 1|m| var		| dst		|

END		>R			|0 1 0 1 1 1 0|m|
LOOPE		imm,dst,>JC		|0 1 0 1 1 1 1|m| imm		| dst		|
PAUSE		-			|0 1 1 0 0 0 0|m|

# Delay in units of 50µs
DELAY		imm			|0 1 1 0 0 0 1|m| imm		|

SET		PT			|0 1 1 0 0 1 0|m|
SET		PX			|0 1 1 0 0 1 1|m|
CLR		PT			|0 1 1 0 1 0 0|m|
CLR		PX			|0 1 1 0 1 0 1|m|
INV		PT			|0 1 1 0 1 1 0|m|
INV		PX			|0 1 1 0 1 1 1|m|
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
INC.W		var			|1 0 0 0 0 1 0|m| var		|

DEC		var			|1 0 0 0 0 1 1|m| var		|
DEC.W		var			|1 0 0 0 1 0 0|m| var		|

INV		var			|1 0 0 0 1 0 1|m| var		|
INV.W		var			|1 0 0 0 1 1 0|m| var		|

MOV		var,var2		|1 0 0 0 1 1 1 0| var		| var2		|
MOV		imm,var			|1 0 0 0 1 1 1 1| imm		| var		|

# Copy two bytes from @var -> @var2
MOV.W		var,var2		|1 0 0 1 0 0 0 0| var		| var2		|

# Store two immediate bytes
MOV.W		wimm,var		|1 0 0 1 0 0 0 1| imm		| imm2		| var		|

ADD		var,var2		|1 0 0 1 0 0 1 0| var		| var2		|
ADD		imm,var			|1 0 0 1 0 0 1 1| imm		| var		|
ADD.W		var,var2		|1 0 0 1 0 1 0 0| var		| var2		|
ADD.W		wimm,var		|1 0 0 1 0 1 0 1| imm		| imm2		| var		|
AND		var,var2		|1 0 0 1 0 1 1 0| var		| var2		|
AND		imm,var			|1 0 0 1 0 1 1 1| imm		| var		|
AND.W		var,var2		|1 0 0 1 1 0 0 0| var		| var2		|
AND.W		wimm,var		|1 0 0 1 1 0 0 1| imm		| imm2		| var		|
OR		var,var2		|1 0 0 1 1 0 1 0| var		| var2		|
OR		imm,var2		|1 0 0 1 1 0 1 1| imm		| var2		|
OR.W		var,var2		|1 0 0 1 1 1 0 0| var		| var2		|
OR.W		wimm,var		|1 0 0 1 1 1 0 1| imm		| imm2		| var		|
XOR		var,var2		|1 0 0 1 1 1 1 0| var		| var2		|
XOR		imm,var			|1 0 0 1 1 1 1 1| imm		| var		|
XOR.W		var,var2		|1 0 1 0 0 0 0 0| var		| var2		|
XOR.W		wimm,var		|1 0 1 0 0 0 0 1| imm		| imm2		| var		|
VADD		vec,imm,var		|1 0 1 0 0 0 1 0| vec		| imm		| var		|
VADD		vec,imm,R3		|1 0 1 0 0 0 1 1| vec		| imm		|
VSUB		vec,imm,var		|1 0 1 0 0 1 0 0| vec		| imm		| var		|
VSUB		vec,imm,R3		|1 0 1 0 0 1 0 1| vec		| imm		|

# A6,A7,AA,AB Vector right shift/rotate ?  imm = nshift-1, imm2 = nbytes
LEFT.0		rot,var,vec		|1 0 1 0 0 1 1 0| rot | vec	| var		|
LEFT.0		rot,R3,vec		|1 0 1 0 0 1 1 1| rot | vec	|
RIGHT.1		rot,var,vec		|1 0 1 0 1 0 1 0| rot | vec	| var		|
RIGHT.1		rot,R3,vec		|1 0 1 0 1 0 1 1| rot | vec	|

# A8,A9,AC,AD Vector left shift/rotate ?  imm = nshift-1, imm2 = nbytes
SR.0		rot,var,vec		|1 0 1 0 1 0 0 0| rot | vec	| var		|
SR.0		rot,R3,vec		|1 0 1 0 1 0 0 1| rot | vec	|
SR.1		rot,var,vec		|1 0 1 0 1 1 0 0| rot | vec	| var		|
SR.1		rot,R3,vec		|1 0 1 0 1 1 0 1| rot | vec	|

# Vector operations, acts on #imm location starting at var/R3
VJMP		Z,vec,var,dst,>JC	|1 0 1 0 1 1 1|0|0 0 0|vec	| var		| dst		|
VJMP		Z,vec,R3,dst,>JC	|1 0 1 0 1 1 1|1|0 0 0|vec	| dst		|
VJMP		NZ,vec,var,dst,>JC	|1 0 1 0 1 1 1|0|0 0 1|vec	| var		| dst		|
VJMP		NZ,vec,R3,dst,>JC	|1 0 1 0 1 1 1|1|0 0 1|vec	| dst		|
VINC		vec,var			|1 0 1 0 1 1 1|0|0 1 0|vec	| var		|
VINC		vec,R3			|1 0 1 0 1 1 1|1|0 1 0|vec	|
VDEC		vec,var			|1 0 1 0 1 1 1|0|0 1 1|vec	| var		|
VDEC		vec,R3			|1 0 1 0 1 1 1|1|0 1 1|vec	|
VINV		vec,var			|1 0 1 0 1 1 1|0|1 0 0|vec	| var		|
VINV		vec,R3			|1 0 1 0 1 1 1|1|1 0 0|vec	|
BAD_INS		-			|1 0 1 0 1 1 1|m|

xAE		dst,>JC			|1 0 1 0 1 1 1 0|0 0 0 0 1 0 0 0|0 0 0 1 1 0 1 0| dst		|

VJMP		EQ,vec,var,var2,dst,>JC	|1 0 1 1 0 0 0 0|0 0 0| vec	| var		| var2		| dst		|
VJMP		EQ,vec,R2,R3,dst,>JC	|1 0 1 1 0 0 0 1|0 0 0| vec	| dst		|
VJMP		NE,vec,var,var2,dst,>JC	|1 0 1 1 0 0 0 0|0 0 1| vec	| var		| var2		| dst		|
VJMP		NE,vec,R2,R3,dst,>JC	|1 0 1 1 0 0 0 1|0 0 1| vec	| dst		|
VMOV		vec,var,var2		|1 0 1 1 0 0 0 0|0 1 0| vec	| var		| var2		|
VMOV		vec,@R2,@R3		|1 0 1 1 0 0 0 1|0 1 0| vec	|
VADD		vec,var,var2		|1 0 1 1 0 0 0 0|0 1 1| vec	| var		| var2		|
VADD		vec,R2,R3		|1 0 1 1 0 0 0 1|0 1 1| vec	|
VAND		vec,var,var2		|1 0 1 1 0 0 0 0|1 0 0| vec	| var		| var2		|
VAND		vec,R2,R3		|1 0 1 1 0 0 0 1|1 0 0| vec	|
VOR		vec,var,var2		|1 0 1 1 0 0 0 0|1 0 1| vec	| var		| var2		|
VOR		vec,R2,R3		|1 0 1 1 0 0 0 1|1 0 1| vec	|
VXOR		vec,var,var2		|1 0 1 1 0 0 0 0|1 1 0| vec	| var		| var2		|
VXOR		vec,R2,R3		|1 0 1 1 0 0 0 1|1 1 0| vec	|

BAD_INS		-			|1 0 1 1 0 0 0|m|

xB2		var,imm,imm2		|1 0 1 1 0 0 1|m| var		| imm		| imm2		|
PARITY		[0x8],var,var2		|1 0 1 1 0 1 0|m| var		| var2		|

# Set parity in bit `imm2` of `var[0:imm]`
EVNPAR		imm,var,imm2		|1 0 1 1 0 1 1 0| imm		| var		| imm2		|
ODDPAR		imm,var,imm2		|1 0 1 1 0 1 1 1| imm		| var		| imm2		|

IDENT		var			|1 0 1 1 1 0 0|m| var		|
xBA		var,var2		|1 0 1 1 1 0 1 0| var		| var2		|
FSM		fsm			|1 0 1 1 1 1 0|m| fsm		|

WP1_FSM		var,fsm			|1 0 1 1 1 1 1 0| var		| fsm		|
WP1_FSM		R2,fsm			|1 0 1 1 1 1 1 1| fsm		|
WP2_FSM		var,fsm			|1 1 0 0 0 0 0 0| var		| fsm		|
WP2_FSM		R2,fsm			|1 1 0 0 0 0 0 1| fsm		|
WP12_FSM	var,fsm			|1 1 0 0 0 0 1 0| var		| fsm		|
WP12_FSM	R2,fsm			|1 1 0 0 0 0 1 1| fsm		|
WFSM.L		imm,fsm			|1 1 0 0 0 1 0|m| imm		| fsm		|
WFSM.H		imm,fsm			|1 1 0 0 0 1 1|m| imm		| fsm		|
WFSM.W		wimm,fsm		|1 1 0 0 1 0 0|m| imm		| imm2		| fsm		|
RFSM.L		fsm,var			|1 1 0 0 1 0 1 0| fsm		| var		|
RFSM.L		fsm,R3			|1 1 0 0 1 0 1 1| fsm		|
RFSM.H		fsm,var			|1 1 0 0 1 1 0 0| fsm		| var		|
RFSM.H		fsm,@R3			|1 1 0 0 1 1 0 1| fsm		|
RFSM.W		fsm,var			|1 1 0 0 1 1 1 0| fsm		| var		|
RFSM.W		fsm,R3			|1 1 0 0 1 1 1 1| fsm		|

FSM_8X		var,fsm			|1 1 0 1 0 0 0 0| var		| fsm		|
FSM_8X		imm,fsm			|1 1 0 1 0 0 1|m| imm		| fsm		|

RCV_P1		imm,fsm,var		|1 1 0 1 0 1 0 0| imm		| fsm		| var		|
RCV_P2		imm,fsm,var		|1 1 0 1 0 1 0 1| imm		| fsm		| var		|
FSM8		-			|1 1 0 1 0 1 1|m|
FSM2		-			|1 1 0 1 1 0 0|m|

CHN_SND		var,chn			|1 1 0 1 1 0 1|m| chn   |0 0 0|0| var		| fsm		|
CHN_SND		@R2,chn			|1 1 0 1 1 0 1|m| chn   |0 0 0|1| fsm		|

CHN_RCV		chn,var			|1 1 0 1 1 0 1|m| chn   |0 0 1|0| var		| fsm		|
CHN_RCV		chn,@R3			|1 1 0 1 1 0 1|m| chn   |0 0 1|1| fsm		|

CHN_CMP		EQ,var,chn,dst,>JC	|1 1 0 1 1 0 1|m| chn   |0 1 0|0| var		| fsm		| dst		|
CHN_CMP		EQ,@R2,chn,dst,>JC	|1 1 0 1 1 0 1|m| chn   |0 1 0|1| fsm		| dst		|
CHN_CMP		NE,var,chn,dst,>JC	|1 1 0 1 1 0 1|m| chn   |0 1 1|0| var		| fsm		| dst		|
CHN_CMP		NE,@R2,chn,dst,>JC	|1 1 0 1 1 0 1|m| chn   |0 1 1|1| fsm		| dst		|

# XXX: Not sure about these lengths
CHN_TST		NZ,chn,dst,>JC		|1 1 0 1 1 0 1|m| chn	|1 0 0 1| fsm		| dst		|
CHN_TST		Z,chn,dst,>JC		|1 1 0 1 1 0 1|m| chn	|1 1 0 1| fsm		| dst		|
CHN_TST		??,chn,dst,>JC		|1 1 0 1 1 0 1|m| chn	|1|y|x|1| fsm		| dst		|

CHN_QQQ		-,>R			|1 1 0 1 1 0 1|m|

P1		imm			|1 1 0 1 1 1 0|m| imm		|
P2		imm			|1 1 0 1 1 1 1|m| imm		|
P1_AO		imm,var			|1 1 1 0 0 0 0 0| imm		| var		|
P1_AO		imm,imm2		|1 1 1 0 0 0 0 1| imm		| imm2		|
P2_AO		imm,var			|1 1 1 0 0 0 1 0| imm		| var		|
P2_AO		imm,imm2		|1 1 1 0 0 0 1 1| imm		| imm2		|
CALL		DFLG,subr,>CC		|1 1 1 0 0 1| x |
CALL		NDFLG,subr,>CC		|1 1 1 0 1 0| x |
RET		DFLG,>RC		|1 1 1 0 1 1 1|m|
JMP		DFLG,dst,>JC		|1 1 1 1 0 0 0|m| dst		|
JMP		NDFLG,dst,>JC		|1 1 1 1 0 0 1|m| dst		|

# Only implemented in MEM32 DIPROC
FAIL4LO		>R			|0| bla		|
FAIL4HI		>R			|1| bla		|
'''

R1K_EXP_IOC = '''
IOC_SND		imm,UIRSC01		|1 1 0 1 0 0 1 0| imm		|0 0 0 1 0 0 0 0|
IOC_SND		imm,UIRSC23		|1 1 0 1 0 0 1 0| imm		|0 0 0 1 0 0 0 1|
IOC_XFR		TYPVAL,DUMMY		|BC|51|
'''


R1K_EXP_FIU = '''
FIU_SND		imm,MDREG		|1 1 0 1 0 0 1 0| imm		|0 0 0 1 0 0 0 0|
FIU_SND		imm,PAREG		|1 1 0 1 0 0 1 0| imm		|0 1 0 1 0 0 0 0|

FIU_RCV		PAREG,var		|1 1 0 1 0 1 0 0|0 0 0 0 1 0 0 0|0 1 0 1 0 0 0 1| var		|
'''

R1K_EXP_SEQ = '''
SEQ_RCV		SEQDG.L,@R3		|1 1 0 0 1 0 1 1|0 0 1 1 0 0 0 1|
SHIFT		S.MISC,imm		|1 1 0 0 0 1 0 0| imm		|0 1 0 0 0 0 1 1|
#SEQ_RCV	TYPVAL,var		|1 1 0 1 1 0 1 0|1 0 0 1 0 0 1 0| var		|0 0 1 1 0 0 0 0|
'''

R1K_EXP_TYP = '''
TYP_RCV		PAREG,var		|1 1 0 1 0 1 0 0|0 0 0 0 1 0 0 0|0 1 0 0 0 0 0 1| var		|
TYP_SND		imm,PAREG		|1 1 0 1 0 0 1 0| imm		|0 1 0 0 0 0 0 0|
TYP_SND		@R2,DICNTR		|1 1 0 0 0 0 1 1|0 0 1 0 1 0 1 1|
TYP_SND		wimm,DICNTR		|1 1 0 0 1 0 0 0| imm		| imm2		|0 0 1 0 1 0 1 1|
TYP_SND		imm,URSR		|1 1 0 1 0 0 1 0| imm		|0 0 1 1 1 0 1 1|
FSM		WRITE_WCS		|1 0 1 1 1 1 0 0|0 1 0 0 1 1 0 0|
FSM		LD_LCNT_FM_WDR		|1 0 1 1 1 1 0 0|0 0 1 1 0 0 1 1|
FSM		FILL_RF			|1 0 1 1 1 1 0 0|0 0 0 1 1 0 0 1|
'''

R1K_EXP_MEM32 = '''
MEM_SND	var,SETLAR			|1 1 0 0 0 0 0 0| var		|0 0 0 0 0 1 0 0|
'''

class R1kExpIns(assy.Instree_ins):
    ''' Experiment Instructions '''

    def assy_vec(self):
        ''' ... '''
        return assy.Arg_verbatim("[0x%x]" % self['vec'])

    def assy_dax(self):
        ''' ... '''
        return assy.Arg_imm(self['dax'] | 0x80)

    def assy_rot(self):
        ''' ... '''
        return assy.Arg_imm(self['rot'] + 1, wid=4)

    def assy_imm(self):
        ''' ... '''
        return assy.Arg_imm(self['imm'], wid=8)

    def assy_wimm(self):
        ''' ... '''
        return assy.Arg_imm((self['imm'] << 8)| self['imm2'], wid=16)

    def assy_chn(self):
        ''' ... '''
        chain = {
            0x00: "M.MAR",
            0x01: "M.DREG_FULL",
            0x02: "M.DREG_VAL_PAR",
            0x03: "TV.WDR",
            0x04: "V.UIR",
            0x05: "T.UIR",
            0x06: "F.MAR",
            0x07: "F.MDREG",
            0x08: "F.UIR",
            0x09: "S.TYPVAL",
            0x0a: "S.UIR",
            0x0b: "S.DECODER",
            0x0c: "S.MISC",
            0x0d: "I.DUMMY",
        }.get(self['chn'], "%02x" % self['chn'])
        return assy.Arg_verbatim("{" + chain + ":%02x}" % self['fsm'])

    def assy_fsm(self):
        ''' ... '''
        return assy.Arg_verbatim("{%02x}" % self['fsm'])

    def assy_imm2(self):
        ''' ... '''
        return assy.Arg_imm(self['imm2'])

    def assy_var(self):
        ''' ... '''
        adr  = self['var']
        if adr >= self.lang.code_base:
            self.lang.m.set_attr(adr, 1)
        return assy.Arg_dst(self.lang.m, adr)

    def assy_var2(self):
        ''' ... '''
        adr  = self['var2']
        if adr >= self.lang.code_base:
            self.lang.m.set_attr(adr, 1)
        return assy.Arg_dst(self.lang.m, adr)

    def assy_dst(self):
        ''' ... '''
        self.dstadr = self['dst']
        return assy.Arg_dst(self.lang.m, self.dstadr)

    def assy_subr(self):
        ''' ... '''
        adr = self['x'] + 0x18
        self.dstadr = self.lang.m[adr]
        if not self.dstadr:
            raise assy.Invalid()
        self.lang.codeptr(adr)
        self.lang.subrs.add(self.dstadr)
        return assy.Arg_dst(self.lang.m, self.dstadr)

class R1kExp(assy.Instree_disass):
    ''' Experiment "CPU" '''
    def __init__(self, lang="R1KEXP", board=None):
        super().__init__(
            lang,
            ins_word=8,
            mem_word=8,
            abits=8,
        )
        self.add_ins(R1K_EXP, R1kExpIns)
        extra = {
            "SEQ": R1K_EXP_SEQ,
            "IOC": R1K_EXP_IOC,
            "FIU": R1K_EXP_FIU,
            "MEM0": R1K_EXP_MEM32,
            "MEM2": R1K_EXP_MEM32,
            "M32": R1K_EXP_MEM32,
            "TYP": R1K_EXP_TYP,
        }.get(board)
        if extra is not None:
            self.add_ins(extra, R1kExpIns)
        self.verbatim += (
            "R2", "R3", "I", "@R2", "@R3",
            "UIRSC01", "UIRSC23",
            "TYPVAL", "DUMMY", "INV",
            "PT", "PX", "NPT", "NPX",
            "NZ", "Z", "NE", "EQ", "LT", "GT",
            "DFLG", "NDFLG",
            "UIR", "MDREG", "MAR", "PAREG",
            "SETLAR", "MDREG", "MAR", "PAREG",
            "[0x8]",
            "SEQDG.L",
            "DICNTR",
            "URSR",
            "WRITE_WCS",
            "LD_LCNT_FM_WDR",
            "FILL_RF",
            "S.MISC",
        )
