import socket

s = socket.socket()
host = ""#sc.gethostname()
port = 24001
s.bind((host, port))

s.listen(5)
while True:
    client, address = s.accept()
    print("Got connection.")
    client.send(b"Thank you for connecting")
    client.close()
