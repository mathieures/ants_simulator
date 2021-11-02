from .InterfaceObject import InterfaceObject

class Pheromone(InterfaceObject):
    """
    Classe représentant une pheromone graphiquement (un carre)
    à des coordonnées précises, et d'une taille et couleur données
    """

    __slots__ = ["_tints", "_tint_index"]
    
    # Teintes roses du clair au fonce
    TINTS = ["#FFDFDB", "#FBBFB8", "#F79F95", "#F38071", "#F0604D"]

    def __init__(self, canvas, origin_coords):
        """Instancie une pheromone graphiquement"""
        self._tint_index = 0 # Index de la teinte qui correspond a la couleur courante
        super().__init__(canvas, origin_coords, size=3, color="#FFDFDB")

        self.draw()


    def draw(self):
        """ Cree la premiere pheromone, override la methode d'origine """
        self._id = self._canvas.create_rectangle(self.drawn_coords, 
                                                 fill=self.color, outline="")
        self._canvas.tag_lower(self._id) # On met les pheromones en arriere-plan


    def darken(self):
        if self._tint_index < 4:
            self._tint_index += 1
            self.color = self.TINTS[self._tint_index]
            self._canvas.itemconfig(self._id, fill=self.color)