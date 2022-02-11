import tkinter as tk
from tkinter import messagebox
import threading
from time import sleep

# import concurrent.futures as cf

from .EasyMenu import EasyMenu
from .EasyButton import EasyButton

from .Ant import Ant
from .Nest import Nest
from .Pheromone import Pheromone
from .Resource import Resource
from .Wall import Wall, WallInAButton

from networks.network_utils import (
    ColorInfo,
    FirstBloodSignal,

    SentObject
)


class Interface:
    """ Classe qui comportera tous les éléments graphiques """

    READY_TEXT = "Ready"
    NOT_READY_TEXT = "Not ready"

    @property
    def root(self):
        return self._root

    @property
    def canvas(self):
        return self._canvas

    @property
    def local_color(self):
        """Couleur locale de l'interface du client"""
        return self._local_color

    @local_color.setter
    def local_color(self, new_color):
        self._local_color = new_color
        self._objects_frame["bg"] = self._local_color


    def __init__(self, client, width, height):
        self._root = tk.Tk()
        self._root.title("Ant Simulator")

        self._client = client
        self._client.interface = self

        self._canvas = tk.Canvas(self._root, width=width, height=height)
        self._canvas.pack(side=tk.BOTTOM)

        # Menus deroulants
        self._menu_frame = tk.Frame(self._root)
        self._menu_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor="n")

        EasyMenu(self._menu_frame, "Network",
                 [("Disconnect", self._disconnect)], width=8)

        EasyMenu(self._menu_frame, "Edit",
                 [("Undo (Ctrl+Z)", self._undo)])

        # Barre de selection de l'objet
        self._objects_frame = tk.Frame(self._root)
        self._objects_frame.pack(
            side=tk.TOP, expand=True, fill=tk.X, anchor="n")

        self._buttons = [
            # Bouton Nid
            EasyButton(self,
                       self._objects_frame, 50, 50,
                       object_type=Nest),

            # Bouton Ressource
            EasyButton(self,
                       self._objects_frame, 50, 50,
                       object_type=Resource),

            # Bouton Mur
            EasyButton(self,
                       self._objects_frame, 50, 50,
                       object_type=WallInAButton),

            # Bouton Ready
            EasyButton(self,
                       self._objects_frame, 70, 50, text=type(self).READY_TEXT,
                       side=tk.RIGHT,
                       command_select=self.set_ready,
                       command_deselect=self.set_notready)
        ]

        # Evenements
        self._canvas.bind("<Button-1>", self.on_click)
        self._canvas.bind("<ButtonRelease-1>", self.on_release)
        self._canvas.bind("<B1-Motion>", self.on_motion)

        self._root.bind("<Control-z>", self._undo)
        self._root.bind("<Escape>", self.deselect_buttons)
        self._root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self._local_color = ""  # par defaut, mais sera change

        self.current_object_type = None
        self._current_wall = None

        # liste d'objets places : [id d'objet + str_type], pour pouvoir annuler les placements
        self._last_objects = []
        self.ants = []  # liste d'objets Ant
        self._resources = []  # liste d'objets Resource, pour pouvoir les rétrécir
        self.pheromones = {}  # dictionnaire de coordonnees, associees a des objets Pheromone

        # Note : la mainloop est lancee dans un thread, par le main


    ## Gestion d'evenements ##

    def on_click(self, event):
        """Callback de l'appui du clic de souris"""
        # print("click ; current :", self.current_object_type)
        if self.current_object_type is None:
            return

        if self.current_object_type is Nest:
            self.ask_nest(event.x, event.y)

        elif self.current_object_type is Resource:
            self.ask_resource(event.x, event.y)

        # La classe contenue dans le bouton n'est pas Wall
        elif self.current_object_type is WallInAButton:
            # On le cree directement, pour avoir un visuel
            self._init_wall(event.x, event.y)
        else:
            current_type = self.current_object_type.__name__
            raise TypeError(f"The current object type ({current_type}) is not configured.")

    def on_release(self, event):
        """Callback du relâchement du clic de souris"""
        if self._current_wall is None:
            return
        wall_coords = self._current_wall.drawn_coords
        wall_size = self._current_wall.size

        self.ask_wall(wall_coords, wall_size)
        self._delete_current_wall()

    def on_motion(self, event):
        """Callback du mouvement de souris"""
        if self._current_wall is not None:
            self._current_wall.expand(event.x, event.y)

    def deselect_buttons(self, event=None):
        """Désélectionne tous les boutons des objets, pour libérer le clic"""
        for button in self._buttons:
            button.deselect(exec_command=False)
        self.current_object_type = None

    def set_ready(self):
        """
        Cache les boutons et informe le Client que
        l'utilisateur a cliqué sur le bouton Ready
        """
        for button in self._buttons:
            if button.text != type(self).READY_TEXT:
                button.hide()
            else:
                # On laisse le bouton Ready toujours actif
                button.text = type(self).NOT_READY_TEXT
        self._client.ready_state = True

    def set_notready(self):
        """
        Montre les boutons et informe le Client que
        l'utilisateur a cliqué sur le bouton Not ready
        """
        for button in self._buttons:
            if button.text != type(self).NOT_READY_TEXT:
                button.show()
            else:
                # Le bouton Ready est toujours actif
                button.text = type(self).READY_TEXT
        self._client.ready_state = False

    def _undo(self, event=None):
        """ Fonction pour annuler un placement """
        # last_object est de la forme : [id, str_type]
        if self._last_objects:
            self._client.ask_undo()
            self._last_objects.pop()
            # La destruction graphique se fait avec la réponse du Serveur

    def _disconnect(self):
        self._client.disconnect()

    def quit_app(self, force=False):
        """Demande à l'utilisateur s'il veut vraiment quitter"""
        if force or messagebox.askyesno("Quit", "Are you sure to quit?"):
            self._root.quit()


    ## Demande de création d'objets côté serveur ##

    def ask_nest(self, x, y, size=20):
        """
        Demande au serveur s'il peut créer un nid à l'endroit donné.
        La couleur est obligatoirement la couleur locale
        """
        new_obj = SentObject("nest", (x, y), size, color=self._local_color)
        self._client.ask_object(new_obj)

    def ask_resource(self, x, y, size=20):
        """Demande une ressource au Server"""
        new_obj = SentObject("resource", (x, y), size, color=None)
        self._client.ask_object(new_obj)

    def ask_wall(self, coords_list, size=20):
        """Demande un mur. Appelé seulement à la fin d'un clic long."""
        new_obj = SentObject("wall", coords_list, size, color=None)
        self._client.ask_object(new_obj)


    ## Creation d'objets graphiques ##

    def create_object(self, str_type, coords, size=None, color=None):
        """Instancie l'objet du type reçu par le Client"""
        if str_type == "pheromone":
            Pheromone(self._canvas, coords)
            return None

        if str_type == "nest":
            obj = Nest(self._canvas, coords, size=size, color=color)
        elif str_type == "resource":
            # On affiche une ressource et on l'ajoute dans
            # la liste pour pouvoir y acceder par la suite
            obj = Resource(self._canvas, coords, size=size)
            self._resources.append(obj)
        elif str_type == "wall":
            obj = Wall(self._canvas, coords, size)
        else:
            raise TypeError(f"The type {str_type} does not exist")
        self._last_objects.append(obj.id)
        return obj.id # Pour l'ajouter au dictionnaire tenu dans le Client

    def _init_wall(self, x, y):
        """On crée un objet Wall, qu'on étendra"""
        self._current_wall = Wall(self._canvas, (x, y))

    def create_pheromone(self, coords):
        """Crée ou fonce une seule phéromone"""
        if coords in self.pheromones:
            self.pheromones[coords].darken()
        else:
            self.pheromones[coords] = Pheromone(self._canvas, coords)

    # def create_pheromones(self, coords_list):
    #     """Crée ou fonce plusieurs phéromones à la fois"""
    #     # peut-être que ça va casser vu qu'on modifie le dico alors qu'on le traverse dans d'autres
    #     step = 20  # on cree ou fonce tel nombre de fourmis dans chaque thread
    #     total_count = len(coords_list)

    #     def create_pheromones_in_thread(start, number):
    #         end = min(start + number, total_count)

    #         for i in range(start, end):
    #             coords = coords_list[i]
    #             if coords in self.pheromones:
    #                 self.pheromones[coords].darken()
    #             else:
    #                 self.pheromones[coords] = Pheromone(self._canvas, coords)

    #     for i in range(0, total_count, step):
    #         threading.Thread(target=create_pheromones_in_thread,
    #                          args=(i, step),
    #                          daemon=True).start()

    def create_ants(self, ants_list):
        """
        Crée toutes les fourmis en fonction
        des coordonnées et couleurs dans la liste
        """
        self.ants = [
            Ant(self._canvas,
                origin_coords=ant[0],
                color=ant[1]
            ) for ant in ants_list
        ]

        # for ant in ants_list:
        #   self.ants.append(Ant(self._canvas, ant[0], ant[1])) # coords, couleur


    ## Modification/suppression d'objets graphiques ##

    def destroy_object(self, object_id):
        """Supprime un objet graphique"""
        self._canvas.delete(object_id)

    def _delete_current_wall(self):
        # print("deleting current wall ;", self._current_wall, self.current_object_type)
        self._canvas.delete(self._current_wall.id)
        self._current_wall = None

    def shrink_resource(self, index):
        """Rétrécit la ressource graphiquement"""
        if self._resources[index].current_size:
            self._resources[index].shrink()
        else:
            self._resources[index].remove()

    def move_ant(self, ant, data):
        """
        Bouge une seule fourmi grâce aux données, qui sont
        un tuple de coordonnées relatives et optionnellement
        un int, un ColorInfo ou un FirstBloodSignal
        """
        ant.move(data[0], data[1])

        if len(data) == 2:
            return

        data = data[2] # On n'a plus besoin des coordonnées
        if isinstance(data, int):
            # Si c'est l'index de la ressource, on la rapetisse
            self.shrink_resource(data)
            ant.set_resource_color()
        # Si c'est une couleur
        elif isinstance(data, ColorInfo):
            ant.change_color(data)
        # Si on a un FirstBloodSignal, on affiche le texte et on rétrécit la ressource
        elif isinstance(data, FirstBloodSignal):
            self.set_first_blood(ant.base_color)
            self.shrink_resource(data.resource_index)
            ant.set_resource_color()

    # def _move_ants_in_thread(self, total_count, start, number, relative_coords_list):
    #     end = min(start + number, total_count)

    #     for i, ant in enumerate(self.ants[start:end], start=start):
    #         data = relative_coords_list[i]

    #         ant.move(data[0], data[1])

    #         if len(data) == 2:
    #             continue

    #         data = data[2] # On n'a plus besoin des coordonnées
    #         if isinstance(data, int):
    #             # Si c'est l'index de la ressource, on la rapetisse
    #             self.shrink_resource(data)
    #             ant.set_resource_color()
    #         # Si c'est une couleur
    #         elif isinstance(data, ColorInfo):
    #             ant.change_color(data)
    #         # Si on a un FirstBloodSignal, on affiche le texte et on rétrécit la ressource
    #         elif isinstance(data, FirstBloodSignal):
    #             self.set_first_blood(ant.base_color)
    #             self.shrink_resource(data.resource_index)
    #             ant.set_resource_color()

    # def move_ants(self, relative_coords_list):
    #     """
    #     Bouge les fourmis grâce à la liste des coordonnées relatives.
    #     Les coordonnées i sont pour la fourmi i.
    #     """

    #     with cf.ThreadPoolExecutor() as executor:
    #         executor.map(self.move_ant, self.ants, relative_coords_list)

    #     # step = 20  # on bouge tel nombre de fourmis dans chaque thread
    #     # total_count = len(relative_coords_list)

    #     # for i in range(0, total_count, step):
    #     #     thread_move = threading.Thread(target=self._move_ants_in_thread,
    #     #                                    args=(total_count, i, step, relative_coords_list),
    #     #                                    daemon=True)
    #     #     thread_move.start()
    #     # # thread_move.join(0.5) # TODO : tenter de commenter pour voir


    ## Modification de l'UI ##

    def set_first_blood(self, color):
        """Affiche la couleur de la première fourmi ayant touché une ressource"""
        w = int(self._canvas["width"])
        h = int(self._canvas["height"])
        self._canvas.create_text(
            w - 150, h - 20, font="Corbel 15 bold", text="First blood:")
        self._canvas.create_rectangle(
            w - 50, h - 30, w - 30, h - 10, fill=color)

    def countdown(self):
        """Affiche un compte a rebours au milieu de la fenetre"""
        # On cache tous les boutons ce coup-ci
        for button in self._buttons:
            # TODO : peut-être faire une classe différente pour les hideable
            if button.hideable:
                button.hide()
        # On affiche le compte a rebours
        height = int(self._canvas["height"]) // 2
        width = int(self._canvas["width"]) // 2
        text = self._canvas.create_text(
            width, height,
            font="Corbel 20 bold",
            text="Starting in…")
        sleep(1)
        for i in range(3, 0, -1):
            self._canvas.itemconfig(text, text=i)
            sleep(1)
        self._canvas.itemconfig(text, text="Let's go!")
        sleep(1)
        self._canvas.delete(self._root, text)

    def show_admin_buttons(self):
        """Affiche les boutons d'admin pour contrôler la simulation"""
        self._buttons.append(EasyButton(self,
                                        self._objects_frame, 50, 50, text="+",
                                        side=tk.RIGHT,
                                        command_select=self._client.ask_faster_sim,
                                        toggle=False, hideable=False))

        self._buttons.append(EasyButton(self,
                                        self._objects_frame, 50, 50, text="-",
                                        side=tk.RIGHT,
                                        command_select=self._client.ask_slower_sim,
                                        toggle=False, hideable=False))


# if __name__ == "__main__":
#     interface = Interface(1050, 750)
