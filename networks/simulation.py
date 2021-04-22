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

	def init_ants(self):
		for nest in self.objects["nest"]:
			# nest est un tuple de la forme (coords, size, width, color)
			x,y = nest[0]
			color = nest[3]
			for i in range(10):
				print("Ajout d'une fourmi en {} {}".format(x,y))
				self.ants.append(ant.Ant(x,y,color))
				self.server.send_to_clients(("ant", (x, y), 3, None, color))
				time.sleep(0.1) # Ajout d'une latence pour bien pouvoir envoyer toutes les donnees