from .network_utils import id_generator as id_generator


class ServerObject:
    """Classe mère des objets côté serveur"""
    __slots__ = ["coords_centre", "color"]

    @classmethod
    def new_id_generator(cls):
        """Renvoie un générateur d'identifiants"""
        return id_generator()

    @property
    def str_type(self):
        """À implémenter dans les classes filles"""
        raise NotImplementedError


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


    def __init__(self, coords_centre, size, color):
        super().__init__(coords_centre, color)
        self.size = size
        self.zone = set()

        self._init_zone()


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