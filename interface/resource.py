from .custom_object import CustomObject


class Resource(CustomObject):
    def __init__(self, canvas, coords, size=20):
        """
        Instancie une ressource.
        Note : ni le paramètre width ni le paramètre color n'ont d'effet ici.
        """
        super().__init__(canvas, coords, size=size)

    def draw(self, offset_coords):
        """Override la méthode d'origine"""
        return self._canvas.create_rectangle(self.get_centre_coords(offset_coords),
                                             fill='#777')

    def shrink(self):
        """ Fonction pour rapetisser une ressource """
        coords = self._canvas.coords(self._id)
        self._canvas.scale(self._id, coords[0], coords[1], 0.95, 0.95)