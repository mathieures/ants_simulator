import custom_object

class Resource(custom_object.CustomObject):
    def __init__(self, canvas, coords, size=15):
        super().__init__(canvas, coords, size=size, color='#777')

    def show(self, offset_coords):
        """Override la méthode d'origine"""
        return self._canvas.create_rectangle(self.get_centre_coords(offset_coords),
                                             fill=self._color)