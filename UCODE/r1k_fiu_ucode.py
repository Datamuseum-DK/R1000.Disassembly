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
   R1000 FIU microcode disassembler
   --------------------------------

   Based on FIU Schematic preamble pages, and Func_Spec ("FS")
'''

def fiu_ucode(octets):
    ''' Yield (field, value) explanation of FIU microcode word '''
    yield "offset_literal", octets[0] & 0x7f

    if octets[1] & 0x40:
        yield "fill", "zero"
    else:
        yield "fill", "sign"

    yield "length_fill_literal", octets[1] & 0x3f

    yield "len_fill_reg_ctl", ["VI[25..31],TI[36..40]", "Lit,Lit", "TI[41:46],TI[36:40]","-,-"][octets[2] >> 6] #FS
    yield "op_select", ["Extract", "Insert Last", "Insert First", "Insert"][(octets[2] >> 4) & 3] #FS
    yield "vmux_sel", ["MDR", "fill", "VI", "FIU"][(octets[2] >> 2) & 3] #FS
    yield "fill_mode_src", (octets[2] >> 1) & 1
    yield "oreg_src", ["FADR.SRC", "LIT"][octets[2] & 1] # schematics

    yield "tivi_src", {
        0: "tar,var",
        1: "tar,val",
        2: "tar,fiu",
        3: "tar,frame",
        4: "fiu,var",
        5: "fiu,val",
        6: "fiu,fiu",
        7: "fiu,frame",
        8: "type,var",
        9: "type,val",
        10: "type,fiu",
        11: "type,frame",
        12: "mar",
        13: "mar",
        14: "mar",
        15: "mar",
    }[octets[3] >> 4]

    yield "oreg", ["load", "hold"][(octets[3] >> 3) & 1]
    yield "var", ["load", "hold"][(octets[3] >> 2) & 1]
    yield "tar", ["load", "hold"][(octets[3] >> 1) & 1]
    yield "mdr", ["load", "hold"][(octets[3] >> 0) & 1]

    yield "mem_start", {
        0x00: "hold0",
        0x01: "hold1",
        0x02: "start-rd",
        0x03: "start-wr",
        0x04: "continue",
        0x05: "start_rd_if_true",
        0x06: "start_rd_if_false",
        0x07: "start_wr_if_true",
        0x08: "start_wr_if_false",
        0x09: "start_continue_if_true",
        0x0a: "start_continue_if_false",
        0x0b: "start_last_cmd",
        0x0c: "start_if_incmplt",
        0x0d: "start_physical_rd",
        0x0e: "start_physical_wr",
        0x0f: "start_physical_tag_rd",
        0x10: "start_physical_tag_wr",
        0x11: "start_tag_query",
        0x12: "start_lru_query",
        0x13: "start_available_query",
        0x14: "start_name_query",
        0x15: "setup_tag_read",
        0x16: "init_mru",
        0x17: "scavenger_write",
        0x18: "ack_refresh",
        0x19: "nop",
        0x1a: "force_miss",
        0x1b: "0x1b",
        0x1c: "0x1c",
        0x1d: "0x1d",
        0x1e: "0x1e",
        0x1f: "0x1f",
    }[(octets[4] >> 2) & 0x1f]

    yield "rdata_bus_src", ["rotator", "mdr"][(octets[4]>>1) & 1]

    yield "parity", octets[4] & 1

    yield "length_source", ["register", "literal"][(octets[5] >> 1) & 1]
    yield "offset_source", ["register", "literal"][(octets[5] >> 0) & 1]

if __name__ == "__main__":
    print("\n\t".join(str(x) for x in fiu_ucode(bytes.fromhex("00 7f c3 78 7e 03"))))
    print("\n\t".join(str(x) for x in fiu_ucode(bytes.fromhex("00 7f c3 08 7e 03"))))
    print("\n\t".join(str(x) for x in fiu_ucode(bytes.fromhex("c0 3f c3 0f 7c 03"))))
