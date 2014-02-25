import socket
import time

import utils

MODE_QUIT, MODE_ROUNDTRIP, MODE_THROUGHPUT, MODE_SIZES = range(4)
NACK, ACK = b'0', b'1'

class mysocket(socket.socket):
    def __init__(self, port=8888, *args, **kwargs):
        super(mysocket, self).__init__(*args, **kwargs)
        self.port = port

    def echo(self, msg, msgsize, bufsize):
        """Sends a message and then waits for an echo, returning the time and
        received message. Assumes that host will echo the message.
        """
        start_time = self.sendby(msg, msgsize, bufsize)
        msg = self.recvby(msgsize, bufsize)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return msg, elapsed_time
    
    def sendby(self, msg, msgsize, bufsize):
        """Sends an entire message in chunks of size bufsize"""
        bufsize += 1 # account for string slicing being end-exclusive
        sent = 0

        start_time = time.time()
        
        while sent < msgsize:
            sent += self.send(msg[sent:sent+bufsize])

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
        if self.type == socket.SOCK_STREAM:
            return self._tcp_loop(*args, **kwargs)
        elif self.type == socket.SOCK_DGRAM:
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

                    if mode == MODE_QUIT:
                        print("Ending server")
                        # the two finally blocks will close all sockets
                        return
                    elif mode == MODE_ROUNDTRIP:
                        self._roundtrip_tcp(client, options[0], *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_tcp(client, options[0],
                                             *args, **kwargs)
                    elif mode == MODE_SIZES:
                        self._sizes_tcp(client, *(options + args), **kwargs)
                    else:
                        client.send(NACK)
                        print("mode not implemented")
                finally:
                    client.close()
        finally:
            self.close()

    def _udp_loop(self, *args, **kwargs):
        print("UDP not yet implemented")

    def _roundtrip_tcp(self, client, msgsize, *args, **kwargs):
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)
        # send message back
        client.sendby(msg, msgsize, msgsize)

    def _roundtrip_udp(self, client, msgsize, *args, **kwargs):
        pass

    def _throughput_tcp(self, client, msgsize, *args, **kwargs):
        msgsize = 2**msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)
        # send ACK
        client.send(ACK)

    def _throughput_udp(self, client, msgsize, *args, **kwargs):
        pass
    
    def _sizes_tcp(self, client, msgsize, n, *args, **kwargs):
        msgsize = 2**msgsize


class clientsocket(mysocket):
    def __init__(self, host='', *args, **kwargs):
        super(clientsocket, self).__init__(*args, **kwargs)
        self.host = host
        self.connect((self.host, self.port))

    def roundtrip(self, msgsize, *args, **kwargs):
        self.sendall(bytes([MODE_ROUNDTRIP, msgsize, 0]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize

        if self.type == socket.SOCK_STREAM:
            return self._roundtrip_tcp(msgsize, *args, **kwargs)
        elif self.type == socket.SOCK_DGRAM:
            return self._roundtrip_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def throughput(self, msgsize, *args, **kwargs):
        self.sendall(bytes([MODE_THROUGHPUT, msgsize]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
        
        if self.type == socket.SOCK_STREAM:
            return self._throughput_tcp(msgsize, *args, **kwargs)
        elif self.type == socket.SOCK_DGRAM:
            return self._throughput_udp(msgsize, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def sizes(self, msgsize, n, *args, **kwargs):
        self.sendall(bytes([MODE_SIZES, msgsize, n]))
        if self.recv(1) is NACK:
            return

        msgsize = 2**msgsize
        n = 2**n
        
        if self.type == socket.SOCK_STREAM:
            return self._sizes_tcp(msgsize, n, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))
    
    def _roundtrip_tcp(self, msgsize, *args, **kwargs):
        msg = utils.makebytes(msgsize)
        
        start_time = time.time()

        self.sendall(msg)
        recvmsg = self.recvby(msgsize, msgsize)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # check for corruption here? #
        
        return elapsed_time
        

    def _roundtrip_udp(self, msgsize, *args, **kwargs):
        command = bytes([MODE_ROUNDTRIP, msgsize])

    def _throughput_tcp(self, msgsize, *args, **kwargs):
        msg = utils.makebytes(msgsize)

        start_time = time.time()

        self.sendall(msg)
        recv(1)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return elapsed_time

    def _throughput_udp(self, *args, **kwargs):
        command = bytes([MODE_THROUGHPUT, msgsize, n])

    def _sizes_tcp(self, *args, **kwargs):
        command = bytes([MODE_SIZES, msgsize, n])

