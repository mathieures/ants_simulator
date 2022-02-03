from .ServerObject import SizedServerObject


class WallServer(SizedServerObject):
    """Mur côté serveur, dont la size correspond à la largeur (width)"""

    def __init__(self, coords_centre, size, color):
        super().__init__(coords_centre, size, color)

        self._init_zone()