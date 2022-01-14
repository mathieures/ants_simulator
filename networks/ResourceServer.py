from ServerObject import SizedServerObject


class ResourceServer(SizedServerObject):
    """Classe utilisée dans Simulation._objects["resource"]"""

    # forme de l'ancien dico d'objets :
    # self._objects[str_type].append((coords, size, width, color))

    __slots__ = ["index"]

    INDEX_GEN = SizedServerObject.get_new_id()

    def __init__(self, coords_centre, size, color):
        super().__init__(coords_centre, size, color)
        self.index = next(self.INDEX_GEN)

        self._init_zone()

    def shrink_resource(self):
        """
        Rétrécit la ressource et sa zone en enlevant les
        pixels étant hors du champ de la nouvelle taille
        """
        x, y = self.get_origin_coords()
        top = [(i, y) for i in range(x, x + self.size)]
        bottom = [(i, y + self.size - 1) for i in range(x + self.size)]
        left = [(x, j) for j in range(y + 1, y + self.size - 1)]
        right = [(x + self.size - 1, j) for j in range(y + 1, y + self.size - 1)]

        self.size -= 1

        self.zone.difference_update(top, bottom, left, right)