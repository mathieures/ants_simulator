import random
import tkinter as tk

class Ant:
	
	def __init__(self, posX, posY, color):
		self.x = posX
		self.y = posY
		self.color = color
		self.direction = random.randint(0,360)
