import argparse

import roundtripclient
import throughputclient
import sizeclient
from testing import do_tests

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

RTT_sizes = range(0, 10, 4)
throughput_sizes = range(10, 22, 2)
size_sizes = range(16, 21)

choice_map = {'TCP' : {'RTT'        : (roundtripclient.test_TCP,
                                       RTT_sizes),
                       'throughput' : (throughputclient.test_TCP,
                                       throughput_sizes),
                       'size'       : (sizeclient.test_TCP,
                                       size_sizes)},
              'UDP' : {'RTT'        : (roundtripclient.test_UDP,
                                       RTT_sizes),
                       'throughput' : (throughputclient.test_UDP,
                                       throughput_sizes),
                       'size'       : (sizeclient.test_UDP,
                                       size_sizes)}}

func, iter = choice_map[args.type][args.mode]
print(do_tests(func, args.host, args.port, iter))
