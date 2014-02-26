import socket
import time

import utils

MODE_ROUNDTRIP, MODE_THROUGHPUT, MODE_SIZES = range(3)
NACK, ACK = b'0', b'1'

class mysocket(socket.socket):
    def __init__(self, port=8888, udp_timeout=1.0, *args, **kwargs):
        super(mysocket, self).__init__(*args, **kwargs)
        self.port = port
        if (self.type % 2**11) == socket.SOCK_DGRAM:
            self.settimeout(udp_timeout)
    
    def sendby(self, msg, msgsize, bufsize):
        """Sends an entire message in chunks of size bufsize"""
        bufsize += 1 # account for string slicing being end-exclusive
        sent = 0

        start_time = time.time()
        
        while sent < msgsize:
            sent += self.send(msg[sent:sent+bufsize])

        return start_time

    def sendtoby(self, msg, msgsize, bufsize, recipient):
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

        while received < msgsize:
            buffer = self.recv(bufsize)
            received += len(buffer)
            msg += buffer

        return msg

    def recvfromby(self, msgsize, bufsize):
        received = 0
        msg = b''

        while received < msgsize:
            buffer, address = self.recvfrom(bufsize)
            received += len(buffer)
            msg += buffer

        return msg, address
                
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
        if (self.type % 2**11) == socket.SOCK_STREAM:
            return self._tcp_loop(*args, **kwargs)
        elif (self.type % 2**11) == socket.SOCK_DGRAM:
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
                    commands = client.recvby(3, 3)
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
                    
                    mode, msgsize = commands

                    if mode == MODE_ROUNDTRIP:
                        self._roundtrip_udp(address, msgsize, *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_udp(address, msgsize, *args, **kwargs)
                    else:
                        self.sendto(NACK, address)
                        print("mode not implemented")
                except socket.timeout as to:
                    pass
        finally:
            self.close()

    def _roundtrip_tcp(self, client, msgsize, *args, **kwargs):
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)
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
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)
        # send ACK
        client.send(ACK)

    def _throughput_udp(self, address, msgsize, *args, **kwargs):
        msgsize = 2**msgsize
        datagram_size = 2**13
        # send ACK
        self.sendto(ACK, address)

        # receive message
        msg = self.recvby(msgsize, datagram_size)
        # send ACK
        self.sendto(ACK, address)

    def _sizes_tcp(self, client, msgsize, n, *args, **kwargs):
        msgsize = 2**msgsize
        n = 2**n
        bufsize = int(msgsize/n)

        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, bufsize)
        # send ACK
        client.send(ACK)

class clientsocket(mysocket):
    def __init__(self, host='', *args, **kwargs):
        super(clientsocket, self).__init__(*args, **kwargs)
        self.host = host
        if (self.type % 2**11) == socket.SOCK_STREAM:
            self.connect((self.host, self.port))
        if (self.type % 2**11) == socket.SOCK_DGRAM:
            self.destination = (self.host, self.port)

    def roundtrip(self, msgsize, *args, **kwargs):
        if (self.type % 2**11) == socket.SOCK_STREAM:
            return self._roundtrip_tcp(msgsize, *args, **kwargs)
        elif (self.type % 2**11) == socket.SOCK_DGRAM:
            return self._roundtrip_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def throughput(self, msgsize, *args, **kwargs):
        if (self.type % 2**11) == socket.SOCK_STREAM:
            return self._throughput_tcp(msgsize, *args, **kwargs)
        elif (self.type % 2**11) == socket.SOCK_DGRAM:
            return self._throughput_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def sizes(self, msgsize, n, *args, **kwargs):
        if (self.type % 2**11) == socket.SOCK_STREAM:
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
        recvmsg = self.recvby(msgsize, msgsize)

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

    def _throughput_udp(self, *args, **kwargs):
        # send data in 8KB blocks
        self.sendto(bytes([MODE_ROUNDTRIP, msgsize, 0]), self.destination)
        try:
            # await ACK
            self.recv(1)

            msgsize = 2**msgsize
            msg = utils.makebytes(msgsize)

            start_time = time.time()

            self.sendtoby(msg, msgsize, 2**13, self.destination)
            response = self.recv(1)

            end_time = time.time()
            elapsed_time = end_time - start_time

            return elapsed_time if response == ACK else None
        except socket.timeout as to:
            print("{} {}".format(self.destination, to))
            time.sleep(1.0)
            return

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
