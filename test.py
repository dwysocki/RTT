import time
import sys
import select
import socket

side = sys.argv[1]
port = int(sys.argv[2])

if side == 'server':
    server = socket.socket()
    host = socket.gethostname()
    server.bind((host, port))
    server.setblocking(0)
    
    try:
        server.listen(1)
    
        while True:
            reads, writes, errs = select.select([server], [], [])
            if server in reads:
                client, address = server.accept()
            else:
                continue
            msg = ''
            
            try:
                reads, writes, errs = select.select([], [client], [])
                while client in writes:
                    start_time = time.time()
                    print("t: {}".format(start_time))

                    msg = client.recv(32)
                    print("m: {}".format(msg))

                    client.send(b'1')
                    reads, writes, errs = select.select([], [client], [])

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
        print(start_time)
        time.sleep(5)
        server.send(msg)
        ACK = server.recv(1)
        end_time = time.time()
        print("ACK? {}".format(ACK))
        print("t = {}".format(end_time-start_time))
    finally:
        server.close()
