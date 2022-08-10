from .ServerObject import SizedServerObject


class WallServer(SizedServerObject):
    """Mur côté serveur, dont la size correspond à la largeur (width)"""

    str_type = "wall"

    # def __init__(self, coords_centre, size, color):
    #     super().__init__(coords_centre, size, color)

    #     # self._init_zone()

    def _init_zone(self):
        """Surcharge la méthode de base"""
        origin_coords = self.get_origin_coords()
        # Pour chaque couple de coordonnées de la liste
        for index in range(0, len(origin_coords), 2):
            x, y = origin_coords[index], origin_coords[index + 1]
            # On ajoute à la zone un carré autour de ce point
            self.zone.update((i, j) for j in range(y, y + self.size)
                                    for i in range(x, x + self.size))