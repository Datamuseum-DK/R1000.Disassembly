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
        return

    def decode(self, data):
        ''' Return dictionary with symbolic chain state '''
        signals = {}
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
                val = (data[octet] >> (7-bitpos)) & 1
                #print("QQQ", bit, row, sig, octet, bitpos, val)
                if '/' in sig:
                    sig, pos = sig.split('/')
                    oval = signals.setdefault(sig, dict())
                    pos = int(pos)
                    oval[pos] = val
                else:
                    signals[sig] = val
        for sig, val in signals.items():
            if isinstance(val, dict):
                #print("WWW", sig, val)
                newval = 0
                for i in range(64):
                    j = val.get(i)
                    if j is None:
                        break
                    newval += newval + j
                    #print("BB", i, j, "0x%x" % newval)
                signals[sig] = newval
        return signals

    def explain(self, data):
        ''' Yield text strings explaining chain state '''
        for sig, val in sorted(self.decode(data).items()):
            fld = getattr(self, "FIELD_" + sig.replace(".", "_"), None)
            if fld and val in fld:
                yield sig + " = 0x%x = " % val + fld[val]
            elif val > 1:
                if sig[-1] == '~':
                    # XXX: This is absurd...
                    inv = bin(val).replace('0', '_').replace('1', '0').replace('_', '1')
                    yield sig + " = 0x%x" % val + " = ~0x%x" % int(inv[2:], 2)
                else:
                    yield sig + " = 0x%x" % val
            elif sig[-1] == "~" and val == 0:
                yield sig + " " + str(val)
            elif sig[-1] != "~" and val == 1:
                yield sig + " " + str(val)

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
        # FUNCSPEC p135
        0x40: "macro_restartable (E)",
        0x41: "restartable_@(PC-1) (E)",
        0x42: "valid_lex(loop_counter) (E)",
        0x43: "loop_counter_zero (E)",
        0x44: "TOS_LATCH_valid (L)",
        0x45: "saved_latched_cond (E)",
        0x46: "previously_latched_cond (E)",
        0x47: "#_entries_in_stack_zero (E)",
        0x48: "ME_CSA_underflow (L)",
        0x49: "ME_CSA_overflow (L)",
        0x4a: "ME_resolve_ref (L)",
        0x4b: "ME_TOS_opt_error (L)",
        0x4c: "ME_dispatch (L)",
        0x4d: "ME_break_class (L)",
        0x4e: "ME_ibuff_empty (L)",
        0x4f: "ME_field_number_error (L)",
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
        0x1a: "LOAD_NAME_OFFSET",	# XXX DUP
        0x1a: "LOAD_RESOLVE",	# XXX DUP
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
        0x401: "CONDITIONAL_LOAD_MPC",
        0x40: "CLEAR_LEX",
        0x41: "SET_LEX",
        0x41d: "READ_MPC_AND_DEC",
        0x42d: "READ_MPC_AND_INC",
        0x435: "CONDITIONAL_INC_MPC",
        0x439: "CONDITIONAL_DEC_MPC",
        0x44: "CLEAR_GREATER_THAN_LEX",
        0x47: "CLEAR_ALL_LEX",
        0x48: "CONDITIONAL_NOP",
        0x50: "LOAD_BREAK_MASK",
        0x51: "LOAD_CUR_INSTR",
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


def test():
    ''' Trivial test function '''
    seq_uir = SeqUir()
    for i in seq_uir.explain(bytes.fromhex("05 a5 04 38 00 62")):
        print(i)

if __name__ == "__main__":
    test()
