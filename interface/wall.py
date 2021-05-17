from .custom_object import CustomObject


class Wall(CustomObject):
    """ Objet Mur représenté graphiquement """ 

    @property
    def size(self):
        """Retourne la largeur, pour homogénéiser les constructeurs"""
        return self._width

    @property
    def width(self):
        return self._width
    
    
    
    # Peut-être qu'on peut faire en sorte que width soit positionnel (et remplacé par size dans le bouton) et que size soit par défaut un truc
    # le if len(coords) peut nous aider à déterminer qu'il faut utiliser size
    def __init__(self, canvas, coords, width=15, size=37.5):
        """
        Crée une ligne de taille size et de largeur width.
        (size est utile pour l'icône du bouton)
        
        Note : on n'appelle pas le constructeur de base,
        car on construit les murs différemment.
        Le paramètre color n'a également pas d'effet ici.
        """
        self._width = width
        self._color = 'black'

        self._canvas = canvas

        # Si on a plus de deux points, alors il faut créer une ligne plus complexe
        if len(coords) > 4:
            self._id = self.draw(coords)
        else:
            offset_coords = (coords[0],
                             coords[1],
                             coords[0] + size,
                             coords[1])
            self._id = self.draw(self.get_centre_coords(offset_coords))

        self._coords = self._canvas.coords(self._id)

    def draw(self, coords):
        """Crée le tout premier mur ; Override la méthode d'origine"""
        return self._canvas.create_line(coords,
                                        width=self._width, fill=self._color)

    def expand(self, x, y):
        """Étend le mur au point donné en paramètre"""
        self._coords.append(x)
        self._coords.append(y)
        self._canvas.coords(self._id, self._coords)
