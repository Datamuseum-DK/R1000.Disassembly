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
   DFS program generic stuff
   -------------------------
'''

from pyreveng import mem, data
import pascal_pseudo_ins

import dfs_syscalls

import omsi.omsi_pascal

class CmdTable():
    ''' ... '''

    def __init__(self, cx, adr):
        self.adr = adr
        self.words = []
        print("CMD TABLE AT 0x%x" % adr)
        cx.m.set_label(adr, "COMMAND_TABLE_%x" % adr)
        cx.m.set_block_comment(adr, "COMMAND TABLE")
        while True:
            self.words.append(data.Txt(cx.m, adr, adr+10, label=False).txt.rstrip())
            if cx.m.bu32(adr) == 0x41534349:
                break
            adr += 10

def FindPushPopArg(cx, adr):
    for i in cx.m.find(adr + 0x00024f6c - 0x00024f4a):
        mne = getattr(i, "mne", None)
        if mne == "JSR":
            cx.m.set_label(i.dstadr, "Pop_Arg(?)")
    for i in cx.m.find(adr + 0x00024f86 - 0x00024f4a):
        mne = getattr(i, "mne", None)
        if mne == "JSR":
            cx.m.set_label(i.dstadr, "Push_Arg(?)")

def FindFindVar(cx, adr):
    for i in cx.m.find(adr + 0x000244de - 0x000244b4):
        mne = getattr(i, "mne", None)
        if mne != "JSR":
            continue
        cx.m.set_label(i.dstadr, "Find_Var(?)")
        j = i.dstadr + (0x00023fec - 0x00023fd0)
        if cx.m.bu16(j) == 0x26b9:
            cx.m.set_label(cx.m.bu32(j + 2), "variables")

def TryPrim(cx, adr, word):
    for n in range(2):
        item = list(cx.m.find(adr))[0]
        if item.mne == "JSR":
            cx.m.set_label(item.dstadr, "PRIM_" + word + "(?)")
            if word == "XOR":
                FindPushPopArg(cx, item.dstadr)
            if word == "KILL":
                FindFindVar(cx, item.dstadr)
            return
        adr = item.hi

def CmdTableRef(cx, item):
    # Look for "CMPI.W  #0x002a,D1"
    if cx.m.bu32(item.lo + (0x00026356 - 0x00026332)) != 0x0c41002a:
        return
    cmdtbl = cx.dfs_cmd_tables[item.dstadr]

    for i in cx.m.find(item.lo + (0x0002634c - 0x00026332)):
        if getattr(i, "mne", None) == "JSR":
            cx.m.set_label(i.dstadr, "CHECK_ARG_CNT(Int32)")

    tbl = []
    adr = item.lo + (0x00026368 - 0x00026332)
    for i in range(0x2b):
        dst = adr + cx.m.bu16(adr + 2 * i)
        TryPrim(cx, dst, cmdtbl.words[i + 1])

def flow_check(asp, ins):
    ''' Quench the "No Memory..." messages from trying to disassemble FS '''
    for f in ins.flow_out:
        syscall = dfs_syscalls.base.SYSCALLS.get(f.to)
        if syscall:
            f.to = None
            syscall.flow_check(asp, ins)

def round_0(cx):
    ''' Things to do before the disassembler is let loose '''
    pascal_pseudo_ins.add_pascal_pseudo_ins(cx)
    cx.dfs_syscalls = dfs_syscalls.DfsSysCalls()
    cx.dfs_syscalls.round_0(cx)
    cx.flow_check.append(flow_check)

    cx.dfs_cmd_tables = {}
    for adr in range(0x20000, cx.m.hi - 7):
        try:
            if cx.m[adr] != 0x21:
                continue
        except mem.MemError:
            break
        if cx.m.bu32(adr) != 0x21402324 or cx.m.bu32(adr + 4) != 0x255e262a:
            continue
        if cx.m[adr + 10] != 0x57:
            continue
        cx.dfs_cmd_tables[adr] = CmdTable(cx, adr)

def round_1(cx):
    ''' Let the disassembler loose '''

    y = data.Const(cx.m, 0x20024, 0x20025)
    cx.m.set_label(y.lo, "exp_init_done")

    y = cx.codeptr(0x20000)
    cx.m.set_line_comment(y.lo, "STACK.END")

    y = cx.codeptr(0x20004)
    cx.m.set_label(y.dst, "START")
    # XXX: should be done through flow-check
    cx.disass(y.dst + 10)
    cx.m.set_label(y.dst + 10, "MAIN")

    y = cx.codeptr(0x20008)

    y = cx.dataptr(0x2000c)

    y = cx.dataptr(0x20010)
    cx.m.set_line_comment(y.lo, "CODE.END")

    z = cx.codeptr(0x20018)
    cx.m.set_label(z.dst, "ProgramFailureHandler()")

    z = cx.codeptr(0x2001c)
    cx.m.set_label(z.dst, "ExperimentFailureHandler()")


def round_2(cx):
    ''' Spelunking in what we already found '''

def round_3(cx):
    ''' Discovery, if no specific hints were encountered '''

    cx.omsi = omsi.omsi_pascal.OmsiPascal(cx)
