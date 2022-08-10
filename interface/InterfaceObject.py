class InterfaceObject:
    """Classe mère des objets, illustre la pose d'objets (à ne pas utiliser seule)"""

    __slots__ = ["_window", "_id", "color", "size",
                 "origin_coords", "drawn_coords"]

    # read-only
    @property
    def id(self):
        """Identifiant donné par dearpygui"""
        return self._id


    def __init__(self, window, origin_coords, size=10, color=""):
        """L'objet calcule son centre et se place au bon endroit tout seul"""
        # La zone de dessin
        self._window = window

        self.origin_coords = origin_coords
        self.size = size
        self.color = color

        # TODO : voir si avec dearpygui on a encore besoin des drawn_coords
        self.drawn_coords = self._init_drawn_coords()

        self._id = None # Doit etre ecrase par les classes filles

    def __repr__(self):
        return f"{type(self).__name__}: {self.origin_coords}, {self.size}, {self.color}"

    def _init_drawn_coords(self):
        """Par défaut, les drawn_coords sont calculées comme ceci"""
        return (self.origin_coords[0] - self.size / 2,
                self.origin_coords[1] - self.size / 2,
                self.origin_coords[0] + self.size / 2,
                self.origin_coords[1] + self.size / 2)

    def draw(self):
        """
        Doit être réécrite dans les classes filles
        et mettre à jour l'id (tag/id dearpygui)
        """
        raise NotImplementedError