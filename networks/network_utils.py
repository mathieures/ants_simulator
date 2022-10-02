"""
Un module qui définit des classes et fonctions utiles
"""

from random import randrange
import socket
import enum


class NetworkMessage(enum.Enum):
    """
    Classe représentant un message/signal sur le réseau, qui
    ne possède pas de valeur particulière si ce n'est son nom.
    """
    STATE_READY = enum.auto()
    STATE_NOT_READY = enum.auto()
    REQUEST_FASTER = enum.auto()
    REQUEST_SLOWER = enum.auto()
    REQUEST_UNDO = enum.auto()
    SIGNAL_GO = enum.auto()
    SIGNAL_ADMIN = enum.auto()

    # Possèdent des infos, donc pas la même chose
    # SIGNAL_DESTROY
    # SIGNAL_FIRST_BLOOD


## Classes utiles ##

# class ReadyState:
#     """
#     Une classe simple qui représente
#     l'état d'un client : prêt ou non.
#     Note 1 : False par défaut.
#     Note 2 : on ne peut pas hériter de bool.
#     """
#     def __init__(self):
#         self.value = False

# class SpeedRequest:
#     """
#     Une classe simple qui représente une demande
#     d'accélération/décélération de la simulation.
#     La valeur de `faster` détermine le type de demande.
#     """
#     def __init__(self, faster):
#         self.faster = faster

#     def __repr__(self):
#         return f"{self.__class__}, faster is {self.faster}"

# class UndoRequest:
#     """Une requête d'annulation, simple objet"""

class GoSignal:
    """Le signal de départ à envoyer aux clients, simple objet"""

class AdminSignal:
    """Le signal de départ à envoyer aux clients, simple objet"""
    # Note : pas sécurisé du tout.

class DestroySignal:
    """Le signal pour la destruction d'un objet à envoyer aux clients"""
    def __init__(self, object_to_destroy):
        self.object_to_destroy = object_to_destroy

class FirstBloodSignal:
    """Contient l'indice de la ressource à rétrécir"""
    def __init__(self, resource_index):
        self.resource_index = resource_index


class ColorInfo(str):
    """
    Classe simple représentant l'information
    d'une couleur envoyée du serveur à un client
    """

class AntsInfo(list):
    """Class simple contenant les coordonnées des fourmis à créer"""

class MoveInfo(list):
    """Classe décrivant les mouvements des fourmis envoyés aux clients"""
    def __init__(self, number_of_ants):
        super().__init__([None] * number_of_ants)

class PheromoneInfo(list):
    """
    Classe simple contenant les positions des
    nouvelles phéromones envoyées aux clients
    """


class SentObject:
    """
    Un objet envoyé sur le réseau par le serveur
    ou un client (mur, nid ou resource)
    """
    @classmethod
    def from_SizedServerObject(cls, obj):
        """Convertit un SizedServerObject en SentObject"""
        return cls(obj.str_type,
                   obj.coords_centre,
                   obj.size,
                   obj.color)


    def __init__(self, str_type, coords, size, color):
        self.str_type = str_type
        self.coords = coords
        self.size = size
        self.color = color


    def __repr__(self):
        return f"{self.__class__.__name__}: {self.str_type}, {self.coords}, {self.size}, {self.color}"

    def __eq__(self, other):
        """
        Permet de déterminer si deux SentObject sont équivalents.
        Utilisé avec self.__hash__ par les clients pour l'undo
        """
        if isinstance(other, self.__class__):
            return (self.str_type == other.str_type) and (
                    self.coords == other.coords) and (
                    self.size == other.size) and (
                    self.color == other.color)
        return NotImplemented

    def __hash__(self):
        return hash((self.str_type, tuple(self.coords), self.size, self.color))


## Fonctions utiles ##

def random_color():
    """Retourne une couleur aléatoire au format '#xxxxxx'"""
    color = "#"
    for _ in range(3):
        current_color = hex(randrange(0, 256))[2:]
        # On rajoute un 0 avant s'il le faut
        color += f"{current_color.rjust(2, '0')}"
    return color

def get_current_ip():
    """Retourne l'IP de la machine actuelle"""
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