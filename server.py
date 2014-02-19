import argparse

import roundtripserver
import throughputserver
import sizeserver

parser = argparse.ArgumentParser(description="Launch server.")
parser.add_argument('mode', metavar='MODE',
                    choices=['RTT', 'throughput', 'size'],
                    help='Select mode of operation.')
parser.add_argument('type', metavar='TYPE',
                    choices=['TCP', 'UDP'],
                    help='Choose between TCP or UDP for transmissions.')
parser.add_argument('port', metavar='PORT',
                    type=int,
                    help='Set port to use.')

args = parser.parse_args()

choice_map = {'TCP' : {'RTT'        : roundtripserver.TCP,
                       'throughput' : throughputserver.TCP,
                       'size'       : sizeserver.TCP},
              'UDP' : {'RTT'        : roundtripserver.UDP,
                       'throughput' : throughputserver.UDP,
                       'size'       : sizeserver.UDP}}

choice_map[args.type][args.mode](args.port)
