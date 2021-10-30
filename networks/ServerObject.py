from collections import namedtuple


def get_new_id():
    current_id = 0
    while True:
        yield current_id
        current_id += 1


class ServerObject:
    __slots__ = ["coords_centre", "color"]


class SizedServerObject(ServerObject):
    __slots__ = ["size", "zone", "width"]

    OFFSETS = {(-1, -1), (-1, 0), (-1, 1), (0, -1),
               (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)}

    def _init_zone(self):
        """
        Initialise la zone de l'objet grâce
        aux coordonnées et à la taille
        """
        zone = set()
        x, y = self.coords_centre
        # Pour chaque size et chaque offset, on ajoute a la zone le pixel decale
        zone.update(
            (x + i * off[0], y + i * off[1])
            for off in self.OFFSETS
            for i in range(self.size // 2 + 1))
        return zone
