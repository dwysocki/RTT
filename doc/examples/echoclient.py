import socket

s = socket.socket()
host = ""#sc.gethostname()
port = 24001

s.connect((host, port))
s.sendmsg(b"echo...echo...echoo...echooo...echoooo")
print(s.recv(1024).decode('utf-8'))
s.close()
