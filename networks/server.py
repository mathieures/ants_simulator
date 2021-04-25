import sys
import socket
import pickle
import threading
import time

import simulation

import color


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

		print(ip, port, max_clients)

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._ip = ip
		self._port = port
		self._max_clients = max_clients

		self._clients_ready = 0

		print("Server online")

	def connect(self):
		"""
		Fonction de connexion utilisée par le serveur pour
		écouter avec l'IP et le port (dans un thread séparé)
		"""
		self._socket.bind((self._ip, self._port))
		self._socket.listen(self._max_clients)

		self.condition()

	def accept(self):
		"""
		Fonction pour accepter quand un client se connecte au serveur
		Stocke le client dans l'attribut de classe 'clients'
		"""
		if len(Server.clients) <= self._max_clients:
			client, address = self._socket.accept()
			self.send_to_client(client, ["color", color.random_rgb()])
			Server.clients.append(client)
		else:
			print("trop de clients")

	def receive(self):
		"""
		Fonction qui sert à réceptionner les données envoyées depuis le client
		Utilise une sous fonction 'under_receive' qui va manipuler dans un thread les données reçues
		"""
		for client in Server.clients:
			def under_receive():
				recv_data = client.recv(10240)
				try:
					data = pickle.loads(recv_data)
				except pickle.UnpicklingError:
					data = recv_data
				# Si c'est une liste, on sait que la demande est effectuée pour créer un élément
				if isinstance(data, list):
					str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]
					self.process_data(str_type, coords, size, width, color)
				elif data.decode() == "Ready":
					self._clients_ready += 1
					if self._clients_ready == len(Server.clients):
						self.send_to_all_clients("GO")
						print("GO")
						time.sleep(5) # On attend 5 secondes le temps que le countdown de interface finisse
						# Lancement de la simulation
						self.simulation = simulation.Simulation(Server.objects, self)
					else:
						print(f"Il manque encore {len(Server.clients) - self._clients_ready} client(s)")

			t1_2_1 = threading.Thread(target=under_receive)
			t1_2_1.start()

	def process_data(self, str_type, coords, size, width, color):
		# print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
		coords = tuple(coords) # normalement, déjà un tuple, mais au cas où
		str_type = str_type.lower() # normalement, déjà en minuscules, mais au cas où

		# Si l'endroit est libre
		if self.check_all_coords(coords, size):
			self._add_to_dict(str_type, coords, size, width, color)

			data = [str_type, coords, size, width, color]
			self.send_to_all_clients(data)


	def _add_to_dict(self, str_type, coords, size, width, color):
		"""Ajoute une entrée au dictionnaire"""
		# Note : Pour les objets 'wall', les coordonnées sont une liste
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
		print("toutes les coords sont ok")
		return True

	def condition(self):
		"""
		Fonction indispensable, elle permet au serveur d'accepter
		des connexions et de recevoir des données en même temps.
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

	def send_to_client(self, client, data):
		"""Envoie des données à un seul client"""
		data = pickle.dumps(data)
		try:
			client.sendall(data)
		except BrokenPipeError as e:
			print(e)
			sys.exit(1)


	def send_to_all_clients(self, data):
		"""
		Fonction envoyant des informations aux clients
		"""
		for client in Server.clients:
			self.send_to_client(client, data)
			# print("sent :", data, "to")


if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("Erreur de format des arguments")
		print("python3 serveur IP PORT NB_MAX_CLIENTS")
		sys.exit(1)
	else:
		ip = sys.argv[1]
		try:
			port = int(sys.argv[2])
			max_clients = int(sys.argv[3])
		except ValueError:
			print("Erreur ces arguments doivent être des entiers")
			sys.exit(1)

	server = Server(ip, port, max_clients)
	server.connect()
