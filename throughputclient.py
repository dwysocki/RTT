import socket
import sys

import mysocket
import utils

def TCP(host, port, msgsize, bufsize):
    """Test throughput in kbps for uploading and downloading a message of size
    2**msgsize to the host server. Returns a tuple (uprate, downrate)"""
#    print("TCP throughput client not yet implemented")
    server = mysocket.MySocket(type=socket.SOCK_STREAM)

    sizemsg = (chr(msgsize) + chr(bufsize)).encode()

    msgsize, bufsize = 2**msgsize, 2**bufsize

    msg = utils.makebytes(msgsize)

    try:
        server.connect((host, port))

    except socket.error:
        return

    try:
        # inform server of msgsize and bufsize
        server.sendall(sizemsg)
        # await confirmation before sending message
        server.recv(1)
        # send message
        server.sendby(msg, msgsize, bufsize)
        # receive time in ms
        uptime = float(server.recv(16).decode('utf-8'))
        # confirm ready to receive
        server.send(b'1')
        # receive message and record throughput
        recvmsg, downtime = server.throughput(msgsize, bufsize)

        # message was corrupted
        if msg != recvmsg:
            return
        
        # the bitrate is 8 times the size of the message in bytes over the
        # time elapsed
        uprate = 8*msgsize/uptime if uptime is not 0 else None
        downrate = 8*msgsize/downtime if downtime is not 0 else None

        return uprate, downrate

    finally:
        server.close()

def test_TCP(host, port, size):
    return TCP(host, port, size, size)
    
def UDP(host, port, msgsize, bufsize):
    print("UDP throughput client not yet implemented")

def test_UDP(host, port, size):
    return UDP(host, port, size, size)
