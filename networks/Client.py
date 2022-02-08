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
        return self._ready_state.value

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

            # test pour voir s'il y a encore des problèmes de pickling
            # try:
            data = pickle.loads(recv_data)
            # except pickle.UnpicklingError:
            #     data = recv_data

            print(f"received : {data}")

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
                # On l'ajoute seulement s'il est important
                if new_object_id is not None:
                    self.sent_to_interface[data] = new_object_id

            # Si on reçoit la couleur locale de l'interface
            elif isinstance(data, ColorInfo):
                self._interface.local_color = data

            # Si on doit bouger les fourmis
            elif isinstance(data, MoveInfo):
                with cf.ThreadPoolExecutor() as executor:
                    executor.map(self.interface.move_ant, self.interface.ants, data)

            elif isinstance(data, list):
                # Si ce sont des SentObject, c'est la synchronisation alors on crée tout
                if isinstance(data[0], SentObject):
                    for sent_object in data:
                        new_object_id = self._interface.create_object(sent_object.str_type,
                                                                      sent_object.coords,
                                                                      sent_object.size,
                                                                      sent_object.color)
                        self.sent_to_interface[sent_object] = new_object_id

                # Si on a les mouvements des fourmis et les pheromones en meme temps
                elif len(data) == 2 and isinstance(data[0], MoveInfo) and isinstance(data[1], PheromoneInfo):
                    with cf.ThreadPoolExecutor() as executor:
                        executor.map(self.interface.move_ant, self.interface.ants, data[0])
                        executor.map(self.interface.create_pheromone, data[1])

                # Si on doit creer des fourmis
                elif isinstance(data, AntsInfo):
                    self._interface.create_ants(data) # On veut qu'il soit bloquant

                else:
                    # Si on arrive ici c'est qu'il manque le type de data qu'il faut analyser
                    raise TypeError(f"[Error] Cannot process received data: {data}")


    ## Demandes au serveur ##

    def ask_object(self, sent_object):
        """
        Demande au serveur si on peut placer
        un élément d'un type et d'une taille
        donnés aux coordonnées données.
        """
        self._send(sent_object)

    def ask_undo(self):
        """ Demande au serveur d'annuler le placement du dernier objet """
        self._send(UndoRequest)

    def ask_faster_sim(self):
        """Demande à la simulation d'accélérer"""
        self._send(SpeedRequest(faster=True))
        print("Asked faster simulation")

    def ask_slower_sim(self):
        """Demande à la simulation de ralentir"""
        self._send(SpeedRequest(faster=False))
        print("Asked slower simulation")
