import sys
import socket
import os.path
import select
import struct
from packet import *


def sender(
    s_in_port,
    s_out_port,
    cs_in_port,
    filename,
    ):

    print 'Inside Sender'
    print (s_in_port, s_out_port, cs_in_port, filename)
    print '''

'''
    while s_in_port < 1024 or s_in_port > 64000:
        s_in_port = \
            input('invalid s_in_port. Must be between 1024 and 64000.')

    while s_out_port < 1024 or s_out_port > 64000:
        s_out_port = \
            input('invalid s_out_port. Must be between 1024 and 64000.')

    if not os.path.isfile(filename):
        print 'No file exists. Exit sender program.'
        return

    s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    UDP_IP = '127.0.0.1'

    s_in.bind((UDP_IP, s_in_port))
    s_out.bind((UDP_IP, s_out_port))
    s_out.connect((UDP_IP, cs_in_port))

    total_packet = 0
    next_one = 0
    time_out = 1.0
    OVERHEAD = 88
    exitFlag = False
    input_list = [s_in]

    f = open(filename, 'rb')

    while True:

        read_n_byte = f.read(512)
        n = len(read_n_byte)
        print ('read: ', n)
        print '\n'

        if n == 0:
            packetBuffered = Packet(0x497E, 0, next_one, 0, '')
            exitFlag = True
            print 'Last packet to go..'
        elif n > 0:
            packetBuffered = Packet(0x497E, 0, next_one, n, read_n_byte)
            
        packetBuffer = ''
        packetBuffer += struct.pack('i', packetBuffered.magicno)
        packetBuffer += struct.pack('i', packetBuffered.datatype)
        packetBuffer += struct.pack('i', packetBuffered.seqno)
        packetBuffer += struct.pack('i', packetBuffered.datalen)
        packetBuffer += struct.pack('512s', packetBuffered.data)

        while True:
            try:
                print 'sending packetBuffer..'
                s_out.send(packetBuffer)
                total_packet += 1
            except socket.error:
                print 'Connection refused. try again.'

            (inputReady, outputReady, exceptReady) = \
                select.select(input_list, [], [], time_out)

            if inputReady == []:
                print 'Input not ready..'
                continue
            else:
                rcv = s_in.recv(512 + OVERHEAD)
                print rcv
                rcvd = struct.unpack('iiii512s', rcv)
                print 'receive s_in'
                print rcvd

                if rcvd[0] != 0x497E or rcvd[1] != 1 or rcvd[3] != 0:
                    print 'Re-transmit. Wrong magicno, not acknowledgement packet, or datalen != 0.'
                    continue

                if rcvd[2] != next_one:
                    print 'Re-transmit. Seqno does not match next one.'
                    continue
                elif rcvd[2] == next_one:

                    print 'Seqno does not match next one.'
                    next_one = 1 - next_one
                    if exitFlag:
                        print ('total packet is', total_packet)
                        print '----------close----------'
                        f.close()
                        s_in.close()
                        s_out.close()
                        return
                    else:
                        print 'Go back for another packet.'
                        break


# example: sender(6005, 5001, 5454, 'input.dat')

sender(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
       sys.argv[4])


			