import dearpygui.dearpygui as dpg
from .InterfaceObject import InterfaceObject


class Resource(InterfaceObject):
    """Ressource représentée graphiquement"""

    __slots__ = ["current_size"]


    def __init__(self, canvas, origin_coords, size=20):
        """
        Instancie une ressource.
        Note : la couleur est toujours la même.
        """
        super().__init__(canvas, origin_coords, size, color="#777")

        self.current_size = self.size

        self.draw()


    def draw(self):
        """Override la méthode d'origine"""
        self._id = dpg.draw_quad(*self.drawn_coords,
                                 fill=self.color)

    def shrink(self):
        """
        Rapetisse la ressource en calculant des
        coordonnées plus proches les unes des autres
        """
        # calcul matriciel ?
        shrinking_factor = 1 - 1 / self.current_size
        self._canvas.scale(self._id, *self.origin_coords,
                           shrinking_factor, shrinking_factor)
        # scale(tagOrId, x, y, sx, sy) : deplacement de tous les
        # pts de l'obj par rapport a (x, y), d'un facteur de (sx, sy)
        self.current_size -= 1

    def remove(self):
        """ Pour faire disparaitre la ressource """
        dpg.delete_item(self._id)
