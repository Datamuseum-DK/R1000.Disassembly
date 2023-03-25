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

# TODO:
#   See PROGRAM_0.M200.omsi @ <MI 15666...>

import sys

from pyreveng import mem

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

        self.debug = False

        self.discovery_phase()
        self.analysis_phase()

    def discovery_phase(self):
        ''' Find the potential PASCAL functions '''
        while True:
            sofar = len(self.discovered)
            if not self.hunt_functions():
                break
            for _lo, func in sorted(self.functions.items()):
                if func.discovered:
                    continue
                if self.debug:
                    try:
                        func.analyze()
                    except Exception as err:
                        print("ERROR", err)
                else:
                    func.analyze()
            if sofar == len(self.discovered):
                break

    def analysis_phase(self):
        ''' Try to make sense of the functions we found '''
        for func in sorted(self.functions.values()):
            if not func.discovered:
                continue
            func.find_locals()

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
        for lo, func in sorted(self.functions.items()):
            file.write("-" * 80 + "\n")
            for lbl in self.cx.m.get_labels(lo):
                file.write(lbl + "\n")
            if self.debug:
                try:
                    func.render(file, self.cx)
                except Exception as err:
                    file.write("\n\nEXCEPTION: %s\n\n" % str(err))
                    print("EXCEPTION in", func, err)
            else:
                func.render(file, self.cx)

    def dot_file(self, file):
        ''' Emit dot(1) sources '''
        for _lo, func in sorted(self.functions.items()):
            func.dot_file(file)

    def hunt_functions(self):
        ''' Hunt for more yet undiscovered functions '''
        did = False
        cur_func = None
        is_switch = False
        for i in self.cx.m:
            mne = getattr(i, "mne", None)
            if not mne and is_switch:
                continue
            if not mne:
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
