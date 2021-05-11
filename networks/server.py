import sys
import socket
import pickle
import threading
<<<<<<< HEAD
import time
=======
from time import sleep
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

import simulation

import color

<<<<<<< HEAD
=======
from config_server import ConfigServer
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

class Server:
	"""
	Application du serveur
	"""
	clients = []

<<<<<<< HEAD
	objects = {}
=======
	@property
	def ip(self):
		return self._ip

	@ip.setter
	def ip(self, new_ip):
		self._ip = new_ip
	
	@property
	def port(self):
		return self._port

	@port.setter
	def port(self, new_port):
		self._port = new_port
	
	@property
	def max_clients(self):
		return self._max_clients
	
	@max_clients.setter
	def max_clients(self, new_max_clients):
		self._max_clients = new_max_clients

>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

	def __init__(self, ip, port, max_clients):
		try:
			assert isinstance(ip, str), "Erreur l'IP n'est pas une chaîne de caractère valide"
			assert isinstance(port, int), "Erreur le port n'est pas un entier valide"
<<<<<<< HEAD
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
=======
			assert isinstance(max_clients, int), "Erreur le nombre de clients maximum n'est pas un entier valide"
		except AssertionError as e:
			print(e)
			sys.exit()
		# S'il n'y a pas eu d'erreur
		else:
			self._ip = ip
			self._port = port
			self._max_clients = max_clients
			print("parametres serveur :", self._ip, self._port, self._max_clients)

			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
			self._clients_ready = 0
			self._receiving_threads = {} # dictionnaire qui associe un client a un thread de reception

			self._simulation = simulation.Simulation(self) # on lui passe une reference au serveur

			print("Server online")

>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

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
<<<<<<< HEAD
=======
			# On lui reserve une entree dans le dictionnaire
			self._receiving_threads[client] = None

>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
		else:
			print("trop de clients")

	def receive(self):
		"""
		Fonction qui sert à réceptionner les données envoyées depuis le client
		Utilise une sous fonction 'under_receive' qui va manipuler dans un thread les données reçues
		"""
<<<<<<< HEAD
		for client in Server.clients:
=======
		for client in Server.clients:			
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
			def under_receive():
				recv_data = client.recv(10240)
				try:
					data = pickle.loads(recv_data)
				except pickle.UnpicklingError:
					data = recv_data
<<<<<<< HEAD
				# Si c'est une liste, on sait que la demande est effectuée pour créer un élément
				if isinstance(data, list):
					str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]
					self.process_data(str_type, coords, size, width, color)
=======
				# Si c'est une liste, on sait que la demande est effectuée pour créer un élément, ou annuler
				if isinstance(data, list):
					if data[0] == "undo":
						print("Annulation coté serv")
						str_type = data[1]
						self._simulation.objects[str_type].pop()
						self.send_to_all_clients("undo")
					else:
						str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]
						self.process_data(str_type, coords, size, width, color)
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
				elif data.decode() == "Ready":
					self._clients_ready += 1
					if self._clients_ready == len(Server.clients):
						self.send_to_all_clients("GO")
						print("GO")
<<<<<<< HEAD
						time.sleep(5) # On attend 5 secondes le temps que le countdown de interface finisse
						# Lancement de la simulation
						self.simulation = simulation.Simulation(Server.objects, self)
					else:
						# print(f"Il manque encore {len(Server.clients) - self._clients_ready} client(s)")
						print("Il manque encore {} client(s)".format(len(Server.clients) - self._clients_ready))

			t1_2_1 = threading.Thread(target=under_receive)
			t1_2_1.start()

	def process_data(self, str_type, coords, size, width, color):
		# print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
		coords = tuple(coords) # normalement, déjà un tuple, mais au cas où
		str_type = str_type.lower() # normalement, déjà en minuscules, mais au cas où

		# Si l'endroit est libre
		if self.check_all_coords(coords, size):
			self._add_to_dict(str_type, coords, size, width, color)
