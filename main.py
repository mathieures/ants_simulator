from threading import Thread
from time import sleep

from interface.Interface import Interface
from networks.Client import Client
from networks.ConfigClient import ConfigClient


def main():

    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        print("Attempting connection…")
        client = Client(config_ip, config_port)

        app = Interface(client, 1050, 600)

        # On lance la connexion au serveur
        Thread(target=client.connect, daemon=True).start()

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
            app.quit_app()


if __name__ == "__main__":
    main()
