from .InterfaceObject import InterfaceObject


class Nest(InterfaceObject):
    def __init__(self, canvas, coords, size=15, color=""):
        """Instancie un nid."""
        super().__init__(canvas, coords, size, color)

        self.draw()

    def draw(self):
        """Écrase la méthode d'origine"""
        self._id = self._canvas.create_oval(self.drawn_coords,
                                            fill=self.color)