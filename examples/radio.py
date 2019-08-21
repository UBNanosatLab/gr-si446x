#!/usr/bin/env python2

import sys
import zmq
import pmt
import numpy as np
from time import sleep

def main():

    sub = 'tcp://127.0.0.1:52000'
    pub = 'tcp://127.0.0.1:52001'
    tx_pkt_len = 64


    if (len(sys.argv) == 1 or sys.argv[1] == 'rx'):
        num_packets = 0
       
        #  Socket to talk to server
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        socket.connect(sub)

        socket.setsockopt_string(zmq.SUBSCRIBE, u'')
        
        while True:
            pkt = socket.recv_serialized(lambda x: pmt.deserialize_str(b''.join(x)))
            print(pmt.to_python(pkt))
            num_packets += 1
            print('Received {} packet(s)'.format(num_packets))
    
    elif (sys.argv[1] == 'tx' and len(sys.argv) == 3):
        sleep(1)
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        #socket.connect(pub)
        socket.bind(pub)
        for i in range(int(sys.argv[2])):
            print(str(i))
            data = 'NOCALL '.ljust(tx_pkt_len, 'x').encode('utf-8')
            # Python 2.7 is dumb, but that's what GR 3.7 requires...
            msg = pmt.cons(pmt.intern('out'), pmt.init_u8vector(len(data), map(ord, data)))
            socket.send(pmt.serialize_str(msg))
            
            print('Sent ' + str(len(data)) + ' byte(s)')
            sleep(0.5)
    else:
        print('Usage: python radio.py [rx | tx n]')


if __name__ == '__main__':
    main()
