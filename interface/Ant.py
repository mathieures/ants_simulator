from .InterfaceObject import InterfaceObject

class Ant(InterfaceObject):
    """
    Classe représentant une fourmi graphiquement (un cercle)
    à des coordonnées précises, et d'une taille et couleur données
    """

    __slots__ = ["_base_color"]

    @property
    def base_color(self):
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
        """Déplace la fourmi avec des coordonnées relatives"""
        self._canvas.move(self._id, delta_x, delta_y)
        self._update_coords()

    def change_color(self, new_color):
        self.color = new_color
        self._canvas.itemconfig(self._id, fill=self.color)