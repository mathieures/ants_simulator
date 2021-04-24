from .custom_object import CustomObject

class Pheromone(CustomObject):
	"""
	Classe représentant une pheromone graphiquement (un carre)
	à des coordonnées précises, et d'une taille et couleur données
	"""

	def __init__(self, canvas, coords):
		"""Instancie une pheromone graphiquement"""
		super().__init__(canvas, coords, size=3,color="#FFDFDB")

		# Teintes roses du clair au fonce
		self.tints = ["#FFDFDB", "#FBBFB8", "#F79F95", "#F38071", "#F0604D"]
		self.curr_tint = 0 # Index de la teinte qui correspond a la couleur courante

	def draw(self, offset_coords):
		""" Cree la premiere pheromone, override la methode d'origine """
		return self._canvas.create_rectangle(self.get_centre_coords(offset_coords), 
											fill=self._color, outline='')

	def darker(self):
		if self.curr_tint == 4:
			return
		self.curr_tint += 1
		self._color = self.tints[self.curr_tint]
		self._canvas.itemconfig(self._id, fill=self._color)