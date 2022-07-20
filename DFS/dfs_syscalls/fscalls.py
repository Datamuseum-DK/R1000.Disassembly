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
    DFS FS calls
    ============
'''

from pyreveng import data

from .base import DfsFsCall

DfsFsCall(0x10284, "?string_lit2something")
DfsFsCall(0x1028c, "?muls_d3_d4_to_d3")        # ref: FS.0 0x107ea
DfsFsCall(0x10290, "?mulu_d3_d4_to_d3")        # ref: FS.0 0x107f4
DfsFsCall(0x10294, "?divs_d3_d4")              # ref: FS.0 0x1080a
DfsFsCall(0x10298, "?divu_d3_d4")              # ref: FS.0 0x10816
DfsFsCall(0x1029c, "Malloc(&Void, Long)")
DfsFsCall(0x102a8, "?Free(PTR, LONG)")
DfsFsCall(0x102b8, "?NewString(&String)")
DfsFsCall(0x102bc, "FreeString(String)")
DfsFsCall(0x102c0, "AppendChar(S, C)")
DfsFsCall(0x102c4, "?fill_str(WORD, WORD, PTR)")
DfsFsCall(0x102c8, "StringEqual(&B, S, S)")
DfsFsCall(0x102cc, "StringDup(&String1, String2)")
DfsFsCall(0x102d0, "StringCat2(&String1, String2, String3)")
DfsFsCall(0x102d4, "StringCat3(&String1, String2, String3, String4)")
DfsFsCall(0x102e4, "LongInt2String(&String1, LongInt)")
DfsFsCall(0x102ec, "String2LongInt(&Byte, &LongInt, String)")
DfsFsCall(0x102f0, "ToUpper(&String1, String2)")
DfsFsCall(0x102f4, "?LeftPad(Word, String, &String)")
DfsFsCall(0x10304, "TimeStamp(&Long)")
DfsFsCall(0x10310, "ConvertTimestamp(String, &Void, &Void)")
DfsFsCall(0x10314, "Add(&Int64, Int64, Int64)")
DfsFsCall(0x10318, "Subtract(&Int64, Int64, Int64)")
DfsFsCall(0x1031c, "Multiply(&Int64, Int64, Int64)")
DfsFsCall(0x10320, "Divide(&Int64, Int64, Int64)")
DfsFsCall(0x10324, "IsGreater(Int64, Int64)")
DfsFsCall(0x10328, "IsSmaller(Int64, Int64)")
DfsFsCall(0x1032c, "IsEqual(Int64, Int64)")
DfsFsCall(0x10330, "BitAnd(&Int64, Int64, Int64)")
DfsFsCall(0x10334, "BitOr(&Int64, Int64, Int64)")
DfsFsCall(0x10338, "BitNot(&Int64, Int64)")
DfsFsCall(0x10340, "BitXor(&Int64, Int64, Int64)")
DfsFsCall(0x10344, "BitShift(&Int64, Int64, Int64)")
DfsFsCall(0x10358, "Modulus(&Int64, Int64, Int64)")
DfsFsCall(0x10364, "MovStringTail(Base, Len, Ptr, Delta)")
DfsFsCall(0x10368, "Lba2Chs(Word, &Word, &Word)")
DfsFsCall(0x1036c, "RW_Sectors(Byte, Word lba, Long nsect, Long dst, &Byte)")
DfsFsCall(0x1036c, "Disk_IO(Byte, Word lba, Long, &void, &void)")
DfsFsCall(0x10380, "OpenFile(S, W, B, W, W, &B, &DirEnt)")
DfsFsCall(0x10384, "ReadFile()")
DfsFsCall(0x10388, "WriteFile()")
DfsFsCall(0x1038c, "CloseFile()")
DfsFsCall(0x103a0, "FsErrMsgStr(&String, Byte)")
DfsFsCall(0x103b0, "PushProgram(S, S, B, &L)")
DfsFsCall(0x103b8, "PopProgram(Byte, String)", dead=True)
DfsFsCall(0x103cc, "GetPushLevel(&L)")
DfsFsCall(0x103d0, "WriteConsole(Char)")
DfsFsCall(0x103d4, "ReadChar(&char)")
DfsFsCall(0x103d8, "WriteConsole(String)")
DfsFsCall(0x103dc, "WriteConsoleCrLf(void)")
DfsFsCall(0x103e0, "WriteLineConsole(String)")
DfsFsCall(0x103e4, "AskConsoleString(&String1, String2)")
DfsFsCall(0x103e8, "?AskOnConsole()")
DfsFsCall(0x1043c, "FileReadLine(File, &String, Byte)")
DfsFsCall(0x1047e, "?exp_xmit(EXP.L,NODE.B)")
DfsFsCall(0x10472, "DiagGetOutParam(&Byte, Long, Long)")
DfsFsCall(0x10496, "?experiment_close")        # ref: FS.0 0x18f4e
DfsFsCall(0x104ba, "DiagDownload(Byte, Byte addr, &Byte)")
DfsFsCall(0x1057a, "Read_HARDWARE.M200_CONFIG(&Byte[6],&Byte[1])")
DfsFsCall(0x10592, "ReadConfig(Long, &Word)")
DfsFsCall(0x105b0, "FifoInit(void)")
DfsFsCall(0x105b6, "R1000_Reset_L(void)")
DfsFsCall(0x105bc, "R1000_Reset_H(void)")
DfsFsCall(0x105ce, "ReadKeySwitch(&Byte)")
DfsFsCall(0x10610, "Check_FC07(&Byte)")

class Fs10568(DfsFsCall):
    ''' Run an experiment with parameters on stack ? '''
    def __init__(self):
        super().__init__(0x10568, "?run_experiment()")

    def flow_check(self, asp, ins):
        if hasattr(ins, "fixed_10568"):
            return
        ins.flow_out = []
        ins.flow_R()
        ptr = ins.hi
        exp_name_len = asp[ins.hi + 2]
        data.Const(asp, ptr, ptr + 3)
        ptr += 3
        y = data.Txt(asp, ptr, ptr + exp_name_len, label=False)
        ptr += exp_name_len
        narg = asp[ptr + 2] + asp[ptr + 3]
        z = data.Const(asp, ptr, ptr + 4 + narg)
        ptr = z.hi
        lbl = "exp_" + y.txt + "("
        asp.set_label(ins.lo, lbl + ")")
        # ins.compact = True
        if ptr & 1 and not asp[ptr]:
            z = data.Const(asp, ptr, ptr + 1)
            z.typ = ".PAD"
        ins.fixed_10568 = True

Fs10568()

DfsFsCall(0x1056e, "?open_file")               # ref: BOOTINFO.M200
DfsFsCall(0x105a4, "Read_fc0c(word *)")
DfsFsCall(0x105aa, "Read_fc00(byte *)")
DfsFsCall(0x105da, "Write_fc01(byte)")
DfsFsCall(0x105e0, "Read_fc01(byte *)")
DfsFsCall(0x105e6, "Set_fc04_to_01()")

_fs = 0
