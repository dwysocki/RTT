import socket

import mysocket

def TCP(port):
    server = mysocket.MySocket(type=socket.SOCK_STREAM)

    host = socket.gethostname()

    server.bind((host, port))

    try:
        server.listen(1)

        while True:
            client, address = server.accept()

            try:
                # receive msgsize and bufsize info
                size_info = client.recv(2)
                msgsize, bufsize = map(lambda x: 2**x,
                                       size_info)

                # confirm to client that transmission is about to begin
                client.send(b'1')

                msg = client.recvby(msgsize, bufsize)
                client.sendby(msg, msgsize, bufsize)

            finally:
                client.close()

    finally:
        server.close()

def UDP(port):
    print("UDP RTT server not yet implemented")
