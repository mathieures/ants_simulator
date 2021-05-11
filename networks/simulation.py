<<<<<<< HEAD
import random
import time

import ant_server


class Simulation:
	""" Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

	def __init__(self, objects, server):
		self.server = server
		self.objects = objects

		self.ants = [] # Liste d'instances de fourmi
		self._pheromone = [] # Liste de coordonnes qui sera completee par une fourmi qui trouve une resource

		self.init_ants()
		time.sleep(0.1) # Ajout d'une latence pour envoyer les donnees
		self.start_simulation()
=======
from time import sleep
import ant_server

class Simulation:
	""" Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

	@property
	def objects(self):
		return self._objects

	@objects.setter
	def objects(self, new_objects):
		self._objects = new_objects

	def __init__(self, server):
		self.server = server

		self.ants = [] # Liste d'instances de fourmi
		self._objects = {}
		# self._all_pheromones = [] # Liste de coordonnes qui sera completee par une fourmi qui trouve une ressource
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
<<<<<<< HEAD
		nests = self.objects.get("nest")
		# Sécurité pour ne pas commencer sans nid
		if nests is not None:
			for nest in self.objects["nest"]:
				# nest est un tuple de la forme (coords, size, width, color)
				x,y = nest[0]
				color = nest[3]
				for i in range(20):
					curr_ant = ant_server.Ant(x,y,color)
					self.ants.append(curr_ant)
					ants.append(((x,y), color))
			self.server.send_to_all_clients(ants)

	def start_simulation(self):
		""" Fonction principale qui lance la simulation et calcule le déplacement de chaque fourmi """
		# for i in range(500):
		while True:
			self.server.send_to_all_clients("clear_ants")
			ants = ["move_ants"] # liste [deltax, deltay] (et parfois une couleur) a envoyer au client pour bouger les fourmis
			pheromones = ["pheromones"]
			for ant in self.ants:
				lastx, lasty = ant.x, ant.y
				if ant.has_resource:
					ant.go_to_nest()
					self._pheromone.append((ant.x, ant.y))
					pheromones.append((ant.x, ant.y))
				else:
					ant.search_resource()
				# Si la fourmi touche un mur, elle prend une direction opposee
				if self.touch_wall(ant.x, ant.y):
					ant.direction = (ant.direction + 180) % 360
				ant.change_position()
				x,y = ant.x, ant.y
				deltax = x - lastx
				deltay = y - lasty
				ants.append([deltax, deltay])
				if self.touch_resource(x, y):
					# La fourmi devient grise car elle touche une ressource
					ant.has_resource = True
					ants[ant.id+1].append("grey") # +1 car le 1er élément est une str
				elif ant.touch_nest():
					ant.has_resource = False
					ants[ant.id+1].append(ant.color) # +1 car le 1er élément est une str
			if len(pheromones) > 1:
				# On envoie les mouvements des fourmis + les pheromones pour eviter encore de la latence
				self.server.send_to_all_clients([ants,pheromones])
			else:
				self.server.send_to_all_clients(ants)
			# time.sleep(0.1) # ajout d'une latence

	def touch_wall(self, x, y):
		""" Fonction qui retourne True si la position touche un mur, False sinon """
		if "wall" not in self.objects:
			return False
		for wall in self.objects["wall"]:
			offset = wall[2] // 2 + 1 # width / 2, +1 pour l'outline
			coords_wall = wall[0]
