import tkinter as tk
from tkinter import messagebox
import threading
import time

from .easy_menu import EasyMenu
from .easy_button import EasyButton
from .nest import Nest
from .resource import Resource
from .wall import Wall
from .pheromone import Pheromone
from .ant import Ant


from networks import client


class Interface:

	@property
	def root(self):
		return self._root

	@property
	def canvas(self):
		return self._canvas

	@property
	def current_object_type(self):
		return self._current_object_type

	@current_object_type.setter
	def current_object_type(self, new_object_type):
		self._current_object_type = new_object_type

	@property
	def local_color(self):
		return self._local_color

	@local_color.setter
	def local_color(self, new_color):
		self._local_color = new_color


	def __init__(self, client, width, height):
		self._root = tk.Tk()
		self._client = client
		self._client.interface = self

		self._canvas = tk.Canvas(self._root, width=width, height=height)
		self._canvas.pack(side=tk.BOTTOM)

		# Menus déroulants
		self._menu_frame = tk.Frame(self._root, bg='red')  # COULEUR À ENLEVER
		self._menu_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor="n")

		self._menu_file = EasyMenu(self._menu_frame, "File",
								   [("Save", self.fonction_bidon),
									("Load", self.fonction_bidon),
									None,
									("Disconnect", self.fonction_bidon)])

		self._menu_edit = EasyMenu(self._menu_frame, "Edit",
								   [("Reset yours", self.fonction_bidon),
									("Undo (Ctrl+Z)", self.undo)])

		# Barre de sélection de l'objet
		self._objects_frame = tk.Frame(self._root, bg='blue')  # COULEUR À ENLEVER
		self._objects_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor="n")

		self._objects_buttons = [
			EasyButton(self,
					   self._objects_frame, 50, 50,
					   object_type=Nest),

			EasyButton(self,
					   self._objects_frame, 50, 50,
					   object_type=Resource),

			EasyButton(self,
					   self._objects_frame, 50, 50,
					   object_type=Wall),

			EasyButton(self,
					   self._objects_frame, 70, 50, text='Ready',
					   side=tk.RIGHT,
					   command_select=self.send_ready,
					   command_deselect=self.send_notready)
		]

		# Évènements
		self._canvas.bind("<Button-1>", self.on_click)
		self._canvas.bind("<ButtonRelease-1>", self.on_release)
		self._canvas.bind("<B1-Motion>", self.on_motion)

		self._root.bind("<Control-z>", self.undo)
		self._root.bind("<Escape>", self.deselect_buttons)
		self._root.protocol("WM_DELETE_WINDOW", self.quit_app)

		self._local_color = '' # par défaut, mais sera changé

		self._current_object_type = None
		self._current_wall = None

		self._last_objects = [] # liste d'objets places : [id d'objet + str_type], pour pouvoir annuler les placements
		self._ants = [] # liste d'objets Ant
		self._resources = [] # liste d'objets Resource
		self._pheromones = {} # dictionnaire de coordonnees, associees a des objets Pheromone

		# Note : la mainloop est lancee dans un thread, par le main

	## Gestion d'évènements ##

	def on_click(self, event):
		# print("click ; current :", self._current_object_type)
		# Normalement c'est la bonne manière de tester, mais faut voir
		if self._current_object_type is Nest:
			self.ask_nest(event.x, event.y)

		elif self._current_object_type is Resource:
			self.ask_resource(event.x, event.y)

		# je crois pas qu'on veuille demander un wall maintenant
		elif self._current_object_type is Wall:
			# On le crée directement, pour avoir un visuel
			self._create_wall(event.x, event.y)

	def on_release(self, event):
		if self._current_wall is not None:
			wall_coords, wall_width = self._current_wall.coords, self._current_wall.width
			self.ask_wall(wall_coords, wall_width)
			self._delete_current_wall()

	def on_motion(self, event):
		if self._current_wall is not None:
			self._current_wall.expand(event.x, event.y)


	def deselect_buttons(self, event=None):
		"""Désélectionne tous les boutons des objets, pour libérer le clic"""
		for button in self._objects_buttons:
			button.deselect(exec_command=False)
		self._current_object_type = None

	def send_ready(self):
		for button in self._objects_buttons:
			if button.text != "Ready":
				button.hide()
			else:
				# On laisse le bouton Ready toujours actif
				button.text = "Not ready"
		self._client.set_ready()

	def send_notready(self):
		for button in self._objects_buttons:
			if button.text != "Not ready":
				button.show()
			else:
				# Le bouton Ready est toujours actif
				button.text = "Ready"
		self._client.set_notready()


	## Demandes de confirmation pour créer les objets ##

	def ask_nest(self, x, y, size=20):
		"""
		Demande au serveur s'il peut créer un nid à l'endroit donné.
		La couleur est obligatoirement la couleur locale
		"""
		self._client.ask_object(Nest, (x, y), size, color=self._local_color)

	def ask_resource(self, x, y, size=20):
		self._client.ask_object(Resource, (x, y), size)

	def ask_wall(self, coords_list, width=20):
		"""Demande un mur. Appelé seulement à la fin d'un clic long."""
		self._client.ask_object(Wall, coords_list, width=width)


	## Création d'objets ##

	def _create_object(self, str_type, coords, size=None, width=None, color=None):
		"""Instancie l'objet du type reçu par le Client"""
		str_type = str_type.lower()
		if str_type == "resource":
			# On affiche une ressource, et on l'ajoute dans la liste de
			# Ressources pour pouvoir y acceder par la suite
			obj = Resource(self._canvas, coords, size=size)
			self._resources.append(obj)
			self._last_objects.append([obj.id, "resource"])
		elif str_type == "nest":
			obj = Nest(self._canvas, coords, size=size, color=color)
			self._last_objects.append([obj.id, "nest"])
		elif str_type == "wall":
			obj = Wall(self._canvas, coords, width=width, size=0)
			self._last_objects.append([obj.id, "wall"])
		elif str_type == "ant":
			Ant(self._canvas, coords, size=size, color=color)
		elif str_type == "pheromone":
			Pheromone(self._canvas, coords)
		else:
			print("mauvais type :", str_type)
			return

	def _delete_current_wall(self):
		print("deleting current wall ;", self._current_wall, self._current_object_type)
		self._canvas.delete(self._current_wall.id)
		self._current_wall = None

	'''
	def _create_nest(self, x, y, size, color):
		#
		# À modifier avec l'interaction avec le serveur
		# (demande de validation de la position par ex)
		#
		Nest(self._canvas, (x, y), size, color)

	def _create_resource(self, x, y, size=20):
		#
		# À modifier avec l'interaction avec le serveur
		# (demande de validation de la position par ex)
		#
		Resource(self._canvas, (x, y), size)
	'''

	def _create_wall(self, x, y, width=10):
		"""On crée un objet Wall, qu'on étendra"""
		self._current_wall = Wall(self._canvas, (x, y), width=width, size=0)

	def create_pheromone(self, coords):
		""" On affiche une phéromone et on l'ajoute dans la liste de phéromones """
		if coords in self._pheromones:
			self._pheromones[coords].darken()
		else:
			self._pheromones[coords] = Pheromone(self._canvas, coords)

	def shrink_resource(self, index):
		self._resources[index].shrink()

	def create_ant(self, coords, color):
		""" On affiche une fourmi et on l'ajoute dans la liste de fourmis """
		self._ants.append(Ant(self._canvas, coords, color))

	def move_ant(self, index, delta_x, delta_y):
		""" Fonction pour déplacer une fourmi """
		self._ants[index].move(delta_x, delta_y)

	def color_ant(self, index, color):
		""" Fonction pour changer la couleur d'une fourmi """
		self._ants[index].color = color

	def undo(self, event=None):
		""" Fonction pour annuler un placement """
		# last_object est de la forme : [id, str_type]
		if len(self._last_objects) > 0:
			last_object = self._last_objects.pop()
			self._canvas.delete(last_object[0])
			self._client.undo_object(last_object[1])

	def fonction_bidon(self, event=None):
		# À ENLEVER
		print("fonction bidon au rapport")

	def countdown(self):
		h = int(self._canvas["height"]) // 2
		w = int(self._canvas["width"]) // 2
		text = self._canvas.create_text(w,h, font="Corbel 20 bold", text="Attention ça commence")
		time.sleep(1)
		for i in range(3, 0, -1):
			self._canvas.itemconfig(text, text=i)
			time.sleep(1)
		self._canvas.itemconfig(text, text="Let's go!")
		time.sleep(1)
		self._canvas.delete(self._root,text)

	def quit_app(self):
		if messagebox.askyesno('Quit', 'Are you sure to quit?'):
			self._root.quit()



if __name__ == '__main__':
	interface = Interface(1050, 750)
