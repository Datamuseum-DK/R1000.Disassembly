#!/bin/env python3

'''
   Structure of the DFS filesystem
   ===============================

   typedef uint16_t lba_t;

   The `superblock` is in sector four, (byteoffset 0x1000 on the disk)
   and contains:

       uint16_t		magic;		// == 0x7fed
       lba_t		freelist;
       lba_t		rank[8];
       xxx_t		unknown_at_14;	// copy of first free-list entry ?

   Each `rank` is an array of 256 sectors of 16 `dirent` slots each.

   A `dirent` slot is unused if the first byte is 0xff

   The `dirent` is 64 bytes and contains:

       char		filename[0x1e];
       uint16_t		hash;
       uint16_t		used_sectors;
       uint16_t		allocated_sectors;
       lba_t		first_sector;
       uint16_t		zero[10];
       uint16_t		time;		// seconds_since_midnight // 2
       uint16_t		date;		// ((YYYY - 1901) << 9) | (MM << 4) | DD
       uint16_t		unknown[1];	// Non-zero only on .M200 files

   Filenames can contain:

       $.0-9?A-Z[\\]_

   Lower case a-z is folded to upper case.

   The 16 bit `hash` is calculated as:

       hash = sum((n+1)*(x&0x3f)**3 for n, x in enumerate(filename)) & 0xffff

   The `hash` determines the `rank` and `bucket` the file belongs in:

       rank = hash >> 13
       bucket = (hash >> 5) & 0xff

   The first sector of a `freelist` entry contains:

       uint16_t		n_sectors;
       lba_t		next_entry;

   The last entry in the freelist has `next_entry=0`

   The freelist does not seem to be sorted.

'''

import struct

DISK1 = "/critter/R1K/DiskImages/PE_R1K_Disk0.dd"
DISK2 = "/critter/R1K/Old/R1K_Seagate/R1K_Seagate0.BIN"

class DiskAccess():

    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")

    def pread(self, lba):
        self.fd.seek(lba << 10, 0)
        return self.fd.read(1024)

class CHS():
    def __init__(self, lbl, octets):
        self.lbl = lbl
        self.cyl, self.hd, self.sect = struct.unpack(">HBB", octets[:4])
        if self.lbl.geom:
            self.lba = self.sect
            self.lba += self.hd * self.lbl.geom.sect
            self.lba += self.cyl * self.lbl.geom.hd * self.lbl.geom.sect
        else:
            self.lba = self.cyl * self.hd * self.sect
        self.lba >>= 1

    def __repr__(self):
        return "<CHS %d/%d/%d 0x%x>" % (self.cyl, self.hd, self.sect, self.lba)

class DiskLabel():

    def __init__(self, disk):
        self.disk = disk
        self.octets = disk.da.pread(2)
        self.disk.unfree[2] = self
        self.geom = None
        self.geom = CHS(self, self.octets[8:12])
        self.part = []
        j = 0xc
        for i in range(5):
            self.part.append(
                (
                    CHS(self, self.octets[j:j+4]),
                    CHS(self, self.octets[j + 4:j+8]),
                )
            )
            j += 8

        self.serial = self.octets[0x36:0x3a].decode('ascii')
        self.label = self.octets[0x65:0x85].decode('ascii')

def filename_hash(name):
    ''' The filename hash function '''
    return sum((n+1)*(x&0x3f)**3 for n, x in enumerate(name)) & 0xffff

