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
	def has_resource(self):
		return self._has_resource

	def __init__(self, posX, posY, color, nest):
		self._x = posX
		self._y = posY
		self.color = color
		self.direction = random.randint(0,360)
		self.nest = nest # nest etat un tuple de coordonnes : (x,y)
		self.fov = 60 # champ de vision d'une fourmi

		self._has_resource = False # Booleen pour indiquer si une fourmi possede une ressource
		self._pheromon = [(posX,posY)] # Pheromone propre a chaque fourmi pour pouvoir retourner dans son nid si elle trouve une ressource

	def search_resource(self):
		side = self._side()
		if side < 3:
			self._y -= 1
			if side == 1:
				self._x += 1
			else:
				self._x -= 1
		else:
			self._y += 1
			if side == 3:
				self._x -= 1
			else:
				self._x += 1
		self.direction = random.randint(self.direction-10, self.direction+10)
		if self.direction > 360:
			self.direction -= 10
		self._pheromon.append((self._x, self._y))

	def go_to_nest(self):
		pass

	def _side(self):
		""" Fonction qui renvoie un int correspondant au numero du quartant de la direction """
		if self.direction < 90:
			return 1
		elif self.direction >= 90 and self.direction < 180:
			return 2
		elif self.direction >= 180 and self.direction < 270:
			return 3
		return 4