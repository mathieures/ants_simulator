import tkinter as tk


class EasyButton:
    """
    Crée un bouton avec du texte et/ou une icône à afficher
    (en réalité un objet comme nid ou ressource par exemple)
    qui sera instancié à l'endroit du bouton
    """
    def __init__(self, interface, parent, width, height,
                 text=None, object_type=None, no_icon=False, large=False,
                 side=tk.LEFT, command=None):
        
        self._interface = interface # utile pour changer l'objet courant
        self._canvas = tk.Canvas(parent, width=width, height=height)
        self._default_bg_color = self._canvas['bg'] # on sauvegarde la couleur par défaut

        # On instancie l'objet, quel que soit son type
        self._object_type = object_type
        # S'il y a bien un type et que l'on veut une icône
        if self._object_type is not None and not no_icon:
            self._icon_object = self._object_type(self._canvas, (width//2, height//2), size=width//2)
        else:
            self._icon_object = None

        self._text = text
        if self._text is not None:
            self._text_id = self._canvas.create_text(width//2, height//2, text=self._text)

        self._command = command

        self._canvas.pack(side=side)
        self._canvas.bind("<Button-1>", self.select)


    def select(self, event=None):
        """
        Désélectionne tous les boutons, change l'apparence
        de celui-ci et change l'objet courant de l'interface
        """
        self._interface.deselect_buttons() # on désélectionne tous les boutons
        self._canvas['relief'] = 'raised' # ne fonctionne pas, je ne sais pas pourquoi
        self._canvas['bg'] = '#999'

        if self._object_type is not None:
            print("selected", self._object_type)
            self._interface.current_object_type = self._object_type
        if self._command is not None:
            self._command()
            self.deselect()

    def deselect(self, event=None):
        """
        Désélectionne le bouton, mais seulement visuellement :
        on modifie l'objet sélectionné dans l'interface
        """
        self._canvas['relief'] = 'flat' # ne fonctionne pas, je ne sais pas pourquoi
        self._canvas['bg'] = self._default_bg_color
        # print("deselected")
