import tkinter as tk


class EasyButton:
    """
    Crée un bouton avec du texte et/ou une icône à afficher
    (en réalité un objet comme nid ou ressource par exemple)
    qui sera instancié à l'endroit du bouton
    """

    @property
    def text(self):
        if self._text_id is not None:
            return self._canvas.itemcget(self._text_id, 'text')
        else:
            return ''
    
    @text.setter
    def text(self, new_text):
        self._canvas.itemconfig(self._text_id, text=new_text)

    @property
    def hideable(self):
        return self._hideable


    def __init__(self, interface, parent, width, height, toggle=True,
                 text=None, object_type=None, no_icon=False, large=False,
                 side=tk.LEFT, command_select=None, command_deselect=None,
                 hideable=True):
        
        self._interface = interface # utile pour changer l'objet courant
        
        self._active_width = width
        self._active_height = height

        self._canvas = tk.Canvas(parent, width=width, height=height)
        self._default_bg_color = self._canvas['bg'] # on sauvegarde la couleur par defaut

        # L'icône
        self._object_type = object_type
        # S'il y a bien un type et que l'on veut une icône
        if self._object_type is not None and not no_icon:
            # On instancie l'objet
            self._icon_object = self._object_type(self._canvas, (width//2, height//2), width//2)
        else:
            self._icon_object = None

        # Le texte
        if text is not None:
            self._text_id = self._canvas.create_text(width//2, height//2, text=text)
        else:
            self._text_id = None

        # La commande
        self._toggle = toggle # determine si le bouton restera actif apres le clic
        self._command_select = command_select
        self._command_deselect = command_deselect

        self._pack_side = side
        self._canvas.pack(side=self._pack_side)
        self._canvas.bind("<Button-1>", self.on_click)

        self._enabled = True
        self._selected = False
        self._hideable = hideable

    def on_click(self, event):
        """Gère le clic sur le canvas qui sert de bouton"""
        if self._enabled:
            if not self._selected:
                self.select()
            else:
                self.deselect()

    def select(self, exec_command=True):
        """
        Désélectionne tous les boutons, change l'apparence
        de celui-ci et change l'objet courant de l'interface
        """
        self._interface.deselect_buttons() # on deselectionne tous les boutons
        # self._canvas['relief'] = 'raised' # ne fonctionne pas, je ne sais pas pourquoi
        self._canvas['bg'] = '#999'

        if self._object_type is not None:
            # print("selected", self._object_type)
            self._interface.current_object_type = self._object_type

        if exec_command and self._command_select is not None:
            self._command_select()
        
        self._selected = True

        if not self._toggle:
            self.deselect()

    def deselect(self, exec_command=True):
        """
        Désélectionne le bouton, mais seulement visuellement :
        on modifie l'objet sélectionné dans l'interface
        """
        # self._canvas['relief'] = 'flat' # ne fonctionne pas, je ne sais pas pourquoi
        self._canvas['bg'] = self._default_bg_color

        if exec_command and self._command_deselect is not None:
            self._command_deselect()
        
        self._selected = False
        
        if self._interface.current_object_type is self._object_type:
            self._interface.current_object_type = None

    def hide(self):
        """
        Désactive et cache le bouton, le rendant insensible aux clics.
        Change aussi la couleur de fond du canvas, pour être invisible.
        """
        if self._hideable:
            self._canvas.pack_forget()
            # self._canvas['width'] = 0
            # self._canvas['height'] = 0
            self._enabled = False

    def show(self):
        """Réactive et réaffiche le bouton"""
        if self._hideable:
            self._canvas.pack(side=self._pack_side)
            # self._canvas['width'] = self._active_width
            # self._canvas['height'] = self._active_height
            self._enabled = True