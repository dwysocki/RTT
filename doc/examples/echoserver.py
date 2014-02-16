import socket

s = socket.socket()
host = ""#sc.gethostname()
port = 24001
s.bind((host, port))

s.listen(5)
while True:
    client, address = s.accept()
    msg = client.recv(1024)
    client.send(msg)
    client.close()
