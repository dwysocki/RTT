import socket

'''
s = sc.socket()
host = ""#sc.gethostname()
port = 24001
s.bind((host, port))

s.listen(5)
while True:
    client, address = s.accept()
    print("Got connection.")
    client.send(b"Thank you for connecting")
    client.close()
'''

class StopWaitSocket(socket.socket):
    def __init__(self, bufsize=1024, **kwargs):
        self.bufsize = bufsize
        super(StopWaitSocket, self).__init__(**kwargs)

    def sendmessage(self, msg, **kwargs):
        totalsent = 0
        msg_len = len(msg)
        while totalsent < msg_len:
            sent = self.send(msg[totalsent:], **kwargs)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent

    def recvmessage(self, **kwargs):
        msg = b""
        while len(msg) < __:
            pass

class ServerSocket:
    def __init__(self, sock=None, family=sc.AF_INET, type=sc.SOCK_STREAM,
                 msg_len=1024):
        if sock is None:
            self.sock = sc.socket(family, type)
        else:
            self.sock = sock
        self.msg_len = msg_len

    def connect(self, host, port):
        self.sock.connect((host, port))

    def listen(self, n):
        self.sock.listen(n)

    def send(self, msg):
        totalsent = 0
        while totalsent < self.msg_len:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent

    def recv(self):
        msg = b""
        while len(msg) < self.msg_len:
            chunk = self.sock.recv(msg_len - len(msg))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            msg += chunk
        return msg


if __name__ == "__main__":
    s = ServerSocket()
    host = ""
    port = 14400
    s.connect(host, port)
    
    s.listen(5)
    while True:
        client, address = s.accept()
        print("Got connection.")
        client.send(b"Thank you for connecting")
        client.close()
