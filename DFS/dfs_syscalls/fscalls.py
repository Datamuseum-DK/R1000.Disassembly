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

DfsFsCall(0x1020e, "KC07_Read_Console_Char(VAR chr : char)")
DfsFsCall(0x10224, "KC12_Sleep(dur : Long)")
DfsFsCall(0x1022a, "KC15_DiagBus(a : Word; b : Long) : Byte")
DfsFsCall(0x10238, "KC1C_ProtCopy(src : Pointer; dst : Pointer; len : Word")
DfsFsCall(0x1023a, "KC1D_BusCopy(src : Pointer; sfc : Word; dst : Pointer; dfc : Word; len : Word")
DfsFsCall(0x10280, "?start_program")
DfsFsCall(0x10284, "?string_lit2something")
DfsFsCall(0x1028c, "?muls_d3_d4")        # ref: FS.0 0x107ea
DfsFsCall(0x10290, "?mulu_d3_d4")        # ref: FS.0 0x107f4
DfsFsCall(0x10294, "?divs_d3_d4")              # ref: FS.0 0x1080a
DfsFsCall(0x10298, "?divu_d3_d4")              # ref: FS.0 0x10816
DfsFsCall(0x1029c, "Malloc1(length : Long) : Pointer")
DfsFsCall(0x102a0, "Malloc2(VAR dst : Pointer; length : Word)")
DfsFsCall(0x102a4, "Free1(a : Pointer; b : Long)")
DfsFsCall(0x102a8, "Free2(a : Pointer; b : Long)")
DfsFsCall(0x102b8, "NewString() : Pointer")
DfsFsCall(0x102bc, "FreeString(a : Pointer)")
DfsFsCall(0x102c0, "AppendChar(MOD b : String; a : char)")
DfsFsCall(0x102c4, "?fill_str(WORD, WORD, PTR)")
DfsFsCall(0x102c8, "StringEqual(a, b : String) : Byte")
DfsFsCall(0x102cc, "StringDup(a : String) : String")
DfsFsCall(0x102d0, "StringCat2(a, b : String) : String")
DfsFsCall(0x102d4, "StringCat3(a, b, c : String) : String")
DfsFsCall(0x102d8, "StringCat4(a, b, c, d : String) : String")
DfsFsCall(0x102dc, "StringCat5(a, b, c, d, e : String) : String")
DfsFsCall(0x102e0, "StringCat6(a, b, c, d, e, f : String) : String")
DfsFsCall(0x102e4, "Long2String(a : Long) : String")
DfsFsCall(0x102ec, "String2Long(src : String; VAR status : Bool; VAR retval : Long)")
DfsFsCall(0x102f0, "ToUpper(a : String) : String")
DfsFsCall(0x102f4, "RightPad(a : String; b : Long) : String")
DfsFsCall(0x102f8, "LeftPad(a : String; b : Long) : String")
DfsFsCall(0x102fc, "FS_102fc(a : String; b : String; c : L")
DfsFsCall(0x10304, "TimeStamp() : Long")
DfsFsCall(0x10308, "TimeToText()")
DfsFsCall(0x10310, "ConvertTimestamp(a, b, c : L)")
DfsFsCall(0x10314, "Add(a, b : Quad) : Quad")
DfsFsCall(0x10318, "Subtract(a, b : Quad) : Quad")
DfsFsCall(0x1031c, "Multiply(a, b : Quad) : Quad")
DfsFsCall(0x10320, "Divide(a, b : Quad) : Quad")
DfsFsCall(0x10324, "IsGreater(a, b : Quad) : Bool")
DfsFsCall(0x10328, "IsSmaller(a, b : Quad) : Bool")
DfsFsCall(0x1032c, "IsEqual(a, b : Quad) : Bool")
DfsFsCall(0x10330, "BitAnd(a, b : Quad) : Quad")
DfsFsCall(0x10334, "BitOr(a, b : Quad) : Quad")
DfsFsCall(0x10338, "BitNot(a : Quad) : Quad")
DfsFsCall(0x1033c, "Negate(a : Quad) : Quad")
DfsFsCall(0x10340, "BitXor(a, b : Quad) : Quad")
DfsFsCall(0x10344, "BitShift(a : Quad ; howmuch : integer) : Quad")
DfsFsCall(0x10348, "?BitField_something_()")
DfsFsCall(0x10350, "Quad2Long(a : Quad) : Long")
DfsFsCall(0x10354, "Long2Quad(a : Long) : Quad")
DfsFsCall(0x10358, "Modulus(a, b : Quad) : Quad")
DfsFsCall(0x1035c, "Quad2String(a : Quad; radix : Long ) : String")
DfsFsCall(0x10360, "?StringToInt64()")
DfsFsCall(0x10364, "MovStringTail(Base, Len, Ptr, Delta)")
DfsFsCall(0x10368, "Lba2Chs(lba : W; VAR cyl : W ; VAR hd_sec : W)")
DfsFsCall(0x1036c, "RW_Sectors(oper : B; lba : Word; cnt : L; ptr : Pointer; VAR status : B)")
DfsFsCall(0x10370, "ReadWords(lba : W; offset : W; ptr : L; nwords : W; VAR status : B)")
DfsFsCall(0x10374, "WriteWords(lba : W; offset : W; ptr : L; nwords : W; VAR status : B)")
DfsFsCall(0x1037c, "FS1037c(MOD a : File)")
DfsFsCall(0x10380, "OpenFile(name : String; a : W; b: B; c : L; VAR status : B; VAR file : File)")
DfsFsCall(0x10384, "ReadFile(y : L; w : W; x : W; a : W; b: B; c : L; d : L)")
DfsFsCall(0x10388, "WriteFile(z : L; y : W; x : W; a : W; b: B; c: L; d: L)")
DfsFsCall(0x1038c, "CloseFile(a : L; VAR status : B; VAR file : File)")
DfsFsCall(0x10390, "WriteFreeList(void)")
DfsFsCall(0x10394, "MountDisk(drive : Word ; VAR status : Byte)")
DfsFsCall(0x103a0, "FsErrMsgStr(&String, Byte)")
DfsFsCall(0x103a4, "Open_ERROR_LOG(void)")
DfsFsCall(0x103ac, "Write_200f0(a : Byte)")
DfsFsCall(0x103b0, "PushProgram(S, S, B, &L)")
DfsFsCall(0x103b4, "WriteProgToSwapFile(prog: String; args: String)")
DfsFsCall(0x103b8, "PopProgram(Byte, String)", dead=True)
DfsFsCall(0x103c4, "GetArgv() : String")
DfsFsCall(0x103cc, "GetPushLevel() : Long")
DfsFsCall(0x103d0, "WriteConsoleChar(chr : char)")
DfsFsCall(0x103d4, "ReadChar(VAR chr : char)")
DfsFsCall(0x103d8, "WriteConsoleString(str : String)")
DfsFsCall(0x103dc, "WriteConsoleCrLf(void)")
DfsFsCall(0x103e0, "WriteConsoleStringCrLf(str : String)")
DfsFsCall(0x103e4, "AskConsoleString(prompt : String) : String")
DfsFsCall(0x103e8, "AskOnConsoleInt(prompt: String) : Long")
DfsFsCall(0x103ec, "AskOnConsoleIntRange(prompt: String; low : Long; High : Long) : Long")
DfsFsCall(0x103f0, "AskOnConsoleYesNo(prompt : String; default : Bool) : Bool")
DfsFsCall(0x103f4, "SetConsoleConfig(a : Long)")
DfsFsCall(0x103f8, "GetConsoleConfig() : Long")
DfsFsCall(0x1043c, "FileReadLine(file : File; VAR a : String; VAR b : Byte)")
DfsFsCall(0x1044c, "FS_1044C(&, L, &)")
DfsFsCall(0x10450, "FS_10450(&, &)")
DfsFsCall(0x10454, "Glob(input : String; pattern : String): Bool")
DfsFsCall(0x10458, "DirFirst(MOD c : Bool; a : String; VAR b : File)")
DfsFsCall(0x1045c, "DirNext(MOD a : Bool; VAR b : File)")
DfsFsCall(0x10460, "ExpLoad(a : String; b: Pointer)")
DfsFsCall(0x10466, "ExpInputParam(exp : Pointer; ptr : Pointer; len : L)")
DfsFsCall(0x1046c, "ExpInputFlag(exp : Pointer; val : Word)")
DfsFsCall(0x10472, "ExpOutputParam(exp : Pointer; b : Pointer; c : L; d : L)")
DfsFsCall(0x10478, "ExpOutputFlag(exp : Pointer; VAR status : Bool)")
DfsFsCall(0x1047e, "ExpXmit(adr : Byte; b : Pointer)")
DfsFsCall(0x10484, "DiProcPing(adr : Byte; VAR status : Byte; VAR b80 : Bool; VAR b40 : Bool)")
DfsFsCall(0x1048a, "DiProcCmd(board : Byte; cmd : Byte)")
DfsFsCall(0x10490, "ExpUpload(adr: Byte; ptr: Pointer; VAR status : Byte)")
DfsFsCall(0x10496, "ExpClose(exp : Pointer)")        # ref: FS.0 0x18f4e
DfsFsCall(0x1049c, "BoardName(address : B) : String") 
DfsFsCall(0x104a2, "ExpStatus2Text(status.B, &String)")
DfsFsCall(0x104ba, "ExpRun(a: Bool; adr: Byte; b: Pointer)")
DfsFsCall(0x104c0, "HasBoard(diproc_addr: Byte) : Byte")
DfsFsCall(0x104c6, "FS104c6(a : Byte) : Bool")
DfsFsCall(0x104cc, "FS104cc() : Byte")
DfsFsCall(0x104d2, "SetExpInitDone(a : Byte)")
DfsFsCall(0x104d8, "ExpInit(a : Long)")
DfsFsCall(0x104f0, "SwapBytes(src : Pointer; dst : Pointer; words : Word)")
DfsFsCall(0x104f6, "CopyBytes(src : Pointer; dst : Pointer; bytes : Word)")
DfsFsCall(0x10526, "FSCALL_10526() : Bool")
DfsFsCall(0x10538, "1c222=0x1fc00(void)")
DfsFsCall(0x1054a, "FS1054a(L, L, B, L, L, B)")
DfsFsCall(0x1054a, "FS1054a(L, L, B, L, L, B)")

