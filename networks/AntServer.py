from random import randrange
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
                 "tries"]

    # Accesseurs et mutateurs
    #########################

    @property
    def direction(self):
        """La direction, en degrés, de la fourmi"""
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction % 360

    # read only
    @property
    def nest(self):
        """Position du nid en un couple (x, y)"""
        return self._nest

    @property
    def is_tired(self):
        """Booléen qui indique si la fourmi est fatiguée"""
        return self.endurance < 1

    ###############################

    # Attributs de classe (read-only a cause des slots, sauf le dictionnaire)

    MAX_ENDURANCE = 512
    MAX_TRIES = 256  # nombre d'essais max pour contourner un mur par la gauche
    ID_GEN = ServerObject.new_id_generator()


    def __init__(self, pos_x, pos_y, color):
        super().__init__([pos_x, pos_y], color)

        self._id = next(self.__class__.ID_GEN)

        self._direction = randrange(0, 360)
        self._nest = self.coords_centre.copy()  # Le nid est la position de depart

        self.has_resource = False  # Booleen pour indiquer si une fourmi possede une ressource
        self.endurance = AntServer.MAX_ENDURANCE
        self.tries = 0  # Nombre d'essais pour le contournement d'un mur


    def simulate(self):
        """Simule la fourmi car on sait qu'il n'y a pas de mur."""
        # Si elle a une ressource, elle pose
        # une phéromone et retourne au nid
        if self.has_resource:
            self.go_to_nest()
            self.lay_pheromone()
        # Si pas de ressource et fatiguée, elle retourne juste au nid
        elif self.is_tired:
            self.go_to_nest()
        # Sinon elle cherche encore
        else:
            self.seek_resource()

    def handle_wall(self):
        """Gère la rencontre avec un mur"""
        # Si elle a une ressource, elle essaie
        # de rejoindre le nid en contournant
        if self.has_resource:
            self.get_around_wall()
            self.lay_pheromone()
        # Sinon elle peut faire demi-tour
        else:
            self.turn_around()

    def move(self):
        """ Méthode qui change la position de la fourmi en fonction de sa direction """
        direction_radians = radians(self._direction)

        delta_x = round(cos(direction_radians), ndigits=0)
        delta_y = -round(sin(direction_radians), ndigits=0)
        # - car c'est un repere orthonorme indirect
        self.coords_centre[0] += delta_x
        self.coords_centre[1] += delta_y

        return delta_x, delta_y

    def seek_resource(self):
        """
        Fonction qui donne une direction aleatoire pour
        chercher une ressource ou fait suivre une phéromone
        """
        self.endurance -= 1

        x, y = self.coords_centre
        # Si la fourmi atteint le bord de gauche ou le bord du haut, elle change de direction
        if x <= 0 or y <= 0:
            self.turn_around()
        else:
            current_phero = PheromoneServer.get_pheromone(x, y)
            # S'il n'y a pas de pheromone on prend une direction aleatoire
            if current_phero is None:
                self.direction = randrange(self._direction - 30, self._direction + 30)
            # Sinon on peut la suivre
            else:
                self.follow_direction_biaised(current_phero.direction)

    def go_to_nest(self):
        """ La fourmi pointe vers le nid """
        x, y = self.coords_centre
        delta_x = self.nest[0] - x
        # on inverse pour le y : repere orthonorme indirect
        delta_y = y - self.nest[1]

        # On arrondit au plus proche entier
        self.direction = round(degrees(atan2(delta_y, delta_x)), ndigits=0)

    def lay_pheromone(self):
        """
        Pose une phéromone autour de la position de la
        fourmi dans la direction dans laquelle elle va
        Note : écrase la potentielle phéromone déjà présente
        """
        dir_to_resource = (self._direction - 180) % 360  # vers la ressource

        new_phero = PheromoneServer(coords_centre=tuple(self.coords_centre),
                                    direction=dir_to_resource)

        old_phero = PheromoneServer.get_pheromone(*self.coords_centre)
        # S'il y a deja au moins un pixel de pheromone a cet endroit
        if old_phero is not None:
            # On supprime de l'ancien les coordonnees qui changent
            # de direction (celles qui sont dans les deux)
            old_phero.zone -= new_phero.zone # old_phero.zone \ new_phero.zone
            # Si l'ancienne a ete completement repassee
            if len(old_phero.zone) == 0:
                PheromoneServer.remove_pheromone(old_phero)

    def follow_direction_biaised(self, direction, proba=60):
        """
        Suit une direction ou pas, suivant une probabilité
        en pourcentage : `proba`% de chances de la suivre
        """
        if randrange(0, 101) > proba:
            self.direction = direction

    def get_around_wall(self):
        """Essaie de contourner un mur"""
        # Si la fourmi n'a pas fait trop d'essais
        if self.tries < self.__class__.MAX_TRIES:
            # Elle contourne le mur par la gauche
            self.direction += 30
            self.tries += 1
        # Sinon elle essaie par la droite
        else:
            self.direction -= 30

    def turn_around(self):
        """Fait demi-tour"""
        self.direction += 180

    def handle_resource(self):
        """
        Méthode simple qui permet de laisser la
        fourmi gérer la découverte d'une ressource
        """
        self.has_resource = True

    def handle_nest(self):
        """
        Remet les attributs à zéro pour que la
        fourmi recommence à chercher comme au début
        """
        self.has_resource = False
        self.endurance = AntServer.MAX_ENDURANCE
        self.tries = 0