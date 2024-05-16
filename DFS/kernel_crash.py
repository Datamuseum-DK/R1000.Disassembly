#!/usr/bin/env python
#
# Copyright (c) 2024 Poul-Henning Kamp <phk@phk.freebsd.dk>
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
   From 30000961 pdf pg 4
'''

IOC_CRASH_CODES = {
    0x17C: "over_temperature",
    0x200: "ac_power_failure",
    0x601: "bus_error",
    0x60f: "disk_ctrl_eeprom_read_failed",
    0x612: "system_call_diag_mode_wrong",
    0x614: "dfs_crash",
    0x617: "disk_ctrl_eeprom_write_failed",
    0x618: "ethernet_config_timer_error",
    0x619: "ethernet_unexpected_cmd_complete",
    0x61A: "ethernet_soreceive_with_no_rcb",
    0x61B: "ethernet_sosend_with_no_rcb",
    0x61C: "ethernet_response_msg_overflow",
    0x61D: "ethernet_udp_blcoked_on_sosend",
    0x61F: "unimplemented_disk_stub",
    0x622: "unimplemented_x25_stub",
    0x626: "tape_invalid_configuration",
    0x629: "priv_violation",
    0x642: "disk_ctrl_unknown_attention_cause",
    0x654: "recursive_bus_error",
    0x659: "chain_with_io_pending",
    0x65A: "rcb_already_active",
    0x66D: "unimplemented",
    0x66E: "io_on_available_rcb",
    0x671: "diag_comm_bus_direction_error",
    0x674: "inactive_rcb_completed",
    0x679: "mux_nonexistent_memory",
    0x67A: "mux_bcr_out_of_range",
    0x67B: "reg_destroyed_by_int_handler",
    0x680: "server_crashed",
    0x684: "hawk_ownership_error",
    0x686: "hawk_software_error",
    0x688: "hawk_ip_fragmented",
    0x68A: "dfs_multi_part_request",
    0x68B: "dfs_multi_part_response",
    0x68C: "rp_data_too_large",
    0x696: "enp_bad_bch_b_type",
    0x697: "enp_bad_wakeup_type",
    0x698: "enp_bad_tx_bfr_list",
    0x699: "enp_paranoid_checking",
    0x69A: "enp_too_many_buffers_allocated",
    0x704: "missed_expected_interrupt",
    0x705: "disk_ctrl_priority_wrong",
    0x70C: "comm_ctrl_priority_wrong",
    0x711: "comm_ctrl_wrong_num_dist_pnls",
    0x71E: "vmegen_selftest_failed",
    0x728: "unknown_interrupt",
    0x738: "disk_ctlr_no_attention_bit_set",
    0x739: "disk_ctlr_unknown_xfer_complete",
    0x73A: "disk_ctlr_drive_not_ready",
    0x73B: "disk_ctlr_drive_clear_failed",
    0x73E: "disk_ctlr_recalibrate_failed",
    0x743: "disk_ctrl_pack_ack_failed",
    0x757: "memory_parity_error",
    0x76F: "unexpected_diag_comm_interrupt",
    0x770: "diag_comm_bus_data_errors",
    0x777: "dh_unit_with_no_dm_unit",
    0x778: "dm_unit_with_no_dh_unit",
    0x782: "boot_tx_retry_expired",
    0x783: "hawk_ram_parity_error",
    0x785: "lance_unrecoverable_error",
    0x787: "hawk_rmd_0_error",
    0x789: "hawk_tmd_0_error",
    0x78D: "rp_retransmits_exceeded",
    0x79E: "enp_sring_error",
    0x806: "request_to_nonexistent_disk_drive",
    0x807: "io_request_to_null_device",
    0x810: "diag_modem_protocol_error",
    0x824: "illegal_comm_output_command",
    0x825: "comm_output_to_illegal_line",
    0x827: "iop_kernel_constraint_error",
    0x83C: "rcb_not_available",
    0x846: "illegal_unit_0_line",
    0x872: "packet_id_mismatch",
    0x873: "error_in_mpart_rsp_req",
    0x875: "more_data_than_packets",
    0x89B: "enp_bad_sc_acpt_open",
    0x89C: "enp_last_tx_frag_too_big",
    0x89D: "enp_tx_frag_not_full",
    0xA16: "disk_error_during_chain",
}

def panic(nbr):
    retval = "PANIC_0x%x" % nbr
    t = IOC_CRASH_CODES.get(nbr)
    if t:
        return retval + "_" + t
    return retval