class Fs10568(DfsFsCall):
    ''' Run an experiment with parameters on stack ? '''

    # See FS_0.M200 @ 0x1a0fc
    param_tbl = {
        0x0: [1],
        0x1: [2],
        0x2: [3],
        0x3: [4],
        0x4: [5],
        0x5: [6],
        0x6: [7],
        0x7: [8],
        0x8: [],
        0x9: [8, 8],
        0xa: [1, 4, 4],
        0xb: [1, 4, 3, 1],
        0xc: [8, 8, 1, 2],
        0xd: [8, 1],
        0xe: [2, 2, 1, 1, 3],
        0xf: [2, 1, 1, 1],
    }

    def __init__(self):
        super().__init__(0x10568, "Run_Experiment()")

    def flow_check(self, asp, ins):
        if hasattr(ins, "fixed_10568"):
            return
        ins.flow_out = []
        ins.flow_R()
        ptr = ins.hi

        data.Const(asp, ptr, ptr + 2, "0x%04x", asp.bu16, 2)
        asp.set_line_comment(ptr, "Stack-delta")
        ptr += 2

        y = data.Txt(asp, ptr, pfx=1, label=False)
        ptr = y.hi

        self.expname = y.txt

        data.Const(asp, ptr, ptr + 1)
        ptr += 1

        data.Const(asp, ptr, ptr + 1)
        asp.set_line_comment(ptr, "DIPROC address")
        ptr += 1

        data.Const(asp, ptr, ptr + 1)
        noutarg = asp[ptr]
        asp.set_line_comment(ptr, "Output Parameters")
        ptr += 1

        data.Const(asp, ptr, ptr + 1)
        ninarg = asp[ptr]
        asp.set_line_comment(ptr, "Input Parameters")
        ptr += 1

        arglist = []

        for i in range(ninarg):
            z = data.Const(asp, ptr, ptr + 1)
            plist = self.param_tbl[asp[ptr]]
            if not plist:
                asp.set_line_comment(ptr, "In arg flag")
                arglist.append("&w")
            else:
                arg = "Sw_" + "_".join("%d" % j for j in plist)
                arglist.append(arg)
                asp.set_line_comment(ptr, "In arg " + str(plist))
            ptr += 1

        for i in range(noutarg):
            z = data.Const(asp, ptr, ptr + 1)
            plist = self.param_tbl[asp[ptr]]
            if not plist:
                asp.set_line_comment(ptr, "Out arg flag")
                arglist.append("&Fr")
            else:
                arg = "&Sr_" + "_".join("%d" % j for j in plist)
                arglist.append(arg)
                asp.set_line_comment(ptr, "Out arg " + str(plist))
            ptr += 1

        lbl = "exp_" + y.txt + "(" + ", ".join(arglist)
        asp.set_label(ins.lo, lbl + ")")

        if ptr & 1 and not asp[ptr]:
            z = data.Const(asp, ptr, ptr + 1)
            z.typ = ".PAD"
        ins.fixed_10568 = True

