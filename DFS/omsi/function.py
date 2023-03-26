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
   OMSI PASCAL functions
   =======================
'''
import sys

from pyreveng import mem, assy, code, data

from omsi import pops

class LocalVar():
    ''' Local variable accessed via FP '''

    def __init__(self, offset):
        assert offset is not None
        self.offset = offset
        self.byref = []
        self.access = {}

    def __repr__(self):
        txt = "<LVAR %4d" % self.offset
        if self.byref:
            txt += " @"
        for width, val in sorted(self.access.items()):
            txt += " %d(" % width
            if len(val[0]):
                txt += "r"
            if len(val[1]):
                txt += "w"
            txt += ")"
        return txt + ">"

    def add_byref(self, ins):
        ''' Instructions which take the address '''
        self.byref.append(ins)

    def add_read(self, ins, width):
        ''' Instructions which read '''
        i = self.access.setdefault(width, [[], []])
        i[0].append(ins)

    def add_write(self, ins, width):
        ''' Instructions which write '''
        i = self.access.setdefault(width, [[], []])
        i[1].append(ins)

class OmsiFunction():
    ''' A PASCAL function '''

    def __init__(self, up, lo):
        self.up = up
        self.lo = lo
        self.body = pops.PopBody()
        self.calls = set()
        self.traps = {}
        self.discovered = False
        self.localvars = {}

    def __iter__(self):
        yield from self.body

    def __repr__(self):
        return "<OMSI function 0x%05x>" % self.lo

    def __lt__(self, other):
        return self.lo < other.lo

    def render(self, file=sys.stdout, cx=None):
        ''' Render to text '''
        file.write("OF %05x\n" % self.lo)
        for _off, val in sorted(self.localvars.items(), reverse=True):
            file.write(" " * 8 + str(val) + "\n")
        for i in self.body.render(pfx="    ", cx=cx):
            file.write(i + "\n")

    def match(self, pattern):
        for pop in self.body:
            yield from pop.match(pattern)

    def dot_file(self, file):
        ''' Produce a dot(1) input file '''
        file.write("digraph {\n")
        for i in sorted(self.body):
            file.write("P%05x [label=\"%05x" % (i.lo, i.lo))
            if i.stack_level is not None:
                file.write("\\n%d + %d" % (i.stack_level, i.stack_delta))
                stknxt = i.stack_level + i.stack_delta
                file.write(" = %d" % stknxt)
            else:
                stknxt = None
            file.write("\"]\n")
            for j in i.go_to:
                file.write("P%05x -> P%05x" % (i.lo, j.lo))
                if j.stack_level != stknxt:
                    file.write(' [color="red"]')
                file.write("\n")
        file.write("}\n")


    def append_code_ins(self, ins):
        ''' Add another M68K instruction '''
        self.body.append_ins(pops.PopMIns(ins))

    def analyze(self):
        ''' Progressively raise the level of abstraction '''

        self.find_stack_check()

        if not self.find_prologue():
            print("NO PROLOGUE", self)
            return

        for ins in self.body:
            if "TRAP" in ins.txt and ("#15" in ins.txt or "#14" in ins.txt):
                self.traps[ins.lo] = ins

        self.find_epilogue()
        self.uncache_registers()
        self.find_stackpush()
        self.find_stackpop()
        self.find_textpush()
        self.find_bailout()
        self.find_jsr()
        self.find_stack_adj()
        self.find_constant_push()

        prev = ""
        for ins in self.body:
            if ins.kind == "Naked" and "DB" in ins.txt and "A7" in prev:
                print("NB: unspotted stack loop", prev, ins.txt)
            prev = ins.txt

        self.assign_stack_delta()
        self.find_malloc_checks()
        self.find_limit_checks()
        self.find_block_moves()
        self.partition()
        self.set_stack_levels()

        self.discovered = True

        self.find_locals()
        self.find_pointer_push()
        self.find_string_lit()

    def find_stack_check(self):
        ''' Find stack overrun checks '''
        for hit in self.body.match(
            (
                ("CMPA.L", "(A5),A7",),
                ("BHI",),
                ("MOVE.W", "#0x2,CCR"),
                ("tRAPV",),
            )
        ):
            if len(hit) != 4:
                continue
            flows = list(hit[1].flow_to())
            if flows[0][1] != hit[3].hi:
                print("FT", flows)
                continue
            hit.replace(pops.PopStackCheck())

    def find_prologue(self):
        ''' Compiler generated prologues '''
        for hit in self.body.match(
            (
                ("LINK.W",),
                ("StackCheck",),
                ("ADDA.W",),
                ("MOVEM.L",),
            )
        ):
            if len(hit) < 3:
                continue
            if hit[2][1] != "A7":
                continue
            hit.replace(pops.PopPrologue())
            return True

        return False

    def find_epilogue(self):
        ''' Find Epilogue '''
        for hit in self.body.match(
            (
                ("MOVEM.L", "(A7)+",),
                ("UNLK",),
                ("RTS",),
            )
        ):
            if len(hit) == 3:
                hit.replace(pops.PopEpilogue())
                return

    def uncache_registers(self):
        ''' Values used multiple times are cached in vacant registers '''
        pop = None

        dsts = set()
        for ins in self.body:
            flow_out = getattr(ins.ins, "flow_out", [])
            for flow in flow_out:
                if flow.typ != "N":
                    dsts.add(flow.to)

        # Must follow Prologue
        idx = 1

        while idx < len(self.body):
            ins = self.body[idx]
            if ins.lo in dsts:
                break
            if "LEA.L" not in ins.txt:
                break
            reg = str(ins.ins.oper[-1])
            writes = self.body.reg_writes(reg)
            # print("UCR", writes, ins)
            if writes != 1:
                break
            if not pop:
                pop = pops.PopRegCacheLoad()
            self.body.del_ins(ins)
            pop.append_ins(ins)
        while idx < len(self.body):
            ins = self.body[idx]
            if ins.lo in dsts:
                break
            if "MOVE" not in ins.txt:
                break
            reg = str(ins.ins.oper[-1])
            if reg[0] != "D":
                break
            writes = self.body.reg_writes(reg)
            if writes != 1:
                break
            if not pop:
                pop = pops.PopRegCacheLoad()
            self.body.del_ins(ins)
            pop.append_ins(ins)

        if not pop:
            return

        self.body.insert_ins(1, pop)

        for ins in pop.ins:
            reg = str(ins.ins.oper[1])
            if reg[0] == "A":
                pat = "(" + reg + ")"
            else:
                pat = reg
            rpl = ins.ins.oper[0]
            if isinstance(rpl, assy.Arg_verbatim):
                rpl = str(rpl)
            elif isinstance(rpl, assy.Arg_dst):
                rpl = "0x%x" % rpl.dst
            else:
                print("RCL unknown arg", ins, type(rpl), rpl)
                continue
            for rins in self.body:
                if not isinstance(rins, pops.PopMIns):
                    continue
                if pat in rins.txt:
                    rins.txt = rins.txt.replace(pat, rpl)
                if reg[0] == 'A' and reg + "," in rins.txt and "MOVEA.L" in rins.txt:
                    dst = rins.txt.split(",")[-1]
                    rins.txt = "LEA.L   " + rpl + "," + dst

    def assign_stack_delta(self):
        ''' Assign stack increment/decrement to each instruction '''
        for ins in self.body:
            if "PEA.L" in ins.txt:
                ins.stack_delta = -4
            elif "-(A7)" in ins.txt:
                ins.stack_delta = - ins.stack_width()
            elif "(A7)+" in ins.txt:
                ins.stack_delta = ins.stack_width()
            elif "A7" in ins.txt:
                if "(A7)" in ins.txt:
                    pass
                elif "A7+0x" in ins.txt:
                    pass
                elif "MOVE" in ins.txt and "A7," in ins.txt:
                    pass
                elif "ADDQ.L" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = int(oper[1:], 16)
                elif "ADDA.W" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = int(oper[1:], 16)
                elif "SUBQ.L" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = -int(oper[1:], 16)
                elif "SUBA.W" in ins.txt:
                    ins.stack_adj = True
                    oper = ins.txt.split()[1].split(",")[0]
                    assert oper[0] == "#"
                    ins.stack_delta = -int(oper[1:], 16)
                else:
                    print("SD A7", ins)

    def find_stackpush(self):
        ''' Find loops which push things on stack '''
        for hit in self.body.match(
            (
                ("SUBA.W", ",A7"),
                ("MOVEA.L", "A7,"),
                ("LEA.L",),
                ("MOVEQ.L",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 6:
                continue
            src = hit[2].ins.oper[0]
            dstreg = hit[1][1]
            srcreg = hit[2][1]
            cnt = hit[0][0]
            cntreg = hit[3][1]
            fmreg = hit[4][0]
            toreg = hit[4][1]
            if hit[5].ins.flow_out[0].to != hit[4].lo:
                continue
            if cntreg != str(hit[5][0]):
                continue
            if "(" + srcreg + ")+" != fmreg:
                continue
            if "(" + dstreg + ")+" != toreg:
                continue
            if cnt[:3] != "#0x":
                continue

            cnt = int(cnt[1:], 16) * hit[4].data_width()
            blob = None
            if isinstance(src, assy.Arg_dst):
                blob = self.get_blob(src.dst, cnt)
            hit.replace(pops.PopBlob(blob=blob, width=cnt, src=hit[2][0]))

        for hit in self.body.match(
            (
                ("MOVEA.L",),
                ("MOVEQ.L",),
                ("MOVE.", "-(A7)"),
                ("DBF",),
            )
        ):
            if len(hit) < 4:
                continue
            src = hit[0].ins.oper[0]
            srcreg = hit[0][1]
            cnt = hit[1][0]
            cntreg = hit[1][1]
            fmreg = hit[2][0]
            if hit[3].ins.flow_out[0].to != hit[2].lo:
                continue
            if cntreg != hit[3][0]:
                continue
            if cnt[:3] != "#0x":
                continue
            cnt = (1 + int(cnt[1:], 16)) * hit[2].stack_width()
            print("WWW", src, srcreg, cnt, cntreg, fmreg)
            hit.replace(pops.PopBlob(width=cnt, src="(" + hit[0][0] + "-" + hex(cnt) + ")"))

        for hit in self.body.match(
            (
                ("MOVE.", "0x", "(A7)"),
            )
        ):
            if hit[0][0][:2] == "0x":
                ptr = int(hit[0][0], 16)
                width = hit[0].stack_width()
                blob = self.get_blob(ptr, width)
                pop = pops.PopBlob(blob=blob, width=width, src=ptr, push=hit[0][1] == "-(A7)")
                hit.replace(pop)

    def find_stackpop(self):
        ''' Find loops which push things on stack '''
        for hit in self.body.match(
            (
                ("MOVEQ.L",),
                ("MOVE.", "(A7)+"),
                ("DBF",),
            )
        ):
            if len(hit) < 3:
                continue
            cntreg = str(hit[0].ins.oper[1])
            if hit[2].ins.flow_out[0].to != hit[1].lo:
                continue
            if cntreg != str(hit[2].ins.oper[0]):
                continue
            pop = hit.replace(pops.PopStackPop())
            cnt = hit[0].txt.split()[1].split(",")[0]
            if cnt[:3] != "#0x":
                print("VVVpop", cnt)
                hit.render()
                return
            pop.stack_delta = int(cnt[3:], 16)
            pop.stack_delta *= hit[1].data_width()

    def get_blob(self, ptr, width):
        ''' Get a blob out of pyreveng memory '''
        retval = bytearray()
        try:
            for offset in range(width):
                retval.append(self.up.cx.m[ptr + offset])
        except mem.MemError:
            return None
        data.Txt(self.up.cx.m, ptr, ptr + width, label=False)
        return retval

    def find_textpush(self):
        ''' Find loops which push string literals on stack '''
        for hit in self.body.match(
            (
                ("LEA.L",),
                ("MOVEQ.L",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 4:
                continue
            src = hit[0].ins.oper[0]
            srcreg = str(hit[0].ins.oper[1])
            cnt = str(hit[1].ins.oper[0])
            cntreg = str(hit[1].ins.oper[1])
            fmreg = str(hit[2].ins.oper[0])
            toreg = str(hit[2].ins.oper[1])
            if hit[3].ins.flow_out[0].to != hit[2].lo:
                continue
            if cntreg != str(hit[3].ins.oper[0]):
                continue
            if "-(" + srcreg + ")" != fmreg:
                continue
            if toreg != "-(A7)":
                continue
            toreg = toreg[1:-2]
            cnt = (1 + int(cnt[1:], 16)) * hit[2].data_width()
            blob = None
            if isinstance(src, assy.Arg_dst):
                blob = self.get_blob(src.dst - cnt, cnt)
            hit.replace(pops.PopBlob(blob=blob, width=cnt, src=hit[0][0]))

    def find_bailout(self):
        ''' Find jumps out of context'''
        for hit in self.body.match(
            (
                ("MOVEA.L", "(A5+0x8),A7"),
                ("MOVE",),
                ("JMP",),
            )
        ):
            if len(hit) < 3:
                continue
            hit.replace(pops.PopBailout())

    def find_jsr(self):
        ''' Find subroutine calls '''
        for hit in self.body.match((("JSR",),)):
            flow_0 = hit[0].ins.flow_out[0]
            if isinstance(flow_0, code.Call) and flow_0.to is not None:
                dst = flow_0.to
            elif hit[0][0][:2] == "0x":
                dst = int(hit[0][0], 16)
            elif isinstance(hit[0].ins.oper[0], assy.Arg_dst):
                dst = hit[0].ins.oper[0].dst
            else:
                print("DISAPPEARING CALL", type(hit[0].ins.oper[0]))
                hit.render()
                continue
            self.up.discover(dst)
            lbls = list(self.up.cx.m.get_labels(dst))
            if lbls:
                lbls = lbls[0]
            pop = hit.replace(pops.PopCall(dst, lbls))
            self.up.add_call(pop)

    def find_malloc_checks(self):
        ''' Find malloc allocation checks '''

        for hit in self.body.match(
            (
                ("CMPA.L", ),
                ("BEQ",),
                ("TRAP", "#13",),
            )
        ):
            if len(hit) < 3:
                continue
            preg = hit[0][1]
            if hit[0][0] != "(" + preg + "-0x4)":
                continue
            flow_to = list(hit[1].flow_to())
            if flow_to[0][1] != hit[2].hi:
                continue
            hit.replace(pops.PopMallocCheck(preg))

    def find_limit_checks(self):
        ''' Find limit checks '''

        conds = ("BLS", "BLT", "BLE", "BGE", "BGT", "BHI")

        for cond in conds:
            for hit in self.body.match(
                (
                    ("CMP",),
                    (cond,),
                )
            ):
                if len(hit) < 2:
                    continue

                if hit[1].ins.flow_out[0].to in self.traps:
                    hit.replace(pops.PopLimitCheck())

        for cond in conds:
            for hit in self.body.match(
                (
                    ("SUB.L",),
                    (cond,),
                    ("TRAP",),
                )
            ):
                if len(hit) < 3:
                    continue

                if hit[1].ins.flow_out[0].to != hit[2].ins.hi:
                    continue

                if hit[2].lo not in self.traps:
                    continue

                hit.replace(pops.PopLimitCheck())


        for cond in conds:
            for hit in self.body.match(
                (
                    ("CMP",),
                    (cond,),
                    ("TRAP",),
                )
            ):
                if len(hit) < 3:
                    continue

                if hit[1].ins.flow_out[0].to != hit[2].ins.hi:
                    continue

                if hit[2].lo not in self.traps:
                    continue

                hit.replace(pops.PopLimitCheck())

        for hit in self.body.match(
            (
                ("ADDQ.W", "#0x1,"),
                ("SUBQ.W", "#0x1,"),
                ("cHK.W",),
            )
        ):
            if len(hit) < 3:
                continue
            treg = str(hit[0].ins.oper[-1])
            if treg != str(hit[1].ins.oper[-1]):
                continue
            if treg != str(hit[2].ins.oper[-1]):
                continue
            hit.replace(pops.PopLimitCheck())

        for hit in self.body.match(
            (
                ("EXTB.W", ),
                ("cHK.W",),
            )
        ):
            if len(hit) < 2:
                continue
            treg = str(hit[0].ins.oper[-1])
            if treg != str(hit[1].ins.oper[-1]):
                continue
            hit.replace(pops.PopLimitCheck())

        for hit in self.body.match(
            (
                ("cHK.W",),
            )
        ):
            if len(hit) < 1:
                continue
            hit.replace(pops.PopLimitCheck())


    def find_stack_adj(self):
        ''' Find limit checks '''

        for idx in range(len(self.body)):
            ins = self.body[idx]
            if not ",A7" in ins.txt:
                continue
            for mne, sign in (
                ("ADDQ.L", 1),
                ("SUBQ.L", -1),
                ("ADDA.W", 1),
                ("SUBA.W", -1),
            ):
                if mne not in ins.txt:
                    continue
                i = ins.txt.split()[-1].split(",")[0]
                assert i[:3] == "#0x"
                pop = pops.PopStackAdj(sign * int(i[1:], 16))
                self.body.del_ins(ins)
                pop.append_ins(ins)
                self.body.insert_ins(idx, pop)

    def find_constant_push(self):
        ''' Find constant pushes '''

        for hit in self.body.match(
            (
                ("MOVE.", "#0x", "(A7)",),
            )
        ):
            if hit[0][0][:3] != "#0x":
                continue
            val = int(hit[0][0][1:], 16)
            if hit[0][1] == "-(A7)":
                hit.replace(pops.PopConst(width=hit[0].stack_width(), val=val, push=True))
            elif hit[0][1] == "(A7)":
                hit.replace(pops.PopConst(width=hit[0].stack_width(), val=val, push=False))
            else:
                print("FCP")
                hit.render()

        for hit in self.body.match(
            (
                ("PEA.L", "0x",),
            )
        ):
            if hit[0][0][:2] != "0x":
                continue
            val = int(hit[0][0], 16)
            hit.replace(pops.PopConst(width=4, val=val, push=True))

    def find_block_moves(self):
        ''' Find block move loops '''

        def looks_good(hit):
            cntreg = hit[-3][1]
            if hit[-1][0] != cntreg:
                print("Bad BlockMove cntreg", hit[-1][0], hit[-2][1])
                hit.render()
                return False
            cnt = hit[-3][0]
            if cnt[:3] != "#0x":
                print("Bad BlockMove cnt", cnt)
                hit.render()
                return False
            cnt = int(cnt[1:], 16) * hit[-2].data_width()
            for i in (hit[-2][0], hit[-2][1]):
                if len(i) != 5 or i[:2] != "(A" or i[-2:] != ")+":
                    print("Bad BlockMove reg", i)
                    hit.render()
                    return False
            return cnt, hit[-2][0][1:3], hit[-2][1][1:3]

        for hit in self.body.match(
            (
                ("MOVE",),
                ("MOVE.",),
                ("DBF",),
            )
        ):
            if len(hit) < 3:
                continue
            i = looks_good(hit)
            if i:
                cnt, srcreg, dstreg = i
                hit.replace(pops.PopBlockMove(srcreg, dstreg, cnt))

    def partition(self):
        ''' partition into basic blocks '''

        # Collect the start-address of all basic blocks
        starts = set()
        starts.add(self.body[0].lo)
        for ins in self.body:
            if not starts and isinstance(ins, pops.PopMIns):
                starts.add(ins.lo)
            for typ, where in ins.flow_to():
                if typ not in ("C", "N",) and where is not None:
                    # print("I", ins, typ, where)
                    assert hex(where)
                    starts.add(where)
        starts.add(self.body[-1].lo)
        # print("Q", [hex(x) for x in sorted(starts)])

        # Collect (psudo-)instructions into basic blocks
        pop = None
        allpops = {}
        idx = 0
        while idx < len(self.body):
            ins = self.body[idx]
            if ins.overhead:
                allpops[ins.lo] = ins
                idx += 1
                continue
            if ins.lo in starts or not pop:
                pop = pops.Pop()
                allpops[ins.lo] = pop
                self.body.insert_ins(idx, pop)
                idx += 1
            self.body.del_ins(ins)
            pop.append_ins(ins)

        # Tie basic blocks together
        for pop in allpops.values():
            if isinstance(pop, pops.PopEpilogue):
                continue
            ins = pop[-1]
            for typ, where in ins.flow_to():
                if where is None:
                    continue
                dst = allpops.get(where)
                if dst is None:
                    print("BLIND dst (switch to trap?)", ins, typ, hex(where))
                else:
                    pop.go_to.append(dst)
                    dst.come_from.append(pop)

    def set_stack_levels(self):
        ''' Assign stack level to each basic block '''
        for ins in self.body:
            if not ins.come_from:
                ins.stack_level = 0
        for ins in self.body:
            if ins.stack_level is None:
                continue
            leave = ins.stack_level + ins.stack_delta
            for dst in ins.go_to:
                if dst.stack_level is None:
                    dst.stack_level = leave
                elif dst.stack_level != leave:
                    print("STACK SKEW", ins, leave, "->", dst, dst.stack_level)

    def find_locals(self):
        ''' Find local variables and arguments as A6+/-n arguments '''

        def offset(arg):
            if arg[:3] != '(A6' or arg[4:6] != '0x' or arg[-1:] != ')':
                return None
            return int(arg[3:-1], 16)

        for pop in self.body:
            if pop.overhead:
                continue
            for ins in pop:
                if not isinstance(ins, pops.PopMIns) or "A6" not in ins.txt:
                    continue
                if "(A6+0x" not in ins[0] and "(A6-0x" not in ins[0]:
                    continue
                src = offset(ins.get(0, ''))
                dst = offset(ins.get(1, ''))
                if src is not None and ("PEA" in ins.txt or "LEA" in ins.txt):
                    lvar = self.localvars.setdefault(src, LocalVar(src))
                    lvar.add_byref(ins)
                else:
                    width = ins.data_width()
                    if src:
                        lvar = self.localvars.setdefault(src, LocalVar(src))
                        lvar.add_read(ins, width)
                    if dst:
                        lvar = self.localvars.setdefault(dst, LocalVar(dst))
                        lvar.add_write(ins, width)

    def find_pointer_push(self):
        ''' Find pointer pushes '''

        for hit in self.match(
            (
                ("PEA.L",),
            )
        ):
            arg = hit[0][0]
            if "(A7+" in arg:
                offset = int(arg[4:-1], 16)
                hit.replace(pops.PopStackPointer(offset))
            elif "(A6" in arg:
                offset = int(arg[3:-1], 16)
                hit.replace(pops.PopFramePointer(offset, self.localvars.get(offset)))

    def find_string_lit(self):
        ''' Find string literal pushes '''
        for hit in self.match(
            (
                ("Pointer.sp",),
                ("Const",),
                ("Const",),
                ("Call",),
                ("StackAdj",),
            )
        ):
            if len(hit) < 4:
                continue
            if "StringLit" not in hit[3].lbl:
                continue
            if hit.idx == 0:
                continue
            if hit[-1].stack_delta != 8:
                item = pops.PopStackAdj(-(8 - hit[-1].stack_delta))
                item.lo = hit[-1].lo
                hit.pop.insert_ins(hit.idx + 5, item)
                hit[-1].stack_delta = 8
            sptr = hit.getstack()
            assert hit[1].val == 1
            string = sptr.getbytes(hit[0].offset, hit[2].val)
            if string:
                hit.replace(pops.PopStringLit(string.decode("ASCII")))
            else:
                print("FSL", hit[0].offset, hit[1].val, hit[2].val, sptr.render())
                print("   stack_bytes", string)
                hit.render()
                hit.replace(pops.PopStringLit())
