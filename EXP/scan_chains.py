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
   R1000 Diagnostic Scan Chains
   ----------------------------
'''

import os

MYDIR = os.path.split(__file__)[0]
FILENAME1 = os.path.join(MYDIR, "P8052AH_9028.bin")
FILENAME2 = os.path.join(MYDIR, "DIPROC-01.bin")

DPROC1 = open(FILENAME1, "rb").read()
DPROC2 = open(FILENAME2, "rb").read()

class Field():
    ''' A field of one or more bits in a scan-chain '''

    def __init__(self, name):
        self.name = name
        self.invert = 0
        self.width = 0
        self.bits = []
        self.parts = []
        self.enum = {}
        self.fmt = "0x%x"

    def __repr__(self):
        return "<Field " + self.name + " " + str(self.bits) + ">"

    def __lt__(self, other):
        return self.name < other.name

    def add_bit(self, pos, octet, bitpos):
        ''' Add a bit to a field '''
        self.bits.append((pos, octet, bitpos))

    def finalize(self, enum):
        ''' ... '''
        if enum:
            self.enum = enum
        self.width = 1 + max(a for a, b, c in self.bits)
        assert self.width == len(self.bits)
        if self.name[-1] == "~":
            self.name = self.name[:-1]
            self.invert = (1 << self.width) - 1
        for pos, octet, bitpos in self.bits:
            j = 1 << (self.width - (pos + 1))
            self.parts.append((octet, 0x80 >> bitpos, j))
        if self.width > 1:
            self.fmt = "0x%0" + "%dx" % ((self.width + 3) // 4)

    def decode(self, data):
        ''' Get the value of this field '''
        val = 0
        for octet, mask, weight in self.parts:
            if data[octet] & mask:
                val |= weight
        return val ^ self.invert

    def explain(self, data):
        ''' Yield string explanation if field is non-zero '''
        val = self.decode(data)
        i = self.enum.get(val)
        if i:
            yield self.name + " = " + self.fmt % val + " " + i
        elif val != 0:
            yield self.name + " = " + self.fmt % val + " "

class ScanChain():
    ''' A R1000 Diagnostic Scan chain '''

    BITSPEC = []
    DIAG_D0 = None
    DIAG_D1 = None
    DIAG_D2 = None
    DIAG_D3 = None
    DIAG_D4 = None
    DIAG_D5 = None
    DIAG_D6 = None
    DIAG_D7 = None

    def __init__(self):
        self.fields = {}
        self.parse()
        for fld in self.fields.values():
            fldnm = "FIELD_" + fld.name
            for find,replace in (
                (".", "_"),
                ("~", ""),
            ):
                fldnm = fldnm.replace(find, replace)
            enum = getattr(self, fldnm, None)
            fld.finalize(enum)
        self.fields = list(sorted(self.fields.values()))

    def parse(self):
        ''' Parse the bit-lists '''
        for bit, spec in enumerate(
            (
                self.DIAG_D0,
                self.DIAG_D1,
                self.DIAG_D2,
                self.DIAG_D3,
                self.DIAG_D4,
                self.DIAG_D5,
                self.DIAG_D6,
                self.DIAG_D7,
            )
        ):
            if spec is None:
                continue
            #print("SS", bit, len(spec), spec)
            for row, sig in enumerate(reversed(spec)):
                what = self.BITSPEC[row * 9 + bit]
                octet = what & 0x1f
                if octet == 0x1f:
                    continue
                bitpos = what >> 5

                #print("QQQ", bit, row, sig, octet, bitpos)
                if '/' in sig:
                    fieldname, pos = sig.split('/')
                    field = self.fields.get(fieldname)
                    if not field:
                        field = Field(fieldname)
                        self.fields[fieldname] = field
                    field.add_bit(int(pos), octet, bitpos)
                else:
                    assert sig not in self.fields
                    field = Field(sig)
                    self.fields[sig] = field
                    field.add_bit(0, octet, bitpos)

    def explain(self, data):
        ''' Yield text strings explaining chain state '''
        for i in self.fields:
            yield from i.explain(data)

class SeqTypVal(ScanChain):
    '''
	Sequencer "OUT CHAIN"

        "The internal sequencer bus (a complemented image of the type and val bus most of the time)"

	See also: https://datamuseum.dk/bits/30000958
    '''
    BITSPEC = DPROC1[0xda0:0xe31]
    DIAG_D0 = ["VAL~/%d" % x for x in range(0, 8)] + ["TYP~/%d" % x for x in range(0, 8)]
    DIAG_D1 = ["VAL~/%d" % x for x in range(8, 16)] + ["TYP~/%d" % x for x in range(8, 16)]
    DIAG_D2 = ["VAL~/%d" % x for x in range(16, 24)] + ["TYP~/%d" % x for x in range(16, 24)]
    DIAG_D3 = ["VAL~/%d" % x for x in range(24, 32)] + ["TYP~/%d" % x for x in range(24, 32)]
    DIAG_D4 = ["VAL~/%d" % x for x in range(32, 40)] + ["TYP~/%d" % x for x in range(32, 40)]
    DIAG_D5 = ["VAL~/%d" % x for x in range(40, 48)] + ["TYP~/%d" % x for x in range(40, 48)]
    DIAG_D6 = ["VAL~/%d" % x for x in range(48, 56)] + ["TYP~/%d" % x for x in range(48, 56)]
    DIAG_D7 = ["VAL~/%d" % x for x in range(56, 64)] + ["TYP~/%d" % x for x in range(56, 64)]

class SeqUir(ScanChain):
    '''
	Sequencer UIR scan chain

	See also: https://datamuseum.dk/bits/30000958
    '''
    BITSPEC = DPROC1[0xe31:0xe7a]
    DIAG_D0 = [
        "BRNCH_ADR/13",
        "BRNCH_ADR/12",
        "BRNCH_ADR/11",
        "BRNCH_ADR/10",
        "BRNCH_ADR/9",
        "BRNCH_ADR/8",
        "BRNCH_ADR/7",
        "BRNCH_ADR/6",
    ]
    DIAG_D1 = [
        "BRNCH_ADR/5",
        "BRNCH_ADR/4",
        "BRNCH_ADR/3",
        "BRNCH_ADR/2",
        "BRNCH_ADR/1",
        "BRNCH_ADR/0",
        "COND_SEL~/6",
        "COND_SEL~/5",
    ]
    DIAG_D2 = [
        "COND_SEL~/2",
        "COND_SEL~/3",
        "COND_SEL~/4",
        "COND_SEL~/1",
        "COND_SEL~/0",
        "BR_TYPE/0",
        "BR_TYPE/1",
        "LATCH",
    ]
    DIAG_D3 = [
        "INT_READS/0",
        "B_TIMING/0",
        "B_TIMING/1",
        "EN_MICRO",
        "BR_TYPE/2",
        "BR_TYPE/3",
        "INT_READS/1",
        "INT_READS/2",
    ]
    DIAG_D4 = []
    DIAG_D5 = [
        "LEX_ADR/0",
        "LEX_ADR/1",
        "PARITY",
        "RANDOM/6",
        "RANDOM/4",
        "RANDOM/5",
        "RANDOM/2",
        "RANDOM/3",
    ]
    DIAG_D6 = [
        "RANDOM/0",
        "RANDOM/1",
        "HALT",
        "L_LATE_MACRO",
        None,
        None,
        None,
        None,
    ]
    DIAG_D7 = [
    ]

    # SEQ page 62
    FIELD_B_TIMING = {
        0: "EARLY CONDITION",
        1: "LATCH CONDITION",
        2: "HINT TRUE",
        3: "HINT FALSE",
    }

    # SEQ page 62
    # See also: FUNCSPEC p109
    FIELD_BR_TYPE = {
        0x0: "BRANCH FALSE",
        0x1: "BRANCH TRUE",
        0x2: "PUSH (BRANCH ADDRESS)",
        0x3: "UNCONDITIONAL BRANCH",
        0x4: "CALL FALSE",
        0x5: "CALL TRUE",
        0x6: "CONTINUE",
        0x7: "UNCONDITIONAL CALL",
        0x8: "RETURN TRUE",
        0x9: "RETURN FALSE",
        0xa: "UNCONDITIONAL RETURN",
        0xb: "CASE FALSE",
        0xc: "DISPATCH TRUE",
        0xd: "DISPATCH FALSE",
        0xe: "DISPATCH",
        0xf: "UNCONDITIONAL CASE_CALL",
    }

    FIELD_COND_SEL = {
        # Ref: R1000_SCHEMATIC_VAP.PDF p44
        0x00: "VAL.ALU_ZERO(late)",
        0x01: "VAL.ALU_NONZERO(late)",
        0x02: "VAL.ALU_A_LT_OR_LE_B(late)",
        0x03: "VAL.spare",
        0x04: "VAL.LOOP_COUNTER_ZERO(early)",
        0x05: "VAL.spare",
        0x06: "VAL.ALU_NONZERO(late)",
        0x07: "VAL.ALU_32_CO(late)",
        0x08: "VAL.ALU_CARRY(late)",
        0x09: "VAL.ALU_OVERFLOW(late)",
        0x0a: "VAL.ALU_LT_ZERO(late)",
        0x0b: "VAL.ALU_LE_ZERO(late)",
        0x0c: "VAL.SIGN_BITS_EQUAL(med_late)",
        0x0f: "VAL.PREVIOUS(early)",
        0x10: "VAL.ALU_32_ZERO(late)",
        0x11: "VAL.ALU_40_ZERO(late)",
        0x12: "VAL.ALU_MIDDLE_ZERO(late)",
        0x13: "VAL.Q_BIT(early)",
        0x14: "VAL.false",
        0x15: "VAL.M_BIT(early)",
        0x16: "VAL.TRUE(early)",
        0x17: "VAL.FALSE(early)",

        # Ref: R1000_SCHEMATIC_TYP.PDF p40
        0x18: "TYP.ALU_ZERO(late)",
        0x19: "TYP.ALU_NONZERO(late)",
        0x1a: "TYP.ALU_A_GT_OR_GE_B(late)",
        0x1b: "TYP.spare",
        0x1c: "TYP.LOOP_COUNTER_ZERO(early)",
        0x1d: "TYP.spare",
        0x1e: "TYP.ALU_ZERO(late, combo)",
        0x1f: "TYP.ALU_32_CARRY_OUT(late)",
        0x20: "TYP.ALU_CARRY(late)",
        0x21: "TYP.ALU_OVERFLOW(late)",
        0x22: "TYP.ALU_LT_ZERO(late)",
        0x23: "TYP.ALU_LE_ZERO(late)",
        0x24: "TYP.SIGN_BITS_EQUAL(med_late)",
        0x25: "TYP.FALSE (early)",
        0x26: "TYP.TRUE (early)",
        0x27: "TYP.PREVIOUS (early)",
        0x28: "TYP.OF_KIND_MATCH (med_late)",
        0x29: "TYP.CLASS_A_EQ_LIT (med_late)",
        0x2a: "TYP.CLASS_B_EQ_LIT (med_late)",
        0x2b: "TYP.CLASS_A_EQ_B (med_late)",
        0x2c: "TYP.CLASS_A_B_EQ_LIT (med_late)",
        0x2d: "TYP.PRIVACY_A_OP_PASS (med_late)",
        0x2e: "TYP.PRIVACY_B_OP_PASS (med_late)",
        0x2f: "TYP.PRIVACY_BIN_EQ_PASS (med_late)",
        0x30: "TYP.PRIVACY_BIN_OP_PASS (med_late)",
        0x31: "TYP.PRIVACY_NAMES_EQ (med_late)",
        0x32: "TYP.PRIVACY_PATHS_EQ (med_late)",
        0x33: "TYP.PRIVACY_STRUCTURE (med_late)",
        0x34: "TYP.PASS_PRIVACY_BIT (early)",
        0x35: "TYP.D_BUS_BIT_32 (med_late)",
        0x36: "TYP.D_BUS_BIT_33 (med_late)",
        0x37: "TYP.D_BUS_BIT_34 (med_late)",
        0x38: "TYP.D_BUS_BIT_35 (med_late)",
        0x39: "TYP.D_BUS_BIT_36 (med_late)",
        0x3a: "TYP.D_BUS_BIT_33_34_OR_36 (med_late)",
        0x3b: "TYP.pull_up",
        0x3c: "TYP.pull_up",
        0x3d: "TYP.pull_up",
        0x3e: "TYP.pull_up",
        0x3f: "TYP.D_BUS_BIT_21 (med_late)",

        # FUNCSPEC p135
        # More in /home/phk/Proj/R1kMicrocode/r1k_ucode_explain.py
        0x40: "RESTARTABLE - macro_restartable (E)",
        0x41: "REST_PC_DEC - restartable_@(PC-1) (E)",
        0x42: "IMPORT.COND~ - valid_lex(loop_counter) (E)",
        0x43: "LEX_VLD.COND~ - loop_counter_zero (E)",
        0x44: "TOS_VLD.COND~ - TOS_LATCH_valid (L)",
        0x45: "SAVED_LATCHED - saved_latched_cond (E)",
        0x46: "LATCHED_COND - previously_latched_cond (E)",
        0x47: "STACK_SIZE_0 - #_entries_in_stack_zero (E)",
        0x48: "M_UNDERFLOW~ - ME_CSA_underflow (L)",
        0x49: "M_OVERFLOW~ - ME_CSA_overflow (L)",
        0x4a: "M_RES_REF~ - ME_resolve_ref (L)",
        0x4b: "M_TOS_INVLD~ - ME_TOS_opt_error (L)",
        0x4c: "M_BRK_CLASS~ - ME_dispatch (L)",
        0x4d: "M_IBUFF_MT~ - ME_break_class (L)",
        0x4e: "{unused seq pg54}",
        0x4f: "DISP_COND0 - ME_field_number_error (L)",

        # Ref: R1000_SCHEMATIC_SEQ p60 - SEQ.COND2
        0x50: "E_MACRO_EVNT~0 - SEQ.E_MACRO_EVENT~0",
        0x51: "E_MACRO_EVNT~2 - SEQ.E_MACRO_EVENT~2",
        0x52: "E_MACRO_EVNT~3 - SEQ.E_MACRO_EVENT~3",
        0x53: "E_MACRO_EVNT~5 - SEQ.E_MACRO_EVENT~5",
        0x54: "E_MACRO_EVNT~6 - SEQ.E_MACRO_EVENT~6",
        0x55: "E_MACRO_PEND - SEQ.E_MACRO_PEND",
        0x56: "LATCHED_COND - SEQ.LATCHED_COND",
        0x57: "FIELD_NUM_ERR - SEQ.FIELD_NUM_ERR",

        # Ref: R1000_SCHEMATIC_FIU.PDF p60
        0x60: "FIU.MEM_EXCEPTION~",
        0x61: "FIU.PHYSICAL_LAST~",
        0x62: "FIU.WRITE_LAST",
        0x63: "CSA_HIT",
        0x64: "OFFSET_REGISTER_????",
        0x65: "CROSS_WORD_FIELD~",
        0x66: "NEAR_TOP_OF_PAGE",
        0x67: "REFRESH_MACRO_EVENT",
        0x68: "CONTROL_ADDRESS_OUT_OF_RANGE",
        0x69: "SCAVENGER_HIT~",
        0x6a: "PAGE_CROSSING~",
        0x6b: "CACHE_MISS~",
        0x6c: "INCOMPLETE_MEMORY_CYCLE",
        0x6d: "MAR_MODIFIED",
        0x6e: "INCOMPLETE_MEMORY_CYCLE_FOR_PAGE_CROSSING",
        0x6f: "MAR_WORD_EQUAL_ZERO~",
        0x70: "IOC.70_pullup",
        0x71: "IOC.71_pullup",
        0x72: "IOC.72_pullup",
        0x73: "IOC.73_pullup",
        0x74: "IOC.74_pullup",
        0x75: "IOC.75_pullup",
        0x76: "IOC.76_pullup",
        0x77: "IOC.77_pullup",
        0x78: "IOC.MULTIBIT_ERROR",
        0x79: "IOC.PFR",
        0x7a: "IOC.CHECKBIT_ERROR~",
        0x7b: "IOC.REQUEST_EMPTY~",
        0x7c: "IOC.IOADDR.OVERFLOW",
        0x7d: "IOC.IOC_XFER.PERR~",
        0x7e: "IOC.RESPONSE_EMPTY~",
        0x7f: "IOC.7f_pullup",

    }

    # SEQ page 77
    FIELD_INT_READS = {
        0: "TYP VAL BUS",
        1: "CURRENT MACRO INSTRUCTION",
        2: "DECODING MACRO INSTRUCTION",
        3: "TOP OF THE MICRO STACK",
        4: "SAVE OFFSET",
        5: "RESOLVE RAM",
        6: "CONTROL TOP",
        7: "CONTROL PRED",
    }

    # From printout at the end of SEQ
    FIELD_RANDOM = {
        0x01: "HALT",
        0x10: "LOAD_TOS",
        0x11: "LOAD_RESOLVE_NAME",
        0x12: "LOAD_RESOLVE_OFFSET",
        0x13: "LOAD_CURRENT_LEX",
        0x14: "LOAD_CURRENT(_NAME)",
        0x15: "LOAD_SAVE_OFFSET",
        0x16: "LOAD_CONTROL_PRED_FIU",
        0x17: "LOAD_CONTROL_PRED",
        0x18: "LOAD_CONTROL_TOP_FIU",
        0x19: "LOAD_CONTROL_TOP",
        0x1a: "LOAD_NAME_OFFSET",	# or "LOAD_RESOLVE" ?
        0x1f: "LOAD_TOS_AND_SAVE",
        0x20: "LOAD_RPC",
        0x23: "LOAD_MPC_OFFSET_ONLY",
        0x25: "INC_MACRO_PC",
        0x27: "DEC_MACRO_PC",
        0x28: "LOAD_MPC_NAME_ONLY",
        0x2d: "INC_MACRO_PC",
        0x2f: "CHECK_EXIT_AND_HALT",
        0x30: "LOAD_MPC_RANDOM_WORD",
        0x31: "CHECK_EXIT",
        0x40: "CLEAR_LEX",
        0x41: "SET_LEX",
        0x44: "CLEAR_GREATER_THAN_LEX",
        0x47: "CLEAR_ALL_LEX",
        0x48: "CONDITIONAL_NOP",
        0x50: "LOAD_BREAK_MASK",
        0x51: "LOAD_CUR_INSTR",
        0x52: "LOAD_IBUFF",
        0x60: "PUSH_STACK",
        0x61: "POP_STACK",
        0x62: "CLEAR_STACK",
        0x63: "NOT_RESTARTABLE",
        0x64: "RESTARTABLE_AT_PC",
        0x65: "RESTARTABLE_AT_PC_DEC",
        0x66: "ENABLE_FIELD_CHECK",
        0x67: "LATE_ABORT",
        0x69: "ENABLE_FIELD_CHECH_AND_HALT",
        0x401: "CONDITIONAL_LOAD_MPC",
        0x41d: "READ_MPC_AND_DEC",
        0x42d: "READ_MPC_AND_INC",
        0x435: "CONDITIONAL_INC_MPC",
        0x439: "CONDITIONAL_DEC_MPC",
    }

class SeqDecoder(ScanChain):
    '''
	Sequencer DECODER scan chain

	See also: https://datamuseum.dk/bits/30000958
    '''
    BITSPEC = DPROC1[0xda0:0xe31]

    BITSPEC = DPROC1[0xe83:0xecc]
    DIAG_D0 = [
        "UADR.DEC/0",
        "UADR.DEC/1",
        "UADR.DEC/4",
        "UADR.DEC/5",
        "UADR.DEC/7",
        "UADR.DEC/8",
        "UADR.DEC/10",
        "UADR.DEC/11",
    ]
    DIAG_D1 = [
        "UADR.DEC/2",
        "UADR.DEC/3",
        "UADR.DEC/6",
        "UADR.DEC/9",
        "UADR.DEC/12",
        "DECODER.PARITY",
        "USES_TOS.DEC",
        "IBUFF_FILL.DEC",
    ]
    DIAG_D2 = [
        "BAND_SELECT",
        "SPARE1",
        "SPARE0",
        "CSA_VALID.DEC/0",
        "CSA_VALID.DEC/1",
        "CSA_VALID.DEC/2",
        "CSA_FREE.DEC/0",
        "CSA_FREE.DEC/1",
    ]
    DIAG_D3 = [
        "SPARE2",
        "MEM_STRT.DEC/0",
        "MEM_STRT.DEC/1",
        "MEM_STRT.DEC/2",
        "CUR_CLASS/0",
        "CUR_CLASS/1",
        "CUR_CLASS/2",
        "CUR_CLASS/3",
    ]
    DIAG_D4 = None
    DIAG_D5 = None
    DIAG_D6 = None
    DIAG_D7 = None

    # SEQ Schematic 12
    FIELD_MEM_STRT_DEC = {
        0: "CONTROL READ, AT CONTROL PRED",
        1: "CONTROL READ, AT LEX LEVEL DELTA",
        2: "CONTROL READ, AT (INNER - PARAMS)",
        3: "TYPE READ, AT TOS PLUS FIELD NUMBER",
        4: "MEMORY NOT STARTED",
        5: "PROGRAM READ, AT MACRO PC PLUS OFFSET",
        6: "CONTROL READ, AT VALUE_ITEM.NAME PLUS FIELD NUMBER",
        7: "TYPE READ, AT TOS TYPE LINK",
    }

class SeqMisc(ScanChain):
    '''
	Sequencer MISCELLANEOUS scan chain

	See also: https://datamuseum.dk/bits/30000958
    '''
    BITSPEC = DPROC1[0xda0:0xe31]

    BITSPEC = DPROC1[0xed5:0xf66]
    DIAG_D0 = None
    DIAG_D1 = None
    DIAG_D2 = None
    DIAG_D3 = None
    DIAG_D4 = [
        # RESTRG
        "RESTARTABLE",
        "RESTRG.SIM",
        "REST_PC_DEC",
        "L_REST_PC_DEC",
        # TSVLD
        "TOS_VLD.STATE",
        "TSVLD.SIM0",
        "DISP_TIME.D",        # XXX: schem has .B
        "TSVLD.SPARE1",
        # PAREG0
        "PERR0~",
        "PERR1~",
        "PERR2~",
        "PERR3~",
        # LTCHRG
        "L_LATCHED_COND",
        "LAST_COND_LATE",
        "LAST_COMM_LATCH",
        "E_OR_ML_COND",
    ]
    DIAG_D5 = [
        # UADR
        "CUR_UADR.P0",
        "CUR_UADR.P1",
        "CUR_UADR/0",
        "CUR_UADR/1",
        "CUR_UADR/2",
        "CUR_UADR/3",
        "CUR_UADR/4",
        "CUR_UADR/5",
        "CUR_UADR/6",
        "CUR_UADR/7",
        "CUR_UADR/8",
        "CUR_UADR/9",
        "CUR_UADR/10",
        "CUR_UADR/11",
        "CUR_UADR/12",
        "CUR_UADR/13",
    ]
    DIAG_D6 = [
        # UEVNT
        "PERR4~",
        "FIELD_ERROR~",
        "CHK_SYS.UE~",
        "CHK_EXIT.UE~",
        "PAGE_X.UE~",
        "TOS1_OP.UE~",
        "TOS_OP.UE~",
        "BIN_OP.UE~",
        "BIN_EQ.UE~",
        "CLASS.UE~",
        "XFER_CP.UE~",
        "NEW_STS.UE~",
        "NEW_PAK.UE~",
        "BKPT.UE~",
        "ECC.UE~",
        "MEM_EXP.UE~",
    ]
    DIAG_D7 = [
        # BHREG0
        "BR_TYPE.BH0",
        "BR_TYPE.BH1",
        "BR_TYPE.BH3",
        "DISP_TIME",
        # BHREG0
        "HINT_DISP.LAST~",
        "DISPACH.LAST~",
        "HINT_LAST~",
        "HINT_T.LAST",
        # MEVNT0
        "REFRESH.ME~",
        "SPARE0.ME~",
        "STATUS.ME~",
        "PACKET.ME~",
        # MEVNT1
        "SPARE1.ME~",
        "SL_TIME.ME~",
        "GP_TIME.ME~",
        "STOP_MACH.ME~",
    ]

class TypUir(ScanChain):
    '''
	Type UIR scan chain

    '''
    BITSPEC = DPROC1[0x812:0x85b]
    DIAG_D0 = [
        "A/0",
        "A/1",
        "A/2",
        "A/3",
        "A/4",
        "A/5",
        "B/0",
        "B/1",
    ]
    DIAG_D1 = [
        "B/2",
        "B/3",
        "B/4",
        "B/5",
        "FRAME/0",
        "FRAME/1",
        "FRAME/2",
        "FRAME/3",
    ]
    DIAG_D2 = [
        "FRAME/4",
        "CLIT/0",
        "CLIT/1",
        "PARITY",
        "RAND/0",
        "RAND/1",
        "RAND/2",
        "RAND/3",
    ]
    DIAG_D3 = [
        "C/0",
        "C/1",
        "C/2",
        "C/3",
        "C/4",
        "C/5",
        "PRIV_CHEK/0",
        "PRIV_CHEK/1",
    ]
    DIAG_D4 = [
        "PRIV_CHEK/2",
        "CMUX_SEL",
        "ALU_FUNC/0",
        "ALU_FUNC/1",
        "ALU_FUNC/2",
        "ALU_FUNC/3",
        "ALU_FUNC/4",
        "C_SOURCE",
    ]
    DIAG_D5 = [
	"MAR_CNTL/0",
	"MAR_CNTL/1",
	"MAR_CNTL/2",
	"MAR_CNTL/3",
	"CSA_CNTL/0",
	"CSA_CNTL/1",
	"CSA_CNTL/2",
    ]
    DIAG_D6 = [
        "NVE/0",
        "NVE/1",
        "NVE/2",
        "NVE/3",
        "D6.4",
        "D6.5",
        "INV_LAST~",
        "PD_CYCLE1~",
    ]
    DIAG_D7 = [ "D7.0", "D7.1", "D7.2", "D7.3", "D7.4", "D7.5", "D7.6", "D7.7"]

class MemDreg(ScanChain):
    '''
	MEM32 DREG scan chain, (must be subclassed)

    '''

    def __init__(self):
        for bit in range(8):
            i = []
            for j in range(bit*8, bit*8+8):
                i.append("TYPB/%d" % j)
            for j in range(bit*8, bit*8+8):
                i.append("VALB/%d" % j)
            if bit == 7:
                for j in range(bit*8, bit*8+8):
                    i.append("VAL_P/%d" % (j & 7))
            else:
                for j in range(bit*8, bit*8+8):
                    i.append("D%d/%d" % (bit, j & 7))
            setattr(self, "DIAG_D%d" % bit, i)
        super().__init__()

class MemDregValPar(MemDreg):
    '''
	MEM32 DREG scan chain, but only VAL+VAL_PAR
    '''

    BITSPEC = DPROC2[0xa8c:0xb65]

class MemDregFull(MemDreg):
    '''
	MEM32 DREG scan chain
    '''

    BITSPEC = DPROC2[0x8da:0x9b3]


def test():
    ''' Trivial test function '''
    seq_uir = SeqUir()
    for i in seq_uir.explain(bytes.fromhex("05 a5 04 38 00 62")):
        print(i)

if __name__ == "__main__":
    test()
