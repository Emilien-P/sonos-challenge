
#!/usr/bin/env python

import socket

HOST = "localhost"
PORT = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

name = "this is the name that the model predicts"
command = "this is the result from google speech api"

sock.sendall(name + "/" + command + "\n")
