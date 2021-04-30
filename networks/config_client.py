import tkinter as tk

class ConfigClient:
    """
    Interface permettant au client de choisir l'IP du
    serveur et le port auquel il veut se connecter.
    """

    @property
    def ip(self):
        # print("type de ip :", type(self._ip.get()))
        return self._ip.get()

    @property
    def port(self):
        # print("type de port :", type(self._port.get()))
        return self._port.get()


    def __init__(self, root):
        self._root = root
        self._window = tk.Toplevel(self._root)
        self._window.title('Ant Simulator')

        self._root.withdraw() # Cache la fenetre principale

        # Frames
        self._labelframe = tk.LabelFrame(self._window, text="Configure which server to join")
        self._labelframe.pack(padx=5)

        self._buttonframe = tk.Frame(self._window)
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

        tk.Label(self._topframe, text='IP:', width=10).pack(side=tk.LEFT)
        self._ip_entry = tk.Entry(self._topframe, textvariable=self._ip)
        self._ip_entry.pack(side=tk.RIGHT)

        tk.Label(self._centerframe, text='PORT:', width=10).pack(side=tk.LEFT)
        self._port_entry = tk.Entry(self._centerframe, textvariable=self._port)
        self._port_entry.pack(side=tk.RIGHT)


        # Bouton pour rejoindre

        self._join_button = tk.Button(self._buttonframe, text='Join', command=self.connection)
        self._join_button.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

    def connection(self):
        if len(self._ip.get()) > 0 and self._port.get() > 0:
            print("Tentative de connexion en cours...")
            self._window.destroy()
            self._root.deiconify() # remet la fenetre principale au premier plan
            self._root.destroy()



if __name__ == '__main__':
    root = tk.Tk()

    c = ConfigClient(root)

    root.mainloop()
