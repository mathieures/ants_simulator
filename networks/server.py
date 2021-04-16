import sys

import socket
import pickle
import threading


class Server:
    """
    Application du serveur
    """
    clients = []

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
        """
        Fonction de connection utilisé par le serveur pour écouter avec l'IP et le port.
        Utilisé dans un thread séparé
        """
        self._socket.bind((self._ip, self._port))
        self._socket.listen(5)

        self.condition()

    def accept(self):
        """
        Fonction pour accepter quand un client se connecte au serveur
        Stocke le client dans l'attribut de classe 'clients'
        """
        client, address = self._socket.accept()
        Server.clients.append(client)
        print("{} connecté.".format(client))

    def receive(self):
        for client in Server.clients:
            def under_receive():
                recv_data = client.recv(1024)
                data = pickle.loads(recv_data)
                print(data)

            t1_2_1 = threading.Thread(target=under_receive)
            t1_2_1.start()

    def condition(self):
        """
        Fonction 'principal' de la classe.
        Elle sert au serveur afin qu'il puisse accepter et recevoir en même temps
        Utilisé dans des threads
        """
        while True:
            t1_1 = threading.Thread(target=self.accept)
            t1_1.daemon = True
            t1_1.start()
            t1_1.join(1)

            t1_2 = threading.Thread(target=self.receive)
            t1_2.daemon = True
            t1_2.start()
            t1_2.join(1)

    def send(self, args):
        """
        Fonction renvoyant des informations au clients
        """
        try:
            data = pickle.dumps(args)
            for client in Server.clients:
                client.sendall(data)
        except BrokenPipeError as e:
            print(e)
            sys.exit(1)


if __name__ == "__main__":
    server = Server("127.0.0.1", 15555)
    server.connect()