class DirEnt():
    def __init__(self, disk, idx, octets):
        self.disk = disk
        self.idx = idx
        self.name = octets[:30].rstrip(b'\x00')
        self.filename = self.name.decode('ascii')
        self.w = struct.unpack(">" + "H"*17, octets[30:])
        for i in range(4, 14):
            assert self.w[i] == 0
        self.w = self.w[:4] + self.w[14:]
        self.hash = filename_hash(self.name)
        self.rank = self.hash >> 13
        self.bucket = 0xff & (self.hash >> 5)
        assert self.rank == self.idx[0]
        assert self.bucket == self.idx[1]
        self.used = self.w[1]
        self.allocated = self.w[2]
        self.first = self.w[3]
        for i in range(self.first, self.first+self.allocated):
            self.disk.unfree[i] = self
        self.time = self.w[4] << 1
        self.hour = self.time // 3600
        self.minute = (self.time // 60) % 60
        self.second = self.time % 60
        self.year = (self.w[5] >> 9) + 1901
        self.month = (self.w[5] >> 5) & 0xf
        self.day = self.w[5] & 0x1f

    def __repr__(self):
        txt = "<DE " + str(self.name).ljust(32)
        txt += "%02d:%02d:%02d" % (self.hour, self.minute, self.second)
        txt += " %04d-%02d-%02d" % (self.year, self.month, self.day)
        txt += " " + ",".join("0x%04x" % x for x in self.w)
        return txt + ">"

    def __lt__(self, other):
        return self.name < other.name

class DirRank():
    def __init__(self, disk, gen, lba):
        self.disk = disk
        self.gen = gen
        self.lba = lba
        self.buckets = []
        self.de = []

        for o in range(256):
            self.buckets.append([])
            i = self.disk.da.pread(lba + o)
            self.disk.unfree[lba + o] = self
            for j in range(0, len(i), 64):
                if i[j] != 0xff:
                    de = DirEnt(self.disk, (self.gen, o, j // 64), i[j:j+64])
                    self.de.append(de)
                    self.buckets[-1].append(de)

    def __iter__(self):
        yield from self.de

class FreeBlock():
    def __init__(self, disk, nbr, lba):
        self.disk = disk
        self.nbr = nbr
        self.lba = lba
        i = self.disk.da.pread(lba)
        self.length, self.next = struct.unpack(">HH", i[:4])
        for i in range(self.length):
            self.disk.unfree[lba + i] = self

    def __repr__(self):
        return "<Free#0x%x 0x%x => 0x%04x>" % (self.nbr, self.length, self.next)

class DFS():
    def __init__(self, disk):
        self.disk = disk
        self.dirranks = []
        self.free = []

        self.sblk = self.disk.da.pread(4)
        self.disk.unfree[4] = self
        for rank in range(8):
            i = struct.unpack(">H", self.sblk[rank * 2 + 4:rank * 2 + 6])
            ds = DirRank(self.disk, rank, i[0])
            self.dirranks.append(ds)
        i = struct.unpack(">H", self.sblk[0x2:0x4])
        self.free.append(FreeBlock(self.disk, 0, i[0]))
        while self.free[-1].next:
            self.free.append(FreeBlock(self.disk, self.free[-1].nbr + 1, self.free[-1].next))

    def file_read(self, filename):
        for de in self:
            if de.filename == filename:
                for bn in range(de.first, de.first + de.allocated):
                    yield self.disk.da.pread(bn)

    def __iter__(self):
        for dr in self.dirranks:
            yield from dr

class R1kDisk():

    def __init__(self, diskaccess):
        self.da = diskaccess
        self.unfree = {}
        self.lbl = DiskLabel(self)
        self.dfs = DFS(self)
        last = None
        last_start = None
        prev = 0

    def catalog(self):
        for i, j in sorted(self.unfree.items()):
            if last != j:
                if last:
                    print("%04x-%04x" % (last_start, prev), last)
                last = j
                last_start = i
            while prev < i:
                x = self.da.pread(prev)
                print("%04x UnAcct" % prev, x[:32].hex())
                prev += 1
            prev = i + 1
        if last:
            print("%04x-%04x" % (last_start, prev), last)


if __name__ == "__main__":

    import os

    BAD_ASCII = set(range(32))
    BAD_ASCII |= set(range(127, 256))
    for i in (9, 10, 12, 13, 27):
        BAD_ASCII.remove(i)

    def fix_ascii(octets):
        fz = octets.find(b'\x00')
        if fz > -1 and max(octets[fz:]):
            return octets
        hist = set(octets[:fz])
        if hist & BAD_ASCII:
            return octets
        return octets[:fz]

    print(DISK1)
    da = DiskAccess(DISK1)
    disk = R1kDisk(da)
    for de in disk.dfs:
        with open("tmp/" + de.filename, "wb") as file:
            body = b''.join(disk.dfs.file_read(de.filename))
            file.write(fix_ascii(body))
