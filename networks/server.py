import sys

import socket
import pickle
import threading


class Server:
    """
    Application du serveur
    """
    clients = []

    objects = {}

    def __init__(self, ip, port, max_clients):
        try:
            assert isinstance(ip, str), "Erreur l'IP n'est pas une chaîne de caractère valide"
            assert isinstance(port, int), "Erreur le port n'est pas un entier valide"
        except AssertionError as e:
            print(e)
            sys.exit()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = ip
        self._port = port
        self._max_clients = max_clients

        self._client_ready = 0

        print("Server online")

    def connect(self):
        """
        Fonction de connection utilisé par le serveur pour écouter avec l'IP et le port.
        Utilisé dans un thread séparé
        """
        self._socket.bind((self._ip, self._port))
        self._socket.listen(self._max_clients)

        self.condition()

    def accept(self):
        """
        Fonction pour accepter quand un client se connecte au serveur
        Stocke le client dans l'attribut de classe 'clients'
        """
        client, address = self._socket.accept()
        Server.clients.append(client)

    def receive(self):
        for client in Server.clients:
            def under_receive():
                recv_data = client.recv(10000) # grand pour les coords des murs
                data = pickle.loads(recv_data)
                '''
                print("data :", data)
                # Si le 1er est None, c'est un signal pour dire qu'on veut juste une confirmation
                if data[0] is None:
                    print("serveur : data[0] is None => test des coords")
                    # On teste, on agit en fonction et on envoie le résultat
                    is_good = self.check_all_coords(data[1:-1], data[-1]) # coordonnées, width
                    
                    if not is_good:
                        print("   -> is not good coords")
                        data = pickle.dumps([None, is_good])
                        client.sendall(data)
                        continue
                    # Si elles étaient correctes, on dit à tous les clients de créer l'objet
                    else:
                        print("   -> is good coords")
                        self._add_to_dict(str_type, coords, size, width, color)

                        data = [str_type, coords, size, width, color]
                        self.send_to_clients(data)

                else:
                '''
                str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]

                self.process_data(str_type, coords, size, width, color)

            t1_2_1 = threading.Thread(target=under_receive)
            t1_2_1.start()

    '''
    def process_data(self, element, pos, size):
        if element == "Resource":
            pos = tuple(pos)
            if pos in Server.resources:
                data = [False, element, pos, size]
                self.send(data)
            else:
                Server.resources[pos] = size
                data = [True, element, pos, size]
                self.send(data)
    '''

    def process_data(self, str_type, coords, size, width, color):
        print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
        coords = tuple(coords) # normalement, déjà un tuple
        str_type = str_type.lower() # normalement, déjà en minuscules, mais au cas où
        
        # Si l'endroit est libre
        if self.check_all_coords(coords, size):
            self._add_to_dict(str_type, coords, size, width, color)

            data = [str_type, coords, size, width, color]
            self.send_to_clients(data)

    def _add_to_dict(self, str_type, coords, size, width, color):
        """Pour les objets 'wall', les coordonnées sont une liste"""
        # Si c'est le premier objet de ce type que l'on voit, on init
        if Server.objects.get(str_type) is None:
            Server.objects[str_type] = []
        if size is None:
            size = width
        # Dans tous les cas, on ajoute les nouvelles coords, taille et couleur
        Server.objects[str_type].append((coords, size, width, color))
        print("ajouté côté serveur :", str_type, coords, size, width, color)

    
    def is_good_spot(self, x, y, size):
        """
        Retourne True si les coordonnées données en paramètre sont
        disponibles en fonction de la taille donnée, False sinon
        """
        for str_type in Server.objects:
            for properties in Server.objects[str_type]:
                coords_obj, size_obj, width_obj, color_obj = properties
                offset = size_obj
                # On teste un espace autour des coords
                for i in range(0, len(coords_obj) - 1, 2):
                    if (coords_obj[i] - offset <= x <= coords_obj[i] + offset) and (
                        coords_obj[i+1] - offset <= y <= coords_obj[i+1] + offset):
                        print("-> is not good spot")
                        return False
        print("-> is good spot")
        return True

    def check_all_coords(self, coords_list, size):
        """Vérifie que toutes les coordonnées de la liste sont valides"""
        # print("len coords :", len(coords_list))
        for i in range(0, len(coords_list) - 1, 2):
            if not self.is_good_spot(coords_list[i], coords_list[i+1], size):
                # print("nope, coords", (coords_list[i], coords_list[i+1]), "size :", size, "pas bonnes")
                return False
        # print("toutes les coords sont ok")
        return True



    def condition(self):
        """
        Fonction 'principale' de la classe.
        Elle permet au serveur d'accepter et recevoir en même temps
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


    def send(self, data):
        """
        Fonction envoyant des informations aux clients
        """
        try:
            for client in Server.clients:
                data = pickle.dumps(data)
                client.send_to_clientsall(data)
        except BrokenPipeError as e:
            print(e)
            sys.exit(1)


    def send_to_clients(self, data):
        """
        Fonction envoyant des informations aux clients
        """
        try:
            for client in Server.clients:
                data = pickle.dumps(data)
                client.sendall(data)
        except BrokenPipeError as e:
            print(e)
            sys.exit(1)


if __name__ == "__main__":
    server = Server("127.0.0.1", 15555, 1)
    server.connect()
