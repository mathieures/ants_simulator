import threading
import tkinter as tk

from interface.interface import Interface
from networks.client import Client
from networks.config_client import ConfigClient


def main():

    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        print("Tentative de connexion en cours...")
        client = Client(config_ip, config_port)

        if client.connected:
            print("Connecté.")
            app = Interface(client, 1050, 600)

            t0 = threading.Thread(target=client.connect)
            t0.start()
            t1 = threading.Thread(target=app.root.mainloop)
            t1.run()
        else:
            print("Serveur non connecté.")
            print("Tentative de connexion interrompue.")


if __name__ == "__main__":
    main()
