import socket

import mysocket
import utils

def roundtrip(msgsizes, type, host, port):
    type = utils.type_map[type]

    return {msgsize : list(roundtrip_generator(msgsize, 1000, type, host, port))
            for msgsize in msgsizes}

def roundtrip_generator(msgsize, iterations, type, host, port):
    for i in range(iterations):
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            yield sock.roundtrip(msgsize)
        finally:
            sock.close()

def throughput(msgsizes, n, type, host, port):
    pass

def sizes(msgsizes, n, type, host, port):
    pass
