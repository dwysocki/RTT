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

    latency = stats.mean(list(roundtrip_generator(8, 10, type, host, port)))/2
    data = numpy.array(
        [list(throughput_generator(msgsize, 10, type, host, port))
         for msgsize in sorted(msgsizes)]) - latency
    data = numpy.reshape(numpy.fromiter((2**m for m in sorted(msgsizes)),
                                         numpy.float),
                         (-1,1)) / data
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

def sizes(msgsize, counts, host, port, *args, **kwargs):
    counts = sorted(counts)
    labels = numpy.fromiter((2**n for n in counts), numpy.float)
    
    latency = stats.mean(list(
        roundtrip_generator(8, 10, socket.SOCK_STREAM, host, port)))/2
    data = msgsize / numpy.array(
        [list(sizes_generator(msgsize, n, 10, host, port))
         for n in counts])

    return data, labels
