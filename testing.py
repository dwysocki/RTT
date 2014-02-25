import numpy
import socket

import mysocket
import stats
import utils

def roundtrip(msgsizes, type, host, port, *args, **kwargs):
    type = utils.type_map[type]

    labels = numpy.fromiter((2**msgsize for msgsize in sorted(msgsizes)),
                            numpy.float)
    data = numpy.array(
        [list(roundtrip_generator(msgsize, 100, type, host, port))
         for msgsize in sorted(msgsizes)])
    return data, labels

def roundtrip_generator(msgsize, iterations, type, host, port):
    sock = None
    for i in range(iterations):
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            yield sock.roundtrip(msgsize)
        finally:
            if sock is not None:
                sock.close()

def throughput(msgsizes, type, host, port, *args, **kwargs):
    type = utils.type_map[type]
    labels = numpy.fromiter((2**msgsize for msgsize in sorted(msgsizes)),
                            numpy.float)

    latency = stats.mean(list(roundtrip_generator(8, 100, type, host, port)))/2
    data = numpy.array(
        [list(throughput_generator(msgsize, 100, type, host, port))
         for msgsize in msgsizes]) - latency
    return data, labels

def throughput_generator(msgsize, iterations, type, host, port):
    sock = None
    for i in range(iterations):
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            yield sock.throughput(msgsize)
        finally:
            if sock is not None:
                sock.close()

def sizes(msgsizes, n, type, host, port, *args, **kwargs):
    pass
