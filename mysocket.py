import socket
import time

class MySocket(socket.socket):
    def __init__(self, **kwargs):
        super(MySocket, self).__init__(**kwargs)

    def accept(self):
        """accept() -> (socket object, address info)

        Wait for an incoming connection.  Return a new socket
        representing the connection, and the address of the client.
        For IP sockets, the address info is a pair (hostaddr, port).
        """
        fd, addr = self._accept()
        sock = MySocket(family=self.family, type=self.type,
                        proto=self.proto, fileno=fd)
        # Issue #7995: if no default timeout is set and the listening
        # socket had a (non-zero) timeout, force the new socket in blocking
        # mode to override platform-specific socket flags inheritance.
        if socket.getdefaulttimeout() is None and self.gettimeout():
            sock.setblocking(True)
        return sock, addr

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

    def throughput(self, msgsize, bufsize):
        """Receives an entire message in chunks of size bufsize. Returns
        both the message and the time elapsed in us."""
        received = 0
        msg = b''

        buffer = self.recv(bufsize)
        # start the timer
        startTime = time.time()
        received += len(buffer)
        msg += buffer

        while received < msgsize:
            buffer = self.recv(bufsize)
            received += len(buffer)
            msg += buffer
        # end the timer
        endTime = time.time()

        timeElapsed = endTime - startTime
        return msg, timeElapsed
            
