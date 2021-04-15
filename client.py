import socket
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('', 16665))

recv_data = s.recv(1024)

data = pickle.loads(recv_data)

print(data)

s.close()
