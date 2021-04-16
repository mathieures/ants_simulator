import tkinter as tk

class EasyMenu:
    """
    Prend en paramètre une liste
    de tuple sous la forme
    (texte_sous_menu, callback)
    ou None s'il faut insérer un séparateur
    """
    def __init__(self, parent, text, sub_menus_list, width=5):
        self._menu = tk.Menubutton(parent, text=text, relief="raised", width=width)
        self._deroul = tk.Menu(self._menu, tearoff=False)

        self._sub_menus = []

        for sub_menu in sub_menus_list:
            if sub_menu is not None:
                self._sub_menus.append(self._deroul.add_command(label=sub_menu[0], command=sub_menu[1]))
            else:
                self._deroul.add_separator()
                self._sub_menus.append(None)

        self._menu['menu'] = self._deroul
        self._menu.pack(side=tk.LEFT)
