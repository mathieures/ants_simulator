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
		self.start_simulation()

	def init_ants(self):
		""" Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
		ants = ["ants"] # liste des fourmis a envoyer au serveur
		for nest in self.objects["nest"]:
			# nest est un tuple de la forme (coords, size, width, color)
			x,y = nest[0]
			color = nest[3]
			for i in range(10):
				print("Ajout d'une fourmi en {} {}".format(x,y))
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
				ants.append(((ant.x,ant.y), ant.color))
			self.server.send_to_clients(ants)
			time.sleep(0.1)
