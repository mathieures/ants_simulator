from .custom_object import CustomObject

class Ant(CustomObject):
	""" Classe fourmi qui sera uniquement utilisee par l'interface pour l'affichage """
	def __init__(self, canvas, coords, size=15, color='', width=None):
		super().__init__(canvas, coords, size=size, color=color)

	def draw(self, offset_coords):
		"""Override la méthode d'origine"""
		return self._canvas.create_oval(self.get_centre_coords(offset_coords),
										fill=self._color, tag="ant")