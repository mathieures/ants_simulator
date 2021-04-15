import custom_object

class Nest(custom_object.CustomObject):
    def __init__(self, canvas, coords, size=15, color='', width=None):
        """Instancie un nid. Note : le paramètre width n'a pas d'effet ici."""
        super().__init__(canvas, coords, size=size, color=color)

    def draw(self, offset_coords):
        """Override la méthode d'origine"""
        return self._canvas.create_oval(self.get_centre_coords(offset_coords),
                                        fill=self._color)