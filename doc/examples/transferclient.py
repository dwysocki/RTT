import socket
import sys
import time

def mod256(x):
    """Finds x modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with n bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))

if len(sys.argv) != 5:
    print("usage: transferclient <host> <port> <log2(msgsize)> <log2(bufsize)>")
    sys.exit(1)

s = socket.socket(type=socket.SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])

# log_2 of size of message and size of buffers
msgsize, bufsize = map(int,sys.argv[3:])

# message to send to server indicating size of whole message and individual
# buffers
sizemsg = (chr(msgsize) + chr(bufsize)).encode()

msgsize, bufsize = map(lambda x: 2**x, (msgsize, bufsize))

# message to send
msg = makebytes(msgsize)

try:
    s.connect((host, port))

except socket.error:
    print("an error occured")
    sys.exit(1)


try:
    # send size message
    s.sendall(sizemsg)
    # await confirmation
    s.recv(1)
    
    # send payload
    sent = 0

    # start timing
    start_time = time.time()
        
    while sent < msgsize:
        sent += s.send(msg[sent:sent+bufsize+1])

    received = 0
    recvmsg = b''

    while received < msgsize:
        buffer = s.recv(bufsize)
        received += len(buffer)
        recvmsg += buffer

    end_time = time.time()
    
    print("received message of size {}B in {}s".format(
        len(recvmsg), end_time-start_time))

finally:
    s.close()







