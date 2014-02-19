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
            size_info = client.recv(2)
            msgsize, bufsize = map(lambda x: 2**x,
                                   size_info)

            print("Receiving {}B message in {}B pieces".format(
                msgsize, bufsize))
            
            client.send(b'1')
        
            received = sent = 0
            msg = b''

            while received < msgsize:
                buffer = client.recv(bufsize)
                received += len(buffer)
                msg += buffer

            while sent < msgsize:
                sent += client.send(msg[sent:sent+bufsize+1])

            print("Message sent")

        finally:
            client.close()
finally:
    s.close()