Fs10568()

DfsFsCall(0x1056e, "?open_config")               # ref: BOOTINFO.M200
DfsFsCall(0x1057a, "Read_HARDWARE.M200_CONFIG(a : Pointer; VAR status : Bool)")
DfsFsCall(0x10580, "Write_HARDWARE.M200_CONFIG(?)")
DfsFsCall(0x10592, "ReadConfig(where : Long) : Word")
DfsFsCall(0x105a4, "Read_fc0c() : Word")
DfsFsCall(0x105aa, "Read_fc00() : Byte")
DfsFsCall(0x105b0, "FifoInit(void)")
DfsFsCall(0x105b6, "R1000_Reset_L(void)")
DfsFsCall(0x105bc, "R1000_Reset_H(void)")
DfsFsCall(0x105c2, "Or_fc0c_80(void)")
DfsFsCall(0x105c8, "And_fc0c_7f(void)")
DfsFsCall(0x105ce, "ReadKeySwitch() : Bool")
DfsFsCall(0x105d4, "Update_fc0c(new : Byte)")
DfsFsCall(0x105da, "Set_fc01(a : Byte)")
DfsFsCall(0x105e0, "Get_fc01() : Byte")
DfsFsCall(0x105e6, "Set_fc04_to_01(void)")
DfsFsCall(0x105ec, "Get_fc05() : Byte")
DfsFsCall(0x105f2, "Get_fc02() : Word")
DfsFsCall(0x105f8, "Is_fc07_one() : Bool")
DfsFsCall(0x105fe, "Is_fc07_two() : Bool")
DfsFsCall(0x10604, "Is_fc07_three() : Bool")
DfsFsCall(0x1060a, "Is_fc07_four() : Bool")
DfsFsCall(0x10610, "Is_fc07_one_or_three() : Bool")
DfsFsCall(0x10616, "Is_fc07_two_or_four() : Bool")

_fs = 0
