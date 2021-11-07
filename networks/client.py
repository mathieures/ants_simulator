import sys

import socket
import pickle
import threading

class Client:
    """
    Classe responsable de la réception, la distribution
    et l'envoi de données depuis et vers le serveur.
    """
    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, new_interface):
        self._interface = new_interface

    @property
    def connected(self):
        return self._connected

    @property
    def is_admin(self):
        return self._is_admin

    def __init__(self, ip, port):
        try:
            assert isinstance(ip, str), "[Error] the server IP is not a valid string"
            assert isinstance(port, int), "[Error] the server port is not a valid integer"
            assert len(ip) > 0, "[Error] the server IP cannot be empty"
        except AssertionError as e:
            print(e)
            sys.exit()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = ip
        self._port = port

        self._connected = True

        self._interface = None
        self._is_admin = False


    def connect(self):
        try:
            self._socket.connect((self._ip, self._port))
            self._connected = True
            self.receive()
        except ConnectionRefusedError:
            print("[Error] No server found")
            sys.exit(1)

    # def send(self, element, pos, data):
    #     """
    #     Fonction d'envoi au serveur
    #     element:  type de donnée
    #     pos: liste de position [x, y]
    #     data: taille de l'objet
    #     """
    #     all = pickle.dumps([element, pos, data])
    #     self._socket.send(all)

    def set_ready(self):
        """Informe le serveur que ce client est prêt"""
        self._socket.send("ready".encode())

    def set_notready(self):
        """Informe le serveur que ce client n'est plus prêt (a faire)"""
        self._socket.send("not ready".encode())

    def ask_object(self, object_type, position, size=None, color=None):
        """
        Demande au serveur si on peut placer
        un élément d'un type et d'une taille donnés
        à la position donnée.
        """
        str_type = object_type.__name__ # Nom de classe de l'objet
        data = pickle.dumps([str_type, position, size, color])
        try:
            self._socket.send(data)
        except BrokenPipeError:
            print("[Error] fatal error while sending data. Exiting.")
            sys.exit(1)

    def undo_object(self, str_type):
        """ Demande au serveur d'annuler le placement d'un objet """
        data = pickle.dumps(["undo", str_type])
        try:
            self._socket.send(data)
        except BrokenPipeError:
            print("[Error] fatal error while sending data. Exiting.")
            sys.exit(1)

    def ask_faster_sim(self):
        print("ask_faster_sim")
        self._socket.send("faster".encode())
    
    def ask_slower_sim(self):
        print("ask_slower_sim")
        self._socket.send("slower".encode())

    def disconnect(self):
        self._socket.close()
        sys.exit(1)

    def receive(self):
        """Reçoit les signaux envoyés par les clients pour les objets créés"""
        # Note : on peut ne pas le mettre dans un thread car le client ne fait que recevoir
        while True:
            try:
                recv_data = self._socket.recv(102400)
            except ConnectionResetError:
                print("[Error] server disconnected.")
                self._interface.quit_app(force=True)
                sys.exit(1)
            try:
                data = pickle.loads(recv_data)
            except pickle.UnpicklingError:
                data = recv_data

            # Si on doit bouger des fourmis
            if isinstance(data, str):
                if data == "GO":
                    self._interface.countdown()
                elif data == "admin":
                    self._admin = True
                    self._interface.show_admin_buttons()
            else:
                '''
                data est de la forme : ["move_ants", [deltax_fourmi1, deltay_fourmi1], [deltax_fourmi2, deltay_fourmi2]...]
                ou alors : [["move_ants", [deltax...]], ["pheromones", (fourmi1x, fourmi1y)...]]
                # Note : les listes internes peuvent contenir un autre élément, la couleur de la fourmi.
                '''

                # Si on a les mouvements des fourmis et les pheromones en meme temps
                if len(data) == 2 and data[0][0] == "move_ants":
                    # On bouge les fourmis
                    self._interface.move_ants(data[0][1:])

                    # On cree ou fonce les pheromones
                    self._interface.create_pheromones(data[1][1:])

                elif data[0] == "move_ants":
                    self._interface.move_ants(data[1:])

                # Si on doit creer des fourmis
                elif data[0] == "ants":
                    # data est de la forme
                    """
                    ["ants",
                        [coords_fourmi1, couleur_fourmi1],
                        [coords_fourmi2, couleur_fourmi2], …]
                    """
                    self._interface.create_ants(data[1:])

                # Si on reçoit la couleur locale de l'interface
                elif data[0] == "color":
                    # print("reçu couleur :", data[1])
                    self._interface.local_color = data[1]

                # Si c'est un objet cree par un client,
                elif data[0] == "create":
                    # data est un tuple de la forme
                    '''
                    ('create', [('str_type', [[(x, y), size, width, 'color'],
                                              [(x2, y2), …]]),
                                ('str_type2', [[(x3, y3), size3, width3, 'color3'],
                                               [(…)]])])
                    '''
                    for creation_type in data[1:]:
                        # creation_type est un tuple ('str_type', (…),(…), …)
                        print(f"{creation_type=}")
                        str_type = creation_type[0]
                        for creation_properties in creation_type[1]:
                            print(f"    {creation_properties=}")
                            pos, size, color = creation_properties
                            # Communique l'information d'un nouvel objet a l'interface
                            self._interface.create_object(str_type, pos, size=size, color=color)
                else:
                    # Si on arrive ici c'est qu'il manque le type de data qu'il faut analyser
                    raise TypeError("[Error] Cannot process received data: parsing hint is missing")
                
