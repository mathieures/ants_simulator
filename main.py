import threading

from interface.interface import Interface
from networks.client import Client


def main():

    client = Client('127.0.0.1', 15555)
    t0 = threading.Thread(target=client.connect)
    t0.start()

    app = Interface(client, 1050, 600)
    t1 = threading.Thread(target=app.root.mainloop)
    t1.run()


main()