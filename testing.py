import socket

import mysocket
import utils

def roundtrip(msgsizes, type, host, port, *args, **kwargs):
    type = utils.type_map[type]

    return {msgsize : list(roundtrip_generator(msgsize, 1000, type, host, port))
            for msgsize in msgsizes}

def roundtrip_generator(msgsize, iterations, type, host, port):
    sock = None
    for i in range(iterations):
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            yield sock.roundtrip(msgsize)
        finally:
            if sock is not None:
                sock.close()

def throughput(msgsizes, n, type, host, port, *args, **kwargs):
    pass

def sizes(msgsizes, n, type, host, port, *args, **kwargs):
    pass
