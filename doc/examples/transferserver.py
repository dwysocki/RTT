import socket
import sys

if len(sys.argv) != 2:
    print("usage: transferserver <port>")
    sys.exit(1)

s = socket.socket(type=socket.SOCK_STREAM)
host = socket.gethostname()
port = int(sys.argv[1])
s.bind((host, port))

s.listen(1)
try:
    while True:
        client, address = s.accept()

        try:
            size_info = client.recv(2) # empty for some reason
            msgsize, bufsize = map(lambda x: 2**x,
                                   size_info)

            print("Receiving {}B message in {}B pieces".format(
                msgsize, bufsize))
            
            client.send(b'1')
        
            received = 0
            expected = msgsize
            recvmsg = b''

            while received < expected:
                buffer = client.recv(bufsize)
                received += len(buffer)
                recvmsg += buffer

            client.sendall(recvmsg)
            print("Message sent")

        finally:
            client.close()
finally:
    s.close()
