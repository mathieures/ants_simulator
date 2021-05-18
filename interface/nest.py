from .custom_object import CustomObject


class Nest(CustomObject):
    def __init__(self, canvas, coords, size=15, color=''):
        """Instancie un nid. Note : le paramètre width n'a pas d'effet ici."""
        super().__init__(canvas, coords, size=size, color=color)

    def draw(self):
        """Override la méthode d'origine"""
        return self._canvas.create_oval(self.centre_coords,
                                        fill=self._color)