class ServerObject:
    """Classe mère des objets côté serveur"""
    __slots__ = ["coords_centre", "color"]

    @staticmethod
    def get_new_id():
        """
        Generator d'id, utile pour donner un identifiant unique à
        un objet d'une classe. N'est pas partagé entre deux classes.
        """
        current_id = 0
        while True:
            yield current_id
            current_id += 1

    def __init__(self, coords_centre, color):
        self.coords_centre = coords_centre
        self.color = color

    def to_tuple(self):
        """
        Retourne un tuple de certains attributs,
        utiles pour le serveur et la simulation
        """
        return (self.coords_centre, self.color)

class SizedServerObject(ServerObject):
    """
    Un objet côté serveur, mais avec une taille
    définie, qui résulte en une zone de pixels occupés.
    """
    __slots__ = ["size", "zone"]

    OFFSETS = {(-1, -1), (-1, 0), (-1, 1), (0, -1),
               (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)}

    def __init__(self, coords_centre, size, color):
        super().__init__(coords_centre, color)
        self.size = size
        self.zone = set()

    def get_origin_coords(self):
        """
        Retourne les coordonnées d'origine de
        l'objet, similaire à ce que fait tkinter
        """
        return [int(coord - self.size // 2) for coord in self.coords_centre]

    def to_tuple(self):
        """Retourne une forme de l'objet exploitable par server.py"""
        # forme de l'ancien dico d'objets :
        # self._objects[str_type].append((coords, size, width, color))
        return (self.coords_centre, self.size, self.color)

    def _init_zone(self):
        """
        Initialise la zone de l'objet grâce
        aux coordonnées et à la taille
        Note : les hitboxes sont seulement des carrés
        """
        # On remplit un carre de pixels en partant de l'origine
        x, y = self.get_origin_coords()
        self.zone.update((i, j) for j in range(y, y + self.size) for i in range(x, x + self.size))

        # x, y = self.coords_centre
        # # Pour chaque size et chaque offset, on ajoute a la zone le pixel decale
        # self.zone.update(
        #     (x + i * off[0], y + i * off[1])
        #     for off in self.OFFSETS
        #     for i in range(self.size // 2 + 1))
