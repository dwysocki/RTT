import argparse

import mysocket

parser = argparse.ArgumentParser(description="Launch server.")
parser.add_argument('type', metavar='TYPE',
                    choices=['TCP', 'UDP'],
                    help='Choose between TCP or UDP for transmissions.')
parser.add_argument('port', metavar='PORT',
                    type=int,
                    help='Set port to use.')

args = parser.parse_args()

server = mysocket.serversocket(type=utils.type_map[type],
                               port=args.port)
server.activate()
