import dearpygui.dearpygui as dpg
from .InterfaceObject import InterfaceObject


class Nest(InterfaceObject):
    """Nid représenté graphiquement"""

    def __init__(self, window, coords, size=15, color=""):
        """Instancie un nid."""
        super().__init__(window, coords, size, color)

        self.draw()

    def _init_drawn_coords(self):
        """Les objets Nest n'en ont pas besoin"""
        return None

    def draw(self):
        """Écrase la méthode d'origine"""
        self._id = dpg.draw_circle(self.origin_coords, self.size, fill=self.color)