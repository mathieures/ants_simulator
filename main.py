import threading
import tkinter as tk

from interface.interface import Interface
from networks.client import Client
from networks.config_client import ConfigClient


def main():

    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        print("Attempting connection…")
        client = Client(config_ip, config_port)

        if client.connected:
            app = Interface(client, 1050, 600)

            t0 = threading.Thread(target=client.connect, daemon=True)
            t0.start()
            print("Connected.")

            app.root.mainloop()
        else:
            print("[Error] No connected server.")


if __name__ == "__main__":
    main()
