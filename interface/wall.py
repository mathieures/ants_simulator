from .custom_object import CustomObject


class Wall(CustomObject):

    @property
    def size(self):
        """Retourne la largeur, pour homogénéiser les constructeurs"""
        return self._width

    @property
    def width(self):
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

        # Si on a plus de deux points, alors il faut créer une ligne plus complexe
        if len(coords) > 4:
            # IL FAUT CREER LA LINGE AVEC TOUTES LES COORDONNEES, QUITTE À NE PAS DRAW AU CENTRE, DU TOUT
            self._id = self.draw(coords)
        else:
            offset_coords = (coords[0],
                             coords[1],
                             coords[0] + size*1.5,
                             coords[1])
            self._id = self.draw(self.get_centre_coords(offset_coords))

        self._coords = self._canvas.coords(self._id)

    def draw(self, coords):
        """Crée le tout premier mur ; Override la méthode d'origine"""
        return self._canvas.create_line(coords,
                                        width=self._width, fill='black')

    def expand(self, x, y):
        """Étend le mur au point donné en paramètre"""
        self._coords.append(x)
        self._coords.append(y)
        self._canvas.coords(self._id, self._coords)