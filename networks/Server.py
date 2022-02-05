import sys
import socket
import pickle
from threading import Thread
from time import sleep
from math import dist as distance

from .utils import (
    random_color,
    ReadyState,
    SpeedRequest,
    id_generator as utils_id_generator
)

from .ServerWindow import ServerWindow
from .Simulation import Simulation


class Server:
    """
    Application du serveur.
    - Si les arguments IP, PORT et MAX_CLIENTS ne sont pas renseignés,
        une fenêtre de configuration s'ouvre.
    - Si le paramètre '-nowindow' est spécifié ou la case correspondante est
        cochée dans la fenêtre de configuration, il n'y aura pas de fenêtre
        ouverte pendant le fonctionnement du serveur, et l'utilisateur devra
        terminer le script par ses propres moyens.
    """
    clients = {} # dictionnaire qui associe un socket a un dict { "ready": bool, "thread": Thread }
    # Note : on est oblige de garder une trace de quel client est pret pour mettre a jour la window

    id_generator = None

    @classmethod
    def get_new_id(cls):
        """Méthode de classe qui permet de générer un identifiant"""
        # S'il n'y en avait pas pour cette classe, on en crée un
        if cls.id_generator is None:
            cls.id_generator = utils_id_generator()
        # Dans tous les cas on renvoit le prochain id
        return next(cls.id_generator)

    @property
    def online(self):
        return self._online

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def max_clients(self):
        return self._max_clients

    def __init__(self, ip, port, max_clients, create_window):
        try:
            assert isinstance(ip, str), "[Error] IP is not a valid string"
            assert isinstance(port, int), "[Error] PORT is not a valid integer"
            assert isinstance(max_clients, int), "[Error] MAX_CLIENTS number is not a valid integer"
        except AssertionError as error:
            print("[Error]", error)
            sys.exit(1)

        # S'il n'y a pas eu d'erreur
        self._ip = ip
        self._port = port
        self._max_clients = max_clients

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._simulation = Simulation(self) # on lui passe une reference au serveur

        if create_window:
            self.window = ServerWindow(self, daemon=True) # daemon precise pour lisibilite
            self.window.start()
        else:
            self.window = None

        self._online = False
        self._connect()


    def _connect(self):
        """Active l'écoute sur les ip et port désignés"""
        try:
            self._socket.bind((self._ip, self._port))
            self._socket.listen(self._max_clients)

        except OSError:
            print("[Error] Port {} not available".format(self._port))
            self.quit()

        else:
            print("Server online with the following parameters:\n",
                "\tIP:", self._ip, '\n',
                "\tPORT:", self._port, '\n',
                "\tMax clients:", self._max_clients)
            self._online = True
            self._condition()

    def _accept(self):
        """
        Fonction pour accepter quand un client se connecte au serveur
        Stocke le client dans l'attribut de classe 'clients'
        """
        if len(Server.clients) <= self._max_clients:
            try:
                client, address = self._socket.accept()
            except OSError:
                # Exception levee quand la connexion est coupee pendant l'attente d'accept
                pass
            else:
                client_color = random_color()
                self._send_to_client(client, ("color", client_color))
                # On lui reserve une entree dans le dictionnaire
                Server.clients[client] = { "ready": False, "thread": None }
                print("Accepted client. Total: {}".format(len(Server.clients)))
                if self.window is not None:
                    self.window.clients += 1

                # Si l'IP du client est celle du serveur, il est admin
                if address[0] == self._ip:
                    self._send_to_client(client, "admin")
                sleep(0.1)
                self._sync_objects(client)
        else:
            print("[Warning] Denied access to a client (max number reached)")

    def _get_ready_clients(self):
        """
        Retourne le nombre de clients prêts en faisant la somme des booléens.
        Utilise un generator, d'où les parenthèses
        """
        return sum(client["ready"] for client in Server.clients.values())

    # À transformer en classmethod ? Ça veut dire mettre simulation en cls attr
    def _sync_objects(self, client):
        """
        Envoie tous les objets déjà
        posés au client en paramètre.
        """
        data = ["create"]
        if len(self._simulation.objects["nest"]) > 0:
            data.append(("nest", [n.to_tuple() for n in self._simulation.objects["nest"]]))
        if len(self._simulation.objects["resource"]) > 0:
            data.append(("resource", [r.to_tuple() for r in self._simulation.objects["resource"]]))

        if len(data) > 1:
            self._send_to_client(client, data)

        # On envoie les murs separement car ils sont gros
        if len(self._simulation.objects["wall"]) > 0:
            data.clear()
            for wall in (w.to_tuple() for w in self._simulation.objects["wall"]):
                data = ["create", ("wall", (wall,))]
                # print("data du mur :", data)
                self._send_to_client(client, data)
            # print("envoyé murs")

    def _receive(self):
        """
        Fonction qui sert à réceptionner les données envoyées depuis
        chaque client. Utilise une sous-fonction 'receive_in_thread'
        qui va manipuler dans un thread les données reçues.
        """
        def receive_in_thread(receiving_client):
            try:
                recv_data = receiving_client.recv(10240)
            except ConnectionResetError:
                self._disconnect_client(receiving_client)
            else:
                # Test pour voir s'il ne vaut pas mieux lever une exception quand ça ne fonctionne pas
                data = pickle.loads(recv_data)
                # try:
                #     data = pickle.loads(recv_data)
                # except pickle.UnpicklingError:
                #     data = recv_data

                if isinstance(data, ReadyState):
                    ready_state = data.value
                    Server.clients[receiving_client]["ready"] = ready_state
                    if ready_state:
                        ready_clients = self._get_ready_clients()
                        self.window.ready_clients = ready_clients
                        if len(Server.clients) and ready_clients == len(Server.clients):
                            print(f"Ready clients: {ready_clients} / {len(Server.clients)}")
                            self.send_to_all_clients("GO")
                            sleep(5) # On attend la fin du compte à rebours de l'interface
                            # Lancement de la simulation
                            Thread(target=self._simulation.start, daemon=True).start()
                        else:
                            print(f"Ready clients: {ready_clients} / {len(Server.clients)}")
                    else:
                        ready_clients = self._get_ready_clients()
                        self.window.ready_clients = ready_clients
                        print(f"Ready clients: {ready_clients} / {len(Server.clients)}")

                # Si c'est une str on réagit juste en fonction de la valeur
                elif isinstance(data, SpeedRequest):
                    if data == "faster":
                        self._simulation.sleep_time /= 2
                        print("Faster simulation")
                    elif data == "slower":
                        self._simulation.sleep_time *= 2
                        print("Slower simulation")
                # Si c'est une liste, c'est une création,
                # modification ou suppression d'objet
                else:
                    if data[0] == "undo":
                        # str_type = data[1] # test pour voir si ça sert…?
                        self._simulation.cancel_last_object()
                    else:
                        # TODO : refaire ça en POO
                        str_type, coords, size, color = data[:5]
                        self._process_data(str_type, coords, size, color)

        # Note : le transtypage copie les cles et permet d'enlever un client sans RuntimeError
        for client in tuple(Server.clients):
            # Si le client n'avait pas de thread associe, on en cree un
            if Server.clients[client]["thread"] is None:
                Server.clients[client]["thread"] = Thread(
                    target=receive_in_thread,
                    args=(client,),
                    daemon=True)
                Server.clients[client]["thread"].start()
            # Si le thread associe a ce client est termine (on a recu de lui), on en refait un
            if not Server.clients[client]["thread"].is_alive():
                Server.clients[client]["thread"] = Thread(
                    target=receive_in_thread,
                    args=(client,),
                    daemon=True)
                Server.clients[client]["thread"].start()

    def _process_data(self, str_type, coords, size, color):
        # print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
        str_type = str_type.lower() # normalement, deja en minuscules, mais au cas ou

        if str_type == "wall":
            # On nettoie le mur de ses points tres proches pour alleger les calculs
            min_distance = 4 # Distance minimale a avoir entre deux points du mur

            current_point = (coords[0], coords[1])
            opti_coords = [*current_point]
            for i in range(2, len(coords), 2):
                # On compare un point avec le point actuel, et si c'est bon on l'ajoute
                next_point = (coords[i], coords[i + 1])

                current_distance = distance(current_point, next_point)

                if current_distance > min_distance:
                    opti_coords.extend(current_point)
                    current_point = next_point
            opti_coords.extend(current_point) # il faut rajouter le dernier
            coords = opti_coords

        # Si l'endroit est libre
        if self._simulation.check_all_coords(coords, size):
            self._simulation.add_to_objects(str_type, coords, size, color)

            data = (str_type, [[coords, size, color]]) # syntaxe de l'envoi de groupe
            self.send_to_all_clients(("create", data))
        # else:
        #     print("[Warning] there is already an object here.")

    def _condition(self):
        """
        Fonction indispensable, elle permet au serveur d'accepter
        des connexions et de recevoir des données en même temps.
        """
        accepting_thread = Thread(target=self._accept, daemon=True)
        accepting_thread.start()
        # accepting_thread.join(0.2)

        receiving_thread = Thread(target=self._receive, daemon=True)
        receiving_thread.start()
        # receiving_thread.join(0.2)

        while self._online:
            # S'ils sont morts, quelque chose a ete recu, donc on en recree
            if not accepting_thread.is_alive():
                accepting_thread = Thread(target=self._accept, daemon=True)
                accepting_thread.start()
            # accepting_thread.join(0.2)

            if not receiving_thread.is_alive():
                receiving_thread = Thread(target=self._receive, daemon=True)
                receiving_thread.start()
            # receiving_thread.join(0.2)

    def _send_to_client(self, client, data):
        """Envoie des données à un seul client"""
        data = pickle.dumps(data)
        try:
            client.sendall(data)
        except BrokenPipeError as error:
            print(error)
            sys.exit(1)
        except ConnectionResetError:
            self._disconnect_client(client)

    def _disconnect_client(self, client):
        print("[Warning] Client disconnected. Closing associated connection.")
        client.close()
        try:
            del Server.clients[client]
        except KeyError:
            pass
        if self.window is not None:
            self.window.clients -= 1
            self.window.ready_clients = self._get_ready_clients()

    def send_to_all_clients(self, data):
        """Envoie des informations à tous les clients"""
        for client in tuple(Server.clients):
            self._send_to_client(client, data)

    def quit(self):
        """Termine le programme proprement"""
        self._online = False
        if self.window is not None:
            self.window.quit_window()
        self._socket.close()
        sys.exit(0)
