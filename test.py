import time
import sys
import socket

side = sys.argv[1]
port = int(sys.argv[2])

if side == 'server':
    server = socket.socket()
    host = socket.gethostname()

    try:
        server.listen(1)
    
        while True:
            client, address = server.accept()
            msg = ''
            
            try:
                while msg == '':
                    start_time = time.time()
                    print("t: {}".format(start_time))

                    msg = client.recv(32)
                    print("m: {}".format(msg))

                    client.send(b'1')

            finally:
                end_time = time.time()
                elapsed_time = end_time - start_time
                print("\n" + "elapsed time: {}".format(elapsed_time))
                client.close()
    finally:
        server.close()
    
elif side == 'client':
    host = sys.argv[3]
    server = socket.socket()

    msg = bytes(range(32))

    server.connect((host, port))

    try:
        start_time = time.time()
        server.send(msg)
        ACK = server.recv(1)
        end_time = time.time()
        print("ACK? {}".format(ACK))
        print("t = {}".format(end_time-start_time))
    finally:
        server.close()
