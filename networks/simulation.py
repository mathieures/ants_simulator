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

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
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
			for i in range(0, len(coords_wall), 2):
				if (coords_wall[i] - offset <= x <= coords_wall[i] + offset) and (
					coords_wall[i+1] - offset <= y <= coords_wall[i+1] + offset):
					return True
		return False

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
