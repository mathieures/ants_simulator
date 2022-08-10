from .InterfaceObject import InterfaceObject


class Wall(InterfaceObject):
    """Mur représenté graphiquement"""

    __slots__ = ["length"]


    def __init__(self, canvas, origin_coords, size=10, length=0):
        """
        Crée une ligne de taille size et de largeur length.
        (size est utile pour l'icône du bouton)
        """
        self.length = length

        super().__init__(canvas, origin_coords, size, color="black")

        self.draw()

    def _init_drawn_coords(self):
        """Les murs fonctionnent d'une manière différente des autres InterfaceObject"""

        # Si on n'a pas deux points, alors on ne crée qu'un rectangle
        if len(self.origin_coords) < 4:
            return [self.origin_coords[0],
                    self.origin_coords[1],
                    self.origin_coords[0] + self.length,
                    self.origin_coords[1]]
        return self.origin_coords


    def draw(self):
        """Crée le tout premier mur, pouvant être étendu."""
        self._id = self._canvas.create_line(self.drawn_coords,
                                            width=self.size, fill=self.color)

    def expand(self, to_x, to_y):
        """Étend le mur au point donné en paramètre"""
        self.drawn_coords.extend((to_x, to_y))
        self._canvas.coords(self._id, self.drawn_coords)


class WallInAButton(Wall):
    """Un Wall, mais dans un EasyButton."""
    def __init__(self, canvas, origin_coords, size, length):

        super().__init__(canvas, origin_coords, size, length)