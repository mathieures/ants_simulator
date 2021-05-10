import sys

import socket
import pickle
import threading


class Client:
	def __init__(self, ip, port):
		try:
			assert isinstance(ip, str), "Erreur l'IP pour se connecter au serveur n'est pas une chaîne de caractère valide"
			assert isinstance(port, int), "Erreur le port pour se connecter au serveur n'est pas un entier valide"
			assert len(ip) > 0, "Erreur l'IP pour se connecter au serveur ne peut pas être vide"
		except AssertionError as e:
			print(e)
			sys.exit()

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._ip = ip
		self._port = port

		self._connected = True

		self._interface = None

	@property
	def interface(self):
		return self._interface

	@interface.setter
	def interface(self, new_interface):
		self._interface = new_interface

	@property
	def connected(self):
		return self._connected


	def connect(self):
		try:
			print(self._ip)
			self._socket.connect((self._ip, self._port))
			self._connected = True
			self.receive()
		except ConnectionRefusedError:
			print("Erreur serveur non connecté")
			sys.exit(1)

	def send(self, element, pos, data):
		"""
		Fonction d'envoi au serveur
		element:  type de donnée
		pos: liste de position [x, y]
		data: taille de l'objet
		"""
		all = pickle.dumps([element, pos, data])
		self._socket.send(all)


	def set_ready(self):
		"""Informe le serveur que ce client est prêt"""
		print("Ready envoyé")
		self._socket.send("Ready".encode())

	def set_notready(self):
		"""Informe le serveur que ce client n'est plus prêt"""
		print("à faire : set notready")
		pass

	def ask_object(self, object_type, position, size=None, width=None, color=None):
		"""
		Demande au serveur si on peut placer
		un élément d'un type et d'une taille donnés
		à la position donnée.
		"""
		print("object_type :", object_type, "name :", object_type.__name__)
		str_type = object_type.__name__
		print("objet demandé : str_type :", str_type, "position :", position, "size :", size, "width :", width, "color :", color)
		data = pickle.dumps([str_type, position, size, width, color])
		try:
			self._socket.send(data)
		except BrokenPipeError:
			print("Erreur envoie donnée. Fermeture")
			sys.exit(1)


	def receive(self):
		"""Reçoit les signaux envoyés par les clients pour les objets créés"""
		while True:
			recv_data = self._socket.recv(10240)
			try:
				data = pickle.loads(recv_data)
			except pickle.UnpicklingError:
				data = recv_data
			except EOFError:
				continue

			if isinstance(data, list) or isinstance(data, tuple):
				# Si on doit bouger des fourmis
				## data est de la forme : ["move_ants", [deltax_fourmi1, deltay_fourmi1], [deltax_fourmi2, deltay_fourmi2]...]
				## data peut aussi etre de la forme [["move_ants", [deltax...]], ["pheromones", (fourmi1x, fourmi1y)...]]
				## Note : les listes internes peuvent contenir un autre élément, la couleur de la fourmi.
				## Note 2 : on soustrait 1 car le 1er élément est la str

				# si on a les mouvements des fourmis et les pheromones en meme temps
				if len(data) == 2 and data[0][0] == "move_ants":
					for i in range(1, len(data[0])):
						self._interface.move_ant(i-1, data[0][i][0], data[0][i][1]) # id, delta_x, delta_y
						if len(data[0][i]) == 3:
							self._interface.color_ant(i-1, data[0][i][2]) # id, couleur
					for i in range(1, len(data[1])):
						self._interface.create_pheromone(data[1][i])

				elif data[0] == "move_ants":
					for i in range(1, len(data)):
						self._interface.move_ant(i-1, data[i][0], data[i][1]) # id, delta_x, delta_y
						if len(data[i]) == 3:
							self._interface.color_ant(i-1, data[i][2]) # id, couleur

				# Si on doit créer des fourmis
				elif data[0] == "ants":
					# data est de la forme : ["ants", [coords_fourmi1, couleur_fourmi1], [coords_fourmi2, couleur_fourmi2]...]
					for i in range(1, len(data)):
						self._interface.create_ant(data[i][0], data[i][1]) # coords, couleur

				# Si on reçoit la couleur locale de l'interface
				elif data[0] == "color":
					self._interface.local_color = data[1]

				# Si c'est un objet créé par un client
				else:
					str_type, pos, size, width, color = data[0], data[1], data[2], data[3], data[4]
					# Communique l'information d'un nouvel objet à l'interface
					# print("dit à interface de créer :", str_type, pos, size, width, color)
					self._interface._create_object(str_type, pos, size=size, width=width, color=color)

			else:
				if data == "clear_ants":
					self._interface.clear_ants()
				elif data == "GO":
					self._interface.countdown()
