import tkinter as tk
from .ip import get_current_ip
# Note : il ne faut pas confondre le module ip et l'attribut


class ConfigClient:
    """
    Interface permettant au client de choisir l'IP du
    serveur et le port auquel il veut se connecter.
    """

    @property
    def ip(self):
        """Attribut ip de la fenêtre, récupéré par le main.py"""
        return self._ip.get()

    @property
    def port(self):
        """Attribut port de la fenêtre, récupéré par le main.py"""
        return self._port.get()


    def __init__(self):
        self._root = tk.Tk()
        self._root.title('Config client')

        # Frames
        labelframe = tk.LabelFrame(self._root, text="Configure which server to join")
        labelframe.pack(padx=5)

        buttonframe = tk.Frame(self._root)
        buttonframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X, anchor='s')

        topframe = tk.Frame(labelframe)
        topframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        centerframe = tk.Frame(labelframe)
        centerframe.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        # Variables
        self._ip = tk.StringVar()
        self._ip.set('127.0.0.1')
        self._port = tk.IntVar()
        self._port.set(15555)


        # Entrées de texte

        # IP
        tk.Label(topframe, text='IP:', width=10).pack(side=tk.LEFT)
        ip_entry = tk.Entry(topframe, textvariable=self._ip, width=15)
        ip_entry.pack(side=tk.LEFT)

        # PORT
        tk.Label(centerframe, text='PORT:', width=10).pack(side=tk.LEFT)
        port_entry = tk.Entry(centerframe, textvariable=self._port, width=26)
        port_entry.pack(side=tk.RIGHT)

        # Bouton pour obtenir l'IP de la machine
        current_ip_button = tk.Button(topframe, text='Current IP', command=self._set_to_current_ip)
        current_ip_button.pack(side=tk.RIGHT)

        # Bouton pour rejoindre

        self._join_button = tk.Button(buttonframe, text='Join', command=self._connection)
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

    def _on_return_key(self, event):
        self._join_button.invoke()

    def _set_to_current_ip(self):
        self._ip.set(get_current_ip())

    def _quit_config(self):
        exit(1)


if __name__ == '__main__':
    c = ConfigClient()