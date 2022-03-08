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
            fld = getattr(self, "FIELD_" + sig, None)
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
    BITSPEC = DPROC1[0xda0:0xe31]
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

    FIELD_RANDOM = {
        0x30: "LOAD_MPC_RANDOM_WORD",
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
