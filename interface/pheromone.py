from .custom_object import CustomObject

class Pheromone(CustomObject):
	"""
	Classe représentant une pheromone graphiquement (un carre)
	à des coordonnées précises, et d'une taille et couleur données
	"""

	def __init__(self, canvas, coords):
		"""Instancie une pheromone graphiquement"""
		super().__init__(canvas, coords, size=3, color="#FFDFDB")

		# Teintes roses du clair au fonce
		self._tints = ["#FFDFDB", "#FBBFB8", "#F79F95", "#F38071", "#F0604D"]
		self._curr_tint = 0 # Index de la teinte qui correspond a la couleur courante

	def draw(self):
		""" Cree la premiere pheromone, override la methode d'origine """
		id = self._canvas.create_rectangle(self.centre_coords, 
										   fill=self._color, outline='')
		self._canvas.tag_lower(id) # On met les pheromones en arriere-plan
		return id


	def darken(self):
		if self._curr_tint < 4:
			self._curr_tint += 1
			self._color = self._tints[self._curr_tint]
			self._canvas.itemconfig(self._id, fill=self._color)
