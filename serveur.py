import socket
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 16665))
s.listen(5)

client, address = s.accept()

liste = [5, 1, 0, 1]

data = pickle.dumps(liste)

client.send(data)

s.close()
