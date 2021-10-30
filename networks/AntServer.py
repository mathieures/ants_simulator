from random import randint
from math import degrees, radians, cos, sin, atan2
# atan2 tient compte des signes

from ServerObject import ServerObject, get_new_id
from PheromoneServer import PheromoneServer


class AntServer(ServerObject):

    __slots__ = ["_direction",
                 "endurance",
                 "_id",
                 "has_resource",
                 "_nest",
                 "tries",
                 "_x",
                 "_y"]

    # Accesseurs et mutateurs
    #########################

    # property pour ne pas qu'elle puisse etre modifiee (read only)
    @property
    def coords_centre(self):
        return (self._x, self._y)

    # property car on veut pouvoir appliquer le modulo a l'affectation
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, pdirection):
        self._direction = pdirection % 360

    # read only
    @property
    def nest(self):
        """Position du nid en un couple (x, y)"""
        return self._nest

    # # read only
    # @property
    # def color(self):
    #     """
    #     Retourne la couleur de base de la fourmi, même
    #     quand elle est grisée à cause d'une ressource
    #     """
    #     return self._color
    #     # TODO: trouver quoi faire avec color, pour qu'il reste
    #     # read-only, et en même temps qu'on puisse le lire avec ant.color
    #     # ou trouver un autre moyen sans altérer la classe de base

    ###############################

    # Attributs de classe (read-only a cause des slots, sauf le dictionnaire)
    # CURRENT_ID = 0
    PHEROMONES = {}  # dictionnaire d'objets PheromoneServer, associes a une direction
    MAX_ENDURANCE = 512
    MAX_TRIES = 256  # nombre d'essais max pour contourner un mur par la gauche
    ID_GEN = get_new_id()

    def __init__(self, pos_x, pos_y, color):
        self._id = next(self.ID_GEN)

        self._x = pos_x
        self._y = pos_y
        self.color = color
        self._direction = randint(0, 360)
        self._nest = (pos_x, pos_y)  # Le nid est la position de depart

        self.has_resource = False  # Booleen pour indiquer si une fourmi possede une ressource
        self.endurance = AntServer.MAX_ENDURANCE
        self.tries = 0  # Nombre d'essais pour le contournement d'un mur

    def to_tuple(self):
        return (self.coords_centre, self.color)

    def move(self):
        """ Méthode qui change la position de la fourmi en fonction de sa direction """
        self._x += round(cos(radians(self._direction)), ndigits=0)
        # -= car c'est un repere orthonorme indirect
        self._y -= round(sin(radians(self._direction)), ndigits=0)
        # intervals = {(0., 22.5): (1, 0),
        #              (22.5, 67.5): (1, -1),
        #              (67.5, 112.5): (0, -1),
        #              (112.5, 157.5): (-1, -1),
        #              (157.5, 202.5): (-1, 0),
        #              (202.5, 247.5): (-1, 1),
        #              (247.5, 292.5): (0, 1),
        #              (292.5, 337.5): (1, 1),
        #              (337.5, 360): (1, 0)}

        # for inter in intervals:
        #     if inter[0] <= self._direction < inter[1]:
        #         self._x += intervals[inter][0]
        #         self._y += intervals[inter][1]
        #         break

        # if 22.5 <= self._direction < 67.5:
        #     self._x += 1
        #     self._y -= 1
        # elif 67.5 <= self._direction < 112.5:
        #     self._y -= 1
        # elif 112.5 <= self._direction < 157.5:
        #     self._x -= 1
        #     self._y -= 1
        # elif 157.5 <= self._direction < 202.5:
        #     self._x -= 1
        # elif 202.5 <= self._direction < 247.5:
        #     self._x -= 1
        #     self._y += 1
        # elif 247.5 <= self._direction < 292.5:
        #     self._y += 1
        # elif 292.5 <= self._direction < 337.5:
        #     self._x += 1
        #     self._y += 1
        # else:
        #     # Entre 337.5 et 22.5
        #     self._x += 1

    def seek_resource(self):
        """
        Fonction qui donne une direction aleatoire pour
        chercher une ressource ou fait suivre une phéromone
        """
        # Si la fourmi atteint le bord de gauche ou le bord du haut, elle change de direction
        x, y = self.coords_centre
        if self._x <= 0 or self._y <= 0:
            self._direction += 180
        else:
            current_phero = PheromoneServer.get_pheromone(self._x, self._y)
            # S'il y a une pheromone
            if current_phero is not None:
                direction = current_phero.direction
                self.follow_direction_biaised(direction)
            # Sinon on prend une direction aleatoire
            else:
                rand_dir = randint(self._direction - 30, self._direction + 30)
                self._direction = rand_dir % 360

    def go_to_nest(self):
        """ La fourmi pointe vers le nid """
        delta_x = self.nest[0] - self._x
        # delta_y = self.nest[1] - self._y
        # on inverse : repere orthonorme indirect
        delta_y = self._y - self.nest[1]

        self._direction = round(degrees(atan2(delta_y, delta_x)), ndigits=0)

    def lay_pheromone(self):
        """
        Pose une phéromone autour de la position de la
        fourmi dans la direction dans laquelle elle va
        Note : écrase la potentielle phéromone déjà présente
        """
        dir_to_resource = (self._direction - 180) % 360  # vers la ressource

        new_phero = PheromoneServer(coords_centre=(self._x, self._y),
                                    direction=dir_to_resource)

        old_phero = PheromoneServer.get_pheromone(self._x, self._y)
        # S'il y a deja au moins un pixel de pheromone a cet endroit
        if old_phero is not None:
            # On supprime de l'ancien les coordonnees qui changent
            # de direction (celles qui sont dans les deux)
            old_phero.zone -= new_phero.zone # old_phero.zone \ new_phero.zone
            # Si l'ancienne a ete completement repassee
            if not len(old_phero.zone):
                PheromoneServer.remove_pheromone(old_phero)

        # phero = PheromoneServer(
        #     coords_centre=(self._x, self._y),
        #     zone=set((self._x + offset[0], self._y + offset[1]) for offset in PheromoneServer.OFFSETS),
        #     direction=dir_to_resource)
        # PheromoneServer.pheromones[phero] = dir_to_resource

        # test pour voir si avec la classe PheromoneServer ça fonctionne, déjà ça, et ensuite on verra
        # s'il y a une meilleure manière de stocker les données (car j'ai l'impression que c'est la même
        # chose qu'avant là en vrai)

        # for offset in offsets:
        #     AntServer.PHEROMONES[(self._x + offset[0], self._y + offset[1])] = dir_to_resource

        """
        Il faudrait trouver un moyen de ne remplir qu'une entrée du dictionnaire,
        et boucler sur les clés, je pense que ça serait plus efficace que d'ajouter énormément
        de clés et de valeurs
        Peut-être avec des objets (classes) ? Càd 1 seul couple (x, y) de base
        Un namedtuple avec des coordonnées de base (centre ou quoi) et toutes les autres ?
        """

    def follow_direction_biaised(self, direction, proba=60):
        """Suit une direction ou pas, suivant une probabilité en pourcentage"""
        # <=> proba % de chances de la suivre
        if randint(0, 100) >= proba:
            self._direction = direction

    # def _sniff_pheromone(self):
    #     """Renvoie une direction s'il y a une phéromone et None sinon"""
    #     for phero in AntServer.PHEROMONES:
    #         if (self._x, self._y) in phero.zone:
    #             return AntServer.PHEROMONES[]
    #     return None
    #     # return AntServer.PHEROMONES.get((self._x, self._y))


