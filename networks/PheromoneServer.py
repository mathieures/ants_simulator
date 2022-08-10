from .ServerObject import SizedServerObject


class PheromoneServer(SizedServerObject):
    """Phéromone côté serveur"""
    __slots__ = ["direction"]

    pheromones = set() # Ensemble contenant toutes les PheromoneServer de la map

    @classmethod
    def get_pheromone(cls, x, y):
        """Renvoie l'objet qui contient les coordonnées (x, y), ou None"""
        # On itere sur une copie de l'ensemble
        for phero in cls.pheromones.copy():
            if (x, y) in phero.zone:
                return phero
        return None

    @classmethod
    def remove_pheromone(cls, pheromone):
        """Supprime une phéromone de l'ensemble"""
        cls.pheromones.discard(pheromone)

    def __init__(self, coords_centre: tuple, direction: int):
        super().__init__(coords_centre, size=1, color="")
        self.direction = direction

        # self._init_zone()

        type(self).pheromones.add(self)