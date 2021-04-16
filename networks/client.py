import sys

import socket
import pickle
import threading


class Client:
    def __init__(self, ip, port):
        try:
            assert isinstance(ip, str), "Erreur l'IP n'est pas une châine de caractère valide"
            assert isinstance(port, int), "Erreur le port n'est pas un entier valide"
        except AssertionError as e:
            print(e)
            sys.exit()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = ip
        self._port = port

    def connect(self):
        try:
            self._socket.connect((self._ip, self._port))
            self.receive()
        except ConnectionRefusedError:
            print("Erreur serveur non connecté")

    def receive(self):
        while True:
            recv_data = self._socket.recv(2048)
            data = pickle.dumps(recv_data)

            print(type(data))

    def send(self, data):
        pass