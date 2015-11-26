import time
import sys
import socket
import select
import random
import pickle
from packet import *
import struct


def channel(
    cs_in_port,
    cs_out_port,
    cr_in_port,
    cr_out_port,
    s_in_port,
    r_in_port,
    P,
    ):

    print 'Inside Channel'
    print (
        cs_in_port,
        cs_out_port,
        cr_in_port,
        cr_out_port,
        s_in_port,
        r_in_port,
        P,
        )

    while cs_in_port < 1024 or cs_in_port > 64000:
        cs_in_port = \
            input('invalid cs_in_port. Must be between 1024 and 64000.')

    while cs_out_port < 1024 or cs_out_port > 64000:
        cs_out_port = \
            input('invalid cs_out_port. Must be between 1024 and 64000.'
                  )

    while cr_in_port < 1024 or cr_in_port > 64000:
        cr_in_port = \
            input('invalid cr_in_port. Must be between 1024 and 64000.')

    while cr_out_port < 1024 or cr_out_port > 64000:
        cr_out_port = \
            input('invalid cr_out_port. Must be between 1024 and 64000.'
                  )

    while P < 0 or P >= 1:
        P = input('Invalid Probability. Must satisfy 0 <= P < 1.')

    cs_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cs_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cr_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cr_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    UDP_IP = '127.0.0.1'

    cs_in.bind((UDP_IP, cs_in_port))
    cs_out.bind((UDP_IP, cs_out_port))
    cr_in.bind((UDP_IP, cr_in_port))
    cr_out.bind((UDP_IP, cr_out_port))

    cs_out.connect((UDP_IP, s_in_port))
    cr_out.connect((UDP_IP, r_in_port))

    time_out = 1.0
    input_list = [cs_in, cr_in]
    OVERHEAD = 88

    while True:
        (inputready, outputready, exceptready) = \
            select.select(input_list, [], [], time_out)

        for i in inputready:
            if i == cs_in:
                print 'receive from sender'
                cs_rcv = cs_in.recv(512 + OVERHEAD)
                cs_rcvd = struct.unpack('iiii512s', cs_rcv)
                print cs_rcvd[4]

                if cs_rcvd[0] != 0x497E:
                    print 'Wrong magicno.'
                    continue
                else:
                    u = random.uniform(0, 1)
                    print u
                    if u < P:
                        print 'Drop packet.'
                        continue
                    else:
                        try:
                            cr_out.send(cs_rcv)
                            print 'sent to channel'
                        except socket.error:
                            print 'Connection refused. try again.'
            elif i == cr_in:

                print 'receive from receiver'
                cr_rcv = cr_in.recv(512 + OVERHEAD)
                cr_rcvd = struct.unpack('iiii512s', cr_rcv)

                if cr_rcvd[0] != 0x497E:
                    print 'Wrong magicno.'
                    continue
                else:
                    u = random.uniform(0, 1)
                    print u
                    if u < P:
                        print 'Drop packet.'
                        continue
                    else:
                        try:
                            cs_out.send(cr_rcv)
                            print 'sent to channel'
                        except socket.error:
                            print 'Connection refused. try again.'


# example: channel(
    #5454,
    #6001,
    #6002,
    #6004,
    #6005,
    #6006,
    #0.2,
    #)
    
list_of_argv = sys.argv
channel(int(list_of_argv[1]),int(list_of_argv[2]),int(list_of_argv[3]),int(list_of_argv[4]),int(list_of_argv[5]), int(list_of_argv[6]), float(list_of_argv[7]))




			