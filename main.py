import argparse
import logging
import sys
import threading
from time import sleep

from interface.interface import Interface
from networks.client import Client
from networks.config_client import ConfigClient
from networks.config_server import ConfigServer
from networks.server import Server

ERROR_NON_INTEGERS_ARGUMENTS = "Arguments must be integers"
ERROR_NO_SERVER_FOUND = "No server found"
WARNING_NOT_ENOUGH_ARGUMENTS = "Not enough arguments; starting configuration window"
INFO_ATTEMPTING_CONNECTION = "Attempting connection..."
INFO_CONNECTED = "Connected"

CLIENT_CONNECTION_TIMEOUT_MS = 3000


def init_args(parser: argparse.ArgumentParser):
    """Initialise les arguments du parser."""
    # Serveur
    group_server = parser.add_argument_group("Server arguments")
    group_server.add_argument(
        "-s", "--server",
        help="start a server",
        action="store_true"
    )
    group_server.add_argument(
        "-nw", "--nowindow",
        help="do not create a window to display the server informations",
        action="store_true"
    )
    group_server.add_argument(
        "-i", "--ip",
        help="IP to use for the server",
        type=int
    )
    group_server.add_argument(
        "-p", "--port",
        help="port to use for the server",
        type=int
    )
    group_server.add_argument(
        "-mc", "--maxclients",
        help="max number of clients that will be able to connect to the server",
        type=int
    )

    # Client
    group_client = parser.add_argument_group("Client arguments")
    group_client.add_argument(
        "-c", "--client",
        help="start a client",
        action="store_true"
    )


def start_server(ip: int, port: int, max_clients: int, create_window: bool):
    Server(ip, port, max_clients, create_window)


def start_client():
    config = ConfigClient() # bloquant
    config_ip, config_port = config.ip, config.port

    if len(config_ip) > 0 and config_port > 0:
        logging.info(INFO_ATTEMPTING_CONNECTION)
        client = Client(config_ip, config_port)

        app = Interface(client, 1050, 600)
        t0 = threading.Thread(target=client.connect, daemon=True)
        t0.start()

        time_since_start = 0
        while not client.connected:
            # On abandonne après un certain temps
            if time_since_start > CLIENT_CONNECTION_TIMEOUT_MS:
                break
            time_since_start += 100
            sleep(0.1)

        if client.connected:
            logging.info(INFO_CONNECTED)
            app.root.mainloop()
        else:
            logging.error(ERROR_NO_SERVER_FOUND)


def main():
    parser = argparse.ArgumentParser(
        description="Start a server or a client depending on the argument."
    )

    init_args(parser)

    args = parser.parse_args()

    if args.server:
        # S'il n'y a pas les bons arguments, on ouvre la fenêtre de config
        if not args.ip or not args.port or not args.maxclients:
            logging.warning(WARNING_NOT_ENOUGH_ARGUMENTS)
            config = ConfigServer() # bloquant

            ip = config.ip
            port = config.port
            max_clients = config.max_clients
            create_window = config.create_window

        else:
            create_window = not args.nowindow

            try:
                ip = args.ip
                port = args.port
                max_clients = args.maxclients
            except ValueError:
                logging.error(ERROR_NON_INTEGERS_ARGUMENTS)
                sys.exit(1)
        print(f"server: {ip = }, {port = }, {max_clients = }, {create_window = }")
        start_server(ip, port, max_clients, create_window)

    elif args.client:
        print("client")
        start_client()


if __name__ == "__main__":
    main()
