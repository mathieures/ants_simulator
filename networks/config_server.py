import tkinter as tk

class ConfigServer:
    """
    Interface permettant au serveur de choisir le port
    du serveur et le nombre de clients maximum
    """

    @property
    def ip(self):
        """
        Retourne une valeur en fonction du mode choisi par l'utilisateur :
        'Local only' renverra '127.0.0.1'
        'Current IP' renverra l'IP de la machine
        """
        mode = self._current_mode.get()
        if mode == self._modes[0]:
            return '127.0.0.1'
        else:
            # ip etc.
            return '127.0.0.1' # à toi de jouer baptiste ;)
    

    @property
    def port(self):
        # print("type de port :", type(self._port.get()))
        return self._port.get()

    @property
    def max_clients(self):
        # print("type de max_clients :", type(self._max_clients.get()))
        return self._max_clients.get()
    


    def __init__(self):
        self._root = tk.Tk()
        self._root.title('Ant Simulator')

        # Frames
        self._labelframe = tk.LabelFrame(self._root, text="Configure the server to create")
        self._labelframe.pack(padx=5)

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


        # Liste deroulante

        tk.Label(self._topframe, text='Mode:', width=10).pack(side=tk.LEFT)
        self._mode_option_menu = tk.OptionMenu(self._topframe, self._current_mode, *self._modes)
        self._mode_option_menu.pack(side=tk.RIGHT)

        # Entrees de texte

        tk.Label(self._centerframe, text='PORT:', width=10).pack(side=tk.LEFT)
        self._port_entry = tk.Entry(self._centerframe, textvariable=self._port)
        self._port_entry.pack(side=tk.RIGHT)

        tk.Label(self._bottomframe, text='Max clients:', width=10).pack(side=tk.LEFT)
        self._max_clients_sb = tk.Spinbox(self._bottomframe, from_=1, to=999, increment=1,
                                          width=18, textvariable=self._max_clients)
        self._max_clients_sb.pack(side=tk.RIGHT)


        # Bouton pour creer le serveur

        self._create_server_button = tk.Button(self._buttonframe, text='Join', command=self.create_server)
        self._create_server_button.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

        self._root.mainloop()

    def create_server(self):
        if self._max_clients.get() > 0 and self._port.get() > 0:
            print("Tentative de connexion en cours...")

            self._root.destroy()




if __name__ == '__main__':
    c = ConfigServer()
