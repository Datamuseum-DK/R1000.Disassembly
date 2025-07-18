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
    Functions explaining microcode fields
    =====================================
'''

class Explain():

    def __init__(self):
        self.uins = None
        for merge_cond in range(8):
            a = self.COND.get(0x00 | merge_cond)
            b = self.COND.get(0x18 | merge_cond)
            self.COND[0x58 | merge_cond] = "(" + a + ") nand (" + b + ")"

    def isdefault(self, uins):
        for fld in uins.fields:
            if "parity" in fld:
                continue
            v = getattr(uins, fld)
            if v is not None and v != self.defaults.get(fld):
                return False
        return True

    def ishalt(self, uins):
        for fld in uins.fields:
            if "parity" in fld:
                continue
            v = getattr(uins, fld)
            if v is not None and v != self.halt.get(fld):
                return False
        return True

    early_macro_events = {
        # R1000_SCHEMATIC_SEQ.PDF p57
        0x100: "ME_STOP_MACH",
        0x108: "ME_GP_TIME",
        0x110: "ME_SL_TIME",
        0x118: "ME_SPARE1",
        0x120: "ME_PACKET",
        0x128: "ME_STATUS",
        0x130: "ME_SPARE0",
        0x138: "ME_REFRESH",
    }

    late_macro_events = {
        # R1000_SCHEMATIC_SEQ.PDF p59
        0x140: "ML_IBUF_empty",
        0x148: "ML_break_class",
        0x150: "ML_pullup",
        0x158: "ML_TOS_INVLD",
        0x160: "ML_Resolve Reference",
        0x168: "ML_SEQ_STOP",
        0x170: "ML_CSA_Underflow",
        0x178: "ML_CSA_overflow",
    }

    micro_events = {
        # Emulator trace
        0x145: "UE_MACHINE_STARTUP",

        # R1000_SCHEMATIC_SEQ.PDF p65
        0x180: "UE_MEM_EXP",
        0x188: "UE_ECC",
        0x190: "UE_BKPT",
        0x198: "UE_CHK_EXIT",
        0x1a0: "UE_FIELD_ERROR",
        0x1a8: "UE_CLASS",
        0x1b0: "UE_BIN_EQ",
        0x1b8: "UE_BIN_OP",

        0x1c0: "UE_TOS_OP",
        0x1c8: "UE_TOSI_OP",
        0x1d0: "UE_PAGE_X",
        0x1d8: "UE_CHK_SYS",
        0x1e0: "UE_NEW_PAK",
        0x1e8: "UE_NEW_STS",
        0x1f0: "UE_XFER_CP",
        # 0x1f8: "UE pullup",
    }

    def decode(self, uins):
        self.uins = uins
        n = 0
        if self.isdefault(uins):
            yield "<default>", "", None
            return
        if self.ishalt(uins):
            yield "<halt>", "", None
            return
        for fld, fmt in uins.fields.items():
            if "parity" in fld:
                continue
            v = getattr(uins, fld)
            if v is None or v == self.defaults.get(fld):
                continue
            n += 1
            fmt = "%0" + "%dx" % ((fmt + 3) // 4)
            if fld == "seq_branch_adr":
                uins.dstadr = v
            i = getattr(self, fld, None)
            if not i:
                yield fld, fmt % v, None
            else:
                yield fld, fmt % v, i(v)
        self.uins = None
        assert n

    def decode_text(self, uins):
        for name, hexval, expl in self.decode(uins):
            if name[0] == '<':
                yield name
            else:
                yield name.ljust(20) + " " + hexval.rjust(4) + " " + str(expl)

    def defaults_text(self):
        class dummy():
            ''' ... '''
        self.uins = dummy()
        for fld, val in self.defaults.items():
            setattr(self.uins, fld, val)
        for fld, val in self.defaults.items():
            if "parity" in fld:
                continue
            fmt = "0x%x"
            i = getattr(self, fld, None)
            if not i:
                yield fld.ljust(20) + " " + (fmt % val).rjust(6)
            else:
                yield fld.ljust(20) + " " + (fmt % val).rjust(6) + " " + i(val)
        self.uins = None

    defaults_doc = {
        "typ_a_adr": 0,             # R1000_SCHEMATIC_TYP p5
        "typ_b_adr": 0,             # R1000_SCHEMATIC_TYP p5
        "typ_c_adr": 0x29,          # R1000_SCHEMATIC_TYP p5
        "typ_frame": 0x1f,          # R1000_SCHEMATIC_TYP p5
        "typ_c_lit": 0x3,           # R1000_SCHEMATIC_TYP p5
        "typ_mar_cntl": 0x0,        # R1000_SCHEMATIC_TYP p5
        "typ_csa_cntl": 0x6,        # R1000_SCHEMATIC_TYP p5
        "typ_c_mux_sel": 0x1,       # R1000_SCHEMATIC_TYP p5
        "typ_rand": 0x0,            # R1000_SCHEMATIC_TYP p5
        "typ_alu_func": 0x1f,       # R1000_SCHEMATIC_TYP p5
        "typ_priv_check": 0x7,      # R1000_SCHEMATIC_TYP p5
        "typ_c_source": 0x1,        # R1000_SCHEMATIC_TYP p5

        "val_a_adr": 0,             # R1000_SCHEMATIC_VAL p2
        "val_b_adr": 0,             # R1000_SCHEMATIC_VAL p2
        "val_c_adr": 0x29,          # R1000_SCHEMATIC_VAL p2
        "val_frame": 0x1f,          # R1000_SCHEMATIC_VAL p2
        "val_c_source": 0x1,        # R1000_SCHEMATIC_VAL p2
        "val_c_mux_sel": 0x3,       # R1000_SCHEMATIC_VAL p2
        "val_alu_func": 0x1f,       # R1000_SCHEMATIC_VAL p2
        "val_rand": 0x0,            # R1000_SCHEMATIC_VAL p2
    }

    # Most common combination
    defaults = {
        "dispatch_ignore": 0x0,
        "dispatch_ibuff_fill": 0x0,
        "dispatch_uses_tos": 0x0,
        "dispatch_mem_strt": 0x4,
        "seq_branch_adr": 0x0000,
        "seq_cond_sel": 0x46,
        "seq_latch": 0x0,
        "seq_br_type": 0x6,
        "seq_int_reads": 0x3,
        "seq_en_micro": 0x1,
        "seq_b_timing": 0x2,
        "seq_random": 0x00,
        "seq_parity": 0x0,
        "seq_lex_adr": 0x0,
        "fiu_len_fill_lit": 0x7f,
        "fiu_offs_lit": 0x00,
        "fiu_len_fill_reg_ctl": 0x3,
        "fiu_oreg_src": 0x1,
        "fiu_fill_mode_src": 0x1,
        "fiu_vmux_sel": 0x2,
        "fiu_op_sel": 0x0,
        "fiu_load_mdr": 0x0,
        "fiu_load_tar": 0x0,
        "fiu_load_var": 0x0,
        "fiu_load_oreg": 0x0,
        "fiu_tivi_src": 0x0,
        "fiu_parity": 0x0,
        "fiu_rdata_src": 0x1,
        "fiu_mem_start": 0x19,
        "fiu_length_src": 0x1,
        "fiu_offset_src": 0x1,
        "typ_b_adr": 0x00,
        "typ_a_adr": 0x00,
        "typ_frame": 0x01,
        "typ_rand": 0xf,
        "typ_parity": 0x0,
        "typ_c_lit": 0x3,
        "typ_priv_check": 0x7,
        "typ_c_adr": 0x29,
        "typ_c_source": 0x1,
        "typ_alu_func": 0x1f,
        "typ_c_mux_sel": 0x1,
        "typ_csa_cntl": 0x6,
        "typ_mar_cntl": 0x0,
        "val_b_adr": 0x00,
        "val_a_adr": 0x00,
        "val_frame": 0x01,
        "val_rand": 0x0,
        "val_parity": 0x1,
        "val_c_mux_sel": 0x3,
        "val_m_a_src": 0x3,
        "val_c_adr": 0x29,
        "val_c_source": 0x1,
        "val_alu_func": 0x1f,
        "val_m_b_src": 0x3,
        "ioc_parity": 0x1,
        "ioc_adrbs": 0x0,
        "ioc_load_wdr": 0x1,
        "ioc_fiubs": 0x3,
        "ioc_random": 0x00,
        "ioc_tvbs": 0x0,
    }

    # Padding combination

    halt = dict(defaults)
    halt["seq_en_micro"] = 0
    halt["seq_random"] = 0x1
    halt["ioc_random"] = 0x14

    #######################################################################
    # DISPATCH
    #######################################################################

    def dispatch_mem_strt(self, val):
        ''' R1000_SCHEMATIC_SEQ p18 '''
        return {
            0x0: "CONTROL READ, AT CONTROL PRED",
            0x1: "CONTROL READ, AT LEX LEVEL DELTA",
            0x2: "CONTROL READ, AT (INNER - PARAMS)",
            0x3: "TYPE READ, AT TOS PLUS FIELD NUMBER",
            0x4: "MEMORY NOT STARTED",
            0x5: "PROGRAM READ, AT MACRO PC PLUS OFFSET",
            0x6: "CONTROL READ, AT VALUE_ITEM.NAME PLUS FIELD NUMBER",
            0x7: "TYPE READ, AT TOS TYPE LINK",
        }.get(val)

    #######################################################################
    # SEQ
    #######################################################################

    def seq_random(self, val):
        ''' R1000_SCHEMATIC_SEQ p84 vs p102 '''
        return {
            0x01: "HALT",
        }.get(val, "?")

    def seq_b_timing(self, val):
        '''
           R1000_SCHEMATIC_SEQ p68
           R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p56
        '''
        return {
            0x0: "Early Condition",
            0x1: "Latch Condition",
            0x2: "Late Condition, Hint True (or unconditional branch)",
            0x3: "Late Condition, Hint False",
        }.get(val)

    def seq_br_type(self, val):
        ''' R1000_SCHEMATIC_SEQ p68 '''
        return {
            0x0: "Branch False",
            0x1: "Branch True",
            0x2: "Push (branch address)",
            0x3: "Unconditional Branch",
            0x4: "Call False",
            0x5: "Call True",
            0x6: "Continue",
            0x7: "Unconditional Call",
            0x8: "Return True",
            0x9: "Return False",
            0xa: "Unconditional Return",
            0xb: "Case False",
            0xc: "Dispatch True",
            0xd: "Dispatch False",
            0xe: "Unconditional Dispatch",
            0xf: "Unconditional Case Call",
        }.get(val)

    def seq_branch_adr(self, val):
        ''' XXX: How do we get hold of pyreveng3 labels ? '''
        return "%04x" % val

    #----------------------------------------------------------------------
    #
    # SEQ p61 conditions
    # ------------------
    #
    # S0 S1 S2 S3 S4 S5 S6
    #
    #  0  X  X  X  -  -  -  CNDMX0
    #
    #  0  0  0  0  -  -  -  COND.VAL.0
    #  0  0  0  1  -  -  -  COND.VAL.1
    #  0  0  1  0  -  -  -  COND.VAL.2
    #  0  0  1  1  -  -  -  COND.TYP.0
    #  0  1  0  0  -  -  -  COND.TYP.1
    #  0  1  0  1  -  -  -  COND.TYP.2
    #  0  1  1  0  -  -  -  COND.TYP.3
    #  0  1  1  1  -  -  -  COND.TYP.4
    #
    #  1  X  X  X  -  -  -  CNDMX1
    #
    #  1  0  0  0  -  -  -  SEQ.COND0
    #  1  0  0  1  -  -  -  SEQ.COND1
    #  1  0  1  0  -  -  -  SEQ.COND2
    #  1  0  1  1  -  -  -  COND.VAL0 & COND.TYP0
    #  1  1  0  0  -  -  -  COND.FIU0
    #  1  1  0  1  -  -  -  COND.FIU1
    #  1  1  1  0  -  -  -  COND.SYS0
    #  1  1  1  1  -  -  -  COND.SYS1
    #
    # TYP p40
    # -------
    #  1  0  1  1  X  X  X = NAND(0000XXX, 0011XXX)
    # SEQ p60 - SEQ.COND0
    # -------------------
    #  1  0  0  0  0  0  0  RESTARTABLE
    #  1  0  0  0  0  0  1  REST_PC_DEC
    #  1  0  0  0  0  1  0  IMPORT.COND~
    #  1  0  0  0  0  1  1  LEX_VLD.COND~
    #  1  0  0  0  1  0  0  TOS_VLD.COND~
    #  1  0  0  0  1  0  1  SAVED_LATCHED
    #  1  0  0  0  1  1  0  LATCHED_COND
    #  1  0  0  0  1  1  1  STACK_SIZE_0
    #
    # SEQ p60 - SEQ.COND1
    # -------------------
    #  1  0  0  1  0  0  0  M_UNDERFLOW~
    #  1  0  0  1  0  0  1  M_OVERFLOW~
    #  1  0  0  1  0  1  0  M_RES_REF~
    #  1  0  0  1  0  1  1  M_TOS_INVLD~
    #  1  0  0  1  1  0  0  M_BRK_CLASS~
    #  1  0  0  1  1  0  1  M_IBUFF_MT~
    #  1  0  0  1  1  1  0  (floating)
    #  1  0  0  1  1  1  1  DISP_COND0
    #
    # SEQ p60 - SEQ.COND2
    # -------------------
    #  1  0  1  0  0  0  0  E_MACRO_EVENT~0
    #  1  0  1  0  0  0  1  E_MACRO_EVENT~2
    #  1  0  1  0  0  1  0  E_MACRO_EVENT~3
    #  1  0  1  0  0  1  1  E_MACRO_EVENT~5
    #  1  0  1  0  1  0  0  E_MACRO_EVENT~6
    #  1  0  1  0  1  0  1  E_MACRO_PEND
    #  1  0  1  0  1  1  0  LATCHED_COND
    #  1  0  1  0  1  1  1  FIELD_NUM_ERR
    #
    # FIU p60 - F.COND.FIU0
    # ---------------------
    #  1  1  0  0  0  0  0  MEM_EXCEPTION
    #  1  1  0  0  0  0  1  PHYS_LAST
    #  1  1  0  0  0  1  0  WRITE_LAST~
    #  1  1  0  0  0  1  1  F.CSA_HIT~
    #  1  1  0  0  1  0  0  OREGOD
    #  1  1  0  0  1  0  1  XWORD.COND
    #  1  1  0  0  1  1  0  NEAR_TOP~
    #  1  1  0  0  1  1  1  F.REFRESH_MACRO~
    #
    # FIU p60 - F.COND.FIU1
    # ---------------------
    #  1  1  0  1  0  0  0  CSA_OOR
    #  1  1  0  1  0  0  1  SCAV_HIT
    #  1  1  0  1  0  1  0  PAGE_XING
    #  1  1  0  1  0  1  1  MISS
    #  1  1  0  1  1  0  0  INCMPLT_MCYC~
    #  1  1  0  1  1  0  1  MAR_MODIFIED~
    #  1  1  0  1  1  1  0  INCMPLT_MCYC~
    #  1  1  0  1  1  1  1  WORD_EQ_ZERO
    #
    # IOP p70 - I.COND.IOC0
    # ---------------------
    #  1  1  1  0  X  X  X  pullup
    #
    # IOP p70 - I.COND.IOC1
    # ---------------------
    #  1  1  1  1  0  0  0  MULTIBIT_ERROR
    #  1  1  1  1  0  0  1  PFR
    #  1  1  1  1  0  1  0  CHECKBIT_ERROR~
    #  1  1  1  1  0  1  1  REQUEST_EMPTY~
    #  1  1  1  1  1  0  0  IOADDR.OVERFLOW
    #  1  1  1  1  1  0  1  IOC_XFER.PERR~
    #  1  1  1  1  1  1  0  RESPONSE_EMPTY~
    #  1  1  1  1  1  1  1  pullup


    COND = {
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

        # Ref: R1000_HARDWARE_FUNCTIONAL_SPECIFICATION.PDF p81
        0x40: "SEQ.macro_restartable",
        0x41: "SEQ.restartable_@(PC-1)",
        0x42: "SEQ.valid_lex(loop_counter)",
        0x43: "SEQ.loop_counter_zero",
        0x44: "SEQ.TOS_LATCH_valid",
        0x45: "SEQ.saved_latched_cond",
        0x46: "SEQ.previously_latched_cond",
        0x47: "SEQ.#_entries_in_stack_zero",
        0x48: "SEQ.ME_CSA_underflow",
        0x49: "SEQ.ME_CSA_overflow",
        0x4a: "SEQ.ME_resolve_ref",
        0x4b: "SEQ.ME_TOS_opt_error",
        0x4c: "SEQ.ME_dispatch",
        0x4d: "SEQ.ME_break_class",
        0x4e: "SEQ.ME_ibuff_emptry",
        0x4f: "SEQ.uE_field_number_error",

        # Ref: R1000_SCHEMATIC_SEQ p60 - SEQ.COND2
        0x50: "SEQ.E_MACRO_EVENT~0",
        0x51: "SEQ.E_MACRO_EVENT~2",
        0x52: "SEQ.E_MACRO_EVENT~3",
        0x53: "SEQ.E_MACRO_EVENT~5",
        0x54: "SEQ.E_MACRO_EVENT~6",
        0x55: "SEQ.E_MACRO_PEND",
        0x56: "SEQ.LATCHED_COND",
        0x57: "SEQ.FIELD_NUM_ERR",

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

    def seq_cond_sel(self, val):
        return self.COND.get(val)

    def seq_int_reads(self, val):
        # R1000_SCHEMATIC_SEQ p83
        return {
            0: "TYP VAL BUS",
            1: "CURRENT MACRO INSTRUCTION",
            2: "DECODING MACRO INSTRUCTION",
            3: "TOP OF THE MICRO STACK",
            4: "SAVE OFFSET",
            5: "RESOLVE RAM",
            6: "CONTROL TOP",
            7: "CONTROL PRED",
        }.get(val)

    #######################################################################
    # FIU
    #######################################################################

    def fiu_load_oreg(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        return {
            0: "load_oreg",
            1: "hold_oreg",
        }.get(val)

    def fiu_load_var(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        return {
            0: "load_var",
            1: "hold_var",
        }.get(val)

    def fiu_load_tar(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        return {
            0: "load_tar",
            1: "hold_tar",
        }.get(val)

    def fiu_load_mdr(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        return {
            0: "load_mdr",
            1: "hold_mdr",
        }.get(val)

    def fiu_length_src(self, val):
        ''' R1000_SCHEMATIC_FIU p9 '''
        return {
            0: "length_register",
            1: "length_literal",
        }.get(val)

    def fiu_offset_src(self, val):
        ''' R1000_SCHEMATIC_FIU p9 '''
        return {
            0: "offset_register",
            1: "offset_literal",
        }.get(val)

    def fiu_rdata_src(self, val):
        ''' R1000_SCHEMATIC_FIU p9 '''
        return {
            0: "rotator",
            1: "mdr",
        }.get(val)

    def fiu_tivi_src(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        return {
            0x0: "tar_var",
            0x1: "tar_val",
            0x2: "tar_fiu",
            0x3: "tar_frame",
            0x4: "fiu_var",
            0x5: "fiu_val",
            0x6: "fiu_fiu",
            0x7: "fiu_frame",
            0x8: "type_var",
            0x9: "type_val",
            0xa: "type_fiu",
            0xb: "type_frame",
            0xc: "mar_0xc",
            0xd: "mar_0xd",
            0xe: "mar_0xe",
            0xf: "mar_0xf",
        }.get(val)

    def fiu_mem_start(self, val):
        ''' R1000_SCHEMATIC_FIU p9 '''
        return {
        0x00: "hold0",
        0x01: "hold1",
        0x02: "start-rd",
        0x03: "start-wr",
        0x04: "continue",
        0x05: "start_rd_if_true",
        0x06: "start_rd_if_false",
        0x07: "start_wr_if_true",
        0x08: "start_wr_if_false",
        0x09: "start_continue_if_true",
        0x0a: "start_continue_if_false",
        0x0b: "start_last_cmd",
        0x0c: "start_if_incmplt",
        0x0d: "start_physical_rd",
        0x0e: "start_physical_wr",
        0x0f: "start_physical_tag_rd",
        0x10: "start_physical_tag_wr",
        0x11: "start_tag_query",
        0x12: "start_lru_query",
        0x13: "start_available_query",
        0x14: "start_name_query",
        0x15: "setup_tag_read",
        0x16: "init_mru",
        0x17: "scavenger_write",
        0x18: "acknowledge_refresh",
        0x19: "nop_0x19",
        0x1a: "force_miss",
        0x1b: "reserved_0x1b",
        0x1c: "reserved_0x1c",
        0x1d: "reserved_0x1d",
        0x1e: "reserved_0x1e",
        0x1f: "reserved_0x1f",
        }.get(val)

    def fiu_len_fill_lit(self, val):
        ''' R1000_SCHEMATIC_FIU p8 '''
        if val & 0x40:
            return "zero-fill 0x%x" % (val & 0x3f)
        return "sign-fill 0x%x" % (val & 0x3f)

    def fiu_len_fill_reg_ctl(self, val):
        ''' R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p125 '''
        return {
            0x0: "Load VI (25:31)  Load TI (36)",
            0x1: "Load Literal     Load Literal",
            0x2: "Load TI (37:42)  Load TI (36)",
            0x3: "no load          no load",
        }.get(val)

    def fiu_op_sel(self, val):
        ''' R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p126 '''
        return {
            0x0: "extract",
            0x1: "insert last",
            0x2: "insert first",
            0x3: "insert",
        }.get(val)

    def fiu_oreg_src(self, val):
        ''' R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p126 '''
        return {
            0x0: "rotator output",
            0x1: "merge data register",
        }.get(val)

    def fiu_vmux_sel(self, val):
        ''' R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p127 '''
        return {
            0x0: "merge data register",
            0x1: "fill value",
            0x2: "VI",
            0x3: "FIU BUS",
        }.get(val)


    #######################################################################
    # TYP&VAL
    #######################################################################

    def typval_a_adr(self, val, frame):
        ''' R1000_SCHEMATIC_TYP p5,  R1000_SCHEMATIC_VAL p2 '''
        if val < 0x10:
            return "GP 0x%x" % val
        if val == 0x10:
            return "TOP"
        if val == 0x11:
            return "TOP + 1"
        if val == 0x12:
            return "SPARE_0x12"
        if val == 0x13:
            return "LOOP_REG"
        if val == 0x14:
            return "ZEROS"
        if val == 0x17:
            return "LOOP_COUNTER"
        if val < 0x20:
            return "TOP - %d" % (0x20 - val)
        return "(0x%x:0x%x)" % (frame, val - 0x20)

    def typval_b_adr(self, val, frame):
        ''' R1000_SCHEMATIC_TYP p5,  R1000_SCHEMATIC_VAL p2 '''
        if val == 0x14:
            return "BOT - 1"
        if val == 0x15:
            return "BOT"
        if val == 0x16:
            return "CSA/VAL_BUS"
        if val == 0x17:
            return "SPARE_0x17"
        return self.typval_a_adr(val, frame)

    def typval_c_adr(self, val, frame):
        ''' R1000_SCHEMATIC_TYP p5,  R1000_SCHEMATIC_VAL p2 '''
        ival = val ^ 0x3f
        if ival < 0x10:
            return "GP 0x%x" % ival
        if ival == 0x10:
            return "TOP"
        if ival == 0x11:
            return "TOP + 1"
        if ival == 0x12:
            return "SPARE_0x12"
        if val == 0x13:
            return "LOOP_REG"
        if ival == 0x14:
            return "BOT - 1"
        if ival == 0x15:
            return "BOT"
        if ival == 0x16:
            return "WRITE_DISABLE"
        if ival == 0x17:
            return "LOOP_COUNTER"
        if ival <= 0x20:
            return "TOP - 0x%x" % (0x20 - ival)
        return "(0x%x:0x%x)" % (frame, ival - 0x20)

    def typval_alu_func(self, val):
        return {
            0x00: "PASS_A",
            0x01: "A_PLUS_B",
            0x02: "INC_A_PLUS_B",
            0x03: "LEFT_I_A",
            0x04: "LEFT_I_A_INC",
            0x05: "DEC_A_MINUS_B",
            0x06: "A_MINUS_B",
            0x07: "INC_A",
            0x08: "PLUS_ELSE_MINUS",
            0x09: "MINUS_ELSE_PLUS",
            0x0a: "PASS_A_ELSE_PASS_B",
            0x0b: "PASS_B_ELSE_PASS_A",
            0x0c: "PASS_A_ELSE_INC_A",
            0x0d: "INC_A_ELSE_PASS_A",
            0x0e: "PASS_A_ELSE_DEC_A",
            0x0f: "DEC_A_ELSE__PASS_A",
            0x10: "NOT_A",
            0x11: "A_NAND_B",
            0x12: "NOT_A_OR_B",
            0x13: "ONES",
            0x14: "A_NOR_B",
            0x15: "NOT_B",
            0x16: "A_XNOR_B",
            0x17: "A_OR_NOT_B",
            0x18: "NOT_A_AND_B",
            0x19: "X_XOR_B",
            0x1a: "PASS_B",
            0x1b: "A_OR_B",
            0x1c: "DEC_A",
            0x1d: "A_AND_NOT_B",
            0x1e: "A_AND_B",
            0x1f: "ZEROS",
        }.get(val)

    def typ_c_source(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return {
            0: "FIU_BUS",
            1: "MUX",
        }.get(val)

    def typ_a_adr(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        if val == 0x15:
            return "SPARE_0x15"
        if val == 0x16:
            return "SPARE_0x16"
        return self.typval_a_adr(val, self.uins.typ_frame)

    def typ_b_adr(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return self.typval_b_adr(val, self.uins.typ_frame)

    def typ_c_adr(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return self.typval_c_adr(val, self.uins.typ_frame)

    def typ_mar_cntl(self, val):
        return {
            0x0: "NOP",
            0x1: "RESTORE_RDR",
            0x2: "DISABLE_DUMMY_ADR_NEXT",
            0x3: "SPARE_0x03",
            0x4: "RESTORE_MAR",
            0x5: "RESTORE_MAR_REFRESH",
            0x6: "INCREMENT_MAR",
            0x7: "INCREMENT_MAR_IF_INCOMPLETE",

            # XXX: R1000_SCHEMATIC_FIU p53 has opposite order
            0x8: "LOAD_MAR_SYSTEM",
            0x9: "LOAD_MAR_CODE",
            0xa: "LOAD_MAR_IMPORT",
            0xb: "LOAD_MAR_DATA",
            0xc: "LOAD_MAR_QUEUE",
            0xd: "LOAD_MAR_TYPE",
            0xe: "LOAD_MAR_CONTROL",
            0xf: "LOAD_MAR_RESERVED",	# For phys mem access
        }.get(val)

    def typ_csa_cntl(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return {
            0x0: "LOAD_CONTROL_TOP",
            0x1: "START_POP_DOWN",
            0x2: "PUSH_CSA",
            0x3: "POP_CSA",
            0x4: "DEC_CSA_BOTTOM",
            0x5: "INC_CSA_BOTTOM",
            0x6: "NOP",
            0x7: "FINISH_POP_DOWN",
        }.get(val)

    def typ_c_mux_sel(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return {
            0x0: "ALU",
            0x1: "WSR",  # XXX: hard to read on p2
        }.get(val)

    def typ_priv_check(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return {
            0x0: "CHECK_BINARY_EQ",
            0x1: "CHECK_BINARY_OP",
            0x2: "CHECK_A_(TOP)_UNARY_OP",
            0x3: "CHECK_A_(TOP-1)_UNARY_OP",
            0x4: "CHECK_B_(TOP)_UNARY_OP",
            0x5: "CHECK_B_(TOP-1)_UNARY_OP",
            0x6: "CLEAR_PASS_PRIVACY_BIT",
            0x7: "NOP"
        }.get(val)

    def typ_rand(self, val):
        ''' R1000_SCHEMATIC_TYP p5 '''
        return {
            0x0: "NO_OP",
            0x1: "INC_LOOP_COUNTER",
            0x2: "DEC_LOOP_COUNTER",
            0x3: "SPLIT_C_SOURCE (C_SRC HI, NON-C_SRC LO)",
            0x4: "CHECK_CLASS_A_LIT",
            0x5: "CHECK_CLASS_B_LIT",
            0x6: "CHECK_CLASS_A_??_B",
            0x7: "CHECK_CLASS_AB_LIT",
            0x8: "SPARE_0x08",
            0x9: "PASS_A_HIGH",
            0xa: "PASS_B_HIGH",
            0xb: "CARRY IN = Q BIT FROM VAL",
            0xc: "WRITE_OUTER_FRAME",
            0xd: "SET_PASS_PRIVACY_BIT",
            0xe: "CHECK_CLASS_SYSTEM_B",
            0xf: "INC_DEC_128",
        }.get(val)

    def typ_alu_func(self, val):
        return self.typval_alu_func(val)

    #######################################################################
    # VAL
    #######################################################################

    def val_a_adr(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        if val == 0x15:
            return "ZERO_COUNTER"
        if val == 0x16:
            return "PRODUCT"
        return self.typval_a_adr(val, self.uins.val_frame)

    def val_b_adr(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        return self.typval_b_adr(val, self.uins.val_frame)

    def val_c_adr(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        return self.typval_c_adr(val, self.uins.val_frame)

    def val_alu_func(self, val):
        return self.typval_alu_func(val)

    def val_m_a_src(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        return {
            0: "Bits 0…15",
            1: "Bits 16…31",
            2: "Bits 32…47",
            3: "Bits 48…63",
        }.get(val)

    def val_m_b_src(self, val):
        return self.val_m_a_src(val)

    def val_rand(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        return {
            0x0: "NO_OP",
            0x1: "INC_LOOP_COUNTER",
            0x2: "DEC_LOOP_COUNTER",
            0x3: "CONDITION_TO_FIU",
            0x4: "SPLIT_C_SOURCE (C_SRC HI, NON-C_SRC LO)",
            0x5: "COUNT_ZEROS",
            0x6: "IMMEDIATE_OP",
            0x7: "SPARE_0x7",
            0x8: "SPARE_0x8",
            0x9: "PASS_A_HIGH",
            0xa: "PASS_B_HIGH",
            0xb: "DIVIDE",
            0xc: "START_MULTIPLY",
            0xd: "PRODUCT_LEFT_16",
            0xe: "PRODUCT_LEFT_32",
            0xf: "SPARE_0xf",
        }.get(val)

    def val_c_source(self, val):
        ''' R1000_SCHEMATIC_VAL p2 '''
        return {
            0: "FIU_BUS",
            1: "MUX",
        }.get(val)

    def val_c_mux_sel(self, val):
        return {
            0: "ALU << 1",
            1: "ALU >> 16",
            2: "ALU",
            3: "WSR",  # XXX: hard to read on p2
        }.get(val)

    #######################################################################
    # IOC
    #######################################################################

    def ioc_random(self, val):
        ''' R1000_SCHEMATIC_IOC.PDF p5
            Checks out against PB010…PB013.
        '''
        return {
            0x00: "noop",
            0x01: "load transfer address",
            0x02: "spare 2",
            0x03: "spare 3",
            0x04: "write request fifo",
            0x05: "read response fifo",
            0x06: "load slice timer",
            0x07: "load delay timer",
            0x08: "read and clear rtc",
            0x09: "read timer/checkbits/errorid",
            0x0a: "clear slice event",
            0x0b: "clear delay event",
            0x0c: "enable slice timer",
            0x0d: "disable slice timer",
            0x0e: "enable delay timer",
            0x0f: "disable delay timer",
            0x10: "load checkbit register",
            0x11: "disable ecc event",
            0x12: "exit function pop below tcb event enable",
            0x13: "set cpu running",
            0x14: "clear cpu running",
            0x15: "clear transfer parity error",
            0x16: "stage data register",
            0x17: "force type bus receivers",
            0x18: "drive diagnostic checkbits",
            0x19: "ecc bench testing random",
            0x1a: "spare 1a",
            0x1b: "spare 1b",
            0x1c: "read ioc memory and increment address",
            0x1d: "read ioc memory",
            0x1e: "write ioc memory and increment address",
            0x1f: "write ioc memory",
        }.get(val)

    def ioc_adrbs(self, val):
        ''' R1000_SCHEMATIC_IOC.PDF p5 '''
        return {
            0x0: "fiu",
            0x1: "val",
            0x2: "typ",
            0x3: "seq",
        }.get(val)

    def ioc_fiubs(self, val):
        '''
            R1000_SCHEMATIC_IOC.PDF p5
            R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p127
        '''
        return {
            0x0: "fiu",
            0x1: "val",
            0x2: "typ",
            0x3: "seq",
        }.get(val)

    def ioc_tvbs(self, val):
        '''
            R1000_SCHEMATIC_IOC.PDF p5
            R1000_HARDWARE_FUNCTIONAL_SPECIFICATION p127
            R1000_Micro_Arch_SysBus.pdf p18
        '''
        return {
            0x0: "typ+val",
            0x1: "typ+fiu",
            0x2: "fiu+val",
            0x3: "fiu+fiu",
            0x4: "ioc+ioc",
            0x5: "seq+seq",
            0x6: "reserved=6",
            0x7: "reserved=7",
            0x8: "typ+mem",
            0x9: "typ+mem",
            0xa: "fiu+mem",
            0xb: "fiu+mem",
            0xc: "mem+mem+csa+dummy",
            0xd: "mem+mem+csa+dummy",
            0xe: "mem+mem+csa+dummy",
            0xf: "mem+mem+csa+dummy",	
        }.get(val)
