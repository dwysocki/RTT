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
while True:
    client, address = s.accept()

    try:
        size_info = client.recv(2) # empty for some reason
        print(size_info.decode('utf-8') + "<<- message")
        msgsize, bufsize = map(lambda x: 2**x,
                               size_info)

        client.send(b'1')
        
        received = 0
        expected = msgsize
        recvmsg = b''

        while received < expected:
            buffer = client.recv(bufsize)
            received += len(buffer)
            recvmsg += buffer

        client.sendall(recvmsg)

    finally:
        client.close()
