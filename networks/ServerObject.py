def get_new_id():
    """
    Generatior d'id, utile pour donner un identifiant unique à
    un objet d'une classe. N'est pas partagé entre deux classes.
    """
    current_id = 0
    while True:
        yield current_id
        current_id += 1


class ServerObject:
    __slots__ = ["coords_centre", "color"]

    def to_tuple(self):
        return (self.coords_centre, self.color)

class SizedServerObject(ServerObject):
    """
    Un objet côté serveur, mais avec une taille
    définie, qui résulte en une zone de pixels occupés.
    """
    __slots__ = ["size", "zone"]

    OFFSETS = {(-1, -1), (-1, 0), (-1, 1), (0, -1),
               (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)}

    def to_tuple(self):
        """Retourne une forme de l'objet exploitable par server.py"""
        # forme de l'ancien dico d'objets :
        # self._objects[str_type].append((coords, size, width, color))
        return (self.coords_centre, self.size, self.color)

    def _init_zone(self):
        """
        Initialise la zone de l'objet grâce
        aux coordonnées et à la taille
        """
        self.zone = set()
        x, y = self.coords_centre
        # Pour chaque size et chaque offset, on ajoute a la zone le pixel decale
        self.zone.update(
            (x + i * off[0], y + i * off[1])
            for off in self.OFFSETS
            for i in range(self.size // 2 + 1))
