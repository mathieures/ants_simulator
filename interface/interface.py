import tkinter as tk
from .easy_menu import EasyMenu
from .easy_button import EasyButton
from .nest import Nest
from .resource import Resource
from .wall import Wall

import threading

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

    def __init__(self, client, width, height):
        self._root = tk.Tk()
        self._client = client
        self._client._set_interface(self)

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
                                    ("Undo (Ctrl+Z)", self.fonction_bidon)])

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
                       self._objects_frame, 50, 50, text='Ready',
                       side=tk.RIGHT, command=self._client.set_ready)
        ]

        # Évènements

        self._canvas.bind("<Button-1>", self.on_click)
        self._canvas.bind("<ButtonRelease-1>", self.on_release)
        self._canvas.bind("<B1-Motion>", self.on_motion)

        self._canvas.bind("<Button-3>", self.on_right_click)

        self._root.bind("<Control-z>", self.fonction_bidon)
        self._root.bind("<Escape>", self.deselect_buttons)

        #
        # Demander au serveur la couleur
        #
        self._local_color = 'red'

        self._current_object_type = None
        self._current_wall = None

    ## Gestion d'évènements ##

    def on_click(self, event):
        print("click ; current :", self._current_object_type)
        # Normalement c'est la bonne manière de tester, mais faut voir
        if self._current_object_type is Nest:
            self.ask_nest(event.x, event.y)

        elif self._current_object_type is Resource:
            self.ask_resource(event.x, event.y)

        elif self._current_object_type is Wall:
            if self._current_wall is not None:
                print("problème")
            self.ask_wall(event.x, event.y)


    def on_release(self, event):
        if self._current_wall:
            self._current_wall = None
            self._client

    def on_right_click(self, event):
        self.create_nest(event.x, event.y, 25)

    def on_motion(self, event):
        if self._current_wall is not None:
            self._current_wall.expand(event.x, event.y)

    def deselect_buttons(self, event=None):
        """Désélectionne tous les boutons des objets, pour libérer le clic"""
        for button in self._objects_buttons:
            button.deselect()  # seulement visuel
        self._current_object_type = None
        print("deselected all")



    ## Demandes pour créer les objets ##
    def ask_nest(self, x, y, size=20):
        """
        Demande au serveur s'il peut créer un nid à l'endroit donné.
        La couleur est obligatoirement la couleur locale
        """
        self._client.ask_object(Nest, (x, y), size, color=self._local_color)

    def ask_resource(self, x, y, size=20):
        self._client.ask_object(Resource, (x, y), size)

    def ask_wall(self, x, y, size=20):
        self._client.ask_object(Wall, (x, y), size)

    ## Création d'objets ##
    def _create_object(self, str_type, position, size=None, width=None, color=None):
        """Instancie l'objet du type reçu par le Client"""
        str_type = str_type.lower()
        if str_type == "resource":
            object_type = Resource
        elif str_type == "nest":
            object_type = Nest
        elif str_type == "wall":
            object_type = Wall
        else:
            print("mauvais type :", str_type)
            return
        object_type(self._canvas, position, size=size, width=width, color=color)


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
        self._client.send("Resource", [x, y], size)
        if self._client.ressource_ok:
            Resource(self._canvas, (x, y), size)
        else:
            print("pas okay")

    def _create_wall(self, x, y, width=10):
        #
        # À modifier avec l'interaction avec le serveur
        # (demande de validation de la position par ex)
        #
        self._client.send("Wall", [x, y], width)
        if self._client.wall_ok:
            self._current_wall = Wall(self._canvas, (x, y), width=width)
        else:
            self._current_wall = None

    def fonction_bidon(self, event=None):
        print("fonction bidon au rapport")

    def start_game(self):
        print("C'est partis")
