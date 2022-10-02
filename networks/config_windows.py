import sys
import tkinter as tk

try:
    from network_utils import get_current_ip
except ImportError:
    from .network_utils import get_current_ip


class ConfigWindow:
    """Class parente aux fenêtres de configuration du client et du serveur"""

    @property
    def ip(self):
        raise NotImplementedError
    
    @property
    def port(self):
        """Attribut port de la fenêtre, récupéré par le main.py"""
        return self._port.get()


    def __init__(self):
        # Variables

        self._root = tk.Tk()

        self._port = tk.IntVar()
        self._port.set(15555)

        # Éléments graphiques

        self._labelframe = tk.LabelFrame(self._root, text="")
        self._labelframe.pack(padx=10, ipadx=10)

        self._topframe = tk.Frame(self._labelframe)
        self._topframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        self._centerframe = tk.Frame(self._labelframe)
        self._centerframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        self._buttonframe = tk.Frame(self._root)
        self._buttonframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')

        self._main_button = tk.Button(self._buttonframe, text="Join", command=self._main_button_callback)
        self._main_button.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        # Bindings

        # Pour gérer la touche Entree
        self._root.bind("<Return>", self._on_return_key)

        # Pour gérer la fermeture de la fenêtre
        self._root.protocol("WM_DELETE_WINDOW", self._quit_config)


    # Méthodes utiles

    def _set_title(self, title):
        """Change le titre de la fenêtre"""
        self._root.title(title)

    def _set_labelframe_text(self, labelframe_text):
        """Change le texte du labelframe"""
        self._labelframe["text"] = labelframe_text

    def _pack_labelframe_with_padx(self, padx, ipadx=0):
        """Pack le labelframe avec du padding en x"""
        self._labelframe.pack(padx=padx, ipadx=ipadx)


    # Bindings

    def _main_button_callback(self, _=None):
        """Callback du bouton principal, à écraser dans les classes filles"""
        raise NotImplementedError

    def _on_return_key(self, _):
        """Callback devant être appelé quand la touche Entrée est pressée"""
        self._main_button.invoke()

    def _quit_config(self):
        sys.exit(0)


class ConfigServer(ConfigWindow):
    """
    Interface permettant au serveur de choisir le port
    du serveur et le nombre de clients maximum
    """

    @property
    def ip(self):
        """
        Retourne une valeur en fonction du mode choisi par l'utilisateur
        'Local only' renverra '127.0.0.1'
        'Current IP' renverra l'IP de la machine
        """
        if self._current_mode.get() == self._modes[0]:
            return '127.0.0.1'
        else:
            return get_current_ip()

    @property
    def max_clients(self):
        return self._max_clients.get()

    @property
    def create_window(self):
        return bool(self._create_window.get())


    def __init__(self):
        super().__init__()

        self._set_title("Server config")

        # Frames
        self._set_labelframe_text("Configure the server to create")
        self._pack_labelframe_with_padx(padx=10, ipadx=10)

        bottomframe = tk.Frame(self._labelframe)
        bottomframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')

        # Variables
        self._modes = ['Local only', 'Current IP']
        self._current_mode = tk.StringVar()
        self._current_mode.set(self._modes[0])

        self._max_clients = tk.IntVar()
        self._max_clients.set(5)

        self._create_window = tk.IntVar()
        self._create_window.set(1)


        # Liste deroulante
        tk.Label(self._topframe, text="Mode:", width=10).pack(side=tk.LEFT)
        mode_option_menu = tk.OptionMenu(self._topframe, self._current_mode, *self._modes)
        mode_option_menu.pack(side=tk.RIGHT)

        # Entrees de texte
        tk.Label(self._centerframe, text="PORT:", width=10).pack(side=tk.LEFT)
        port_entry = tk.Entry(self._centerframe, textvariable=self._port)
        port_entry.pack(side=tk.RIGHT)

        tk.Label(bottomframe, text="Max clients:", width=10).pack(side=tk.LEFT)
        max_clients_sb = tk.Spinbox(bottomframe, from_=1, to=999, increment=1,
                                          width=18, textvariable=self._max_clients)
        max_clients_sb.pack(side=tk.RIGHT)


        # Case à cocher pour savoir si on crée la fenêtre avec les propriétés du serveur
        create_window_cb = tk.Checkbutton(self._buttonframe, text="Create window?", variable=self._create_window)
        create_window_cb.pack(side=tk.TOP)


        self._root.mainloop()


    # Bindings

    def _main_button_callback(self, _=None):
        """
        Callback du bouton principal.
        Lance l'écoute sur le port défini.
        """
        try:
            if self._max_clients.get() > 0 and self._port.get() > 0:
                print("Attempting connection…")

                self._root.destroy()
        except tk.TclError:
            print("[Error] Wrong port or max clients' number")


class ConfigClient(ConfigWindow):
    """
    Interface permettant au client de choisir l'IP du
    serveur et le port auquel il veut se connecter.
    """

    @property
    def ip(self):
        """Attribut ip de la fenêtre, récupéré par le main.py"""
        return self._ip.get()


    def __init__(self):
        super().__init__()

        self._set_title("Config client")

        # Frames
        self._set_labelframe_text("Configure which server to join")
        self._pack_labelframe_with_padx(padx=5)

        # Variables
        self._ip = tk.StringVar()
        self._ip.set('127.0.0.1')


        # Entrées de texte

        # IP
        tk.Label(self._topframe, text='IP:', width=10).pack(side=tk.LEFT)
        ip_entry = tk.Entry(self._topframe, textvariable=self._ip, width=15)
        ip_entry.pack(side=tk.LEFT)

        # PORT
        tk.Label(self._centerframe, text='PORT:', width=10).pack(side=tk.LEFT)
        port_entry = tk.Entry(self._centerframe, textvariable=self._port, width=26)
        port_entry.pack(side=tk.RIGHT)

        # Bouton pour obtenir l'IP de la machine
        current_ip_button = tk.Button(self._topframe, text='Current IP', command=self._set_to_current_ip)
        current_ip_button.pack(side=tk.RIGHT)


        self._root.mainloop()


    # Bindings

    def _set_to_current_ip(self):
        self._ip.set(get_current_ip())

    def _main_button_callback(self, _=None):
        """
        Callback du bouton principal.
        Lance la connexion au serveur en laissant la main au programme principal.
        """
        if len(self._ip.get()) > 0 and self._port.get() > 0:
            self._root.destroy()


def main():
    """Fonction de test"""
    _ = ConfigClient()
    _ = ConfigServer()


if __name__ == '__main__':
    main()