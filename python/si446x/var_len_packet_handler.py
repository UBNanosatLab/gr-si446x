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

class var_len_packet_handler(gr.basic_block):

    STATE_SYNC = 0
    STATE_LEN = 1
    STATE_PAYLOAD = 2

    def __init__(self, sync, has_crc=True, check_crc=True, crc_poly=0x8005):
        gr.basic_block.__init__(self,
            name="var_len_packet_handler",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.message_port_register_out(pmt.intern('out'))

        self.reg = 0
        self.sync = sync
        self.length = 0
        self.has_crc = has_crc
        self.check_crc = check_crc
        self.crc_poly = crc_poly
        self.state = self.STATE_SYNC

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        in0 = input_items[0]

        for x in in0:

            if (self.state == self.STATE_PAYLOAD):
                if (self.index < self.length * 8 + (16 if self.has_crc else 0)):
                    self.buf[self.index] = x
                    self.index += 1
                if (self.index == self.length * 8 + (16 if self.has_crc else 0)):
                    self.state = self.STATE_SYNC
                    self.reg = 0
                    packed = numpy.packbits(self.buf)

                    if (self.has_crc):
                        arr = array.array('B', packed[:-2])
                    else:
                        arr = array.array('B', packed)

                    if (self.check_crc):
                        rx = (packed[-2] << 8) + packed[-1]
                        calc = self.crc([self.length] + packed[:-2].tolist())
                        if (calc == rx):
                            self.send_message(arr)
                        else:
                            print('[crc mismatch] calc: ' + hex(calc)
                                    + '\trx: ' + hex(rx))
                    else:
                        self.send_message(arr)

            elif (self.state == self.STATE_SYNC):
                self.reg = ((self.reg << 1) & 0xFFFF) | x
                if (self.reg == self.sync):
                    self.state = self.STATE_LEN
                    self.index = 0
                    self.reg = 0

            elif (self.state == self.STATE_LEN):
                self.reg = (self.reg << 1) | x
                self.index += 1
                if (self.index == 8):
                    self.length = self.reg
                    self.state = self.STATE_PAYLOAD
                    self.index = 0
                    self.buf = numpy.zeros(self.length * 8 +
                                (16 if self.has_crc else 0), dtype=numpy.uint8)

        self.consume_each(len(in0))
        return len(in0)

