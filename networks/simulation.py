import random
import ant
import time

class Simulation():
	""" Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

	def __init__(self, objects, server):
		self.server = server
		self.objects = objects

		self.ants = [] # Liste d'instances de fourmi

		self.init_ants()
		time.sleep(0.1)
		self.start_simulation()

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
		for nest in self.objects["nest"]:
			# nest est un tuple de la forme (coords, size, width, color)
			x,y = nest[0]
			color = nest[3]
			for i in range(10):
				curr_ant = ant.Ant(x,y,color, (x,y))
				self.ants.append(curr_ant)
				ants.append(((x,y), color))
		self.server.send_to_clients(ants)

	def start_simulation(self):
		for i in range(200):
			self.server.send_to_clients("clear_ants")
			ants = ["ants"] # liste des fourmis a envoyer au serveur
			for ant in self.ants:
				if ant.has_resource == False:
					ant.search_resource()
				else:
					ant.go_to_nest()
				x,y = ant.x, ant.y
				# Si la fourmi touche un mur, elle prend une direction opposee
				if self.touch_wall(x,y, 3):
					ant.direction = (ant.direction + 180) % 360 
				ants.append(((x,y), ant.color))
			self.server.send_to_clients(ants)
			time.sleep(0.1)

	def touch_wall(self, x, y, size):
		""" Fonction qui retourne True si la position touche un mur, False sinon """
		for wall in self.objects["wall"]:
			offset = wall[2]
			coords_obj = wall[0]
			for i in range(0,len(wall[0]), 2):
				if (coords_obj[i] - offset <= x+size <= coords_obj[i] + offset) and (
					coords_obj[i+1] - offset <= y+size <= coords_obj[i+1] + offset):
					return True
		return False
