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
parser.add_argument('msgsize', metavar='MS', type=int,
                    help='Set log_2 size of message.')
parser.add_argument('bufsize', metavar='BS', type=int,
                    help='Set log_2 size of buffers.')


args = parser.parse_args()

choice_map = {'TCP' : {'RTT'        : roundtripclient.TCP,
                       'throughput' : throughputclient.TCP,
                       'size'       : sizeclient.TCP},
              'UDP' : {'RTT'        : roundtripclient.UDP,
                       'throughput' : throughputclient.UDP,
                       'size'       : sizeclient.UDP}}

print(choice_map[args.type][args.mode](args.host, args.port,
                                       args.msgsize, args.bufsize))
