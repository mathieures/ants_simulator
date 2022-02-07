import sys

import socket
import pickle
# from threading import Thread
import concurrent.futures as cf

from time import perf_counter

from .network_utils import (
    ReadyState,
    SpeedRequest,
    UndoRequest,

    GoSignal,
    AdminSignal,
    DestroySignal,

    SentObject,
    ColorInfo,
    AntsInfo,
    MoveInfo,
    PheromoneInfo
)


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

    @property
    def ready_state(self):
        return self._ready_state

    @ready_state.setter
    def ready_state(self, new_state):
        """Assigne l'état de préparation et informe le serveur."""
        self._ready_state.value = new_state
        self._send(self._ready_state)


    def __init__(self, ip, port):
        try:
            assert isinstance(ip, str), "[Error] the server IP is not a valid string"
            assert isinstance(port, int), "[Error] the server port is not a valid integer"
            assert len(ip) > 0, "[Error] the server IP cannot be empty"
        except AssertionError as error:
            print(error)
            sys.exit()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = ip
        self._port = port

        self._connected = True

        self._interface = None
        self._is_admin = False

        self._ready_state = ReadyState()

        self.sent_to_interface = {} # Associe un SentObject reçu à un InterfaceObject


    def connect(self):
        """Connecte le client au serveur"""
        try:
            self._socket.connect((self._ip, self._port))
            self._connected = True
            self._receive()
        except ConnectionRefusedError:
            print("[Error] No server found")
            sys.exit(1)

    def disconnect(self):
        self._socket.close()
        sys.exit(1)


    ## Envoi et réception ##

    def _send(self, data):
        """
        Envoie les données converties. À utiliser
        quand on veut envoyer quoi que ce soit.
        """
        try:
            self._socket.send(pickle.dumps(data))
        except BrokenPipeError:
            print("[Error] fatal error while sending data. Exiting.")
            sys.exit(1)

    def _receive(self):
        """
        Reçoit les signaux envoyés par les clients pour les objets créés.
        Pour ne pas bloquer les actions avec l'interface, on
        appelle les méthodes de l'interface dans des threads.
        """
        # Note : le client ne fait que recevoir, donc pas besoin de thread
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

            if data is GoSignal:
                self._interface.countdown()
            elif data is AdminSignal:
                self._is_admin = True
                self._interface.show_admin_buttons()

            elif isinstance(data, DestroySignal):
                interface_obj = self.sent_to_interface[data.object_to_destroy]
                self._interface.destroy_object(interface_obj)

            # Si c'est un objet cree par un client
            elif isinstance(data, SentObject):
                new_object_id = self._interface.create_object(data.str_type,
                                                              data.coords,
                                                              data.size,
                                                              data.color)
                # On ne l'ajoute pas s'il n'est pas important
                if new_object_id is not None:
                    self.sent_to_interface[data] = new_object_id

            # Si on reçoit la couleur locale de l'interface
            elif isinstance(data, ColorInfo):
                self._interface.local_color = data

            elif isinstance(data, MoveInfo):
                # temps_move = perf_counter()

                with cf.ThreadPoolExecutor() as executor:
                    executor.map(self.interface.move_ant, self.interface.ants, data)

                # thread_move = Thread(target=self._interface.move_ants,
                #                      args=(data,),
                #                      daemon=True)
                # thread_move.start()
                # thread_move.join(0.5)
                # print("temps move_ants :", perf_counter() - temps_move)

            elif isinstance(data, list):
                # Si ce sont des SentObject, c'est la synchronisation alors on crée tout
                if isinstance(data[0], SentObject):
                    for sent_object in data:
                        new_object_id = self._interface.create_object(sent_object.str_type,
                                                                      sent_object.coords,
                                                                      sent_object.size,
                                                                      sent_object.color)
                        self.sent_to_interface[sent_object] = new_object_id

                # Si on doit bouger des fourmis

                # data est de la forme : ["move_ants", [deltax_fourmi1, deltay_fourmi1], [deltax_fourmi2, deltay_fourmi2]...]
                # ou alors : [["move_ants", [deltax...]], ["pheromones", (fourmi1x, fourmi1y)...]]
                # Note : les listes internes peuvent contenir un autre élément, la couleur de la fourmi.

                # Si on a les mouvements des fourmis et les pheromones en meme temps
                elif len(data) == 2 and isinstance(data[0], MoveInfo) and isinstance(data[1], PheromoneInfo):
                    # On bouge les fourmis
                    # temps_move_phero = perf_counter()

                    with cf.ThreadPoolExecutor() as executor:
                        executor.map(self.interface.move_ant, self.interface.ants, data[0])
                        executor.map(self.interface.create_pheromone, data[1])

                    # thread_move = Thread(target=self._interface.move_ants,
                    #                      args=(data[0],),
                    #                      daemon=True)
                    # thread_move.start()
                    # thread_move.join(0.5)

                    # # On cree ou fonce les pheromones
                    # thread_phero = Thread(target=self._interface.create_pheromones,
                    #                       args=(data[1],),
                    #                       daemon=True)
                    # thread_phero.start()
                    # thread_phero.join(0.5)
                    # print("temps move_ants + phero :", perf_counter() - temps_move_phero)

                # Si on doit creer des fourmis
                elif isinstance(data, AntsInfo):
                    self._interface.create_ants(data) # On veut qu'il soit bloquant

                else:
                    # Si on arrive ici c'est qu'il manque le type de data qu'il faut analyser
                    raise TypeError("[Error] Cannot process received data: operation string is missing")


    ## Demandes au serveur ##

    def ask_object(self, str_type, position, size=None, color=None):
        """
        Demande au serveur si on peut placer
        un élément d'un type et d'une taille
        donnés à la position donnée.
        """
        self._send((str_type, position, size, color))

    def ask_undo(self):
        """ Demande au serveur d'annuler le placement du dernier objet """
        self._send(UndoRequest)

    def ask_faster_sim(self):
        """Demande à la simulation d'accélérer"""
        self._send(SpeedRequest(faster=True))
        print("Asked faster simulation")
        # self._socket.send("faster".encode())

    def ask_slower_sim(self):
        """Demande à la simulation de ralentir"""
        self._send(SpeedRequest(faster=False))
        print("Asked slower simulation")
        # self._socket.send("slower".encode())