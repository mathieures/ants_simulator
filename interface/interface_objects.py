class InterfaceObject:
    """Classe mère des objets, illustre la pose d'objets (à ne pas utiliser seule)"""

    __slots__ = ["_canvas", "_id", "color", "size",
                 "origin_coords", "drawn_coords",
                 "coords_centre", "_prev_coords"]

    # read-only
    @property
    def id(self):
        """Identifiant donné par tkinter"""
        return self._id


    def __init__(self, canvas, origin_coords, size=10, color=""):
        """L'objet calcule son centre et se place au bon endroit tout seul"""
        self._canvas = canvas
        self.origin_coords = origin_coords
        self.size = size
        self.color = color

        self.drawn_coords = (self.origin_coords[0] - self.size / 2,
                             self.origin_coords[1] - self.size / 2,
                             self.origin_coords[0] + self.size / 2,
                             self.origin_coords[1] + self.size / 2)

        self.coords_centre = self._get_centre_coords()

        self._id = None # Doit etre ecrase par les classes filles


    def __repr__(self):
        return f"{self.__class__.__name__}: {self.origin_coords}, {self.size}, {self.color}"

    def draw(self):
        """
        Doit être réécrite dans les classes filles et
        mettre à jour l'id (objet de canvas tkinter)
        """
        raise NotImplementedError

    def _get_drawn_coords(self):
        return self._canvas.coords(self._id)

    def _get_centre_coords(self):
        return (self.drawn_coords[2] - self.drawn_coords[0], self.drawn_coords[3] - self.drawn_coords[1])


class Ant(InterfaceObject):
    """
    Classe représentant une fourmi graphiquement (un cercle)
    à des coordonnées précises, et d'une taille et couleur données
    """

    __slots__ = ["_base_color"]

    @property
    def base_color(self):
        """Couleur de base de la fourmi, en lecture seule"""
        return self._base_color


    def __init__(self, canvas, origin_coords, size=3, color="black"):
        """Instancie une fourmi graphiquement"""
        super().__init__(canvas, origin_coords, size, color)

        self._base_color = self.color
        self.draw()


    def draw(self):
        self._id = self._canvas.create_oval(self.drawn_coords,
                                            fill=self.color, outline="")

    def move(self, delta_x, delta_y):
        """
        Déplace la fourmi avec des coordonnées relatives
        puis met à jour les coordonnées calculées
        """
        self._canvas.move(self._id, delta_x, delta_y)

        self.coords_centre = self._get_centre_coords()
        self.drawn_coords = self._get_drawn_coords()

    def change_color(self, new_color):
        """
        Change la couleur de la fourmi. Si la couleur donnée en
        paramètre est "base", la couleur est celle par défaut
        """
        if new_color == "base":
            self.color = self.base_color
        else:
            self.color = new_color
        self._canvas.itemconfig(self._id, fill=self.color)

    def set_resource_color(self):
        """Change la couleur de la fourmi pour montrer qu'elle a une ressource"""
        self.change_color("grey") # Couleur qu'aura la fourmi


class Nest(InterfaceObject):
    """Nid représenté graphiquement"""

    def __init__(self, canvas, coords, size=15, color=""):
        """Instancie un nid."""
        super().__init__(canvas, coords, size, color)

        self.draw()


    def draw(self):
        """Écrase la méthode d'origine"""
        self._id = self._canvas.create_oval(self.drawn_coords,
                                            fill=self.color)


class Pheromone(InterfaceObject):
    """
    Classe représentant une phéromone graphiquement (un carre)
    à des coordonnées précises, et d'une taille et couleur données
    """

    __slots__ = ["_tints", "_tint_index"]

    # Teintes roses du clair au fonce
    TINTS = ["#FFDFDB", "#FBBFB8", "#F79F95", "#F38071", "#F0604D"]

    def __init__(self, canvas, origin_coords):
        """Instancie une phéromone graphiquement"""
        self._tint_index = 0 # Index de la teinte qui correspond a la couleur courante
        super().__init__(canvas, origin_coords, size=3, color="#FFDFDB")

        self.draw()


    def draw(self):
        """ Crée la premiere phéromone, override la méthode d'origine """
        self._id = self._canvas.create_rectangle(self.drawn_coords,
                                                 fill=self.color, outline="")
        self._canvas.tag_lower(self._id) # On met les pheromones en arrière-plan


    def darken(self):
        """
        Fonce la couleur de la phéromone pour montrer
        que plusieurs sont déposées au même endroit
        """
        if self._tint_index < 4:
            self._tint_index += 1
            self.color = self.TINTS[self._tint_index]
            self._canvas.itemconfig(self._id, fill=self.color)


class Resource(InterfaceObject):
    """Ressource représentée graphiquement"""

    __slots__ = ["current_size"]


    def __init__(self, canvas, origin_coords, size=20):
        """
        Instancie une ressource.
        Note : la couleur est toujours la même.
        """
        super().__init__(canvas, origin_coords, size, color="#777")
        self.current_size = self.size

        self.draw()


    def draw(self):
        """Override la méthode d'origine"""
        self._id = self._canvas.create_rectangle(self.drawn_coords,
                                                 fill=self.color)

    def shrink(self):
        """Rapetisse la ressource."""
        shrinking_factor = 1 - 1 / self.current_size
        self._canvas.scale(self._id, *self.origin_coords,
                           shrinking_factor, shrinking_factor)
        # scale(tagOrId, x, y, sx, sy) : deplacement de tous les
        # pts de l'obj par rapport a (x, y), d'un facteur de (sx, sy)
        self.current_size -= 1

    def remove(self):
        """ Pour faire disparaitre une ressource """
        self._canvas.delete(self.id)


class Wall(InterfaceObject):
    """Mur représenté graphiquement"""

    __slots__ = ["length"]


    def __init__(self, canvas, origin_coords, size=10, length=0):
        """
        Crée une ligne de taille size et de largeur length.
        (size est utile pour l'icône du bouton)
        """
        super().__init__(canvas, origin_coords, size, color="black")

        self.length = length

        # On écrase les coordonnées de dessin, car
        # les murs fonctionnent d'une autre manière

        # Si on n'a pas deux points, alors on ne crée qu'un rectangle
        if len(origin_coords) < 4:
            # test avec une array
            self.drawn_coords = [self.origin_coords[0],
                                 self.origin_coords[1],
                                 self.origin_coords[0] + self.length,
                                 self.origin_coords[1]]
        else:
            self.drawn_coords = self.origin_coords

        self.draw()


    def draw(self):
        """Crée le tout premier mur, pouvant être étendu."""
        self._id = self._canvas.create_line(self.drawn_coords,
                                            width=self.size, fill=self.color)

    def expand(self, to_x, to_y):
        """Étend le mur au point donné en paramètre"""
        self.drawn_coords.extend((to_x, to_y))
        self._canvas.coords(self._id, self.drawn_coords)


class WallInAButton(Wall):
    """Un Wall, mais dans un EasyButton."""
    def __init__(self, canvas, origin_coords, size, length):

        super().__init__(canvas, origin_coords, size, length)

        self.drawn_coords = [self.origin_coords[0],
                             self.origin_coords[1],
                             self.origin_coords[0] + self.size,
                             self.origin_coords[1]]