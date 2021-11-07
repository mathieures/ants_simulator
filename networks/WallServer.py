from ServerObject import SizedServerObject


class WallServer(SizedServerObject):

    def __init__(self, coords_centre, size, color):
        self.coords_centre = coords_centre
        self.size = size # la width
        self.color = color

        self._init_zone()