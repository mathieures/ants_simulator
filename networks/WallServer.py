from ServerObject import SizedServerObject


class WallServer(SizedServerObject):

    # Tous les murs
    walls = set()

    @classmethod
    def get_wall(cls, x, y):
        for wall in cls.walls:
            if (x, y) in wall.zone:
                return wall
        return None

    def __init__(self, coords_centre, size, color):
        self.coords_centre = coords_centre
        self.size = size # la width
        self.color = color

        self._init_zone()

        self.walls.add(self)