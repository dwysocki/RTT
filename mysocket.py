"""This module provides special modifications to Python's base socket.socket
class for performance testing over TCP and UDP.
"""

import socket
import time

import utils

# special bytes for sending messages
ACK, NACK, MODE_ROUNDTRIP, MODE_THROUGHPUT, MODE_SIZES = range(25, 100, 15)
ACK = bytes([ACK])
NACK = bytes([NACK])
# most efficient UDP datagram size
datagram_size = 2**13

def total_transferred(send_size, recv_size):
    """Estimate the total amount of data received by the client and server combined,
    assuming an equal amount was lost in each direction.

    Example: If the client sends 100B, but only receives 80B, then we assume 10B were
    lost on the way to the server, and 10B were lost on the way back to the client.
    This means the server received 90B, making the total transfer 170B.
    (3 * 80B + 100B) / 2 = 170B, so the math checks out."""
    return (3 * recv_size + send_size) / 2

class mysocket(socket.socket):
    """A subclass of socket adding methods for TCP and UDP performance testing.
    Not intended to be used by itself, but through its subclasses serversocket
    and clientsocket."""
    def __init__(self, port=8888, udp_timeout=1.0, *args, **kwargs):
        super(mysocket, self).__init__(*args, **kwargs)
        self.port = port
        if self.is_udp():
            self.settimeout(udp_timeout)
    
    def sendby(self, msg, msgsize, bufsize):
        """Sends an entire message in chunks of size bufsize"""
        if msgsize < bufsize:
            bufsize = msgsize
        bufsize += 1 # account for string slicing being end-exclusive
        sent = 0

        start_time = time.time()
        
        while sent < msgsize:
            sent += self.send(msg[sent:sent+bufsize])

        return start_time

    def sendtoby(self, msg, msgsize, bufsize, recipient):
        """Send `msg` to `recipient` in pieces of size `bufsize`"""
        if msgsize < bufsize:
            bufsize = msgsize
        bufsize += 1
        sent = 0

        start_time = time.time()

        while sent < msgsize:
            sent += self.sendto(msg[sent:sent+bufsize], recipient)

        return start_time
    
    def recvby(self, msgsize, bufsize):
        """Receives an entire message in chunks of size bufsize"""
        received = 0
        msg = b''
        timed_out = False

        try:
            while received < msgsize:
                buffer = self.recv(bufsize)
                received += len(buffer)
                msg += buffer
        except socket.timeout:
            timed_out = True
        finally:
            return msg, received, timed_out

    def recvfromby(self, msgsize, bufsize):
        received = 0
        msg = b''

        while received < msgsize:
            buffer, address = self.recvfrom(bufsize)
            received += len(buffer)
            msg += buffer

        return msg, address

    def is_tcp(self):
        """Return whether or not the socket is using TCP"""
        return utils.get_bit(self.type, socket.SOCK_STREAM-1)

    def is_udp(self):
        """Return whether or not the socket is using UDP"""
        return utils.get_bit(self.type, socket.SOCK_DGRAM-1)
                
