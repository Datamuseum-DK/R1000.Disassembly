#!/usr/bin/env python3
#
# Copyright (c) 2023 Poul-Henning Kamp <phk@phk.freebsd.dk>
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
   OMSI PASCAL unwrangling
   =======================
'''

import sys
import os
import html
import subprocess

from pyreveng import mem, assy

from omsi import function
from omsi import function_call

class OmsiPascal():

    ''' Identify and analyse PASCAL functions '''

    def __init__(self, cx):
        self.cx = cx
        self.functions = {}
        self.discovered = set()
        self.calls = {}
        self.called_functions = {}
        self.gvars = {}
        print("MMM", hex(cx.m.lo), hex(cx.m.hi), cx.m)

        self.discovery_phase()

    def discovery_phase(self):
        ''' Find the potential PASCAL functions '''
        self.hunt_main()
        while True:
            sofar = len(self.discovered)
            if not self.hunt_functions():
                break
            for _lo, func in sorted(self.functions.items()):
                if func.discovered:
                    continue
                func.analyze()
            if sofar == len(self.discovered):
                break

    def add_call(self, popcall):
        ''' Register a function call '''
        self.calls[popcall.lo] = popcall
        func = self.called_functions.get(popcall.dst)
        if not func:
            lbls = list(self.cx.m.get_labels(popcall.dst))
            func = function_call.CalledFunction(
                popcall.dst,
                lbls[:1],
            )
            self.called_functions[popcall.dst] = func
        func.add_call(popcall)

    def discover(self, where):
        ''' More code to disassemble '''
        if where in self.discovered:
            return
        self.discovered.add(where)
        try:
            self.cx.m[where]
        except mem.MemError:
            return
        # print("OMSI Discover", where)
        self.cx.disass(where)

    def render(self, file=sys.stdout):
        ''' Render what we have found out '''
        file.write("-" * 80 + "\n")
        for gvar in sorted(self.gvars.values()):
            gvar.render(file)
        for _lo, func in sorted(self.functions.items()):
            file.write("-" * 80 + "\n")
            func.render(file, self.cx)

    def aarender(self, file, filepfx):
        ''' Render HTML for AutoArchaeologist '''
        for _lo, func in sorted(self.functions.items()):
            if not func.discovered:
                continue

            fname = filepfx + "_%05x" % func.lo
            with open(fname + ".dot", "w") as dotfile:
                func.dot_file(dotfile)
            subprocess.run(
                [
                    "dot",
                    "-Tsvg",
                    fname + ".dot",
                ],
                stdout=open(fname + ".svg", "wb"),
            )

            svgfile = os.path.basename(fname) + ".svg"
            file.write('<H4><A id="0x%05x">0x%05x</A></H4>\n' % (func.lo, func.lo))
            file.write('<a href="%s">' % svgfile)
            file.write('<img src="%s" width="200" height="200"/>\n' % svgfile)
            file.write('</a>\n')
            file.write('<br/>\n')
            file.write('<pre>\n')
            for i in func.render_iter(self.cx):
                file.write(html.escape(i) + "\n")
            file.write('</pre>\n')

    def dot_file(self, file):
        ''' Emit dot(1) sources '''
        for _lo, func in sorted(self.functions.items()):
            func.dot_file(file)

    def hunt_main(self):
        ''' Hunt the main function '''
        cur_func = None
        is_switch = False
        for ins in self.cx.m:
            mne = getattr(ins, "mne", None)
            if not mne:
                if not is_switch:
                    cur_func = None
                continue
            is_switch = ins.mne == "SWITCH"
            if mne == "LEA.L" and ins.oper[1].txt == "A7" and ins.oper[0].dst == ins.lo + 10:
                cur_func = function.OmsiFunction(self, ins.lo)
                cur_func.ismain = True
                self.functions[ins.lo] = cur_func
                cur_func.append_code_ins(ins)
            elif not cur_func:
                continue
            elif mne == "LINK.W":
                return
            elif mne != "JSR":
                cur_func.append_code_ins(ins)
            elif not isinstance(ins.oper[0], assy.Arg_dst):
                cur_func.append_code_ins(ins)
            elif ins.oper[0].dst != 0x10284:
                cur_func.append_code_ins(ins)
            else:
                cur_func.has_rts = True
                cur_func.append_code_ins(ins)
                return

    def hunt_functions(self):
        ''' Hunt for more yet undiscovered functions '''
        did = False
        cur_func = None
        is_switch = False
        for i in self.cx.m:
            mne = getattr(i, "mne", None)
            if not mne:
                if not is_switch:
                    cur_func = None
                continue
            is_switch = i.mne == "SWITCH"
            if mne == "LINK.W" and cur_func:
                cur_func = None
            if mne == "LINK.W" and i.lo not in self.functions:
                cur_func = function.OmsiFunction(self, i.lo)
                self.functions[i.lo] = cur_func
                did = True
            elif mne == "RTS" and cur_func:
                cur_func.has_rts = True
                cur_func.append_code_ins(i)
                cur_func = None
            if cur_func:
                cur_func.append_code_ins(i)
        return did
