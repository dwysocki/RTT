import socket

class MySocket(socket.socket):
    def __init__(self, **kwargs):
        super(MySocket, self).__init__(**kwargs)

    def sendby(self, msg, msgsize, bufsize):
        """Sends an entire message in chunks of size bufsize"""
        bufsize += 1 # account for string slicing being end-exclusive
        sent = 0
        
        while sent < msgsize:
            sent += self.send(msg[sent:sent+bufsize])

    def recvby(self, msgsize, bufsize):
        """Receives an entire message in chunks of size bufsize"""
        received = 0
        msg = b''

        while received < msgsize:
            buffer = self.recv(bufsize)
            received += len(buffer)
            msg += buffer

        return msg
