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


        self._resource_ok = False
        self._nest_ok = False
        self._wall_ok = False

    @property
    def ressource_ok(self):
        return self._resource_ok

    @property
    def nest_ok(self):
        return self._nest_ok

    @property
    def wall_ok(self):
        return self._wall_ok

    def connect(self):
        try:
            self._socket.connect((self._ip, self._port))
            self.receive()
        except ConnectionRefusedError:
            print("Erreur serveur non connecté")

    def receive(self):
        while True:
            recv_data = self._socket.recv(1024)
            data = pickle.loads(recv_data)
            is_good, element = data[0], data[1]
            if is_good:
                if element == "Resource":
                    self._resource_ok = True
                elif element == "Wall":
                    self._wall_ok = True
            else:
                self._resource_ok = False
                self._nest_ok = False
                self._wall_ok = False

    def send(self, element, pos, data):
        """
        Fonction d'envoit au serveur
        element:  type de donnée
        pos: liste de position [x, y]
        data: taille de l'objet
        """
        all = pickle.dumps([element, pos, data])
        self._socket.send(all)
