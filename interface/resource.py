from .custom_object import CustomObject


class Resource(CustomObject):
    def __init__(self, canvas, coords, size=20, width=None, color=None):
        """
        Instancie une ressource.
        Note : ni le paramètre width ni le paramètre color n'ont d'effet ici.
        """
        super().__init__(canvas, coords, size=size)

    def draw(self, offset_coords):
        """Override la méthode d'origine"""
        return self._canvas.create_rectangle(self.get_centre_coords(offset_coords),
                                             fill='#777')