=======
		nests = self._objects.get("nest")
		# Sécurité pour ne pas commencer sans nid
		if nests is not None:
			for nest in self._objects["nest"]:
				# nest est un tuple de la forme (coords, size, width, color)
				x, y = nest[0]
				color = nest[3]
				for i in range(20):
					curr_ant = ant_server.AntServer(x, y, color)
					self.ants.append(curr_ant)
					ants.append(((x,y), color))
			self.server.send_to_all_clients(ants)
			sleep(0.1) # Ajout d'une latence pour envoyer les donnees

	def start(self):
		""" Fonction principale qui lance la simulation et calcule le déplacement de chaque fourmi """
		self.init_ants()

		for i in range(1500):
			ants = [] # liste [deltax, deltay] (et parfois une couleur) a envoyer au client pour bouger les fourmis
			pheromones = []

			for ant in self.ants:
				x, y = ant.coords # position actuelle
				if ant.has_resource:
					# self._all_pheromones.append((x, y)) # a pas l'air d'etre utilise
					pheromones.append((x, y)) # test de pas envoyer les phero pour voir si c'est ça qui fait laguer

					# S'il y a un mur mais que la fourmi porte une ressource,
					# elle essaie de contourner le mur par la gauche
					if self.is_wall(x, y):
						ant.direction += 30
					else:
						ant.go_to_nest()
					ant.lay_pheromone()
				# Si elle n'en a pas mais qu'il y a un mur, elle fait demi-tour
				elif self.is_wall(x, y):
					ant.direction += 180
				# Sinon elle n'a rien trouve
				else:
					ant.seek_resource()

				ant.move()
				new_x, new_y = ant.coords # la position a change
				deltax = new_x - x # deplacement relatif
				deltay = new_y - y
				ants.append([deltax, deltay]) # les fourmis sont toujours dans le meme ordre

				index_resource = self.is_resource(new_x, new_y)
				# Si la fourmi touche une ressource
				if not ant.has_resource and index_resource is not None:
					# On donne aux clients l'index de la ressource touchee
					ant.has_resource = True
					ants[ant.id].append(index_resource)
				# Si la fourmi est sur son nid
				elif ant.coords == ant.nest:
					ant.has_resource = False
					ants[ant.id].append(-1) # Signal pour dire de reprendre la couleur d'origine
			ants.insert(0, "move_ants") # on precise que l'on veut bouger les fourmis
			# S'il y a de nouvelles pheromones
			if pheromones:
				# On envoie les mouvements des fourmis + les pheromones pour eviter encore de la latence
				pheromones.insert(0, "pheromones") # on precise que l'on veut ajouter des pheromones
				self.server.send_to_all_clients([ants, pheromones])

			# Sinon on n'envoie que les positions
			else:
				self.server.send_to_all_clients(ants)

			# sleep(0.1) # ajout d'une latence
			sleep(0.05) # ajout d'une latence # note de mathieu : j'ai accéléré un peu
		print("[simulation terminee]")

	def is_wall(self, x, y):
		""" Fonction qui retourne True s'il y a un mur à cette position, False sinon """
		if "wall" not in self._objects:
			return False
		for wall in self._objects["wall"]:
			coords_wall, width = wall[0], wall[2]
			offset = width // 2 + 1 # +1 pour l'outline
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
			for i in range(0, len(coords_wall), 2):
				if (coords_wall[i] - offset <= x <= coords_wall[i] + offset) and (
					coords_wall[i+1] - offset <= y <= coords_wall[i+1] + offset):
					return True
		return False

<<<<<<< HEAD
	def touch_resource(self, x, y):
		""" Fonction qui retourne True si la position touche une ressource, False sinon """
		if "resource" not in self.objects:
			return False
		for resource in self.objects["resource"]:
			coords_resource = resource[0]
			offset = resource[1] // 2 + 1 # size / 2, +1 pour l'outline
			if (coords_resource[0] - offset <= x <= coords_resource[0] + offset) and (
				coords_resource[1] - offset <= y <= coords_resource[1] + offset):
					return True
		return False
=======
	def is_resource(self, x, y):
		""" Fonction qui retourne True s'il y a une ressource à cette position, False sinon """
		if "resource" not in self._objects:
			return None
		i = 0
		for resource in self._objects["resource"]:
			coords_resource, size = resource[0], resource[1]
			offset = size // 2 + 1 # +1 pour l'outline
			if (coords_resource[0] - offset <= x <= coords_resource[0] + offset) and (
				coords_resource[1] - offset <= y <= coords_resource[1] + offset):
					return i # On retourne l'index de la ressource
			i += 1
		return None

	def _is_good_spot(self, x, y, size):
		"""
		Retourne True si les coordonnées données en paramètre sont
		disponibles en fonction de la taille donnée, False sinon
		"""
		for str_type in self._objects:
			for properties in self._objects[str_type]:
				coords_obj, size_obj, width_obj, color_obj = properties
				offset = size_obj
				# On teste un espace autour des coords
				for i in range(0, len(coords_obj) - 1, 2):
					if (coords_obj[i] - offset <= x <= coords_obj[i] + offset) and (
						coords_obj[i+1] - offset <= y <= coords_obj[i+1] + offset):
						print("-> is not good spot")
						return False
		# print("-> is good spot")
		return True

	def check_all_coords(self, coords_list, size):
		"""Vérifie que toutes les coordonnées de la liste sont valides"""
		for i in range(0, len(coords_list) - 1, 2):
			if not self._is_good_spot(coords_list[i], coords_list[i+1], size):
				# print("non, coords", (coords_list[i], coords_list[i+1]), "size :", size, "pas bonnes")
				return False
		print("toutes les coords sont ok")
		return True

	def add_to_objects(self, str_type, coords, size, width, color):
		"""Ajoute une entrée au dictionnaire d'objets de la simulation"""
		# Note : Pour les objets 'wall', les coordonnées sont une liste
		# Si c'est le premier objet de ce type que l'on voit, on init
		if self._objects.get(str_type) is None:
			self._objects[str_type] = []
		if size is None:
			size = width
		# Dans tous les cas, on ajoute les nouvelles coords, taille et couleur
		self._objects[str_type].append((coords, size, width, color))
		print("ajouté côté serveur :", str_type, coords, size, width, color)
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
