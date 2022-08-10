import concurrent.futures as cf

from time import sleep
from time import perf_counter # Pour le debug
from math import dist as distance
from collections import defaultdict
from itertools import chain

from .ServerObject import SizedServerObject
from .ResourceServer import ResourceServer
from .NestServer import NestServer
from .WallServer import WallServer

from .network_utils import (
    AntsInfo,
    MoveInfo,
    PheromoneInfo,
    ColorInfo,

    FirstBloodSignal
)



# def timer(func):
#     '''Decorator that reports the execution time.'''
#     def wrap(*args, **kwargs):
#         start = perf_counter()
#         result = func(*args, **kwargs)
#         end = perf_counter()

#         print("time", func.__name__, ":", end - start)
#         return result
#     return wrap


class Simulation:
    """Classe qui gère toute la simulation de fourmis"""

    __slots__ = ["objects", "_sleep_time", "_first_blood_happened", "_server", "_timeline", "_tired_ants"]

    @staticmethod
    def optimize_wall(wall_coords):
        """Nettoie le mur de ses points très proches pour alléger les calculs"""
        min_distance = 4 # Distance minimale a avoir entre deux points du mur

        current_point = (wall_coords[0], wall_coords[1])
        opti_coords = [*current_point]
        for i in range(2, len(wall_coords), 2):
            # On compare un point avec le point actuel, et si c'est bon on l'ajoute
            next_point = (wall_coords[i], wall_coords[i + 1])

            current_distance = distance(current_point, next_point)

            if current_distance > min_distance:
                opti_coords.extend(current_point)
                current_point = next_point
        opti_coords.extend(current_point) # il faut rajouter le dernier
        return opti_coords

    @property
    def sleep_time(self):
        """Temps d'attente entre deux étapes de la simulation"""
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, new_time):
        self._sleep_time = round(new_time, 3)


    def __init__(self, server):
        self._server = server

        # Dictionnaire de tous les objets
        self.objects = {
            "nest": set(),
            "resource": set(),
            "wall": set()
        }

        self._timeline = defaultdict(list) # Associe un id client à une liste d'objets

        self._first_blood_happened = False
        self._tired_ants = set()

        self._sleep_time = 0.05


    def start(self):
        """
        Fonction principale qui lance la simulation
        et calcule le déplacement de chaque fourmi
        """
        all_ants = self._get_all_ants_as_list()
        number_of_ants = len(all_ants)

        self._server.send_to_all_clients(AntsInfo(a.to_tuple() for a in all_ants))
        # self._server.send_to_all_clients(["ants", *(a.to_tuple() for a in all_ants)])

        # liste [delta_x, delta_y] (et parfois une couleur) pour bouger les fourmis
        move_info = MoveInfo(number_of_ants=number_of_ants)
        # liste de coordonnees (x, y), qu'on remet a zero
        pheromone_info = PheromoneInfo()

        def _simulate_ant(ant, index):
            """Simule une seule fourmi"""
            x, y = ant.coords_centre  # position actuelle

            if self._get_wall(x, y) is None:
                ant.simulate()
            else:
                ant.handle_wall()

            if ant.has_resource:
                pheromone_info.append((x, y)) # l'ordre n'est pas important


            # if self._get_wall(x, y) is None:
            #     # elle peut faire ses trucs
            #     if ant.has_resource:
            #         # Elle retourne au nid puisqu'il n'y a pas de mur
            #         ant.go_to_nest()

            #         ant.lay_pheromone()
            #         pheromone_info.append((x, y))  # l'ordre n'est pas important

            #     # Si elle n'en a pas mais qu'elle est fatiguée
            #     elif ant.is_tired:
            #         # Il n'y a pas de mur donc elle peut retourner au nid
            #         ant.go_to_nest()
            #     # Si elle n'a ni ressource ni fatigue, elle continue à chercher
            #     else:
            #         ant.seek_resource()
            # else:
            #     # Si elle a une ressource, elle doit essayer de rejoindre le nid en contournant
            #     if ant.has_resource:
            #         ant.get_around_wall()

            #         ant.lay_pheromone()
            #         pheromone_info.append((x, y))  # l'ordre n'est pas important

            #     # Sinon elle peut continuer à chercher autre part
            #     else:
            #         ant.turn_around()
            #         # ant.seek_resource()


            delta_x, delta_y = ant.move() # déplacement relatif

            # les fourmis sont toujours dans le meme ordre
            move_info[index] = [delta_x, delta_y]

            # Si la fourmi est sur son nid
            if ant.coords_centre == ant.nest:
                ant.handle_nest()
                # Reprendre la couleur d'origine
                move_info[index].append(ColorInfo("base"))
                self._tired_ants.remove(ant)

            # Si la fourmi est fatiguée, on l'ajoute à celles qui le sont
            elif ant.is_tired:
                if ant not in self._tired_ants:
                    move_info[index].append(ColorInfo("black"))
                    self._tired_ants.add(ant)
                # On retourne caron ne veut pas qu'elle ramasse de ressource une fois fatiguée
                return

            spotted_resource = self._get_resource(*ant.coords_centre)

            # Si la fourmi n'a pas déjà de ressource
            if not ant.has_resource:
                if spotted_resource is None:
                    return
                if spotted_resource.size == 0:
                    self.objects["resource"].remove(spotted_resource)
                    return
                # Sinon la fourmi a touche une ressource
                ant.handle_resource()
                spotted_resource.shrink_resource() # On reduit la ressource

                # On donne aux clients l'index de la ressource touchee
                # Si ce n'est pas la première, on l'ajoute simplement à la liste
                if self._first_blood_happened:
                    move_info[index].append(spotted_resource.index)
                # Sinon on ajoute un FirstBloodSignal
                else:
                    move_info[index].append(FirstBloodSignal(spotted_resource.index))
                    print("First ant to find resource was color:", ant.color)
                    self._first_blood_happened = True

        while self._server.online:
            # temps_sim = perf_counter()

            # temps_ants = perf_counter() # assez rapide

            # TODO : peut-être bouger ça en dehors de la boucle
            with cf.ThreadPoolExecutor() as executor:
                executor.map(_simulate_ant, all_ants, range(len(all_ants)))

            # print(f"temps_ants : {perf_counter() - temps_ants}")

            # S'il y a de nouvelles pheromones
            if pheromone_info:
                # On envoie les mouvements des fourmis + les pheromones pour eviter de la latence
                self._server.send_to_all_clients([move_info, pheromone_info])
                pheromone_info.clear()

            # Sinon on n'envoie que les positions
            else:
                self._server.send_to_all_clients(move_info)

            # print("temps_sim :", perf_counter() - temps_sim)

            sleep(self._sleep_time)  # ajout d'une latence
        print("End of the simulation.")
        # TODO: afficher la couleur vainqueure a la fin (il faut d'abord une condition de victoire)

    def _is_good_spot(self, x, y, size):
        """
        Retourne True si les coordonnées données en paramètre sont
        disponibles en fonction de la taille donnée, False sinon
        """

        taken_coords = chain.from_iterable(
            obj.zone for values in self.objects.values()
                     for obj in values
        )
        temp_obj = SizedServerObject((x, y), size, color=None)

        if temp_obj.zone.isdisjoint(taken_coords):
            return True
        return False

        # # Pour chaque ensemble d'objets
        # for objects in self.objects.values():
        #     # idée : mettre dans des threads pour calculer les distances parallèlement

        #     # S'il y a au moins un objet
        #     if objects:
        #         # On associe une distance au carre a un objet
        #         all_distances = {distance((x, y), obj.coords_centre): obj for obj in objects}

        #         min_dist = min(all_distances) # Min entre tous les premiers éléments
        #         closest_obj = all_distances[min_dist]

        #         # Pourquoi on n'utilise pas la size donnée en paramètre ?
        #         if min_dist <= closest_obj.size:
        #             return False
        # return True

    def check_all_coords(self, coords_list, size):
        """Vérifie que toutes les coordonnées de la liste sont valides"""
        for i in range(0, len(coords_list), 2):
            if not self._is_good_spot(coords_list[i], coords_list[i + 1], size):
                return False
        return True

    def add_to_objects(self, source_client_id, sent_object):
        """Ajoute une entrée au dictionnaire d'objets de la simulation"""
        # Note : Pour les objets de str_type 'wall', les coordonnees sont une liste de couples

        str_type = sent_object.str_type

        if str_type == "wall":
            new_obj = WallServer.from_SentObject(sent_object)
        elif str_type == "resource":
            new_obj = ResourceServer.from_SentObject(sent_object)
        elif str_type == "nest":
            new_obj = NestServer.from_SentObject(sent_object)
        else:
            raise TypeError(f"[Error] type {str_type} does not exist")

        self.objects[new_obj.str_type].add(new_obj)
        self._timeline[source_client_id].append(new_obj) # KeyError évitée par defaultdict

    def undo_object_from_client(self, client_id):
        """Annule le dernier placement du client avec l'id donné"""
        if self._timeline[client_id]:
            obj = self._timeline[client_id].pop()
            self.objects[obj.str_type].remove(obj) # str_type() renvoie "nest", "resource"…
            self._server.send_destroy_signal(obj)

    def _get_all_ants_as_list(self):
        """
        Retourne la liste de toutes les fourmis
        (contenues dans les objets NestServer)
        Note : on ne peut pas utiliser de compréhension de liste
        """
        # Met bout à bout les fourmis de chaque nid
        return list(chain.from_iterable(nest.ants for nest in self.objects["nest"]))

    def _get_resource(self, target_x, target_y):
        """Retourne l'objet ResourceServer à cette position ou None s'il n'y en a pas"""
        for resource in self.objects["resource"]:
            if (target_x, target_y) in resource.zone:
                return resource
        return None

    def _get_wall(self, x, y):
        for wall in self.objects["wall"]:
            if (x, y) in wall.zone:
                return wall
        return None