import tkinter as tk
import threading

class ServerWindow(threading.Thread):
    """
    Interface permettant à l'utilisateur de connaître en tout
    temps l'IP et le nombre de clients connectés et attendus.
    """

    @property
    def ip(self):
        """
        Retourne une valeur en fonction du mode choisi par l'utilisateur
        'Local only' renverra '127.0.0.1'
        'Current IP' renverra l'IP de la machine
        """
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def max_clients(self):
        return self._max_clients

    @property
    def clients(self):
        return self._clients.get()

    @clients.setter
    def clients(self, new_number):
        self._clients.set(new_number)

    @property
    def ready_clients(self):
        return self._ready_clients.get()

    @ready_clients.setter
    def ready_clients(self, new_number):
        self._ready_clients.set(new_number)
    

    def __init__(self, server, daemon):
        """Le daemon permet de tuer le thread quand on tue les autres fils"""
        threading.Thread.__init__(self, daemon=daemon)

        self._ip = server.ip
        self._port = str(server.port)
        self._max_clients = str(server.max_clients)
        self._clients = None
        self._ready_clients = None
        
        self._server = server # on le garde pour pouvoir le quitter
        self._server.window = self


    def run(self):
        """Écrase la méthode d'origine"""
        self._root = tk.Tk()
        self._root.title("Server")

        # Variables
        self._clients = tk.IntVar()
        self._clients.set(0)

        self._ready_clients = tk.IntVar()
        self._ready_clients.set(0)

        # Frames
        self._labelframe = tk.LabelFrame(self._root, text="Server sneak peek")
        self._labelframe.pack(padx=14, ipadx=20, pady=8)

        self._cc_frame = tk.Frame(self._labelframe) # cc = current clients
        self._cc_frame.pack(side=tk.BOTTOM)

        # Labels et entries (pour pouvoir les selectionner)
        port_text = tk.Entry(self._labelframe, width=20, relief='flat')
        port_text.insert(0, 'PORT: ' + self._port)
        port_text['state'] = "readonly"
        port_text.pack(side=tk.TOP)

        ip_text = tk.Entry(self._labelframe, width=20, relief='flat')
        ip_text.insert(0, 'IP: ' + self._ip)
        ip_text['state'] = "readonly"
        ip_text.pack(side=tk.TOP)

        tk.Label(self._cc_frame, text='Clients ready: ').pack(side=tk.LEFT)

        tk.Label(self._cc_frame, textvariable=self._ready_clients, width=2).pack(side=tk.LEFT)

        tk.Label(self._cc_frame, text='/').pack(side=tk.LEFT)

        tk.Label(self._cc_frame, textvariable=self._clients, width=2).pack(side=tk.LEFT)

        tk.Label(self._cc_frame, text='(max: {})'.format(self._max_clients)).pack(side=tk.LEFT)
        
        # Pour gerer la fermeture de la fenetre
        self._root.protocol("WM_DELETE_WINDOW", self._quit_server)

        self._root.mainloop()

    def quit_window(self):
        """Ferme la fenêtre. Méthode utilisée par le serveur."""
        self._root.destroy()

    def _quit_server(self):
        """Notifie au serveur qu'il doit s'arrêter"""
        self._server.quit()


if __name__ == '__main__':
    c = ServerWindow('127.0.1.1', 15555, 5)
