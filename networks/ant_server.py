from random import randint

class AntServer:

    # Accesseurs et mutateurs
    #########################

    @property
    def id(self):
        return self._id
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def coords(self):
        return (self._x, self._y)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, pdirection):
        self._direction = pdirection % 360

    @property
    def nest(self):
        return self._nest

    @property
    def has_resource(self):
        return self._has_resource

    @has_resource.setter
    def has_resource(self, pbool):
        self._has_resource = pbool

    @property
    def color(self):
        """
        Retourne la couleur de base de la fourmi, même
        quand elle est en gris à cause d'une ressource
        """
        return self._color

    # N'est pas utilisé
    # @color.setter
    # def color(self, pcolor):
    #   self._color = pcolor

    ###############################

    # Attributs de classe
    ID = 0
    PHEROMONES = {} # dictionnaire de coordonnees, associees a une direction

    def __init__(self, posX, posY, color):
        self._id = AntServer.ID
        AntServer.ID += 1

        self._x = posX
        self._y = posY
        self._color = color
        self._direction = randint(0,360)
        self._nest = (posX, posY) # couple de coordonnees : (x, y)

        self._has_resource = False # Booleen pour indiquer si une fourmi possede une ressource
        # self._nest_pheromone = [(posX, posY)] # Pheromone propre a chaque fourmi pour pouvoir retourner dans son nid si elle trouve une ressource


    # def change_position(self):
    def move(self):
        """ Méthode qui change la position de la fourmi en fonction de sa direction """
        # Direction
        # Note Maximino : J'ai mis en commentaire car c'est la simulation qui fait les tests
        """if self._has_resource:
            self._go_to_nest()
            self.lay_pheromone()
        else:
            self._seek_resource()"""
        
        # Mouvement
        if 22.5 <= self._direction < 67.5:
            self._x += 1
            self._y -= 1
        elif 67.5 <= self._direction < 112.5:
            self._y -= 1
        elif 112.5 <= self._direction < 157.5:
            self._x -= 1
            self._y -= 1
        elif 157.5 <= self._direction < 202.5:
            self._x -= 1
        elif 202.5 <= self._direction < 247.5:
            self._x -= 1
            self._y += 1
        elif 247.5 <= self._direction < 292.5:
            self._y += 1
        elif 292.5 <= self._direction < 337.5:
            self._x += 1
            self._y += 1
        else:
            # Entre 337.5 et 22.5
            self._x += 1

    def seek_resource(self):
        """
        Fonction qui donne une direction aleatoire pour
        chercher une ressource ou fait suivre une phéromone
        """
        # Si la fourmi atteint le bord de gauche ou le bord du haut, elle change de direction
        if self._x <= 0 or self._y <= 0:
            self._direction += 180
        else:
            direction = self._sniff_pheromone()

            # S'il y a une pheromone
            if direction is not None:
                self.follow_direction_biaised(direction)
            # Sinon on randomize la direction pour donner un effet de mouvement aleatoire
            else:
                self._direction = randint(self._direction-30, self._direction+30) % 360

    def go_to_nest(self):
        """ La fourmi pointe vers le nid """
        delta_x = self._nest[0] - self._x
        delta_y = self._nest[1] - self._y
        # Si delta_x est positif, la fourmi doit aller vers la droite
        if delta_x > 0:
            # Si delta_y est positif, la fourmi doit aller vers le bas
            if delta_y > 0:
                # Elle doit aller en bas a droite
                self._direction = 315
            elif delta_y < 0:
                # En haut a droite
                self._direction = 45
            else:
                # A droite
                self._direction = 0
        # Sinon s'il est negatif, vers la gauche
        elif delta_x < 0:
            if delta_y > 0:
                # En bas a gauche
                self._direction = 225
            elif delta_y < 0:
                # En haut a gauche
                self._direction = 135
            else:
                # A gauche
                self._direction = 180
        # Sinon on va en haut ou en bas
        else:
            # En bas
            if delta_y > 0:
                self._direction = 270
            # En haut
            else:
                self._direction = 90

    def lay_pheromone(self):
        """
        Pose une phéromone exactement où est la fourmi,
        dans la direction dans laquelle elle va
        Note : écrase la potentielle phéromone déjà présente
        """
        AntServer.PHEROMONES[(self._x, self._y)] = ((self._direction - 180) % 360, 3) # direction, size
        # print("phéromone posée en :", self._x, self._y, "direction :", self._direction)
    
    def follow_direction_biaised(self, direction, proba=60):
        """Suit une direction ou pas, suivant une probabilité"""
        # 90% de chances de la suivre
        if randint(0, 100) >= proba:
            self._direction = direction

    def _sniff_pheromone(self):
        """
        Renvoie True si la fourmi est sur une phéromone
        en fonction de la taille des phéromones (3 pixels)
        """
        # Faire une copie des cles permet d'eviter les RuntimeError
        for coords_phero in tuple(AntServer.PHEROMONES):
            direction, size = AntServer.PHEROMONES.get(coords_phero)
            offset = size // 2 + 1 # +1 pour l'outline
            if (coords_phero[0] - offset <= self._x <= coords_phero[0] + offset) and (
                coords_phero[1] - offset <= self._y <= coords_phero[1] + offset):
                    return direction
        return None