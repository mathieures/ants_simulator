import sys
import socket
import pickle
from threading import Thread
import concurrent.futures as cf
from time import sleep
# from math import dist as distance

from .network_utils import (
    random_color,
    id_generator,

    ReadyState,
    SpeedRequest,
    UndoRequest,

    GoSignal,
    AdminSignal,
    DestroySignal,

    SentObject,
    ColorInfo
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

    CLIENT_ID_GEN = id_generator()

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

        self.clients = {}
        """
        Dictionnaire qui associe un id a un dict
        {
            "id": int,
            "ready": bool,
            # "thread": Thread
            "thread": Future
        }
        """
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
        if len(self.clients) <= self._max_clients:
            try:
                client, address = self._socket.accept()
            except OSError:
                # Exception levee quand la connexion est coupee pendant l'attente d'accept
                pass
            else:
                self._send_to_client(client, ColorInfo(random_color()))
                # On lui reserve une entree dans le dictionnaire
                self.clients[client] = {
                    "id": next(self.__class__.CLIENT_ID_GEN),
                    "ready": False,
                    "thread": None
                    # "thread": None
                }

                print(f"Accepted client. Total: {len(self.clients)}")

                if self.window is not None:
                    self.window.clients += 1

                # Si l'IP du client est celle du serveur, il est admin
                if address[0] == self._ip:
                    self._send_to_client(client, AdminSignal)
                sleep(0.1)

                # Envoie les objets au Client dans un thread
                Thread(target=self._sync_objects, args=(client,)).start()

        else:
            print("[Warning] Denied access to a client (max number reached)")

    def _get_ready_clients(self):
        """
        Retourne le nombre de clients prêts en faisant la somme des booléens.
        Utilise un generator, d'où le manque de parenthèses
        """
        return sum(client["ready"] for client in self.clients.values())

    def _sync_objects(self, client):
        """
        Envoie tous les objets déjà
        posés au client en paramètre.
        """
        data = []

        for str_type in ("nest", "resource"):
            if self._simulation.objects[str_type]:
                for obj in self._simulation.objects[str_type]:
                    data.append(SentObject(str_type, *obj.to_tuple()))

        if data:
            self._send_to_client(client, data)
            sleep(0.01)

        del data

        # On envoie les murs separement car ils sont plus lourds
        if self._simulation.objects["wall"]:
            for wall in self._simulation.objects["wall"]:
                self._send_to_client(client, SentObject("wall", *wall.to_tuple()))
                sleep(0.01) # La latence permet au Client de tout recevoir

    def _receive(self):
        """
        Méthode qui sert à réceptionner les données envoyées depuis
        chaque client. Utilise une sous-fonction 'receive_in_thread_from'
        qui va manipuler dans un thread les données reçues.
        """
        def receive_in_thread_from(source_client):
            try:
                recv_data = source_client.recv(10240)
            except ConnectionResetError:
                self._disconnect_client(source_client)
            else:
                data = pickle.loads(recv_data)

                if isinstance(data, ReadyState):
                    ready_state = data.value
                    self.clients[source_client]["ready"] = ready_state

                    ready_clients = self._get_ready_clients()
                    self.window.ready_clients = ready_clients
                    print(f"Ready clients: {ready_clients} / {len(self.clients)}")

                    if ready_state and ready_clients == len(self.clients):
                        self.send_to_all_clients(GoSignal)
                        sleep(5) # On attend la fin du compte à rebours de l'interface

                        # Lancement de la simulation dans un thread
                        Thread(target=self._simulation.start).start()

                # Si c'est une str on réagit juste en fonction de la valeur
                elif isinstance(data, SpeedRequest):
                    if data.faster:
                        self._simulation.sleep_time /= 2
                        print("Faster simulation")
                    else:
                        self._simulation.sleep_time *= 2
                        print("Slower simulation")
                # Si c'est une liste, c'est une création,
                # modification ou suppression d'objet
                else:
                    client_id = self.clients[source_client]["id"]
                    if data is UndoRequest:
                        self._simulation.undo_object_from_client(client_id)
                    elif isinstance(data, SentObject):
                        self._process_data(client_id, data)


        # Note : le transtypage copie les cles et permet d'enlever un client sans RuntimeError
        for client in tuple(self.clients):
            # S'il n'y a pas encore de thread associé au client ou
            # s'il est terminé (on a reçu de lui), on en cree un
            client_thread = self.clients[client]["thread"]
            if client_thread is None or not client_thread.is_alive():
                self.clients[client]["thread"] = Thread(target=receive_in_thread_from,
                                                        args=(client,), daemon=True)
                self.clients[client]["thread"].start()

        # executor = cf.ThreadPoolExecutor()
        # # Note : le transtypage copie les cles et permet d'enlever un client sans RuntimeError
        # for client in tuple(self.clients):
        #     # S'il n'y a pas encore de thread associé au client ou
        #     # s'il est terminé (on a reçu de lui), on en cree un
        #     if self.clients[client]["thread"] is None or self.clients[client]["thread"].done():
        #         self.clients[client]["thread"] = executor.submit(receive_in_thread_from, client)

    def _process_data(self, source_client_id, sent_object):
        """Crée un objet en fonction du client et des caractéristiques de l'objet voulu."""
        if sent_object.str_type == "wall":
            sent_object.coords = self._simulation.optimize_wall(sent_object.coords)

        # Si l'endroit est libre
        if self._simulation.check_all_coords(sent_object.coords, sent_object.size):
            self._simulation.add_to_objects(source_client_id, sent_object)

            self.send_to_all_clients(sent_object)

    def _condition(self):
        """
        Fonction indispensable, elle permet au serveur d'accepter
        des connexions et de recevoir des données en même temps.
        """
        # TODO : peut-être refaire ça avec un ThreadPoolExecutor

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
            del self.clients[client]
        except KeyError:
            pass
        if self.window is not None:
            self.window.clients -= 1
            self.window.ready_clients = self._get_ready_clients()

    def send_to_all_clients(self, data):
        """Envoie des informations à tous les clients"""
        for client in tuple(self.clients):
            self._send_to_client(client, data)

    def send_destroy_signal(self, obj):
        """Envoie un signal de destruction de l'objet spécifié à tous les clients"""
        self.send_to_all_clients(DestroySignal(SentObject.from_SizedServerObject(obj)))

    def quit(self):
        """Termine le programme proprement"""
        self._online = False
        # if self.window is not None:
        #     self.window.quit_window()
        self._socket.close()
        sys.exit(0)