class serversocket(mysocket):
    """A subclass of mysocket for server-side network performance testing"""
    def __init__(self, *args, **kwargs):
        super(serversocket, self).__init__(*args, **kwargs)
        self.host = socket.gethostname()

    def accept(self):
        """accept() -> (socket object, address info)

        Wait for an incoming connection.  Return a new socket
        representing the connection, and the address of the client.
        For IP sockets, the address info is a pair (hostaddr, port).
        """
        fd, addr = self._accept()
        sock = serversocket(family=self.family, type=self.type,
                            proto=self.proto, fileno=fd)
        # Issue #7995: if no default timeout is set and the listening
        # socket had a (non-zero) timeout, force the new socket in blocking
        # mode to override platform-specific socket flags inheritance.
        if socket.getdefaulttimeout() is None and self.gettimeout():
            sock.setblocking(True)
        return sock, addr

    def activate(self, *args, **kwargs):
        self.bind((self.host, self.port))
        if self.is_tcp():
            print("TCP: {}".format(self.is_tcp()))
            return self._tcp_loop(*args, **kwargs)
        elif self.is_udp():
            print("UDP: {}".format(self.is_udp()))
            return self._udp_loop(*args, **kwargs)
        else:
            raise ValueError("type {} serversocket not implemented".format(
                self.type))

    def _tcp_loop(self, *args, **kwargs):
        """Listen for client connections over TCP and react accordingly."""
        try:
            self.listen(1)

            while True:
                client, address = self.accept()
                print("connected to {}".format(address))

                try:
                    # receive 2-byte command message from client.
                    # first byte selects the mode, the other is a mode-specific option
                    # to be interpreted by that mode's function
                    commands = client.recv(2)
                    mode, option = commands

                    if mode == MODE_ROUNDTRIP:
                        self._roundtrip_tcp(client, option, *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_tcp(client, option, *args, **kwargs)
                    elif mode == MODE_SIZES:
                        self._sizes_tcp(client, option, *args, **kwargs)
                    else:
                        client.send(NACK)
                        print("mode {} not implemented".format(mode))
                finally:
                    client.close()
        finally:
            self.close()

    def _udp_loop(self, *args, **kwargs):
        """Listen for client connections over UDP and react accordingly."""
        try:
            while True:
                try:
                    commands, address = self.recvfrom(2)
                    print("connected to {}".format(address))
                    if len(commands) != 2:
                        continue
                    mode, msgsize = commands

                    if mode == MODE_ROUNDTRIP:
                        self._roundtrip_udp(address, msgsize, *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_udp(address, msgsize, *args, **kwargs)
                    else:
                        self.sendto(NACK, address)
                        print("mode not implemented")
                except socket.timeout as to:
                    print(".", end="")
        finally:
            self.close()

    def _roundtrip_tcp(self, client, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements using TCP,
        server-side."""
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # send message back
        client.sendby(msg, msgsize, msgsize)

    def _roundtrip_udp(self, address, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements using UDP,
        server-side."""
        msgsize = 2**msgsize
        # send ACK
        self.sendto(ACK, address)

        # receive message
        try:
            msg = self.recv(msgsize)
            self.sendto(msg, address)
        except socket.timeout as to:
            print("{} {}".format(address, to))

    def _throughput_tcp(self, client, msgsize, *args, **kwargs):
        """Perform throughput performance measurements using TCP,
        server-side."""
        msgsize = 2**msgsize
        client.send(ACK)
        

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # send ACK
        client.send(ACK)

    def _throughput_udp(self, address, msgsize, *args, **kwargs):
        """Perform throughput performance measurements using UDP,
        server-side."""
        msgsize = 2**msgsize

        # send the client the server's timeout duration, so it can be subtracted
        # from the elapsed time
        self.sendto(bytes([int(self.timeout)]), address)
        
        # receive message
        msg, received, timed_out = self.recvby(msgsize, datagram_size)
        # echo message back if one was received
        self.sendtoby(msg, received, datagram_size, address)

        # double timeout in case client times out
        self.settimeout(2 * self.timeout)
        
        try:
            # wait for client to ACK that all data was received
            self.recv(1)
            # tell client whether we timed out when receiving the message or not
            self.sendto(ACK if timed_out else NACK, address)
        finally:
            self.settimeout(self.timeout / 2)

    def _sizes_tcp(self, client, n, *args, **kwargs):
        """Perform size-number of message interaction measurements using TCP,
        server-side."""
        msgsize = 2**30
        n = 2**n
        bufsize = msgsize // n

        print("ACKING")
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, bufsize)[0]
        print("msg received")
        # send ACK
        client.send(ACK)

class clientsocket(mysocket):
    """A subclass of mysocket for client-side network performance testing"""
    def __init__(self, host='', *args, **kwargs):
        super(clientsocket, self).__init__(*args, **kwargs)
        self.host = host
        if self.is_tcp():
            self.connect((self.host, self.port))
        elif self.is_udp():
            self.destination = (self.host, self.port)

    def roundtrip(self, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements, client-side.
        Determines whether to use TCP or UDP based on the type of the socket"""
        if self.is_tcp():
            return self._roundtrip_tcp(msgsize, *args, **kwargs)
        elif self.is_udp():
            return self._roundtrip_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def throughput(self, msgsize, latency, *args, **kwargs):
        """Perform throughput performance measurements, client-side.
        Determines whether to use TCP or UDP based on the type of the socket"""
        if self.is_tcp():
            return self._throughput_tcp(msgsize, latency, *args, **kwargs)
        elif self.is_udp():
            return self._throughput_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def sizes(self, n, *args, **kwargs):
        """Perform size-number of message interaction measurements, client-side.
        Determines whether to use TCP or UDP based on the type of the socket"""
        if self.is_tcp():
            return self._sizes_tcp(n, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def _roundtrip_tcp(self, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements using TCP,
        client-side."""
        self.sendall(bytes([MODE_ROUNDTRIP, msgsize]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
        msg = utils.makebytes(msgsize)
        
        start_time = time.time()

        self.sendall(msg)
        recvmsg = self.recvby(msgsize, msgsize)[0]

        end_time = time.time()
        elapsed_time = end_time - start_time

        # check for corruption here? #
        
        return elapsed_time

    def _roundtrip_udp(self, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements using UDP,
        client-side."""
        self.sendto(bytes([MODE_ROUNDTRIP, msgsize]), self.destination)
        try:
            self.recv(1)

            msgsize = 2**msgsize
            msg = utils.makebytes(msgsize)

            start_time = time.time()

            self.sendto(msg, self.destination)
            recvmsg = self.recv(msgsize)

            end_time = time.time()
            elapsed_time = end_time - start_time

            return elapsed_time
        except socket.timeout as to:
            print("{} {}".format(self.destination, to))
            time.sleep(1.0)
            return

    def _throughput_tcp(self, msgsize, latency, *args, **kwargs):
        """Perform throughput performance measurements using TCP,
        client-side."""
        self.sendall(bytes([MODE_THROUGHPUT, msgsize]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
        msg = utils.makebytes(msgsize)

        start_time = time.time()

        self.sendall(msg)
        self.recv(1)

        end_time = time.time()
        elapsed_time = end_time - start_time - latency

        return msgsize / elapsed_time

    def _throughput_udp(self, msgsize, *args, **kwargs):
        """Perform throughput performance measurements using UDP,
        client-side."""
        # send setup message
        self.sendto(bytes([MODE_THROUGHPUT, msgsize]), self.destination)
        
        try:
            # server ACKs by sending its timeout duration, which will be used
            # in the total time calculation
            server_timeout = self.recv(1)[0]
            print("server timeout: {}".format(server_timeout))

            timeout_multiplier = 1# msgsize * 2
            msgsize = 2**msgsize
            msg = utils.makebytes(msgsize)

            try:
                self.settimeout(timeout_multiplier * self.timeout)
                start_time = time.time()

                # send the message
                self.sendtoby(msg, msgsize, datagram_size, self.destination)
                # receive the echoed message and record how much was actually
                # received
                recvmsg, received, timed_out = self.recvby(msgsize, datagram_size)

                end_time = time.time()
                elapsed_time = (end_time - start_time -
                                (self.timeout if timed_out else 0))

                # let server know that message has been received, so that server can
                # ACK or NACK whether or not it timed out
                self.sendto(ACK, self.destination)

                try:
                    # await server's confirmation that its timeout was reached
                    timed_out = self.recv(1) is ACK
                    elapsed_time -= server_timeout if timed_out else 0
                    data_transferred = total_transferred(msgsize, received)
                    throughput = data_transferred / elapsed_time

                    return throughput
                except socket.timeout:
                    # throw away this trial
                    return
            finally:
                self.settimeout(self.timeout / timeout_multiplier)
        except socket.timeout as to:
            print("{} {}".format(self.destination, to))
            # give the server a chance to time out
            time.sleep(1.0)

    def _sizes_tcp(self, n, *args, **kwargs):
        """Perform size-number of message interaction measurements using TCP,
        client-side."""
        self.sendall(bytes([MODE_SIZES, n]))
#        if self.recv(1) is NACK:
#            return
        self.recv(1)
        
        msgsize = 2**30
        n = 2**n
        msg = utils.makebytes(msgsize)
        bufsize = int(msgsize/n)

        start_time = time.time()

        # send messages
        self.sendby(msg, msgsize, bufsize)
        # wait for ACK
        self.recv(1)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return elapsed_time
