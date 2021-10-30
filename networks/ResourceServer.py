from ServerObject import SizedServerObject, get_new_id as get_new_index


class ResourceServer(SizedServerObject):
    """Classe utilisée dans Simulation._objects["resource"]"""

    # forme de l'ancien dico d'objets :
    # self._objects[str_type].append((coords, size, width, color))

    __slots__ = ["index"]
    # __slots__ = ["coords_centre", "size", "width", "color", "index"]

    resources = set()
    INDEX_GEN = get_new_index()
    # Moche de le repeter dans 2 classes differentes, mais a voir

    @classmethod
    def get_resource(cls, x, y):
        """Retourne l'objet ResourceServer à cette position ou None s'il n'y en a pas"""
        for resource in cls.resources:
            if (x, y) in resource.zone:
                return resource
        return None
        # if "resource" in self._objects:
        #     for i, resource in enumerate(self._objects["resource"]):
        #         coords_resource, size = resource[0], resource[1]
        #         offset = size // 2 + 1  # +1 pour l'outline
        #         if (coords_resource[0] - offset <= x <= coords_resource[0] + offset) and (
        #             coords_resource[1] - offset <= y <= coords_resource[1] + offset) and (
        #             resource[1] != 0):
        #                 return i  # On retourne l'index de la ressource
        # return None

    @classmethod
    def get_all_resources(cls):
        return {r._to_tuple() for r in cls.resources}

    def __init__(self, coords_centre, size, width, color):
        self.index = next(self.INDEX_GEN)

        self.coords_centre = coords_centre
        self.size = size
        self.width = width
        self.color = color

        self.zone = self._init_zone()

        self.resources.add(self)

    def _to_tuple(self):
        """Retourne une forme de la resource exploitable par server.py"""
        # forme de l'ancien dico d'objets :
        # self._objects[str_type].append((coords, size, width, color))
        return (self.coords_centre, self.size, self.width, self.color)

    def shrink_resource(self):
        self.size -= 1
        # On supprime les pixels de la zone 
        x, y = self.coords_centre
        # test pour voir si la zone diminue en mettant size (ou est-ce qu'il faut mettre size-1)
        # print(f"AVANT : taille de la zone de la ressource : {len(self.zone)}")
        self.zone -= set(
            (x + self.size * off[0], y + self.size * off[1])
            for off in self.OFFSETS)
        # Ne supprime rien la 1ere fois, je crois, mais pas sur d'ou cela vient
        # print(f"APRÈS : taille de la zone de la ressource : {len(self.zone)}")
