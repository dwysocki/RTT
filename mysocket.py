import socket
import time

import utils

MODE_ROUNDTRIP, MODE_THROUGHPUT, MODE_SIZES = range(3)
NACK, ACK = b'0', b'1'

class mysocket(socket.socket):
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

        try:
            while received < msgsize:
                buffer = self.recv(bufsize)
                received += len(buffer)
                msg += buffer
        finally:
            return msg, received

    def recvfromby(self, msgsize, bufsize):
        received = 0
        msg = b''

        while received < msgsize:
            buffer, address = self.recvfrom(bufsize)
            received += len(buffer)
            msg += buffer

        return msg, address

    def is_tcp(self):
        return utils.get_bit(self.type, socket.SOCK_STREAM-1)

    def is_udp(self):
        return utils.get_bit(self.type, socket.SOCK_DGRAM-1)
                
class serversocket(mysocket):
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
        try:
            self.listen(1)

            while True:
                client, address = self.accept()
                print("connected to {}".format(address))

                try:
                    # receive 3-byte command message from client.
                    # first byte selects the mode, the other two are
                    # mode-specific options, to be parsed by that mode's
                    # function
                    commands = client.recvby(3, 3)[0]
                    mode, options = commands[0], commands[1:]

                    if mode == MODE_ROUNDTRIP:
                        self._roundtrip_tcp(client, options[0], *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_tcp(client, options[0],
                                             *args, **kwargs)
                    elif mode == MODE_SIZES:
                        self._sizes_tcp(client, *(tuple(options) + args),
                                        **kwargs)
                    else:
                        client.send(NACK)
                        print("mode not implemented")
                finally:
                    client.close()
        finally:
            self.close()

    def _udp_loop(self, *args, **kwargs):
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
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # send message back
        client.sendby(msg, msgsize, msgsize)

    def _roundtrip_udp(self, address, msgsize, *args, **kwargs):
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
        """Server-side TCP throughput method"""
        msgsize = 2**msgsize
        client.send(ACK)
        

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # send ACK
        client.send(ACK)

    def _throughput_udp(self, address, msgsize, *args, **kwargs):
        """Server-side UDP throughput method"""
        msgsize = 2**msgsize
        datagram_size = 2**13

        # send the client the server's timeout duration, so it can be subtracted
        # from the elapsed time
        self.sendto(bytes([int(self.timeout)]), address)
        
        # receive message
        msg, received = self.recvby(msgsize, datagram_size)
        # echo message back if one was received
        if received > 0:
            self.sendtoby(msg, received, datagram_size, address)
            tries_left = 10
            while tries_left > 0:
                try:
                    print("ACK: {}".format(self.recv(1)))
                    self.sendto(str(received).encode(), address)
                    return      
                except socket.timeout:
                    tries_left -= 1
                    print("tries left: {}".format(tries_left))

    def _sizes_tcp(self, client, msgsize, n, *args, **kwargs):
        msgsize = 2**msgsize
        n = 2**n
        bufsize = int(msgsize/n)

        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, bufsize)[0]
        # send ACK
        client.send(ACK)

class clientsocket(mysocket):
    def __init__(self, host='', *args, **kwargs):
        super(clientsocket, self).__init__(*args, **kwargs)
        self.host = host
        if self.is_tcp():
            self.connect((self.host, self.port))
        elif self.is_udp():
            self.destination = (self.host, self.port)

    def roundtrip(self, msgsize, *args, **kwargs):
        if self.is_tcp():
            return self._roundtrip_tcp(msgsize, *args, **kwargs)
        elif self.is_udp():
            return self._roundtrip_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def throughput(self, msgsize, *args, **kwargs):
        if self.is_tcp():
            return self._throughput_tcp(msgsize, *args, **kwargs)
        elif self.is_udp():
            return self._throughput_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def sizes(self, msgsize, n, *args, **kwargs):
        if self.is_tcp():
            return self._sizes_tcp(msgsize, n, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))
    
    def _roundtrip_tcp(self, msgsize, *args, **kwargs):
        self.sendall(bytes([MODE_ROUNDTRIP, msgsize, 0]))
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
        self.sendto(bytes([MODE_ROUNDTRIP, msgsize, 0]), self.destination)
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

    def _throughput_tcp(self, msgsize, *args, **kwargs):
        self.sendall(bytes([MODE_THROUGHPUT, msgsize, 0]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
        msg = utils.makebytes(msgsize)

        start_time = time.time()

        self.sendall(msg)
        self.recv(1)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return elapsed_time

    def _throughput_udp(self, msgsize, *args, **kwargs):
        """Client-side UDP throughput method"""
        # send setup message
        self.sendto(bytes([MODE_THROUGHPUT, msgsize, 0]), self.destination)
        
        try:
            # server ACKs by sending its timeout duration, which will be used
            # in the total time calculation
            server_timeout = self.recv(1)[0]
            print("server timeout: {}".format(server_timeout))

            timeout_multiplier = msgsize * 2
            msgsize = 2**msgsize
            # send 8KB datagrams
            datagram_size = 2**13
            msg = utils.makebytes(msgsize)

            try:
                self.settimeout(timeout_multiplier * self.timeout)
                start_time = time.time()

                # send the message
                self.sendtoby(msg, msgsize, datagram_size, self.destination)
                # receive the echoed message and record how much was actually
                # received
                recvmsg, client_received = self.recvby(msgsize, datagram_size)

                end_time = time.time()
                elapsed_time = (end_time - start_time -
                                server_timeout - self.timeout)
                print("elapsed time: {}".format(elapsed_time))
                print("client received: {}".format(client_received))

                ##!!##
                ## We need to spin on the following part. The server is
                ## spinning here, but the client needs to spin as well.
                ## Do 10 tries
                ##!!##
                tries_left = 10
                while tries_left > 0:
                    try:
                        self.sendto(ACK, self.destination)
                        server_received = int(self.recv(8).decode('utf-8'))
                        print("server received: {}".format(server_received))
                        data_transmitted = client_received + server_received
                        throughput = data_transmitted / elapsed_time
                        return throughput
                    except socket.timeout:
                        tries_left -= 1
                        print("tries left: {}".format(tries_left))
                # tell server that we've finished receiving and want to know
                # how much the server received
                # self.sendto(ACK, self.destination)
                # server_received = int(self.recv(8).decode('utf-8'))
                # print("server received: {}".format(server_received))

                # data_transmitted = client_received + server_received
                # throughput = data_transmitted / elapsed_time
                # return throughput
            finally:
                self.settimeout(self.timeout / timeout_multiplier)
        except socket.timeout as to:
            print("{} {}".format(self.destination, to))
            # give the server a chance to stop sending
            time.sleep(1.0)

    def _sizes_tcp(self, msgsize, n, *args, **kwargs):
        self.sendall(bytes([MODE_SIZES, msgsize, n]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
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
