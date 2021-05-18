import threading
import tkinter as tk

from interface.interface import Interface
from networks.client import Client
from networks.config_client import ConfigClient

from time import sleep


def main():

    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        print("Attempting connection…")
        client = Client(config_ip, config_port)

        app = Interface(client, 1050, 600)
        t0 = threading.Thread(target=client.connect, daemon=True)
        t0.start()

        time_since_start = 0
        while not client.connected:
            # On abandonne apres 3000ms
            if time_since_start > 3000:
                break
            time_since_start += 100
            sleep(0.1)

        if client.connected:
            print("Connected.")
            app.root.mainloop()
        else:
            print("[Error] No connected server.")


if __name__ == "__main__":
    main()
