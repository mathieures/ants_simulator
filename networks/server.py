import sys
import socket
import pickle
import threading
from time import sleep

import simulation

import color

from config_server import ConfigServer
from server_window import ServerWindow


# pour le debug
from time import time


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
	clients = []

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

	@property
	def window(self):
		return self._window

	@window.setter
	def window(self, new_window):
		self._window = new_window


	def __init__(self, ip, port, max_clients):
		try:
			assert isinstance(ip, str), "[Error] IP is not a valid string"
			assert isinstance(port, int), "[Error] PORT is not a valid integer"
			assert isinstance(max_clients, int), "[Error] MAX_CLIENTS number is not a valid integer"
		except AssertionError as e:
			print(e)
			sys.exit()
		# S'il n'y a pas eu d'erreur
		else:
			self._ip = ip
			self._port = port
			self._max_clients = max_clients

			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
			self._clients_ready = 0
			self._receiving_threads = {} # dictionnaire qui associe un client a un thread de reception

			self._simulation = simulation.Simulation(self) # on lui passe une reference au serveur

			if create_window:
				self._window = ServerWindow(self, daemon=True) # daemon precise pour lisibilite
				self._window.start()
			else:
				self._window = None

			self._online = False
			self.connect()


	def connect(self):
		"""Active l'écoute sur les ip et port désignés"""
		try:
			self._socket.bind((self._ip, self._port))
			self._socket.listen(self._max_clients)

		except OSError:
			print("[Error] Port {} not available".format(self._port))
			self.quit()
		
		else:
			print("Server online with the following parameters:",
				"IP:", self._ip,
				"PORT:", self._port,
				"Max clients:", self._max_clients)
			self._online = True
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
			if self._window is not None:
				self._window.clients += 1

		else:
			print("[Warning] Denied access to a client (max number reached)")

	def receive(self):
		"""
		Fonction qui sert à réceptionner les
		données envoyées depuis chaque client.
		Utilise une sous-fonction 'under_receive' qui
		va manipuler dans un thread les données reçues.
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
					self._window.ready_clients += 1
					if self._clients_ready == len(Server.clients):
						self.send_to_all_clients("GO")
						print("GO")
						sleep(5) # On attend 5 secondes le temps que le countdown de interface finisse
						# Lancement de la simulation (bloquante)
						self._simulation.start()
					else:
						print("Il manque encore {} client(s)".format(len(Server.clients) - self._clients_ready))
			
			# Si le client n'avait pas de thread associe, on en cree un
			if self._receiving_threads[client] is None:
				self._receiving_threads[client] = threading.Thread(target=under_receive, daemon=True)
				self._receiving_threads[client].start()
			# Si le thread associe a ce client est termine (on a recu de lui), on en refait un
			if not self._receiving_threads[client].is_alive():
				self._receiving_threads[client] = threading.Thread(target=under_receive, daemon=True)
				self._receiving_threads[client].start()

			# print("threads courants :", threading.active_count())

	def process_data(self, str_type, coords, size, width, color):
		# print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
		coords = tuple(coords) # normalement, deja un tuple, mais au cas ou
		str_type = str_type.lower() # normalement, deja en minuscules, mais au cas ou

		# Si l'endroit est libre
		if self._simulation.check_all_coords(coords, size):
			self._simulation.add_to_objects(str_type, coords, size, width, color)

			data = [str_type, coords, size, width, color]
			self.send_to_all_clients(data)

	def condition(self):
		"""
		Fonction indispensable, elle permet au serveur d'accepter
		des connexions et de recevoir des données en même temps.
		"""
		accepting_thread = threading.Thread(target=self.accept, daemon=True)
		accepting_thread.start()
		accepting_thread.join(0.2)

		receiving_thread = threading.Thread(target=self.receive, daemon=True)
		receiving_thread.start()
		receiving_thread.join(0.2)

		while self._online:
			# On teste s'ils sont morts (quelque chose a ete recu), on en recree
			if not accepting_thread.is_alive():
				accepting_thread = threading.Thread(target=self.accept, daemon=True)
				accepting_thread.start()
			accepting_thread.join(0.2)

			if not receiving_thread.is_alive():
				receiving_thread = threading.Thread(target=self.receive, daemon=True)
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
		"""Envoie des informations à tous les clients"""
		for client in Server.clients:
			self.send_to_client(client, data)

	def quit(self):
		self._online = False
		if self._window is not None:
			self._window.quit_window()
		sys.exit(0)


if __name__ == "__main__":
	# On regarde d'abord si l'utilisateur veut une fenetre
	if "-nowindow" in sys.argv:
		create_window = False
		sys.argv.pop(sys.argv.index("-nowindow"))
		print("new args :", sys.argv)
	else:
		create_window = True
	
	# S'il n'y a pas assez d'arguments, on ouvre la fenetre de config
	if len(sys.argv) < 4:
		config = ConfigServer() # bloquant

		ip = config.ip
		port = config.port
		max_clients = config.max_clients
		create_window = config.create_window

	else:
		try:
			ip = int(sys.argv[1])
			port = int(sys.argv[2])
			max_clients = int(sys.argv[3])
		except ValueError:
			print("[Error] Arguments must be integers")
			print("Syntax:\n\tpython3 server.py <IP> <PORT> <NB_MAX_CLIENTS> [-nowindow]")
			sys.exit(1)

	server = Server(ip, port, max_clients)
