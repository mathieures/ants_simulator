from .custom_object import CustomObject

class Ant(CustomObject):
    """
    Classe représentant une fourmi graphiquement (un cercle)
    à des coordonnées précises, et d'une taille et couleur données
    """    

    @property
    def color(self):
        """On a besoin qu'elle soit accessible"""
        return self._color
    
    @color.setter
    def color(self, new_color):
        self._color = new_color
        self._canvas.itemconfig(self._id, fill=self._color)
    

    def __init__(self, canvas, coords, color, size=3):
        """Instancie une fourmi graphiquement"""
        super().__init__(canvas, coords, size=size, color=color)

    def draw(self, offset_coords):
        return self._canvas.create_oval(self.get_centre_coords(offset_coords),
                                        fill=self._color, outline='')
    
    def move(self, delta_x, delta_y):
        """Déplace la fourmi avec des coordonnées relatives"""
        self._canvas.move(self._id, delta_x, delta_y)