class CustomObject:
	"""Classe mère des objets, illustre la pose d'objets (à ne pas utiliser seule)"""

	@property
	def id(self):
		return self._id

	@property
	def coords(self):
		return self._canvas.coords(self._id)

	@property
	def centre_coords(self):
		return self.get_centre_coords(self.coords)
	

	def __init__(self, canvas, coords, size=10, color='', width=0):
		"""L'objet calcule son centre et se place au bon endroit tout seul"""
		self._canvas = canvas
		self._color = color
		
		offset_coords = (coords[0],
						 coords[1],
						 coords[0] + size,
						 coords[1] + size)
		
		self._id = self.draw(offset_coords)

	def get_centre_coords(self, coords):
		"""
		Prend en paramètre les coordonnées des deux points
		qui définissent l'objet (tuple de 4 entiers positifs)
		"""
		offset_x = (coords[2] - coords[0]) / 2
		offset_y = (coords[3] - coords[1]) / 2
		
		centre_coords = (coords[0] - offset_x,
						 coords[1] - offset_y,
						 coords[2] - offset_x,
						 coords[3] - offset_y)
		return centre_coords

	def draw(self, centre_coords):
		"""
		Doit être réécrite dans les classes filles pour
		retourner l'id d'un objet de canvas tkinter
		"""
		raise NotImplementedError