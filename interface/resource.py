from .custom_object import CustomObject


class Resource(CustomObject):
    def __init__(self, canvas, coords, size=20):
        """
        Instancie une ressource.
        Note : ni le paramètre width ni le paramètre color n'ont d'effet ici.
        """
        self.max_shrinking = 23
        super().__init__(canvas, coords, size=size)


    def draw(self, offset_coords):
        """Override la méthode d'origine"""
        return self._canvas.create_rectangle(self.get_centre_coords(offset_coords),
                                             fill='#777')

    def shrink(self):
        """ Fonction pour rapetisser une ressource """
        self._canvas.scale(self._id, *self.centre_coords[2:4], 0.95, 0.95)
        self.max_shrinking -= 1

    def remove(self):
        """ Pour faire disparaitre une ressource """
        self._canvas.delete(self.id)
