from ServerObject import SizedServerObject
from AntServer import AntServer


class NestServer(SizedServerObject):

    __slots__ = ["ants"]

    # Tous les nids
    nests = set()

    @classmethod
    def get_all_ants_as_list(cls):
        # On ne peut pas unpack dans une comprehension
        all_ants = []
        for nest in cls.nests:
            all_ants.extend(nest.ants)
        # print("all ants :", all_ants)
        return all_ants
        # return [*nest.ants for nest in cls.nests]

    def __init__(self, coords_centre, size, color, ants_per_nest=20):
        self.coords_centre = coords_centre
        self.size = size
        self.color = color

        # Cree et stocke toutes les fourmis du nid
        self.ants = [AntServer(*self.coords_centre, self.color)
                     for _ in range(ants_per_nest)]

        self._init_zone()

        self.nests.add(self)