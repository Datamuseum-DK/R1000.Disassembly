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
   Load a DFS file into PyReveng3 memory
   -------------------------------------
'''

import hashlib

from pyreveng import mem
import pyreveng.toolchest.srecords as srecords


class LoadError(Exception):
    ''' ... '''


def load_m200_file(asp, load_address, octets):
    ''' Binary File Load '''

    # Strip trailing zeros, if the last thing is an RTS instruction
    i = octets.rstrip(b'\x00')
    if i[-2:] == b'Nu':
        octets = i

    memory = mem.ByteMem(load_address, load_address + len(octets))
    memory.load_data(load_address, 1, octets)
    asp.map(memory, memory.lo, memory.hi, offset=memory.lo)

    # Ident is hash of the bytes
    return hashlib.sha256(octets).hexdigest()[:16], memory.lo, memory.hi

def load_ioc_eeprom(asp, octets):
    ''' IOC EEPROM '''

    load_address = 0x80000000

    memory = mem.ByteMem(load_address, load_address + len(octets))
    memory.load_data(load_address, 1, octets[:0x2000])
    memory.load_data(load_address + 0x2000, 1, octets[0x4000:0x6000])
    memory.load_data(load_address + 0x4000, 1, octets[0x2000:0x4000])
    memory.load_data(load_address + 0x6000, 1, octets[0x6000:])
    asp.map(memory, memory.lo, memory.hi, offset=memory.lo)

    # Ident is hash of the bytes
    return hashlib.sha256(octets).hexdigest()[:16], memory.lo, memory.hi


def load_s_records(asp, octets):
    ''' S-Record Load '''

    # Strip trailing zeros and assume ASCII
    octets = octets.rstrip(b'\x00')
    octets = octets.decode("ascii")

    extra = []
    srecset = srecords.SRecordSet()
    for i in octets.split("\n"):
        try:
            srecset.from_string(i)
            j = srecset[-1]
            if j.iscomment():
                extra.append(j.octets)
        except srecords.IgnoredLine:
            extra.append(i)

    srecset.map(asp)

    # Ident is valid ranges, prefixed by their address
    ident = hashlib.sha256()
    low = 1<<32
    for i, j in srecset.sections():
        low = min(low, i)
        ident.update(("%08x" % i).encode("ascii"))
        ident.update(asp.bytearray(i, j - i))

    if extra:
        # add any comments/extras from SREC as initial block comment
        asp.set_block_comment(low, "Info from S-Records:")
        for i in extra:
            if i.strip():
                asp.set_block_comment(low, "    " + i.strip())

    low, high = srecset.range()
    return ident.hexdigest()[:16], low, high


def load_dfs_file(asp, filename):
    ''' Load a DFS file for disassembly '''
    fi = open(filename, "rb")
    b = fi.read(4)

    if b[:3] == b'\x00\x0f\x58':
        raise LoadError("Wrong file type (R1000 code segment)")

    if b == b'\x00\x07\xff\xfc':
        # IOC EEPROM, swap two middle quarters
        return load_ioc_eeprom(asp, octets=b + fi.read())

    i = {
        b'NqH\xe7': 0x54000,               # Bootblocks
        b'\x00\x00\xfc\x00': 0x0,          # KERNEL
        b'\x00\x02\x00\x00': 0x10000,      # FS
        b'\x00\x04\x00\x00': 0x20000,      # PROGRAM
    }.get(b)
    if i is not None:
        return load_m200_file(asp, load_address=i, octets=b + fi.read())

    if b[0] == 0x53 and 0x30 <= b[1] <= 0x39:
        return load_s_records(asp, b + fi.read())

    raise LoadError("Unknown magic (%s)" % b.hex())
