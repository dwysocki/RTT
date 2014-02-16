import socket
import sys

def mod256(x):
    """Finds x modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with n bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))

if len(sys.argv) != 4:
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
    s.send(sizemsg)
    # await confirmation
    s.recv(1)
    # send payload
    s.sendall(msg)

    received = 0
    expected = msgsize
    recvmsg = b''

    while received < expected:
        buffer = s.recv(bufsize)
        received += len(buffer)
        recvmsg += buffer

    print("received message of size " + str(len(recvmsg)))

finally:
    s.close()







