import socket
import time

import mysocket
import utils

def TCP(host, port, msgsize, bufsize):
    """Measures round-trip time (RTT) in ms over TCP to host:port for a
    message of size 2**msgsize bytes in chunks of size 2**bufsize bytes.

    Returns the time as an integer measured in milliseconds.
    Returns nothing if there are any errors."""
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
        # start timer
#        start_time = time.time()
        # send message
#        server.sendby(msg, msgsize, bufsize)
        # receive echoed message
#        recvmsg = server.recvby(msgsize, bufsize)
        # end timer
#        end_time = time.time()

        # echo message and find time
        recvmsg, elapsed_time = server.echo(msg, msgsize, bufsize)

        # message was corrupted
        if msg != recvmsg:
            return
        
        return elapsed_time

    finally:
        server.close()

def test_TCP(host, port, size):
    return TCP(host, port, size, size)
        
def UDP(host, port, msgsize, bufsize):
    """Look here
    <http://www.binarytides.com/programming-udp-sockets-in-python/>
    """
    print("UDP RTT client not yet implemented")

def test_UDP(host, port, size):
    return UDP(host, port, size, size)
