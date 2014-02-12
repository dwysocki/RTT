import socket as sc

s = sc.socket()
host = ""#sc.gethostname()
port = 24001

s.connect((host, port))
print(s.recv(1024))
s.close()
