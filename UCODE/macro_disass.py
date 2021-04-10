'''
   Enlist PyReveng3 to disassemble a macro instruction
'''

from pyreveng import mem
import pyreveng.cpu.r1000 as r1000

CACHE_FILE = "_pyreveng3_cache.txt"
pyreveng3_cache = {}

def read_cache():
    ''' Read the cache file if there is one '''
    try:
        fi = open(CACHE_FILE)
    except FileNotFoundError:
        return
    for i in fi:
        j = i.split('\x01')
        pyreveng3_cache[int(j[0], 16)] = j[1]
    fi.close()

def add_to_cache(ins, txt):
    ''' Add entry to cache file '''
    fo = open(CACHE_FILE, "a")
    fo.write("0x%x" % ins + '\x01' + txt + '\n')
    fo.close()

def disassemble(ins):
    ''' Disassemble a macro instruction to a text-string '''
    if not pyreveng3_cache:
        read_cache()
    i = pyreveng3_cache.get(ins)
    if i:
        return i
    ram = mem.WordMem(0, 0x10, bits=16)
    ram[0] = ins
    ram[1] = 2
    ram[2] = 0
    ram[3] = 0
    cpu = r1000.r1000()
    cpu.m = ram
    cpu.disass(0)
    for i in ram:
        j = i.render()
        add_to_cache(ins, j)
        return j
    return "PyReveng3 could not disassemble 0x%04x" % ins
