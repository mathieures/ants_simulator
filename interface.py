import tkinter as tk
import easy_menu as ezm
import easy_button as ezb
import custom_object
import nest
import resource
import wall

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
    

    def __init__(self, width, height):
        self._root = tk.Tk()

        self._canvas = tk.Canvas(self._root, width=width, height=height)
        self._canvas.pack(side=tk.BOTTOM)


        # Menus déroulants

        self._menu_frame = tk.Frame(self._root, bg='red') # COULEUR À ENLEVER
        self._menu_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor="n")
        
        self._menu_file = ezm.EasyMenu(self._menu_frame, "File",
                                      [("Save", self.fonction_bidon),
                                       ("Load", self.fonction_bidon),
                                       None,
                                       ("Disconnect", self.fonction_bidon)])

        self._menu_edit = ezm.EasyMenu(self._menu_frame, "Edit",
                                      [("Reset yours", self.fonction_bidon),
                                       ("Undo (Ctrl+Z)", self.fonction_bidon)])


        # Barre de sélection de l'objet
        
        self._objects_frame = tk.Frame(self._root, bg='blue') # COULEUR À ENLEVER
        self._objects_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor="n")

        self._objects_buttons = [
            ezb.EasyButton(self,
                self._objects_frame, 50, 50,
                object_type=nest.Nest),
            
            ezb.EasyButton(self,
                self._objects_frame, 50, 50,
                object_type=resource.Resource),
            
            ezb.EasyButton(self,
                self._objects_frame, 50, 50, text='',
                object_type=wall.Wall, no_icon=False)
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


        self._root.mainloop()


    ## Gestion d'évènements ##

    def on_click(self, event):
        print("click ; current :", self._current_object_type)
        # Normalement c'est la bonne manière de tester, mais faut voir
        if self._current_object_type is nest.Nest:
            self.create_nest(event.x, event.y)
        
        elif self._current_object_type is resource.Resource:
            self.create_resource(event.x, event.y)
        
        elif self._current_object_type is wall.Wall:
            if self._current_wall is not None:
                print("problème")
            self.create_wall(event.x, event.y)

    def on_release(self, event):
        if self._current_wall:
            self._current_wall = None


    def on_right_click(self, event):
        self.create_nest(event.x, event.y, 25)

    def on_motion(self, event):
        if self._current_wall is not None:
            self._current_wall.expand(event.x, event.y)


    def deselect_buttons(self, event=None):
        """Désélectionne tous les boutons des objets, pour libérer le clic"""
        for button in self._objects_buttons:
            button.deselect() # seulement visuel
        self._current_object_type = None
        print("deselected all")



    ## Création d'objets ##
    def create_nest(self, x, y, size=20):
        """La couleur est obligatoirement la couleur locale"""
        #
        # À modifier avec l'interaction avec le serveur
        # (demande de validation de la position par ex)
        #
        nest.Nest(self._canvas, (x, y), size, color=self._local_color)

    def create_resource(self, x, y, size=20):
        #
        # À modifier avec l'interaction avec le serveur
        # (demande de validation de la position par ex)
        #
        resource.Resource(self._canvas, (x, y), size)

    def create_wall(self, x, y, width=10):
        #
        # À modifier avec l'interaction avec le serveur
        # (demande de validation de la position par ex)
        #
        self._current_wall = wall.Wall(self._canvas, (x, y), width=width)



    def fonction_bidon(self, event=None):
        print("fonction bidon au rapport")


if __name__ == '__main__':
    interface = Interface(1050, 750)
