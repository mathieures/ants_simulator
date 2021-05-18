from interface.custom_object import CustomObject

class Ant(CustomObject):
    """
    Classe représentant une fourmi graphiquement (un cercle)
    à des coordonnées précises, et d'une taille et couleur données
    """

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, new_color):
        self._color = new_color
        self._canvas.itemconfig(self._id, fill=self._color)

    @property
    def base_color(self):
        return self._base_color


    def __init__(self, canvas, coords, color, size=3):
        """Instancie une fourmi graphiquement"""
        super().__init__(canvas, coords, size=size, color=color)
        self._base_color = color


    def draw(self):
        return self._canvas.create_oval(self.centre_coords,
                                        fill=self._color, outline='')

    def move(self, delta_x, delta_y):
        """Déplace la fourmi avec des coordonnées relatives"""
        self._canvas.move(self._id, delta_x, delta_y)
