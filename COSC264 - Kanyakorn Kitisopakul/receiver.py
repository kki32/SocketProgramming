import sys
import socket
import time
import os.path
import struct
from packet import *

def receiver(
    r_in_port,
    r_out_port,
    cr_in_port,
    filename,
    ):

    print 'Inside Receiver'
    print (r_in_port, r_out_port, cr_in_port, filename)

    while r_in_port < 1024 or r_in_port > 64000:
        r_in_port = \
            input('invalid r_in_port. Must be between 1024 and 64000.')

    while r_out_port < 1024 or r_out_port > 64000:
        r_out_port = \
            input('invalid r_out_port. Must be between 1024 and 64000.')

    if os.path.isfile(filename):
        print 'File already exists. Exit receiver program.'
        return

    r_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    r_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    UDP_IP = '127.0.0.1'

    r_in.bind((UDP_IP, r_in_port))
    r_out.bind((UDP_IP, r_out_port))
    r_out.connect((UDP_IP, cr_in_port))

    expected = 0
    OVERHEAD = 88

    f = open(filename, 'wb')

    while True:
        r_in.setblocking(1)
        rcv = r_in.recv(520 + OVERHEAD)
        rcvd = struct.unpack('iiii512s', rcv)
        print 'Receive something'
        if rcvd[0] != 0x497E:
            print 'Wrong magicno.'
            continue
        if rcvd[1] != 0:
            print 'Not data packet.'
            continue
        if rcvd[2] != expected:
            ack_packet = ''
            ack_packet += struct.pack('i', 0x497E)
            ack_packet += struct.pack('i', 1)
            ack_packet += struct.pack('i', rcvd[2])
            ack_packet += struct.pack('i', 0)
            ack_packet += struct.pack('512s', 'N/A')
            try:
                r_out.send(ack_packet)
                print 'Send acknowledgement packet #1 to channel'
                print ack_packet
                continue
            except socket.error:
                print 'Connection refused. try again.'

        if rcvd[2] == expected:
            ack_packet = ''
            ack_packet += struct.pack('i', 0x497E)
            ack_packet += struct.pack('i', 1)
            ack_packet += struct.pack('i', rcvd[2])
            ack_packet += struct.pack('i', 0)
            ack_packet += struct.pack('512s', '')
            try:
                r_out.send(ack_packet)
                print 'Send acknowledgement packet #2 to channel'
                print ack_packet
                expected = 1 - expected
            except socket.error:
                print 'Connection refused. try again.'

            if rcvd[3] > 0:
                #struct object has fixed length.  we use slice to prevent the padding being
                #written to the file
                to_write = (rcvd[4])[:rcvd[3]]

                f.write(to_write)
                print 'write it down'
                print to_write

                continue
            elif rcvd[3] == 0:
                print '----------close----------'
                f.close()
                r_in.close()
                r_out.close()
                return


# example: receiver(6006, 5000, 6002, 'output.dat')

receiver(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
         sys.argv[4])


			