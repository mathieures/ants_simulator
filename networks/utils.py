"""
Un module qui définit des classes et fonctions utiles
"""

class ReadyState:
    """
    Une classe simple qui représente
    l'état d'un client : prêt ou non.
    Note 1 : False par défaut.
    Note 2 : on ne peut pas hériter de bool.
    """
    def __init__(self):
        self.value = False

class SpeedRequest(str):
    """
    Une classe simple qui représente une demande
    d'accélération/décélération de la simulation.
    La valeur détermine le type :
        - faster : plus vite
        - slower : moins vite
    """


from random import randrange


def random_color():
    """Retourne une couleur aléatoire au format '#xxxxxx'"""
    color = "#"
    for _ in range(3):
        current_color = hex(randrange(0, 256))[2:]
        # On rajoute un 0 avant s'il le faut
        color += f"{current_color.rjust(2, '0')}"
    return color


import socket


def get_current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    return local_ip_address


def id_generator():
    """
    Generator d'id, utile pour donner un identifiant unique à
    un objet d'une classe. N'est pas partagé entre deux classes.
    """
    current_id = 0
    while True:
        yield current_id
        current_id += 1