=======
						sleep(5) # On attend 5 secondes le temps que le countdown de interface finisse
						# Lancement de la simulation
						self._simulation.start()
					else:
						print("Il manque encore {} client(s)".format(len(Server.clients) - self._clients_ready))
			
			# Si le client n'avait pas de thread associe, on en cree un
			if self._receiving_threads[client] is None:
				self._receiving_threads[client] = threading.Thread(target=under_receive)
				self._receiving_threads[client].start()
			# Si le thread associe a ce client est termine (on a recu de lui), on en refait un
			if not self._receiving_threads[client].is_alive():
				self._receiving_threads[client] = threading.Thread(target=under_receive)
				self._receiving_threads[client].start()

			# print("threads courants :", threading.active_count())

	def process_data(self, str_type, coords, size, width, color):
		# print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
		coords = tuple(coords) # normalement, deja un tuple, mais au cas ou
		str_type = str_type.lower() # normalement, deja en minuscules, mais au cas ou

		# Si l'endroit est libre
		if self._simulation.check_all_coords(coords, size):
			self._simulation.add_to_objects(str_type, coords, size, width, color)
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

			data = [str_type, coords, size, width, color]
			self.send_to_all_clients(data)

<<<<<<< HEAD

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

=======
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
	def condition(self):
		"""
		Fonction indispensable, elle permet au serveur d'accepter
		des connexions et de recevoir des données en même temps.
		"""
<<<<<<< HEAD
		while True:
			t1_1 = threading.Thread(target=self.accept)
			t1_1.daemon = True
			t1_1.start()
			t1_1.join(1)

			t1_2 = threading.Thread(target=self.receive)
			t1_2.daemon = True
			t1_2.start()
			t1_2.join(1)
=======
		accepting_thread = threading.Thread(target=self.accept, daemon=True)
		accepting_thread.start()
		accepting_thread.join(0.2)

		receiving_thread = threading.Thread(target=self.receive, daemon=True)
		receiving_thread.start()
		receiving_thread.join(0.2)

		while True:
			if not accepting_thread.is_alive():
				# print("accepting dead")
				accepting_thread = threading.Thread(target=self.accept)
				accepting_thread.daemon = True
				accepting_thread.start()
			accepting_thread.join(0.2)

			if not receiving_thread.is_alive():
				# print("receiving dead")
				receiving_thread = threading.Thread(target=self.receive)
				receiving_thread.daemon = True
				receiving_thread.start()
			receiving_thread.join(0.2)
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

	def send_to_client(self, client, data):
		"""Envoie des données à un seul client"""
		data = pickle.dumps(data)
		try:
			client.sendall(data)
		except BrokenPipeError as e:
			print(e)
			sys.exit(1)

<<<<<<< HEAD

=======
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
	def send_to_all_clients(self, data):
		"""
		Fonction envoyant des informations aux clients
		"""
		for client in Server.clients:
			self.send_to_client(client, data)
			# print("sent :", data, "to")


if __name__ == "__main__":
<<<<<<< HEAD
	if len(sys.argv) < 4:
		print("Erreur de format des arguments")
		print("python3 serveur IP PORT NB_MAX_CLIENTS")
		sys.exit(1)
	else:
		ip = sys.argv[1]
		try:
=======
	# S'il n'y a pas assez d'arguments, on ouvre la fenetre
	if len(sys.argv) < 4:
		config = ConfigServer() # bloquant

		ip = config.ip
		port = config.port
		max_clients = config.max_clients

		# print("Erreur de format des arguments")
		# print("Syntaxe : python3 serveur <IP> <PORT> <NB_MAX_CLIENTS>")
		# sys.exit(1)
	else:
		try:
			ip = int(sys.argv[1])
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
			port = int(sys.argv[2])
			max_clients = int(sys.argv[3])
		except ValueError:
			print("Erreur ces arguments doivent être des entiers")
			sys.exit(1)

	server = Server(ip, port, max_clients)
	server.connect()
