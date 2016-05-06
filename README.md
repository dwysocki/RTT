RTT
===

CSC445 Assignment 1: An exercise in measuring transfer times and throughput over
TCP and UDP.


Requirements
============

client side
  - Python 3.3+
  - numpy
  - matplotlib

server side
  - Python 3.3+


Usage
=====

client side

```
python client.py [-h] [--client CLIENT] OUTPUT MODE TYPE HOST PORT

Launch server.

positional arguments:
  OUTPUT           Output directory
  MODE             Select mode of operation.
  TYPE             Choose between TCP or UDP for transmissions.
  HOST             Set host to connect to.
  PORT             Set port to use.

optional arguments:
  -h, --help       show this help message and exit
  --client CLIENT  Name of client, for use in plot titles.
```

server side

```
python server.py [-h] TYPE PORT

Launch server.

positional arguments:
  TYPE        Choose between TCP or UDP for transmissions.
  PORT        Set port to use.

optional arguments:
  -h, --help  show this help message and exit
```


Example
=======

First run from server `name.host@example.com`

```
python server.py TCP 8888
```

Then run from client

```
python client.py outdir all TCP name.host@example.com 8888
```


Description
===========

Server waits for an initialization message from the client. Client sends a
2-byte message, where the first byte represents the testing mode
(either round-trip, throughput, or size-message count interaction), and the
second byte is a parameter to the test mode (representing either message size
or message count, as a power of 2). The server receives the message, prepares
to receive from the client, and sends and ACK to the client.

For round-trip, the client simply sends a message to the server, and the server
echoes it back as soon as possible. The client records the time elapsed.

For throughput, the server also echoes a message back to the client. Under TCP,
we simply record the elapsed time, and divide two times the message size by the
elapsed time to get throughput. Under UDP, we have to account for lost packets
and timeouts. Both the client and server try to receive the full message, but
if they time out, they just stop receiving and record the fact that they timed
out. First the client and server echo the message, and the client records the
elapsed time. Then the client subtracts its timeout from the elapsed time if it
timed out, and the server sends an ACK or NACK to signify whether it timed out
as well, and the client subtracts another timeout if that's the case. Instead
of multiplying the received message size by two in the throughput calculation,
we take (3 times the received message size + the sent message size) divided by
two. This model assumes that exactly half of the packets were lost during each
transmission. The throughput is calculated as the estimated transmitted data
divided by the elapsed time.

Size-message count interaction is measured by sending a 1MiB message in varying
packet-sizes from the client to the server. The server simply sends an ACK to
the client, and the elapsed time divided by 1MiB is recorded.

The result of each of these tests is output to `outdir` as a box-and-whisker
plot. A sample of these plots, run between several Oswego servers and my
laptop over wifi, are in the results/ folder, and hosted [here](http://cs.oswego.edu/~dwysocki/445_1/NetworkingAssignment1.html).
