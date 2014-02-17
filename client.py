import argparse

import roundtripclient
import throughputclient
import sizeclient

parser = argparse.ArgumentParser(description="Launch server.")
parser.add_argument('mode', metavar='M', choices=['RTT', 'throughput', 'size'],
                    help='Select mode of operation.')
parser.add_argument('type', metavar='T', choices=['TCP', 'UDP'],
                    help='Choose between TCP or UDP for transmissions.')
parser.add_argument('host', metavar='H',
                    help='Set host to connect to.')
parser.add_argument('port', metavar='P', type=int,
                    help='Set port to use.')



args = parser.parse_args()

RTT_sizes = (0, 4, 8)
throughput_sizes = (10, 12, 14, 16, 18, 20)
size_sizes = (16, 17, 18, 19, 20)

choice_map = {'TCP' : {'RTT'        : (roundtripclient.TCP, RTT_sizes),
                       'throughput' : (throughputclient.TCP, throughput_sizes),
                       'size'       : (sizeclient.TCP, size_sizes)},
              'UDP' : {'RTT'        : (roundtripclient.UDP, RTT_sizes),
                       'throughput' : (throughputclient.UDP, throughput_sizes),
                       'size'       : (sizeclient.UDP, size_sizes)}}

func, lst = choice_map[args.type][args.mode]
for n in lst:
    size = 2**n
    print("2^{}B in {}s".format(n, func(args.host, args.port,
                                        size, size)))
