
'''
   Take a .M200_UCODE file apart
   =============================
'''

class R1kM200UcodeFile():

    ''' A Rational 1000 .M200_UCODE file '''

    def __init__(self, source="FPTEST.M200_UCODE"):
        self.ucode = open(source, "rb").read()

    def __len__(self):
        return (len(self.ucode) - 0xa400) // 32

    def dispatch_ram_low(self):
        ''' LOAD_DISPATCH_RAMS_200.SEQ '''
        for i in range(0x6400, 0x8400, 8):
            yield self.ucode[i:i+8]

    def dispatch_ram_high(self):
        ''' LOAD_DISPATCH_RAMS_200.SEQ '''
        for i in range(0x8400, 0xa400, 8):
            yield self.ucode[i:i+8]

    def typ_regfile(self):
        ''' LOAD_REGISTER_FILE_200.TYP '''
        for a in range(0x400, 0x6400, 24):
            yield self.ucode[a:a+12]

    def val_regfile(self):
        ''' LOAD_REGISTER_FILE_200.VAL '''
        for a in range(0x400, 0x6400, 24):
            yield self.ucode[a+16:a+24] + self.ucode[a+12:a+16]

    def ioc_ucode(self):
        ''' LOAD_CONTROL_STORE_200.IOC '''
        for a in range(0xa400, len(self.ucode), 32):
            i = 0
            for c in self.ucode[a+16:a+16+8]:
                i <<= 2
                i |= c & 3
            yield bytes((i >> 8, i & 0xff))

    def val_ucode(self):
        ''' LOAD_CONTROL_STORE_200.VAL '''
        for a in range(0xa400, len(self.ucode), 32):
            yield self.ucode[a+8:a+8+8]

    def seq_ucode(self):
        ''' LOAD_CONTROL_STORE_200.SEQ '''
        for a in range(0xa400, len(self.ucode), 32):
            yield self.ucode[a+24:a+24+8]

    def typ_ucode(self):
        ''' LOAD_CONTROL_STORE_200.TYP '''
        for a in range(0xa400, len(self.ucode), 32):
            yield self.ucode[a:a+8]

    def fiu_ucode(self):
        ''' LOAD_CONTROL_STORE_200.FIU '''
        for a in range(0xa400, len(self.ucode), 32):
            # Strip out IOC bits
            yield bytes(i & 0xfc for i in self.ucode[a+16:a+16+8])
            #yield self.ucode[a+16:a+16+8]

    def fiu_ucode_raw(self):
        ''' LOAD_CONTROL_STORE_200.FIU '''
        for a in range(0xa400, len(self.ucode), 32):
            yield self.ucode[a+16:a+16+8]
