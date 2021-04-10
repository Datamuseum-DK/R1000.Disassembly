#!/usr/bin/env python3

''' Machine Generated file, see r1k_ucode_codegen.p'''

class Ucode():
    ''' Machine Generated file, see r1k_ucode_codegen.p'''

    def __init__(self, adr):
        self.adr = adr
        self.dispatch_uword = None
        self.seq_uword = None
        self.fiu_uword = None
        self.typ_uword = None
        self.val_uword = None
        self.ioc_uword = None
        self.dispatch_macro_ins = None
        self.dispatch_csa_free = None
        self.dispatch_csa_valid = None
        self.dispatch_cur_class = None
        self.dispatch_ibuff_fill = None
        self.dispatch_ignore = None
        self.dispatch_macro_ins = None
        self.dispatch_mem_strt = None
        self.dispatch_parity = None
        self.dispatch_uadr = None
        self.dispatch_uses_tos = None
        self.fiu_fill_mode_src = None
        self.fiu_len_fill_lit = None
        self.fiu_len_fill_reg_ctl = None
        self.fiu_length_src = None
        self.fiu_load_mdr = None
        self.fiu_load_oreg = None
        self.fiu_load_tar = None
        self.fiu_load_var = None
        self.fiu_mem_start = None
        self.fiu_offs_lit = None
        self.fiu_offset_src = None
        self.fiu_op_sel = None
        self.fiu_oreg_src = None
        self.fiu_parity = None
        self.fiu_rdata_src = None
        self.fiu_tivi_src = None
        self.fiu_vmux_sel = None
        self.ioc_adrbs = None
        self.ioc_fiubs = None
        self.ioc_load_wdr = None
        self.ioc_parity = None
        self.ioc_random = None
        self.ioc_tvbs = None
        self.seq_b_timing = None
        self.seq_br_type = None
        self.seq_branch_adr = None
        self.seq_cond_sel = None
        self.seq_en_micro = None
        self.seq_int_reads = None
        self.seq_latch = None
        self.seq_lex_adr = None
        self.seq_parity = None
        self.seq_random = None
        self.typ_a_adr = None
        self.typ_alu_func = None
        self.typ_b_adr = None
        self.typ_c_adr = None
        self.typ_c_lit = None
        self.typ_c_mux_sel = None
        self.typ_c_source = None
        self.typ_csa_cntl = None
        self.typ_frame = None
        self.typ_mar_cntl = None
        self.typ_parity = None
        self.typ_priv_check = None
        self.typ_rand = None
        self.val_a_adr = None
        self.val_alu_func = None
        self.val_b_adr = None
        self.val_c_adr = None
        self.val_c_mux_sel = None
        self.val_c_source = None
        self.val_frame = None
        self.val_m_a_src = None
        self.val_m_b_src = None
        self.val_parity = None
        self.val_rand = None

    fields = {
        "dispatch_csa_free": 1,
        "dispatch_csa_valid": 2,
        "dispatch_cur_class": 3,
        "dispatch_ibuff_fill": 1,
        "dispatch_ignore": 1,
        "dispatch_macro_ins": 16,
        "dispatch_mem_strt": 2,
        "dispatch_parity": 1,
        "dispatch_uadr": 13,
        "dispatch_uses_tos": 1,
        "fiu_fill_mode_src": 1,
        "fiu_len_fill_lit": 6,
        "fiu_len_fill_reg_ctl": 1,
        "fiu_length_src": 1,
        "fiu_load_mdr": 1,
        "fiu_load_oreg": 1,
        "fiu_load_tar": 1,
        "fiu_load_var": 1,
        "fiu_mem_start": 4,
        "fiu_offs_lit": 6,
        "fiu_offset_src": 1,
        "fiu_op_sel": 1,
        "fiu_oreg_src": 1,
        "fiu_parity": 1,
        "fiu_rdata_src": 1,
        "fiu_tivi_src": 3,
        "fiu_vmux_sel": 1,
        "ioc_adrbs": 1,
        "ioc_fiubs": 1,
        "ioc_load_wdr": 1,
        "ioc_parity": 1,
        "ioc_random": 4,
        "ioc_tvbs": 3,
        "seq_b_timing": 1,
        "seq_br_type": 3,
        "seq_branch_adr": 13,
        "seq_cond_sel": 6,
        "seq_en_micro": 1,
        "seq_int_reads": 2,
        "seq_latch": 1,
        "seq_lex_adr": 1,
        "seq_parity": 1,
        "seq_random": 6,
        "typ_a_adr": 5,
        "typ_alu_func": 4,
        "typ_b_adr": 5,
        "typ_c_adr": 5,
        "typ_c_lit": 1,
        "typ_c_mux_sel": 1,
        "typ_c_source": 1,
        "typ_csa_cntl": 2,
        "typ_frame": 4,
        "typ_mar_cntl": 3,
        "typ_parity": 1,
        "typ_priv_check": 2,
        "typ_rand": 3,
        "val_a_adr": 5,
        "val_alu_func": 4,
        "val_b_adr": 5,
        "val_c_adr": 5,
        "val_c_mux_sel": 1,
        "val_c_source": 1,
        "val_frame": 4,
        "val_m_a_src": 1,
        "val_m_b_src": 1,
        "val_parity": 1,
        "val_rand": 3,
    }

    def __iter__(self):
        for i in self.fields:
            yield i, getattr(self, i)

    def load_dispatch_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.dispatch_uword = bytes(uword)

        a = uword[0] ^ 0x40
        self.dispatch_uadr = (a & 0x80) >> 5
        self.dispatch_ibuff_fill = (a & 0x40) >> 6
        self.dispatch_csa_free = (a & 0x20) >> 5
        self.dispatch_cur_class = (a & 0x10) >> 4
        assert not a & 0x0f

        a = uword[1]
        self.dispatch_uadr |= (a & 0x80) >> 4
        self.dispatch_uses_tos = (a & 0x40) >> 6
        self.dispatch_csa_free |= (a & 0x20) >> 4
        self.dispatch_cur_class |= (a & 0x10) >> 3
        assert not a & 0x0f

        a = uword[2]
        self.dispatch_uadr |= (a & 0x80) >> 2
        self.dispatch_parity = (a & 0x40) >> 6
        self.dispatch_csa_valid = (a & 0x20) >> 5
        self.dispatch_cur_class |= (a & 0x10) >> 2
        assert not a & 0x0f

        a = uword[3]
        self.dispatch_uadr |= (a & 0x80) >> 1
        self.dispatch_uadr |= (a & 0x40) >> 5
        self.dispatch_csa_valid |= (a & 0x20) >> 4
        self.dispatch_cur_class |= (a & 0x10) >> 1
        assert not a & 0x0f

        a = uword[4]
        self.dispatch_uadr |= (a & 0x80) << 1
        self.dispatch_uadr |= (a & 0x40) >> 2
        self.dispatch_csa_valid |= (a & 0x20) >> 3
        self.dispatch_mem_strt = (a & 0x10) >> 4
        assert not a & 0x0f

        a = uword[5]
        self.dispatch_uadr |= (a & 0x80) << 2
        self.dispatch_uadr |= (a & 0x40) << 1
        self.dispatch_mem_strt |= (a & 0x10) >> 3
        assert not a & 0x2f

        a = uword[6]
        self.dispatch_uadr |= (a & 0x80) << 5
        self.dispatch_uadr |= (a & 0x40) << 4
        self.dispatch_mem_strt |= (a & 0x10) >> 2
        assert not a & 0x2f

        a = uword[7]
        self.dispatch_uadr |= (a & 0x80) << 6
        self.dispatch_uadr |= (a & 0x40) << 5
        self.dispatch_ignore = (a & 0x20) >> 5
        assert not a & 0x1f

    def load_seq_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.seq_uword = bytes(uword)

        a = uword[0] ^ 0x40
        self.seq_branch_adr = (a & 0x80)
        self.seq_cond_sel = (a & 0x40) >> 5
        self.seq_latch = (a & 0x20) >> 5
        self.seq_int_reads = (a & 0x10) >> 4
        self.seq_random = (a & 0x04) << 1
        assert not a & 0x0b

        a = uword[1] ^ 0x40
        self.seq_branch_adr |= (a & 0x80) >> 1
        self.seq_cond_sel |= (a & 0x40) >> 6
        self.seq_br_type = (a & 0x20) >> 3
        self.seq_int_reads |= (a & 0x10) >> 3
        self.seq_random |= (a & 0x04) << 2
        assert not a & 0x0b

        a = uword[2]
        self.seq_branch_adr |= (a & 0x80) >> 2
        self.seq_branch_adr |= (a & 0x40) << 7
        self.seq_br_type |= (a & 0x20) >> 2
        self.seq_br_type |= (a & 0x10) >> 4
        self.seq_random |= (a & 0x04) >> 1
        assert not a & 0x0b

        a = uword[3] ^ 0x20
        self.seq_branch_adr |= (a & 0x80) >> 3
        self.seq_branch_adr |= (a & 0x40) << 6
        self.seq_cond_sel |= (a & 0x20) << 1
        self.seq_br_type |= (a & 0x10) >> 3
        self.seq_random |= (a & 0x04)
        assert not a & 0x0b

        a = uword[4] ^ 0x20
        self.seq_branch_adr |= (a & 0x80) >> 4
        self.seq_branch_adr |= (a & 0x40) << 5
        self.seq_cond_sel |= (a & 0x20)
        self.seq_en_micro = (a & 0x10) >> 4
        self.seq_random |= (a & 0x04) >> 2
        assert not a & 0x0b

        a = uword[5] ^ 0x20
        self.seq_branch_adr |= (a & 0x80) >> 5
        self.seq_branch_adr |= (a & 0x40) << 4
        self.seq_cond_sel |= (a & 0x20) >> 3
        self.seq_b_timing = (a & 0x10) >> 4
        self.seq_parity = (a & 0x04) >> 2
        assert not a & 0x0b

        a = uword[6] ^ 0x20
        self.seq_branch_adr |= (a & 0x80) >> 6
        self.seq_branch_adr |= (a & 0x40) << 3
        self.seq_cond_sel |= (a & 0x20) >> 2
        self.seq_b_timing |= (a & 0x10) >> 3
        self.seq_lex_adr = (a & 0x04) >> 2
        self.seq_random |= (a & 0x02) << 4
        assert not a & 0x09

        a = uword[7] ^ 0x20
        self.seq_branch_adr |= (a & 0x80) >> 7
        self.seq_branch_adr |= (a & 0x40) << 2
        self.seq_cond_sel |= (a & 0x20) >> 1
        self.seq_int_reads |= (a & 0x10) >> 2
        self.seq_lex_adr |= (a & 0x04) >> 1
        self.seq_random |= (a & 0x02) << 5
        assert not a & 0x09

    def load_fiu_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.fiu_uword = bytes(uword)

        a = uword[0]
        self.fiu_len_fill_lit = (a & 0x80) >> 1
        self.fiu_len_fill_reg_ctl = (a & 0x40) >> 6
        self.fiu_load_mdr = (a & 0x10) >> 4
        self.fiu_parity = (a & 0x08) >> 3
        assert not a & 0x27

        a = uword[1] ^ 0x10
        self.fiu_offs_lit = (a & 0x80) >> 7
        self.fiu_len_fill_reg_ctl |= (a & 0x40) >> 5
        self.fiu_load_tar = (a & 0x10) >> 4
        assert not a & 0x2f

        a = uword[2] ^ 0x10
        self.fiu_offs_lit |= (a & 0x80) >> 6
        self.fiu_len_fill_lit |= (a & 0x40) >> 6
        self.fiu_oreg_src = (a & 0x20) >> 5
        self.fiu_load_var = (a & 0x10) >> 4
        self.fiu_rdata_src = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[3] ^ 0x10
        self.fiu_offs_lit |= (a & 0x80) >> 5
        self.fiu_len_fill_lit |= (a & 0x40) >> 5
        self.fiu_fill_mode_src = (a & 0x20) >> 5
        self.fiu_load_oreg = (a & 0x10) >> 4
        self.fiu_mem_start = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[4]
        self.fiu_offs_lit |= (a & 0x80) >> 4
        self.fiu_len_fill_lit |= (a & 0x40) >> 4
        self.fiu_vmux_sel = (a & 0x20) >> 5
        self.fiu_tivi_src = (a & 0x10) >> 4
        self.fiu_mem_start |= (a & 0x08) >> 2
        assert not a & 0x07

        a = uword[5]
        self.fiu_offs_lit |= (a & 0x80) >> 3
        self.fiu_len_fill_lit |= (a & 0x40) >> 3
        self.fiu_vmux_sel |= (a & 0x20) >> 4
        self.fiu_tivi_src |= (a & 0x10) >> 3
        self.fiu_mem_start |= (a & 0x08) >> 1
        assert not a & 0x07

        a = uword[6]
        self.fiu_offs_lit |= (a & 0x80) >> 2
        self.fiu_len_fill_lit |= (a & 0x40) >> 2
        self.fiu_op_sel = (a & 0x20) >> 5
        self.fiu_tivi_src |= (a & 0x10) >> 2
        self.fiu_mem_start |= (a & 0x08)
        self.fiu_length_src = (a & 0x04) >> 2
        assert not a & 0x03

        a = uword[7]
        self.fiu_offs_lit |= (a & 0x80) >> 1
        self.fiu_len_fill_lit |= (a & 0x40) >> 1
        self.fiu_op_sel |= (a & 0x20) >> 4
        self.fiu_tivi_src |= (a & 0x10) >> 1
        self.fiu_mem_start |= (a & 0x08) << 1
        self.fiu_offset_src = (a & 0x04) >> 2
        assert not a & 0x03

    def load_typ_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.typ_uword = bytes(uword)

        a = uword[0] ^ 0xc0
        self.typ_b_adr = (a & 0x80) >> 3
        self.typ_frame = (a & 0x40) >> 5
        self.typ_rand = (a & 0x20) >> 5
        self.typ_priv_check = (a & 0x10) >> 3
        self.typ_c_source = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[1] ^ 0xc0
        self.typ_b_adr |= (a & 0x80) >> 2
        self.typ_frame |= (a & 0x40) >> 4
        self.typ_rand |= (a & 0x20) >> 4
        self.typ_priv_check |= (a & 0x10) >> 2
        self.typ_alu_func = (a & 0x08) >> 3
        self.typ_csa_cntl = (a & 0x04) >> 2
        assert not a & 0x03

        a = uword[2] ^ 0xc0
        self.typ_a_adr = (a & 0x80) >> 7
        self.typ_frame |= (a & 0x40) >> 3
        self.typ_rand |= (a & 0x20) >> 3
        self.typ_c_adr = (a & 0x10) >> 4
        self.typ_alu_func |= (a & 0x08) >> 2
        self.typ_csa_cntl |= (a & 0x04) >> 1
        assert not a & 0x03

        a = uword[3] ^ 0xc0
        self.typ_a_adr |= (a & 0x80) >> 6
        self.typ_frame |= (a & 0x40) >> 2
        self.typ_rand |= (a & 0x20) >> 2
        self.typ_c_adr |= (a & 0x10) >> 3
        self.typ_alu_func |= (a & 0x08) >> 1
        self.typ_csa_cntl |= (a & 0x04)
        assert not a & 0x03

        a = uword[4] ^ 0xc0
        self.typ_a_adr |= (a & 0x80) >> 5
        self.typ_b_adr |= (a & 0x40) >> 6
        self.typ_parity = (a & 0x20) >> 5
        self.typ_c_adr |= (a & 0x10) >> 2
        self.typ_alu_func |= (a & 0x08)
        self.typ_mar_cntl = (a & 0x04) >> 2
        assert not a & 0x03

        a = uword[5] ^ 0xe0
        self.typ_a_adr |= (a & 0x80) >> 4
        self.typ_b_adr |= (a & 0x40) >> 5
        self.typ_c_lit = (a & 0x20) >> 5
        self.typ_c_adr |= (a & 0x10) >> 1
        self.typ_alu_func |= (a & 0x08) << 1
        self.typ_mar_cntl |= (a & 0x04) >> 1
        assert not a & 0x03

        a = uword[6] ^ 0xe0
        self.typ_a_adr |= (a & 0x80) >> 3
        self.typ_b_adr |= (a & 0x40) >> 4
        self.typ_c_lit |= (a & 0x20) >> 4
        self.typ_c_adr |= (a & 0x10)
        self.typ_c_mux_sel = (a & 0x08) >> 3
        self.typ_mar_cntl |= (a & 0x04)
        assert not a & 0x03

        a = uword[7] ^ 0xc0
        self.typ_a_adr |= (a & 0x80) >> 2
        self.typ_b_adr |= (a & 0x40) >> 3
        self.typ_frame |= (a & 0x20) >> 5
        self.typ_c_adr |= (a & 0x10) << 1
        self.typ_priv_check |= (a & 0x08) >> 3
        self.typ_mar_cntl |= (a & 0x04) << 1
        assert not a & 0x03

    def load_val_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.val_uword = bytes(uword)

        a = uword[0] ^ 0xe0
        self.val_b_adr = (a & 0x80) >> 3
        self.val_frame = (a & 0x40) >> 5
        self.val_rand = (a & 0x20) >> 5
        self.val_m_a_src = (a & 0x10) >> 4
        self.val_c_source = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[1] ^ 0xe0
        self.val_b_adr |= (a & 0x80) >> 2
        self.val_frame |= (a & 0x40) >> 4
        self.val_rand |= (a & 0x20) >> 4
        self.val_m_a_src |= (a & 0x10) >> 3
        self.val_alu_func = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[2] ^ 0xe0
        self.val_a_adr = (a & 0x80) >> 7
        self.val_frame |= (a & 0x40) >> 3
        self.val_rand |= (a & 0x20) >> 3
        self.val_c_adr = (a & 0x10) >> 4
        self.val_alu_func |= (a & 0x08) >> 2
        assert not a & 0x07

        a = uword[3] ^ 0xe0
        self.val_a_adr |= (a & 0x80) >> 6
        self.val_frame |= (a & 0x40) >> 2
        self.val_rand |= (a & 0x20) >> 2
        self.val_c_adr |= (a & 0x10) >> 3
        self.val_alu_func |= (a & 0x08) >> 1
        assert not a & 0x07

        a = uword[4] ^ 0xc0
        self.val_a_adr |= (a & 0x80) >> 5
        self.val_b_adr |= (a & 0x40) >> 6
        self.val_parity = (a & 0x20) >> 5
        self.val_c_adr |= (a & 0x10) >> 2
        self.val_alu_func |= (a & 0x08)
        assert not a & 0x07

        a = uword[5] ^ 0xe0
        self.val_a_adr |= (a & 0x80) >> 4
        self.val_b_adr |= (a & 0x40) >> 5
        self.val_c_mux_sel = (a & 0x20) >> 5
        self.val_c_adr |= (a & 0x10) >> 1
        self.val_alu_func |= (a & 0x08) << 1
        assert not a & 0x07

        a = uword[6] ^ 0xe0
        self.val_a_adr |= (a & 0x80) >> 3
        self.val_b_adr |= (a & 0x40) >> 4
        self.val_c_mux_sel |= (a & 0x20) >> 4
        self.val_c_adr |= (a & 0x10)
        self.val_m_b_src = (a & 0x08) >> 3
        assert not a & 0x07

        a = uword[7] ^ 0xc0
        self.val_a_adr |= (a & 0x80) >> 2
        self.val_b_adr |= (a & 0x40) >> 3
        self.val_frame |= (a & 0x20) >> 5
        self.val_c_adr |= (a & 0x10) << 1
        self.val_m_b_src |= (a & 0x08) >> 2
        assert not a & 0x07

    def load_ioc_uword(self, uword):
        ''' Machine Generated file, see r1k_ucode_codegen.p'''

        self.ioc_uword = bytes(uword)

        a = uword[0]
        self.ioc_parity = (a & 0x80) >> 7
        self.ioc_load_wdr = (a & 0x20) >> 5
        self.ioc_random = (a & 0x10)
        self.ioc_random |= (a & 0x08)
        self.ioc_random |= (a & 0x04)
        self.ioc_random |= (a & 0x02)
        self.ioc_random |= (a & 0x01)
        assert not a & 0x40

        a = uword[1]
        self.ioc_adrbs = (a & 0x80) >> 6
        self.ioc_adrbs |= (a & 0x40) >> 6
        self.ioc_fiubs = (a & 0x20) >> 4
        self.ioc_fiubs |= (a & 0x10) >> 4
        self.ioc_tvbs = (a & 0x08)
        self.ioc_tvbs |= (a & 0x04)
        self.ioc_tvbs |= (a & 0x02)
        self.ioc_tvbs |= (a & 0x01)
