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
        assert ' ' not in self.name
        tmp = tmp[0].split(')', 1)
        self.argstring = tmp.pop(0).strip()
        if tmp and ':' in tmp[0]:
            tmp = tmp[0].split(":", 1)
            assert tmp[0].strip() == ""
            self.retval = PREDEF_TYPES[tmp[1].strip()]
            self.stack.append(PascalStackEntity("RETURN", self.retval, True))
        else:
            self.retval = None

        if self.argstring and self.argstring != "void":
            for argatom in self.argstring.split(";"):
                tmp = argatom.split(":")
                assert len(tmp) == 2
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

def main():
    ''' ... '''
    pd = PascalDecl("DiProc?Something(diproc_addr: Byte) : Byte")
    for i in pd.stack_map():
        print(i)

if __name__ == "__main__":
    main()
