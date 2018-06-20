#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy
from gnuradio import gr
import pmt
import array

class var_len_packet_creator(gr.basic_block):
    def __init__(self, preamble_bytes, sync, has_crc, crc_poly=0x1021):
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
                     reg = ((reg << 1) ^ self.crc_poly ) & 0xffff ;
                 else:
                     reg = (reg << 1) & 0xffff;
                 x = (x << 1) & 0xff;
        return reg

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
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

        buff = array.array('B', numpy.unpackbits(numpy.array(data, dtype=numpy.uint8)))

        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
