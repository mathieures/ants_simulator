from .custom_object import CustomObject


class Wall(CustomObject):

    @property
    def size(self):
        return self._width
    
    
    def __init__(self, canvas, coords, width=15, size=None, color=None):
        """
        Crée une ligne de taille size*1.5 et de largeur width.
        (size est utile pour l'icône du bouton)
        
        Note : on n'appelle pas le constructeur de base,
        car on construit les murs différemment.
        Le paramètre color n'a également pas d'effet ici.
        """
        self._width = width
        self._color = color
        if size is None:
            size = 0

        self._canvas = canvas
        
        offset_coords = (coords[0],
                         coords[1],
                         coords[0] + size*1.5,
                         coords[1])
        
        self._id = self.draw(offset_coords)

        self._coords = self._canvas.coords(self._id)

    def draw(self, offset_coords):
        """Crée le tout premier mur ; Override la méthode d'origine"""
        return self._canvas.create_line(self.get_centre_coords(offset_coords),
                                        width=self._width, fill='black')

    def expand(self, x, y):
        """Étend le mur au point donné en paramètre"""
        self._coords.append(x)
        self._coords.append(y)
        self._canvas.coords(self._id, self._coords)