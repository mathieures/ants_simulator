class InterfaceObject:
    """Classe mère des objets, illustre la pose d'objets (à ne pas utiliser seule)"""

    __slots__ = ["_canvas", "_id", "color", "size",
                 "origin_coords", "drawn_coords",
                 "coords_centre", "_prev_coords"]

    # read-only
    @property
    def id(self):
        return self._id    

    def __init__(self, canvas, origin_coords, size=10, color=""):
        """L'objet calcule son centre et se place au bon endroit tout seul"""
        self._canvas = canvas
        self.origin_coords = origin_coords
        self.size = size
        self.color = color

        self.drawn_coords = (self.origin_coords[0] - self.size / 2,
                             self.origin_coords[1] - self.size / 2,
                             self.origin_coords[0] + self.size / 2,
                             self.origin_coords[1] + self.size / 2)

        self.coords_centre = self._get_centre_coords()

        self._id = None # Doit etre ecrase par les classes filles

    def draw(self):
        """
        Doit être réécrite dans les classes filles et
        mettre à jour l'id (objet de canvas tkinter)
        """
        raise NotImplementedError

    def _get_drawn_coords(self):
        return self._canvas.coords(self._id)

    def _get_centre_coords(self):
        return (self.drawn_coords[2] - self.drawn_coords[0], self.drawn_coords[3] - self.drawn_coords[1])

    def _update_coords(self):
        """
        Utilisé pour mettre à jour les attributs
        des objets, après un déplacement par exemple
        """
        self.coords_centre = self._get_centre_coords()
        self.drawn_coords = self._get_drawn_coords()