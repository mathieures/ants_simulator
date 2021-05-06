import sys
import socket
import pickle
import threading
from time import sleep

import simulation

import color

from config_server import ConfigServer

# pour le debug
from time import time


class Server:
	"""
	Application du serveur
	"""
	clients = []

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


	def __init__(self, ip, port, max_clients):
		try:
			assert isinstance(ip, str), "Erreur l'IP n'est pas une chaîne de caractère valide"
			assert isinstance(port, int), "Erreur le port n'est pas un entier valide"
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
			# On lui reserve une entree dans le dictionnaire
			self._receiving_threads[client] = None

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
				# Si c'est une liste, on sait que la demande est effectuée pour créer un élément, ou annuler
				if isinstance(data, list):
					if data[0] == "undo":
						print("Annulation coté serv")
						str_type = data[1]
						self._simulation.objects[str_type].pop()
					else:
						str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]
						self.process_data(str_type, coords, size, width, color)
				elif data.decode() == "Ready":
					self._clients_ready += 1
					if self._clients_ready == len(Server.clients):
						self.send_to_all_clients("GO")
						print("GO")
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
		t0 = time()
		coords = tuple(coords) # normalement, déjà un tuple, mais au cas où
		str_type = str_type.lower() # normalement, déjà en minuscules, mais au cas où

		# Si l'endroit est libre
		if self._simulation.check_all_coords(coords, size):
			self._simulation.add_to_objects(str_type, coords, size, width, color)

			data = [str_type, coords, size, width, color]
			self.send_to_all_clients(data)
		
		t1 = time()
		print("temps :", t1 - t0)

	def condition(self):
		"""
		Fonction indispensable, elle permet au serveur d'accepter
		des connexions et de recevoir des données en même temps.
		"""
		accepting_thread = threading.Thread(target=self.accept)
		accepting_thread.daemon = True
		accepting_thread.start()
		accepting_thread.join(0.2)

		receiving_thread = threading.Thread(target=self.receive)
		receiving_thread.daemon = True
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
			port = int(sys.argv[2])
			max_clients = int(sys.argv[3])
		except ValueError:
			print("Erreur ces arguments doivent être des entiers")
			sys.exit(1)

	server = Server(ip, port, max_clients)
	server.connect()
