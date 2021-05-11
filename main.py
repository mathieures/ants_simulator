import threading
import tkinter as tk

from interface.interface import Interface
from networks.client import Client
from networks.config_client import ConfigClient


<<<<<<< HEAD
def ask_connection():
    root = tk.Tk()

    config = ConfigClient(root)

    root.mainloop()

    return config.ip, config.port

def main():

    config_ip, config_port = ask_connection()

    if len(config_ip) > 0 and config_port > 0:
        client = Client(config_ip, config_port)

        if client.connected:
=======
def main():

    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        print("Tentative de connexion en cours...")
        client = Client(config_ip, config_port)

        if client.connected:
            print("Connecté.")
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76
            app = Interface(client, 1050, 600)

            t0 = threading.Thread(target=client.connect)
            t0.start()
<<<<<<< HEAD
            t1 = threading.Thread(target=app.root.mainloop)
            t1.run()
        else:
            print("Serveur non connecté.")
            print("Tentative de connexion interrompu.")
=======
            
            app.root.mainloop()
        else:
            print("Serveur non connecté.")
            print("Tentative de connexion interrompue.")
>>>>>>> 6134ee3db050b403d2a71a44b59253abfd271e76


if __name__ == "__main__":
    main()
