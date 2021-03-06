import tkinter as tk
from tkinter import messagebox
import threading
from time import sleep

from .easy_menu import EasyMenu
from .easy_button import EasyButton

from .Ant import Ant
from .Nest import Nest
from .Pheromone import Pheromone
from .Resource import Resource
from .Wall import Wall


from networks import client


class Interface:
    """ Classe qui comportera tous les éléments graphiques """

    @staticmethod
    def get_centre(p1, p2):
        """Retourne un point au milieu des deux passés en paramètres"""
        return ()

    @property
    def root(self):
        return self._root

    @property
    def canvas(self):
        return self._canvas

    # @property
    # def current_object_type(self):
    #     return self._current_object_type

    # @current_object_type.setter
    # def current_object_type(self, new_object_type):
    #     self._current_object_type = new_object_type

    @property
    def local_color(self):
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

        self._menu_file = EasyMenu(self._menu_frame, "Network",
                                   [("Disconnect", self._disconnect_client)], width=8)

        self._menu_edit = EasyMenu(self._menu_frame, "Edit",
                                   [("Undo (Ctrl+Z)", self._undo)])

        # Barre de selection de l'objet
        self._objects_frame = tk.Frame(self._root)
        self._objects_frame.pack(
            side=tk.TOP, expand=True, fill=tk.X, anchor="n")

        self._buttons = [
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
                       self._objects_frame, 70, 50, text="Ready",
                       side=tk.RIGHT,
                       command_select=self.send_ready,
                       command_deselect=self.send_notready)
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
        self._ants = []  # liste d'objets Ant
        self._resources = []  # liste d'objets Resource
        self._pheromones = {}  # dictionnaire de coordonnees, associees a des objets Pheromone

        # Note : la mainloop est lancee dans un thread, par le main

    ## Gestion d'evenements ##

    def on_click(self, event):
        # print("click ; current :", self.current_object_type)
        # Normalement c'est la bonne manière de tester, mais faut voir
        if self.current_object_type is Nest:
            self.ask_nest(event.x, event.y)

        elif self.current_object_type is Resource:
            self.ask_resource(event.x, event.y)

        # je crois pas qu'on veuille demander un wall maintenant
        elif self.current_object_type is Wall:
            # On le cree directement, pour avoir un visuel
            self._create_wall(event.x, event.y)

    def on_release(self, event):
        if self._current_wall is not None:
            wall_coords, wall_width = self._current_wall.drawn_coords, self._current_wall.width
            self.ask_wall(wall_coords, wall_width)
            self._delete_current_wall()

    def on_motion(self, event):
        if self._current_wall is not None:
            self._current_wall.expand(event.x, event.y)

    def deselect_buttons(self, event=None):
        """Désélectionne tous les boutons des objets, pour libérer le clic"""
        for button in self._buttons:
            button.deselect(exec_command=False)
        self.current_object_type = None

    def send_ready(self):
        for button in self._buttons:
            if button.text != "Ready":
                button.hide()
            else:
                # On laisse le bouton Ready toujours actif
                button.text = "Not ready"
        self._client.set_ready()

    def send_notready(self):
        for button in self._buttons:
            if button.text != "Not ready":
                button.show()
            else:
                # Le bouton Ready est toujours actif
                button.text = "Ready"
        self._client.set_notready()

    ## Demandes de confirmation pour creer les objets ##

    def ask_nest(self, x, y, size=20):
        """
        Demande au serveur s'il peut créer un nid à l'endroit donné.
        La couleur est obligatoirement la couleur locale
        """
        self._client.ask_object(Nest, (x, y), size, color=self._local_color)

    def ask_resource(self, x, y, size=20):
        self._client.ask_object(Resource, (x, y), size)

    def ask_wall(self, coords_list, size=20):
        """Demande un mur. Appelé seulement à la fin d'un clic long."""
        self._client.ask_object(Wall, coords_list, size)

    ## Creation d'objets ##

    def create_object(self, str_type, coords, size=None, width=None, color=None):
        """Instancie l'objet du type reçu par le Client"""
        str_type = str_type.lower()
        if str_type == "resource":
            # On affiche une ressource, et on l'ajoute dans la liste de
            # ressources pour pouvoir y acceder par la suite
            obj = Resource(self._canvas, coords, size=size)
            self._resources.append(obj)
            self._last_objects.append([obj.id, "resource"])
        elif str_type == "nest":
            obj = Nest(self._canvas, coords, size=size, color=color)
            self._last_objects.append([obj.id, "nest"])
        elif str_type == "wall":
            obj = Wall(self._canvas, coords, size=0, width=size) # bizarrerie ; à revoir
            self._last_objects.append([obj.id, "wall"])
        elif str_type == "ant":
            Ant(self._canvas, coords, size, color)
        elif str_type == "pheromone":
            Pheromone(self._canvas, coords)
        else:
            print("mauvais type :", str_type)

    def _delete_current_wall(self):
        # print("deleting current wall ;", self._current_wall, self.current_object_type)
        self._canvas.delete(self._current_wall.id)
        self._current_wall = None

    def _create_wall(self, x, y, width=10):
        """On crée un objet Wall, qu'on étendra"""
        self._current_wall = Wall(self._canvas, (x, y), size=0, width=width)

    def create_pheromones(self, coords_list):
        """Crée ou fonce plusieurs phéromones à la fois"""
        # peut-être que ça va casser vu qu'on modifie le dico alors qu'on le traverse dans d'autres
        step = 20  # on cree ou fonce tel nombre de fourmis dans chaque thread
        length = len(coords_list)

        def create_pheromones_in_thread(start, number):
            end = start + number
            if end > len(coords_list):
                end = len(coords_list)

            for i in range(start, end):
                coords = coords_list[i]
                if coords in self._pheromones:
                    self._pheromones[coords].darken()
                else:
                    self._pheromones[coords] = Pheromone(self._canvas, coords)

        for i in range(0, length, step):
            threading.Thread(target=create_pheromones_in_thread,
                             args=(i, step)).start()

    def shrink_resource(self, index):
        if self._resources[index].current_size:
            self._resources[index].shrink()
        else:
            self._resources[index].remove()

    def create_ants(self, ants_list):
        """
        Crée toutes les fourmis en fonction
        des coordonnées et couleurs dans la liste
        """
        self._ants.extend(
            Ant(self._canvas,
                origin_coords=ant[0],
                color=ant[1]
                ) for ant in ants_list)
        # for ant in ants_list:
        # 	self._ants.append(Ant(self._canvas, ant[0], ant[1])) # coords, couleur

    # def move_ant(self, index, delta_x, delta_y):
    #     """ Fonction pour déplacer une fourmi """
    #     self._ants[index].move(delta_x, delta_y)

    def move_ants(self, relative_coords):
        """
        Bouge les fourmis grâce à la liste des coordonnées relatives.
        Les coordonnées i sont pour la fourmi i.
        """
        step = 20  # on bouge tel nombre de fourmis dans chaque thread
        length = len(relative_coords)

        def move_ants_in_thread(start, number):
            end = start + number
            if end > length:
                end = length

            for i in range(start, end):
                ant = self._ants[i]
                ant.move(relative_coords[i][0], relative_coords[i][1])
                if len(relative_coords[i]) > 2:
                    resource_index = relative_coords[i][2]
                    # Nous devons rapetisser la ressource
                    if isinstance(resource_index, int):
                        self.shrink_resource(resource_index)
                        ant.change_color("grey")
                    elif resource_index == "base":
                        ant.change_color(ant.base_color)
                    # Si on a une liste, c'est la premiere fourmi
                    elif isinstance(resource_index, list):
                        self.set_first_ant(ant.base_color)
                        self.shrink_resource(resource_index[0])
                        ant.change_color("grey")
                    else:
                        ant.change_color(resource_index)

        for i in range(0, length, step):
            threading.Thread(target=move_ants_in_thread,
                             args=(i, step), daemon=True).start()

    def set_first_ant(self, color):
        w = int(self._canvas["width"])
        h = int(self._canvas["height"])
        self._canvas.create_text(
            w - 200, h - 20, font="Corbel 15 bold", text="First blood:")
        self._canvas.create_rectangle(
            w - 50, h - 30, w - 30, h - 10, fill=color)

    def _undo(self, event=None):
        """ Fonction pour annuler un placement """
        # last_object est de la forme : [id, str_type]
        if len(self._last_objects) > 0:
            last_object = self._last_objects.pop()
            self._canvas.delete(last_object[0])
            self._client.undo_object(last_object[1])

    def _disconnect_client(self):
        self._client.disconnect()

    def show_admin_buttons(self):
        self._buttons.append(EasyButton(self,
                                        self._objects_frame, 50, 50, text="+",
                                        side=tk.RIGHT,
                                        command_select=self.faster_sim,
                                        toggle=False, hideable=False))

        self._buttons.append(EasyButton(self,
                                        self._objects_frame, 50, 50, text="-",
                                        side=tk.RIGHT,
                                        command_select=self.slower_sim,
                                        toggle=False, hideable=False))

    def faster_sim(self):
        self._client.ask_faster_sim()

    def slower_sim(self):
        self._client.ask_slower_sim()

    def countdown(self):
        """Affiche un compte a rebours au milieu de la fenetre"""
        # On cache tous les boutons ce coup-ci
        for button in self._buttons:
            if button.hideable:
                button.hide()
        # On affiche le compte a rebours
        h = int(self._canvas["height"]) // 2
        w = int(self._canvas["width"]) // 2
        text = self._canvas.create_text(
            w, h, font="Corbel 20 bold", text="Starting in…")
        sleep(1)
        for i in range(3, 0, -1):
            self._canvas.itemconfig(text, text=i)
            sleep(1)
        self._canvas.itemconfig(text, text="Let's go!")
        sleep(1)
        self._canvas.delete(self._root, text)

    def quit_app(self, force=False):
        if force or messagebox.askyesno("Quit", "Are you sure to quit?"):
            self._root.quit()


if __name__ == "__main__":
    interface = Interface(1050, 750)
