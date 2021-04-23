import random
import ant
import time

class Simulation():
	""" Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

	def __init__(self, objects, server):
		self.server = server
		self.objects = objects

		self.ants = [] # Liste d'instances de fourmi
		self._pheromon = [] # Liste de coordonnes qui sera completee par une fourmi qui trouve une resource

		self.init_ants()
		time.sleep(0.1) # Ajout d'une latence pour envoyer les donnees
		self.start_simulation()

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
		for nest in self.objects["nest"]:
			# nest est un tuple de la forme (coords, size, width, color)
			x,y = nest[0]
			color = nest[3]
			for i in range(20):
				curr_ant = ant.Ant(x,y,color)
				self.ants.append(curr_ant)
				ants.append(((x,y), color))
		self.server.send_to_all_clients(ants)

	def start_simulation(self):
		for i in range(500):
			self.server.send_to_all_clients("clear_ants")
			ants = ["move_ants"] # liste de [deltax, deltay (,couleur)] a envoyer au client pour bouger les fourmis
			for ant in self.ants:
				lastx, lasty = ant.x, ant.y
				if ant.has_resource:
					ant.go_to_nest()
					self._pheromon.append((ant.x, ant.y))
				else:
					ant.search_resource()
				x,y = ant.x, ant.y
				deltax = x - lastx
				deltay = y - lasty
				ants.append([deltax, deltay])
				# Si la fourmi touche un mur, elle prend une direction opposee
				if self.touch_wall(x,y, 4):
					try:
						ant.direction = (ant.direction + 180) % 360
					except:
						print("bug de direction")
						print(ant.direction, type(ant.direction))
				elif self.touch_resource(x, y, 4):
					# La fourmi devient grise car elle touche une ressource
					ant.has_resource = True
					ants[ant.id+1].append("grey")
				elif ant.touch_nest():
					ant.has_resource = False
					ants[ant.id+1].append(ant.color)
			self.server.send_to_all_clients(ants)
			time.sleep(0.1) # Ajout de latence

	def touch_wall(self, x, y, size):
		""" Fonction qui retourne True si la position touche un mur, False sinon """
		if "wall" not in self.objects:
			return False
		for wall in self.objects["wall"]:
			offset = wall[2]
			coords_obj = wall[0]
			for i in range(0,len(wall[0]), 2):
				if (coords_obj[i] - offset <= x <= coords_obj[i] + offset) and (
					coords_obj[i+1] - offset <= y <= coords_obj[i+1] + offset):
					return True
		return False

	def touch_resource(self, x, y, size):
		""" Fonction qui retourne True si la position touche une ressource, False sinon """
		if "resource" not in self.objects:
			return False
		for resource in self.objects["resource"]:
			coords_obj = resource[0]
			offset = resource[1]
			if (coords_obj[0] - offset <= x <= coords_obj[0] + offset) and (
					coords_obj[1] - offset <= y <= coords_obj[1] + offset):
					return True
		return False

