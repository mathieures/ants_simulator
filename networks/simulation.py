import threading
from time import sleep
import ant_server

# pour le debug
from time import time


class Simulation:
	""" Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

	@property
	def objects(self):
		return self._objects

	@objects.setter
	def objects(self, new_objects):
		self._objects = new_objects

	def __init__(self, server):
		self._server = server

		self._ants = [] # Liste d'instances de fourmi
		self._objects = {}
		# self._all_pheromones = [] # Liste de coordonnes qui sera completee par une fourmi qui trouve une ressource

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
		nests = self._objects.get("nest")
		# Sécurité pour ne pas commencer sans nid
		if nests is not None:
			for nest in self._objects["nest"]:
				# nest est un tuple de la forme (coords, size, width, color)
				x, y = nest[0]
				color = nest[3]
				for i in range(20):
					curr_ant = ant_server.AntServer(x, y, color)
					self._ants.append(curr_ant)
					ants.append(((x,y), color))
			self._server.send_to_all_clients(ants)
			sleep(0.1) # Ajout d'une latence pour envoyer les donnees

	def start(self):
		""" Fonction principale qui lance la simulation et calcule le déplacement de chaque fourmi """
		self.init_ants()

		step = 20
		length = len(self._ants)

		ants = [None] * len(self._ants) # liste [delta_x, delta_y] (et parfois une couleur) pour bouger les fourmis		
		
		def simulate_ants_in_thread(start, number):
			end = start + number
			if end > length:
				end = length
			
			for i in range(start, end):
				ant = self._ants[i]

				x, y = ant.coords # position actuelle
				if ant.has_resource:
					pheromones.append((x, y)) # on peut ne pas les ajouter dans l'ordre

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
				new_x, new_y = ant.coords # on sait que la position a change
				delta_x = new_x - x # deplacement relatif
				delta_y = new_y - y
				ants[ant.id] = [delta_x, delta_y] # les fourmis sont toujours dans le meme ordre

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


		# for i in range(1500):
		while self._server.online:
			temps_sim = time()
			pheromones = [] # liste de coordonnees (x, y), qu'on remet a zero

			for i in range(0, length, step):
				curr_thread = threading.Thread(target=simulate_ants_in_thread, args=(i, step), daemon=True)
				curr_thread.start()
			curr_thread.join(1) # on donne 1s au dernier pour finir sinon tant pis


			# dans un thread maintenant
			'''
			for ant in self._ants:
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
				new_x, new_y = ant.coords # on sait que la position a change
				delta_x = new_x - x # deplacement relatif
				delta_y = new_y - y
				ants.append([delta_x, delta_y]) # les fourmis sont toujours dans le meme ordre

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
			'''

			ants.insert(0, "move_ants") # on precise que l'on veut bouger les fourmis
			# S'il y a de nouvelles pheromones
			if pheromones:
				# On envoie les mouvements des fourmis + les pheromones pour eviter de la latence
				pheromones.insert(0, "pheromones") # on precise que l'on veut ajouter des pheromones
				self._server.send_to_all_clients([ants, pheromones])
				ants.pop(0) # pour le test, jusqu'à une nouvelle solution

			# Sinon on n'envoie que les positions
			else:
				self._server.send_to_all_clients(ants)
				ants.pop(0) # pour le test, jusqu'à une nouvelle solution

			# print("temps sim :", time() - temps_sim)
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
			for i in range(0, len(coords_wall), 2):
				if (coords_wall[i] - offset <= x <= coords_wall[i] + offset) and (
					coords_wall[i+1] - offset <= y <= coords_wall[i+1] + offset):
					return True
		return False

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