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

        self._interface = None

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

    '''
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

    '''
    def send(self, element, pos, data):
        """
        Fonction d'envoi au serveur
        element:  type de donnée
        pos: liste de position [x, y]
        data: taille de l'objet
        """
        all = pickle.dumps([element, pos, data])
        self._socket.send(all)


    def set_ready(self):
        """Informe le serveur que ce client est prêt"""
        print("Ready envoyé")
        self._socket.send("Ready".encode())

    def unset_ready(self):
        """Informe le serveur que ce client n'est plus prêt"""
        pass

    def ask_object(self, object_type, coords, size=None, width=None, color=None):
        """
        Demande au serveur si on peut placer
        un élément d'un type et d'une taille donnés,
        aux coordonnées données.
        """
        print("object_type :", object_type, "name :", object_type.__name__)
        str_type = object_type.__name__
        print("objet demandé : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
        data = pickle.dumps([str_type, coords, size, width, color])
        self._socket.send(data)

    # def ask_check_all_coords(self, coords_list, width):
    #     """
    #     Demande au serveur si la liste de positions ne pose pas problème.
    #     La première valeur, None, signale au serveur que ce n'est qu'un test.
    #     """
    #     print("demande pour les coords :", coords_list)
    #     data = pickle.dumps([None, coords_list, width])
    #     self._socket.send(data)

    def receive(self):
        """Reçoit les signaux envoyés par les clients pour les objets créés"""
        while True:
            recv_data = self._socket.recv(1024)
            try:
                data = pickle.loads(recv_data)
            except pickle.UnpicklingError:
                data = recv_data
            if type(data) == list:
                # Si c'est une liste, on sait que la demande est éffectuée pour crée un élément
                str_type, pos, size, width, color = data[0], data[1], data[2], data[3], data[4]

                # Communique l'information d'un nouvel objet à l'interface
                print("dit à interface de créer :", str_type, pos, size, width, color)
                self._interface._create_object(str_type, pos, size=size, width=width, color=color)
            elif data.decode() == "GO":
                self._interface.start_game()


    def _set_interface(self, interface):
        """
        Garde en mémoire l'interface, pour
        pouvoir lui envoyer des informations
        """
        self._interface = interface
