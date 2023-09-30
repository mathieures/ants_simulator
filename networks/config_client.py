import sys
import tkinter as tk

from .ip import get_current_ip


class ConfigClient:
    """
    Interface permettant au client de choisir l'IP du
    serveur et le port auquel il veut se connecter.
    """

    @property
    def ip(self):
        return self._ip.get()

    @property
    def port(self):
        return self._port.get()


    def __init__(self):
        self._root = tk.Tk()
        self._root.title('Config client')

        # Frames
        self._labelframe = tk.LabelFrame(self._root, text="Configure which server to join")
        self._labelframe.pack(padx=5)

        self._buttonframe = tk.Frame(self._root)
        self._buttonframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')

        self._topframe = tk.Frame(self._labelframe)
        self._topframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        self._centerframe = tk.Frame(self._labelframe)
        self._centerframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        # Variables
        self._ip = tk.StringVar()
        self._ip.set('127.0.0.1')
        self._port = tk.IntVar()
        self._port.set(15555)


        # Entrées de texte

        # IP
        tk.Label(self._topframe, text='IP:', width=10).pack(side=tk.LEFT)
        self._ip_entry = tk.Entry(self._topframe, textvariable=self._ip, width=15)
        self._ip_entry.pack(side=tk.LEFT)

        # PORT
        tk.Label(self._centerframe, text='PORT:', width=10).pack(side=tk.LEFT)
        self._port_entry = tk.Entry(self._centerframe, textvariable=self._port, width=26)
        self._port_entry.pack(side=tk.RIGHT)

        # Bouton pour obtenir l'IP de la machine
        self._current_ip_button = tk.Button(self._topframe, text='Current IP',
                                            command=self._set_to_current_ip)
        self._current_ip_button.pack(side=tk.RIGHT)

        # Bouton pour rejoindre

        self._join_button = tk.Button(self._buttonframe, text='Join',
                                      command=self._connection)
        self._join_button.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        # Bindings

        # Pour gerer la touche Entree
        self._root.bind("<Return>", self._on_return_key)

        # Pour gerer la fermeture de la fenetre
        self._root.protocol("WM_DELETE_WINDOW", self._quit_config)

        self._root.mainloop()


    # Bindings

    def _connection(self):
        if len(self._ip.get()) > 0 and self._port.get() > 0:
            self._root.destroy()

    def _on_return_key(self, _):
        self._join_button.invoke()

    def _set_to_current_ip(self):
        self._ip.set(get_current_ip())

    def _quit_config(self):
        sys.exit(1)


if __name__ == '__main__':
    root = tk.Tk()

    c = ConfigClient(root)

    root.mainloop()
