import tkinter as tk

from .ip import get_current_ip


class ConfigServer:
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
        mode = self._current_mode.get()
        if mode == self._modes[0]:
            return '127.0.0.1'
        else:
            return get_current_ip()

    @property
    def port(self):
        return self._port.get()

    @property
    def max_clients(self):
        return self._max_clients.get()

    @property
    def create_window(self):
        return bool(self._create_window.get())
    


    def __init__(self):
        self._root = tk.Tk()
        self._root.title("Server config")

        # Frames
        self._labelframe = tk.LabelFrame(self._root, text="Configure the server to create")
        self._labelframe.pack(padx=10, ipadx=10)

        self._buttonframe = tk.Frame(self._root)
        self._buttonframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')


        self._topframe = tk.Frame(self._labelframe)
        self._topframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        self._centerframe = tk.Frame(self._labelframe)
        self._centerframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X)
        self._bottomframe = tk.Frame(self._labelframe)
        self._bottomframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')

        # Variables
        self._modes = ['Local only', 'Current IP']
        self._current_mode = tk.StringVar()
        self._current_mode.set(self._modes[0])

        self._max_clients = tk.IntVar()
        self._max_clients.set(5)

        self._port = tk.IntVar()
        self._port.set(15555)

        self._create_window = tk.IntVar()
        self._create_window.set(1)


        # Liste deroulante
        tk.Label(self._topframe, text="Mode:", width=10).pack(side=tk.LEFT)
        self._mode_option_menu = tk.OptionMenu(self._topframe, self._current_mode, *self._modes)
        self._mode_option_menu.pack(side=tk.RIGHT)

        # Entrees de texte
        tk.Label(self._centerframe, text="PORT:", width=10).pack(side=tk.LEFT)
        self._port_entry = tk.Entry(self._centerframe, textvariable=self._port)
        self._port_entry.pack(side=tk.RIGHT)

        tk.Label(self._bottomframe, text="Max clients:", width=10).pack(side=tk.LEFT)
        self._max_clients_sb = tk.Spinbox(self._bottomframe, from_=1, to=999, increment=1,
                                          width=18, textvariable=self._max_clients)
        self._max_clients_sb.pack(side=tk.RIGHT)

        

        self._create_window_cb = tk.Checkbutton(self._buttonframe, text="Create window?", variable=self._create_window)
        self._create_window_cb.pack(side=tk.TOP)



        # Bouton pour creer le serveur
        self._create_server_button = tk.Button(self._buttonframe, text="Join", command=self._create_server)
        self._create_server_button.pack(side=tk.BOTTOM, expand=True, fill=tk.X, padx=1, pady=1)

        # Bindings

        # Pour gerer la touche Entree
        self._root.bind("<Return>", self._on_return_key)
        
        # Pour gerer la fermeture de la fenetre
        self._root.protocol("WM_DELETE_WINDOW", self._quit_config)
        
        self._root.mainloop()


    # Bindings

    def _create_server(self, event=None):
        try:
            if self._max_clients.get() > 0 and self._port.get() > 0:
                print("Attempting connection…")

                self._root.destroy()
        except tk._tkinter.TclError:
            print("[Error] Wrong port or max clients' number")

    def _on_return_key(self, event):
        self._create_server_button.invoke()

    def _quit_config(self):
        exit(1)


if __name__ == '__main__':
    c = ConfigServer()
