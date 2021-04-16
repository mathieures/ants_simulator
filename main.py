import threading

from interface.interface import Interface


def main():

    app = Interface(1050, 750)
    t0 = threading.Thread(target=app.root.mainloop)
    t0.run()


main()
