RTT
===

CSC445 Assignment 1: An exercise in measuring transfer times and throughput over
TCP and UDP.


Requirements
============

client side
  - Python 3.3 or higher (will probably work on earlier releases as well)
  - numpy
  - matplotlib

server side
  - Python 3.3 or higher


Usage
=====

client side

    python client.py [-h] [--client CLIENT] OUTPUT MODE TYPE HOST PORT

server side

    python server.py [-h] TYPE PORT


Example
=======

First run from server `name@example.com`

    python server.py TCP 8888

Then run from client

    python client.py outdir all TCP 8888 name@example.com


License
=======

Copyright © Dan Wysocki

GNU General Public License version 3
