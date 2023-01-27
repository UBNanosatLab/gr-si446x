#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Grant Iraci.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import pmt
import array

class var_len_packet_creator(gr.basic_block):
    """
    docstring for block var_len_packet_creator
    """
    def __init__(self, preamble_bytes, sync, has_crc, crc_poly):
        gr.basic_block.__init__(self,
            name="var_len_packet_creator",
            in_sig=None,
            out_sig=None)

        self.preamble_bytes = preamble_bytes
        self.sync = sync
        self.has_crc = has_crc
        self.crc_poly = crc_poly

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))


    def crc(self, data):
        reg = 0xFFFF
        for x in data:
            for _ in range(0, 8):
                 if(((reg & 0x8000) >> 8) ^ (x & 0x80)):
                     reg = ((reg << 1) ^ self.crc_poly ) & 0xffff
                 else:
                     reg = (reg << 1) & 0xffff
                 x = (x << 1) & 0xff
        return reg
    
    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return

        data = [0xAA] * self.preamble_bytes
        data += [(self.sync >> 8) & 0xFF, self.sync & 0xFF]

        payload = [len(pmt.u8vector_elements(msg)) & 0xFF]
        payload += list(pmt.u8vector_elements(msg))

        data += payload

        if (self.has_crc):
            crc = self.crc(payload)
            data.append((crc >> 8) & 0xff)
            data.append(crc & 0xff)

        data.append(0x00)
        data.append(0x00)
        data.append(0x00)
        data.append(0x00)

        buff = array.array('B', numpy.unpackbits(numpy.array(data, dtype=numpy.uint8)))

        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))

    def general_work(self, input_items, output_items):
        return 0

