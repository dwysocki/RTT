import argparse
from os.path import isdir

import plot
import testing

parser = argparse.ArgumentParser(description="Launch server.")
parser.add_argument('output', metavar='OUTPUT',
                    help='Output directory')
parser.add_argument('mode', metavar='MODE',
                    choices=['roundtrip', 'throughput', 'sizes', 'all'],
                    help='Select mode of operation.')
parser.add_argument('type', metavar='TYPE',
                    choices=['TCP', 'UDP'],
                    help='Choose between TCP or UDP for transmissions.')
parser.add_argument('host', metavar='HOST',
                    help='Set host to connect to.')
parser.add_argument('port', metavar='PORT',
                    type=int,
                    help='Set port to use.')
parser.add_argument('--client', metavar='CLIENT',
                    default='client',
                    help='Name of client, for use in plot titles.')

args = parser.parse_args()

if not isdir(args.output):
    parser.error('directory {} does not exist'.format(args.output))

roundtrip_msgsizes = range(0, 10, 4)
throughput_msgsizes = range(10, 21, 2)
size_counts = range(8, 13)

roundtrip_mode = lambda: plot.box_plot(
    *testing.roundtrip(roundtrip_msgsizes, **args.__dict__), output=args.output,
    title='{} Round Trip Time from {} to {}'.format(args.type, args.client, args.host),
    xlabel='Packet Size (B)', ylabel='RTT (ms)', ymul=1000)

throughput_mode = lambda: plot.box_plot(
    *testing.throughput(throughput_msgsizes, **args.__dict__), output=args.output,
    title='{} Throughput from {} to {}'.format(args.type, args.client, args.host),
    xlabel='Message Size (kB)', ylabel='throughput (kbps)',
    xmul=2**-10, ymul=8*2**-10)

sizes_mode = lambda: plot.box_plot(
    *testing.sizes(size_counts, **args.__dict__), output=args.output,
    title='{} Size-Number Interaction from {} to {}'.format(
        args.type, args.client, args.host),
    xlabel='Number of messages', ylabel='throughput (kbps)',
    ymul=8*2**-10)

if args.mode in ['roundtrip', 'all']:
    roundtrip_mode()
if args.mode in ['throughput', 'all']:
    throughput_mode()
if args.mode in ['sizes', 'all'] and args.type is not 'UDP':
    sizes_mode()
