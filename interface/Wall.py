from .InterfaceObject import InterfaceObject


class Wall(InterfaceObject):
    """Mur représenté graphiquement"""

    __slots__ = ["width"]


    def __init__(self, canvas, origin_coords, size=37.5, width=15):
        """
        Crée une ligne de taille size et de largeur width.
        (size est utile pour l'icône du bouton)
        """
        if size is None:
            # size = width
            raise ValueError("Size of Wall is None, I don't think that's normal")
        super().__init__(canvas, origin_coords, size, color="black")

        self.width = width

        # On ecrase les coordonnees de dessin, car
        # les murs fonctionnent d'une autre maniere
        # Si on a plus de deux points, alors il faut creer une ligne complexe
        if len(origin_coords) > 4:
            self.drawn_coords = self.origin_coords
        else:
            self.drawn_coords = [self.origin_coords[0],
                                 self.origin_coords[1],
                                 self.origin_coords[0] + self.size,
                                 self.origin_coords[1]]
        self.draw()


    def draw(self):
        """Crée le tout premier mur, pouvant être étendu."""
        self._id = self._canvas.create_line(self.drawn_coords,
                                            width=self.width, fill=self.color)

    def expand(self, to_x, to_y):
        """Étend le mur au point donné en paramètre"""
        self.drawn_coords.extend((to_x, to_y))
        self._canvas.coords(self._id, self.drawn_coords)