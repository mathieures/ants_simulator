from ServerObject import SizedServerObject
from AntServer import AntServer


class NestServer(SizedServerObject):

    __slots__ = ["ants"]

    def __init__(self, coords_centre, size, color, ants_per_nest=20):
        self.coords_centre = coords_centre
        self.size = size
        self.color = color

        # Cree et stocke toutes les fourmis du nid
        self.ants = [AntServer(*self.coords_centre, self.color)
                     for _ in range(ants_per_nest)]

        self._init_zone()