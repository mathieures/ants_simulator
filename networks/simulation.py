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
		
		self._first_ant = True

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

		length = len(self._ants)

		ants = ["move_ants"] + [None] * len(self._ants) # liste [delta_x, delta_y] (et parfois une couleur) pour bouger les fourmis

		def simulate_ants_in_thread(start, number):
			end = start + number
			if end > length:
				end = length

			for i in range(start, end):
				ant = self._ants[i]
				ant_index = i+1 # indice dans ants

				x, y = ant.coords # position actuelle
				if ant.has_resource:
					pheromones.append((x, y)) # l'ordre n'est pas important
					# S'il y a un mur mais que la fourmi porte une ressource,
					if self.is_wall(x, y):
						# On contourne le mur par la gauche
						ant.direction += 45
					else:
						ant.go_to_nest()
					ant.lay_pheromone()
				# Si elle n'en a pas mais qu'il y a un mur, elle fait demi-tour
				elif self.is_wall(x, y):
					ant.direction += 180
				# Sinon elle n'a rien trouve
				elif ant.endurance > 0:
					ant.seek_resource()
					ant.endurance -= 1
				else:
					ant.go_to_nest()

				ant.move()
				new_x, new_y = ant.coords # on sait que la position a change
				delta_x = new_x - x # deplacement relatif
				delta_y = new_y - y
				ants[ant_index] = [delta_x, delta_y] # les fourmis sont toujours dans le meme ordre

				index_resource = self.is_resource(new_x, new_y)
				# Si la fourmi touche une ressource
				if not ant.has_resource and index_resource is not None:
					# Une fourmi a touche une ressource
					# On donne aux clients l'index de la ressource touchee
					ant.has_resource = True
					if self._first_ant:
						ants[ant_index].append([index_resource, "first_ant"])
						self._first_ant = False
					else:
						ants[ant_index].append(index_resource)
				# Si la fourmi est sur son nid
				elif ant.coords == ant.nest:
					ant.has_resource = False
					ant.endurance = ant.MAX_ENDURANCE
					ants[ant_index].append('base') # Reprendre la couleur d'origine
				elif ant.endurance <= 0:
					ants[ant_index].append("black")


		step = 20
		while self._server.online:
			temps_sim = time()
			pheromones = ["pheromones"] # liste de coordonnees (x, y), qu'on remet a zero

			curr_thread = None
			for i in range(0, length, step):
				curr_thread = threading.Thread(target=simulate_ants_in_thread, args=(i, step), daemon=True)
				curr_thread.start()
			if curr_thread is not None:
				curr_thread.join(1) # on donne 1s maximum au dernier pour finir

			# S'il y a de nouvelles pheromones
			if len(pheromones) > 1:
				# On envoie les mouvements des fourmis + les pheromones pour eviter de la latence
				self._server.send_to_all_clients([ants, pheromones])

			# Sinon on n'envoie que les positions
			else:
				self._server.send_to_all_clients(ants)

			# print("temps sim :", time() - temps_sim)
			sleep(0.05) # ajout d'une latence
		print("[simulation terminee]")
		# faudra afficher le vainqueur ou quoi par là

	def is_wall(self, x, y):
		""" Retourne True s'il y a un mur à cette position, False sinon """
		# Note : peu optimal
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
		""" Retourne l'indice de la ressource à cette position ou None s'il n'y en a pas """
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
						# print("-> is not good spot")
						return False
		# print("-> is good spot")
		return True

	def check_all_coords(self, coords_list, size):
		"""Vérifie que toutes les coordonnées de la liste sont valides"""
		for i in range(0, len(coords_list) - 1, 2):
			if not self._is_good_spot(coords_list[i], coords_list[i+1], size):
				# print("non, coords", (coords_list[i], coords_list[i+1]), "size :", size, "pas bonnes")
				return False
		# print("toutes les coords sont ok")
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
		# print("ajouté côté serveur :", str_type, coords, size, width, color)
