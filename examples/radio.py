import sys
import socket
from time import sleep

class Radio(object):
    """A wrapper around a KISS TNC"""

    FEND = '\xC0'
    FESC = '\xDB'
    TFEND = '\xDC'
    TFESC = '\xDD'

    def __init__(self, address="127.0.0.1", port=52001):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((address, port))
        self.sock.listen(1)

        self.con = None

        self.rxbuf = ''

    def accept(self):
        self.con, address = self.sock.accept()

    def sendPacket(self, data):

        packet = ''

        for b in data:
            if (b == Radio.FESC):
                packet += Radio.FESC + Radio.TFESC
            elif (b == Radio.FEND):
                packet += Radio.FESC + Radio.TFEND
            else:
                packet += b

        packet += Radio.FEND

        # I have no idea why this null byte is needed
        # but gr-kiss / GRC wants it
        self.con.sendall('\x00' + packet)


    def receivePacket(self, debug = False):

        packet = ''

        # This is probably more efficient than it needs to be,
        # but I made a mistake and thought this would fix it
        # and there's no point going back

        while True:
            while len(self.rxbuf):
                (b, self.rxbuf) = (self.rxbuf[0], self.rxbuf[1:])
                if (b == Radio.FEND):
                    # gr-kiss adds a stray null byte at the beginning
                    # TODO: assert(packet[0] == '\x00')
                    packet = packet[1:]
                    if (len(packet) > 0):
                        if (debug):
                            print(packet)

                        return packet

                elif (b == Radio.FESC):
                    b = self.con.recv(1)
                    if (b == Radio.TFEND):
                        packet += Radio.FEND
                    elif (b == Radio.TFESC):
                        packet += Radio.FESC
                    else:
                        # Invalid escape sequence, gr-kiss messed up
                        # Do something, right now we ignore it
                        pass
                else:
                    packet += b
            self.rxbuf += self.con.recv(1024)
            if (not self.rxbuf):
                raise Exception("GRC socket disconnected!")


def main():

    radio = Radio()
    print('Waiting for GRC...')
    radio.accept()
    print('Got connection from GRC!')

    if (len(sys.argv) == 1 or sys.argv[1] == 'rx'):
        numPackets = 0
        try:
            while True:
                radio.receivePacket(True)
                numPackets += 1
                print('Received ' + str(numPackets) + ' packet(s)')
        except Exception as e:
            return

    elif (sys.argv[1] == 'tx' and len(sys.argv) == 3):
        sleep(1)
        for i in range(int(sys.argv[2])):
            print(str(i))
            radio.sendPacket('KC2QOL')
            sleep(1)

        # Attempt to receive, this way GNU Radio won't crash on socket closing
        numPackets = 0
        try:
            while True:
                radio.receivePacket(True)
                numPackets += 1
                print('Received ' + str(numPackets) + ' packet(s)')
        except Exception as e:
            return


    else:
        print('Usage: python radio.py [rx | tx n]')


if __name__ == '__main__':
    main()
