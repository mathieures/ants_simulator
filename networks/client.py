import sys

import socket
import pickle
import threading


# pour le debug
from time import time


class Client:

	@property
	def ressource_ok(self):
		return self._resource_ok

	@property
	def nest_ok(self):
		return self._nest_ok

	@property
	def wall_ok(self):
		return self._wall_ok

	@property
	def interface(self):
		return self._interface

	@interface.setter
	def interface(self, new_interface):
		self._interface = new_interface

	@property
	def connected(self):
		return self._connected

	@connected.setter
	def connected(self, is_connected):
		self._connected = is_connected


	def __init__(self, ip, port):
		try:
			assert isinstance(ip, str), "Erreur l'IP pour se connecter au serveur n'est pas une châine de caractère valide"
			assert isinstance(port, int), "Erreur le port pour se connecter au serveur n'est pas un entier valide"
			assert len(ip) > 0, "Erreur l'IP pour se connecter au serveur ne peut pas être vide"
		except AssertionError as e:
			print(e)
			sys.exit()

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._ip = ip
		self._port = port

		self._resource_ok = False
		self._nest_ok = False
		self._wall_ok = False

		self._connected = True

		self._interface = None


	def connect(self):
		try:
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
		str_type = object_type.__name__ # nom de classe de l'objet
		# print("objet demandé : str_type :", str_type, "position :", position, "size :", size, "width :", width, "color :", color)
		data = pickle.dumps([str_type, position, size, width, color])
		try:
			self._socket.send(data)
		except BrokenPipeError:
			print("Erreur envoi donnée. Fermeture")
			sys.exit(1)

	def undo_object(self, str_type):
		""" Demande au serveur d'annuler le placement d'un objet """
		print("Demande d'annulation objet {}".format(str_type))
		data = pickle.dumps(["undo",str_type])
		try:
			self._socket.send(data)
		except BrokenPipeError:
			print("Erreur envoi donnée. Fermeture")
			sys.exit(1)


	def receive(self):
		"""Reçoit les signaux envoyés par les clients pour les objets créés"""
		# Note : on peut ne pas le mettre dans un thread car le client ne fait que recevoir
		while True:
			temps_attente0 = time()
			recv_data = self._socket.recv(10240)
			temps_attente1 = time()
			try:
				data = pickle.loads(recv_data)
			except pickle.UnpicklingError:
				data = recv_data
			temps_receive0 = time()
			print("temps d'attente :", temps_attente1 - temps_attente0, end=' ; ')

			# Si on doit bouger des fourmis
			if isinstance(data, list) or isinstance(data, tuple):
				'''
				data est de la forme : ["move_ants", [deltax_fourmi1, deltay_fourmi1], [deltax_fourmi2, deltay_fourmi2]...]
				data peut aussi etre de la forme [["move_ants", [deltax...]], ["pheromones", (fourmi1x, fourmi1y)...]]
				Note : les listes internes peuvent contenir un autre élément, la couleur de la fourmi.
				Note 2 : on soustrait 1 car le 1er élément est la str
				'''

				# Si on a les mouvements des fourmis et les pheromones en meme temps
				if len(data) == 2 and data[0][0] == "move_ants":
					# On bouge les fourmis
					self._interface.move_ants(data[0][1:])

					temps_ph = time()
					# On cree ou fonce les pheromones
					self._interface.create_pheromones(data[1][1:])
					# print("temps phéros :", time() - temps_ph)

				elif data[0] == "move_ants":
					self._interface.move_ants(data[1:])

				# Si on doit creer des fourmis
				elif data[0] == "ants":
					# data est de la forme : ["ants", [coords_fourmi1, couleur_fourmi1], [coords_fourmi2, couleur_fourmi2]...]
					self._interface.create_ants(data[1:])

				# Si on reçoit la couleur locale de l'interface
				elif data[0] == "color":
					self._interface.local_color = data[1]

				# Si c'est un objet cree par un client
				else:
					str_type, pos, size, width, color = data[0], data[1], data[2], data[3], data[4]
					# Communique l'information d'un nouvel objet à l'interface
					self._interface._create_object(str_type, pos, size=size, width=width, color=color)

			else:
				if data == "GO":
					self._interface.countdown()
			temps_receive1 = time()
			print("receive :", temps_receive1 - temps_receive0)
