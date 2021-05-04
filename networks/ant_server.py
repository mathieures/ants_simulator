import random
import tkinter as tk

class Ant:

	# Accesseurs et mutateurs
	#########################
	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def direction(self):
		return self._direction

	@direction.setter
	def direction(self, pdirection):
		self._direction = pdirection

	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, pcolor):
		self._color = pcolor

	@property
	def has_resource(self):
		return self._has_resource

	@has_resource.setter
	def has_resource(self, pbool):
		self._has_resource = pbool

	@property
	def id(self):
		return self._id

	###############################

	ID = 0

	def __init__(self, posX, posY, color):
		self._x = posX
		self._y = posY
		self._color = color
		self._direction = random.randint(0,360)
		self.nest = (posX, posY) # nest etant un tuple de coordonnes : (x, y)

		self._has_resource = False # Booleen pour indiquer si une fourmi possede une ressource
		#self._pheromone = [(posX,posY)] # Pheromone propre a chaque fourmi pour pouvoir retourner dans son nid si elle trouve une ressource

		self._id = Ant.ID
		Ant.ID += 1

	def change_position(self):
		""" Méthode qui change la position de la fourmi en fonction de sa direction """
		side = self._side()
		# Si c'est le 1er ou 2e quartant
		if side < 3:
			self._y -= 1
			if side == 1:
				self._x += 1
			else:
				self._x -= 1
		# Si c'est le 3e ou 4e quartant
		else:
			self._y += 1
			if side == 3:
				self._x -= 1
			else:
				self._x += 1

	def search_resource(self):
		""" Fonction qui donne une direciton aleatoire pour chercher une ressource """

		# Si la fourmi atteint un bord du haut ou un bord gauche, elle change de direction
		if self._y <= 0 or self._x <= 0:
			self._direction = 315
		else:
			# On randomize la direction pour donner un effet de mouvement aleatoire
			self._direction = random.randint(self._direction-30, self._direction+30) % 360

	def go_to_nest(self):
		""" La fourmi pointe vers le nid """
		deltax = self.nest[0] - self.x
		deltay = self.nest[1] - self.y
		# Si deltax est positif, la fourmi doit aller vers la droite
		if deltax > 0:
			# Si deltay est positif, la fourmi doit aller vers le bas
			if deltay > 0:
				# On met une direction dans le 4 eme quartant
				self._direction = 315
			else:
				# direction dans le 1er quartant
				self._direction = 45
		else:
			if deltay > 0:
				# direction dans le 3 eme quartant
				self._direction = 225
			else:
				# 2 eme quartant
				self._direction = 135

	def touch_nest(self):
		if self._x == self.nest[0] and self._y == self.nest[1]:
			return True
		return False

	def _side(self):
		""" Fonction qui renvoie un int correspondant au numéro du quartant de la direction """
		if self._direction < 90:
			return 1
		elif self._direction >= 90 and self._direction < 180:
			return 2
		elif self._direction >= 180 and self._direction < 270:
			return 3
		return 4