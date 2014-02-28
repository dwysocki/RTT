import numpy
import socket

import mysocket
import stats
import utils

def roundtrip(msgsizes, type, host, port, *args, **kwargs):
    type = utils.type_map[type]
    msgsizes = sorted(msgsizes)

    labels = numpy.fromiter((2**msgsize for msgsize in msgsizes),
                            numpy.float)
    data = numpy.array(
        [list(roundtrip_generator(msgsize, 100, type, host, port))
         for msgsize in msgsizes])
    return data, labels

def roundtrip_generator(msgsize, iterations, type, host, port):
    sock = None
    tries = 4
    while iterations > 0:
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            RTT = sock.roundtrip(msgsize)
            print(RTT)
            if RTT is not None:
                iterations -= 1
                yield RTT
            elif tries > 0:
                tries -= 1
            else:
                iterations -= 1
        finally:
            tries = 4
            if sock is not None:
                sock.close()

def throughput(msgsizes, type, host, port, *args, **kwargs):
    type = utils.type_map[type]
    labels = numpy.fromiter((2**msgsize for msgsize in sorted(msgsizes)),
                            numpy.float)

    data = numpy.array(
        [list(throughput_generator(msgsize, 10, type, host, port))
         for msgsize in sorted(msgsizes)])

    return data, labels

def throughput_generator(msgsize, iterations, type, host, port):
    sock = None
    while iterations > 0:
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            throughput = sock.throughput(msgsize, latency)
            print(throughput)
            if throughput is not None:
                iterations -= 1
                yield throughput
        finally:
            if sock is not None:
                sock.close()

def sizes(counts, host, port, *args, **kwargs):
    counts = sorted(counts)
    labels = numpy.fromiter((2**n for n in counts), int)
    
    latency = stats.mean(list(
        roundtrip_generator(8, 10, socket.SOCK_STREAM, host, port)))/2
    data = numpy.array([list(sizes_generator(n, 10, host, port))
                        for n in counts]) - latency
    data = 2**20 / data

    return data, labels

def sizes_generator(count, iterations, host, port):
    sock = None
    for i in range(iterations):
        try:
            sock = mysocket.clientsocket(host=host, port=port)
            time = sock.sizes(count)
            if time is not None:
                yield time
        finally:
            if sock is not None:
                sock.close()
