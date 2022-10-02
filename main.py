import sys

from threading import Thread
from time import sleep

from interface.Interface import Interface
from networks.Client import Client
from networks.ConfigClient import ConfigClient

from networks.ConfigServer import ConfigServer
from networks.Server import Server


def start_client():
    """Lance le client"""
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

def start_server():
    """Lance le serveur"""
    # On regarde d'abord si l'utilisateur veut une fenêtre
    if "-nowindow" in sys.argv:
        create_window = False
        sys.argv.pop(sys.argv.index("-nowindow"))
        # print("new args :", sys.argv)
    else:
        create_window = True

    # S'il n'y a pas assez d'arguments, on ouvre la fenêtre de config
    if len(sys.argv) < 4:
        config = ConfigServer() # bloquant

        ip = config.ip
        port = config.port
        max_clients = config.max_clients
        create_window = config.create_window

    else:
        try:
            ip = int(sys.argv[1])
            port = int(sys.argv[2])
            max_clients = int(sys.argv[3])
        except ValueError:
            print("[Error] Arguments must be integers")
            print("Syntax:\n\tpython3 main.py [server [IP PORT NB_MAX_CLIENTS] [-nowindow]]")
            sys.exit(1)

    Server(ip, port, max_clients, create_window)

if len(sys.argv) > 1 and sys.argv[1] == "server":
    sys.argv.pop(sys.argv.index("server"))
    start_server()
else:
    start_client()