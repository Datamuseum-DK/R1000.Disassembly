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
   PASCAL unwrangling
   ==================
'''

from pyreveng import code, data

class BadPascalSyntax(Exception):
    ''' Not a well-formed PASCAL syntax '''

class BadPascalFunction(Exception):
    ''' Not a well-formed PASCAL function '''

class PascalType():
    ''' A PASCAL data type '''

    def __init__(self, tdesc, width, dbg = None):
        self.tdesc = tdesc
        self.width = width
        self.dbg = dbg

    def __repr__(self):
        return "<PTYP " + self.tdesc + "|%d>" % self.width

PREDEF_TYPES = {
    "char": PascalType("char", 1),
    "Bool": PascalType("Bool", 1),
    "Byte": PascalType("Byte", 1),
    "Word": PascalType("Word", 2),
    "integer": PascalType("integer", 4),
    "Long": PascalType("Long", 4),
    "Pointer": PascalType("Pointer", 4),
    "Quad": PascalType("Quad", 8),
    "String": PascalType("String", 4, "String"),
    "File": PascalType("File", 4, "Dirent"),
    "B": PascalType("B", 1),
    "W": PascalType("W", 2),
    "L": PascalType("L", 4),
    "Q": PascalType("Q", 8),
}


class PascalStackEntity():
    ''' ... '''

    def __init__(self, name, ptyp, var=False, mod=False):
        self.name = name
        self.ptyp = ptyp
        self.var = var
        self.mod = mod
        self.offset = 0

    def __repr__(self):
        txt = "<PSE " + self.name
        txt += " " + str(self.ptyp)
        txt += " " + str(self.var)
        txt += " /@0x%x" % self.offset
        txt += ">"
        return txt

    def put_on_stack(self, offset):
        ''' allocate on stack '''
        self.offset = offset
        if self.var:
            return offset + 4
        return offset + (self.ptyp.width + 1) & ~1

class PascalDecl():
    ''' A PASCAL function or procedure declaration '''

    def __init__(self, decl):
        self.decl = decl
        self.stack = []

        tmp = decl.split('(', 1)
        self.name = tmp.pop(0).strip()
        if ' ' in self.name:
            raise BadPascalSyntax("SP in name")
        if not tmp:
            raise BadPascalSyntax("no '(' in name")
        tmp = tmp[0].split(')', 1)
        self.argstring = tmp.pop(0).strip()
        if tmp and ':' in tmp[0]:
            tmp = tmp[0].split(":", 1)
            if tmp[0].strip() != "":
                raise BadPascalSyntax("SP after colon")
            self.retval = PREDEF_TYPES[tmp[1].strip()]
            self.stack.append(PascalStackEntity("RETURN", self.retval, True))
        else:
            self.retval = None

        if self.argstring and self.argstring != "void":
            for argatom in self.argstring.split(";"):
                tmp = argatom.split(":")
                if len(tmp) != 2:
                    raise BadPascalSyntax("BAD ARG", argatom, "IN", self.decl)
                argtype = PREDEF_TYPES[tmp[1].strip()]
                for argname in tmp[0].split(","):
                    tmp2 = argname.split()
                    if len(tmp2) == 2 and tmp2[0] == "VAR":
                        self.stack.append(PascalStackEntity(tmp2[1], argtype, var=True))
                    elif len(tmp2) == 2 and tmp2[0] == "MOD":
                        self.stack.append(PascalStackEntity(tmp2[1], argtype, mod=True))
                    else:
                        assert len(tmp2) == 1
                        self.stack.append(PascalStackEntity(tmp2[0], argtype))

        offset = 0
        for sentry in self.stack[::-1]:
            offset = sentry.put_on_stack(offset)

    def stack_map(self):
        ''' Yield a stack-map for the implementing function '''
        off = 8
        yield "Stack:"
        for sentry in self.stack:
            txt = "    "
            txt += "A6+0x%-3x" % (off + sentry.offset)
            if sentry.var:
                txt += "VAR "
            else:
                txt += "    "
            txt += " %s : " % sentry.name
            txt += sentry.ptyp.tdesc
            yield txt

class PascalFunction():

    def __init__(self, cx, lo, proto=None):
        self.cx = cx
        self.lo = lo
        if not proto:
            proto = "PF%x()" % lo
        self.proto = proto

        self.ins = []
        nxt = self.lo
        had_switch = False
        while True:
            i = list(self.cx.m.find(lo = nxt))
            if len(i) != 1:
                # print(hex(nxt), i, '#' * 20)
                raise BadPascalFunction
            i = i[0]
            assert i.lo == nxt
            self.ins.append(i)
            if had_switch and isinstance(i, data.Data):
                pass
            elif not isinstance(i, code.Code) or i.lang != cx:
                # print(hex(i.lo), i.render(), '=' * 20)
                raise BadPascalFunction
            else:
                had_switch = i.mne == "SWITCH"
                if i.mne == "RTS":
                    break
            nxt = i.hi
        self.hi = self.ins[-1].hi

        try:
            self.pd = PascalDecl(proto)
        except BadPascalSyntax as e:
            print(proto, e)
            self.pd = None

        cx.m.set_label(lo, proto)
        cx.m.set_block_comment(lo,
            "Pascal Function 0x%x-0x%x" % (self.lo, self.hi)
        )
        cx.m.set_block_comment(lo, " ")
        cx.m.set_block_comment(lo, proto)
        cx.m.set_block_comment(lo, " ")
        if self.pd:
            for i in self.pd.stack_map():
                cx.m.set_block_comment(lo, i)
        

def main():
    ''' ... '''
    pd = PascalDecl("DiProc?Something(diproc_addr: Byte) : Byte")
    for i in pd.stack_map():
        print(i)

if __name__ == "__main__":
    main()
