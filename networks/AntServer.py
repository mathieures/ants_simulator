from random import randint
from math import degrees, radians, cos, sin, atan2
# atan2 tient compte des signes

from .ServerObject import ServerObject
from .PheromoneServer import PheromoneServer


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

    ###############################

    # Attributs de classe (read-only a cause des slots, sauf le dictionnaire)

    PHEROMONES = {}  # dictionnaire d'objets PheromoneServer, associes a une direction
    MAX_ENDURANCE = 512
    MAX_TRIES = 256  # nombre d'essais max pour contourner un mur par la gauche
    ID_GEN = ServerObject.new_id_generator()

    def __init__(self, pos_x, pos_y, color):
        self._id = next(type(self).ID_GEN)

        self._x = pos_x
        self._y = pos_y
        self.color = color
        self._direction = randint(0, 360)
        self._nest = (pos_x, pos_y)  # Le nid est la position de depart

        self.has_resource = False  # Booleen pour indiquer si une fourmi possede une ressource
        self.endurance = AntServer.MAX_ENDURANCE
        self.tries = 0  # Nombre d'essais pour le contournement d'un mur

    def move(self):
        """ Méthode qui change la position de la fourmi en fonction de sa direction """
        self._x += round(cos(radians(self._direction)), ndigits=0)
        # -= car c'est un repere orthonorme indirect
        self._y -= round(sin(radians(self._direction)), ndigits=0)

    def seek_resource(self):
        """
        Fonction qui donne une direction aleatoire pour
        chercher une ressource ou fait suivre une phéromone
        """
        # Si la fourmi atteint le bord de gauche ou le bord du haut, elle change de direction
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
        # on inverse pour le y : repere orthonorme indirect
        delta_y = self._y - self.nest[1]

        # On arrondit au plus proche entier
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
            if len(old_phero.zone) == 0:
                PheromoneServer.remove_pheromone(old_phero)

    def follow_direction_biaised(self, direction, proba=60):
        """Suit une direction ou pas, suivant une probabilité en pourcentage"""
        # <=> proba % de chances de la suivre
        if randint(0, 100) >= proba:
            self._direction = direction