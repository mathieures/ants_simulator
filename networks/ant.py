import random
import tkinter as tk

class Ant:

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
	def has_resource(self):
		return self._has_resource

	def __init__(self, posX, posY, color, nest_coords):
		self._x = posX
		self._y = posY
		self.color = color
		self._direction = random.randint(0,360)
		self.nest = nest_coords # nest etat un tuple de coordonnes : (x,y)

		self._has_resource = False # Booleen pour indiquer si une fourmi possede une ressource
		self._pheromon = [(posX,posY)] # Pheromone propre a chaque fourmi pour pouvoir retourner dans son nid si elle trouve une ressource

	def search_resource(self):
		""" methode qui change la position de la fourmi en fonction de sa direction """
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
		# Si la fourmi atteint un bord du haut ou un bord gauche
		if self._y <= 0 or self._x <= 0:
			self._direction = 315
		else:
			# On randomize la direction pour donner un effet de mouvement aleatoire
			self._direction = random.randint(self._direction-30, self._direction+30)
		if self._direction > 360:
			self._direction -= 30
		self._pheromon.append((self._x, self._y))

	def go_to_nest(self):
		if self._x == self.nest[0] and self._y == self.nest[1]:
			self.has_resource = False
			return
		self._x,self._y = self._pheromon.pop()

	def _side(self):
		""" Fonction qui renvoie un int correspondant au numero du quartant de la direction """
		if self._direction < 90:
			return 1
		elif self._direction >= 90 and self._direction < 180:
			return 2
		elif self._direction >= 180 and self._direction < 270:
			return 3
		return 4