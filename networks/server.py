import sys
import socket
import pickle
import threading
from time import sleep

import simulation

import color

from config_server import ConfigServer
from server_window import ServerWindow

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
	clients = {} # dictionnaire qui associe un client a un dict { 'ready': bool, 'thread': thread_reception }
	# Note : on est obliges de garder une trace de quel client est pret pour mettre a jour la window

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
			print("[Error]", e)
			sys.exit(1)
		
		# S'il n'y a pas eu d'erreur
		self._ip = ip
		self._port = port
		self._max_clients = max_clients

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self._simulation = simulation.Simulation(self) # on lui passe une reference au serveur

		if create_window:
			self._window = ServerWindow(self, daemon=True) # daemon precise pour lisibilite
			self._window.start()
		else:
			self._window = None

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
				# levee quand la connexion est coupee pendant l'attente d'accept
				pass
			else:
				self._send_to_client(client, ("color", color.random_rgb()))
				# On lui reserve une entree dans le dictionnaire
				Server.clients[client] = { 'ready':False, 'thread': None }
				print("Accepted client. Total: {}".format(len(Server.clients)))
				if self._window is not None:
					self._window.clients += 1

				# Si l'IP du client est celle du serveur, il est admin
				if address[0] == self._ip:
					self._send_to_client(client, "admin")
				self._sync_objects(client)
		else:
			print("[Warning] Denied access to a client (max number reached)")

	def _get_ready_clients(self):
		"""Retourne le nombre de clients prêts en faisant la somme des booléens"""
		return sum([ Server.clients[client]['ready'] for client in Server.clients ])

	def _sync_objects(self, client):
		"""
		Envoie tous les objets déjà
		posés au client en paramètre.
		Note : n'envoie pas les murs
		"""
		nests = self._simulation.objects.get("nest")
		if nests is not None:
			for nest in nests:
				data = ["nest", *nest]
				self._send_to_client(client, data)
				sleep(0.01)
		resources = self._simulation.objects.get("resource")
		if resources is not None:
			for resource in resources:
				data = ["resource", *resource]
				self._send_to_client(client, data)

	def _receive(self):
		"""
		Fonction qui sert à réceptionner les
		données envoyées depuis chaque client.
		Utilise une sous-fonction 'under_receive' qui
		va manipuler dans un thread les données reçues.
		"""
		# Note : faire une copie permet d'enlever un client sans RuntimeError
		for client in tuple(Server.clients):
			def under_receive():
				try:
					recv_data = client.recv(10240)
				except ConnectionResetError:
					self._disconnect_client(client)
				else:
					try:
						data = pickle.loads(recv_data)
					except pickle.UnpicklingError:
						data = recv_data
					# Si c'est une liste, on sait que la demande est effectuee pour
					# creer un element, ou annuler un placement, ou supprimer une ressource
					if isinstance(data, list):
						if data[0] == "undo":
							str_type = data[1]
							self._simulation.objects[str_type].pop()
							print("Cancelled last object.")
						else:
							str_type, coords, size, width, color = data[0], data[1], data[2], data[3], data[4]
							self._process_data(str_type, coords, size, width, color)
					else:
						data = data.decode()
						if data == "Ready":
							Server.clients[client]['ready'] = True
							ready_clients = self._get_ready_clients()
							self._window.ready_clients = ready_clients
							if ready_clients == len(Server.clients):
								self.send_to_all_clients("GO")
								sleep(5) # On attend 5 secondes le temps que le countdown de interface finisse
								# Lancement de la simulation
								threading.Thread(target=self._simulation.start, daemon=True).start()
							else:
								print("Ready clients: {} / {}".format(ready_clients, len(Server.clients)))
						elif data == "Not ready":
							Server.clients[client]['ready'] = False
							ready_clients = self._get_ready_clients()
							self._window.ready_clients = ready_clients
							print("Ready clients: {} / {}".format(ready_clients, len(Server.clients)))

						elif data == "faster":
							self._simulation.sleep_time /= 2
							print("Faster simulation")
						elif data == "slower":
							self._simulation.sleep_time *= 2
							print("Slower simulation")


			# Si le client n'avait pas de thread associe, on en cree un
			if Server.clients[client]['thread'] is None:
				Server.clients[client]['thread'] = threading.Thread(target=under_receive, daemon=True)
				Server.clients[client]['thread'].start()
			# Si le thread associe a ce client est termine (on a recu de lui), on en refait un
			if not Server.clients[client]['thread'].is_alive():
				Server.clients[client]['thread'] = threading.Thread(target=under_receive, daemon=True)
				Server.clients[client]['thread'].start()

			# print("threads courants :", threading.active_count())

	def _process_data(self, str_type, coords, size, width, color):
		# print("process data : str_type :", str_type, "coords :", coords, "size :", size, "width :", width, "color :", color)
		coords = tuple(coords) # normalement, deja un tuple, mais au cas ou
		str_type = str_type.lower() # normalement, deja en minuscules, mais au cas ou

		# Si l'endroit est libre
		if self._simulation.check_all_coords(coords, size):
			self._simulation.add_to_objects(str_type, coords, size, width, color)

			data = [str_type, coords, size, width, color]
			self.send_to_all_clients(data)

	def _condition(self):
		"""
		Fonction indispensable, elle permet au serveur d'accepter
		des connexions et de recevoir des données en même temps.
		"""
		accepting_thread = threading.Thread(target=self._accept, daemon=True)
		accepting_thread.start()
		accepting_thread.join(0.2)

		receiving_thread = threading.Thread(target=self._receive, daemon=True)
		receiving_thread.start()
		receiving_thread.join(0.2)

		while self._online:
			# S'ils sont morts, quelque chose a ete recu, donc on en recree
			if not accepting_thread.is_alive():
				accepting_thread = threading.Thread(target=self._accept, daemon=True)
				accepting_thread.start()
			accepting_thread.join(0.2)

			if not receiving_thread.is_alive():
				receiving_thread = threading.Thread(target=self._receive, daemon=True)
				receiving_thread.start()
			receiving_thread.join(0.2)

	def _send_to_client(self, client, data):
		"""Envoie des données à un seul client"""
		data = pickle.dumps(data)
		try:
			client.sendall(data)
		except BrokenPipeError as e:
			print(e)
			sys.exit(1)
		except ConnectionResetError:
			self._disconnect_client(client)

	def _disconnect_client(self, client):
		print("[Warning] Client disconnected. Closing associated connection.")
		client.close()
		del Server.clients[client]
		if self._window is not None:
			self._window.clients -= 1
			self._window.ready_clients = self._get_ready_clients()

	def send_to_all_clients(self, data):
		"""Envoie des informations à tous les clients"""
		for client in Server.clients:
			self._send_to_client(client, data)

	def quit(self):
		self._online = False
		if self._window is not None:
			self._window.quit_window()
		self._socket.close()
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
