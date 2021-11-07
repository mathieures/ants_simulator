from ServerObject import SizedServerObject, get_new_id as get_new_index


class ResourceServer(SizedServerObject):
    """Classe utilisée dans Simulation._objects["resource"]"""

    # forme de l'ancien dico d'objets :
    # self._objects[str_type].append((coords, size, width, color))

    __slots__ = ["index"]

    INDEX_GEN = get_new_index()

    def __init__(self, coords_centre, size, color):
        self.index = next(self.INDEX_GEN)

        self.coords_centre = coords_centre
        self.size = size
        self.color = color

        self._init_zone()

    def shrink_resource(self):
        self.size -= 1
        # On supprime les pixels de la zone qui sont en dehors de la nouvelle size
        x, y = self.coords_centre
        self.zone.difference_update(
            (x + self.size * off[0], y + self.size * off[1])
            for off in self.OFFSETS)
        # Je crois que ca ne supprime rien au 1er tour, mais pas sur d'ou cela vient