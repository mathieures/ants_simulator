# TODO: trouver pourquoi ça affiche plus rien


import threading
from time import sleep
from math import sqrt
from collections import namedtuple

from AntServer import AntServer
from ResourceServer import ResourceServer
from NestServer import NestServer


import tracemalloc
from time import perf_counter

# Pour le debug


def timer(func):
    '''Decorator that reports the execution time.'''
    def wrap(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()

        print("time", func.__name__, ":", end - start)
        return result
    return wrap


class Simulation:
    """ Classe qui lance toute la simulation de fourmis a partir du dico d'objets defini par le serveur """

    __slots__ = ("objects", "_sleep_time", "_first_ant", "_server")
    # @property
    # def objects(self):
    #     """
    #     Dictionnaire de tous les objets
    #     """
    #     return self._objects

    # @objects.setter
    # def objects(self, new_objects):
    #     self._objects = new_objects

    @property
    def sleep_time(self):
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, new_sleep_time):
        # print("sim : new_sleep_time :", new_sleep_time)
        self._sleep_time = new_sleep_time

    def __init__(self, server):
        self._server = server

        # self._ants = []  # Liste d'instances AntServer
        self.objects = {
            "nest": set(),  # ça serait cool que les NestServer contiennent leurs fourmis
            "resource": set(),  # remplace par ResourceServer.resources
            "wall": set()
        }  # Dictionnaire de tous les objets

        self._first_ant = True

        self._sleep_time = 0.05

    # def _init_ants(self, number=20):
    #     """ Fonction qui ajoute les fourmis dans chaque nid (envoi des donnees aux clients)"""
    #     ants = ["ants"]  # liste des fourmis a envoyer au serveur
    #     # Securite pour ne pas commencer sans nid
    #     if "nest" in self.objects:
    #         for nest in self.objects["nest"]:
    #             # nest est un tuple de la forme (coords, size, width, color)
    #             x, y = nest[0]
    #             color = nest[3]
    #             for i in range(number):
    #                 curr_ant = AntServer(x, y, color)
    #                 self._ants.append(curr_ant)
    #                 ants.append(((x, y), color))
    #         self._server.send_to_all_clients(ants)

    def start(self):
        """
        Fonction principale qui lance la simulation
        et calcule le déplacement de chaque fourmi
        """
        all_ants = NestServer.get_all_ants_as_list()
        number_of_ants = len(all_ants)
        # number_of_ants = len(self._ants)

        # self._ants = AntServer.init_ants(
        #     self.objects["nest"], ants_per_nest=20)
        self._server.send_to_all_clients(["ants", *(a.to_tuple() for a in all_ants)])

        # liste [delta_x, delta_y] (et parfois une couleur) pour bouger les fourmis
        move_ants = ["move_ants"] + number_of_ants * [None]

        def simulate_ants_in_thread(start, number):
            end = start + number
            if end > number_of_ants:
                end = number_of_ants

            for i in range(start, end):
                ant = all_ants[i]
                ant_index = i + 1  # indice dans move_ants

                x, y = ant.coords_centre  # position actuelle
                if ant.has_resource:
                    pheromones.append((x, y))  # l'ordre n'est pas important
                    # S'il y a un mur mais que la fourmi porte une ressource,
                    if self._is_wall(x, y):
                        # Si elle n'a pas fait trop d'essais
                        if ant.tries < ant.MAX_TRIES:
                            # Elle contourne le mur par la gauche
                            ant.direction += 30
                            ant.tries += 1
                        # Sinon elle essaie par la droite
                        else:
                            ant.direction -= 30
                    else:
                        ant.go_to_nest()
                    ant.lay_pheromone()
                # Si elle n'en a pas mais qu'il y a un mur, elle fait demi-tour
                elif self._is_wall(x, y):
                    if ant.endurance > 0:
                        ant.direction += 180
                    else:
                        # Si elle est fatiguee, elle contourne par la gauche
                        ant.direction += 30
                # Sinon elle n'a rien trouve
                elif ant.endurance > 0:
                    ant.seek_resource()
                    ant.endurance -= 1
                else:
                    ant.go_to_nest()

                ant.move()
                new_x, new_y = ant.coords_centre  # on sait que la position a change
                delta_x = new_x - x  # deplacement relatif
                delta_y = new_y - y
                # les fourmis sont toujours dans le meme ordre
                move_ants[ant_index] = [delta_x, delta_y]

                spotted_resource = ResourceServer.get_resource(new_x, new_y)
                # Si la fourmi touche une ressource
                if (not ant.has_resource) and (
                        spotted_resource is not None) and (
                        spotted_resource.size != 0):
                        # Une fourmi a touche une ressource
                    spotted_resource.shrink_resource()  # On reduit la ressource
                    # self.objects["resource"][index_resource] = (resource[0], resource[1] - 1)
                    # self.objects["resource"][index_resource][1] -= 1 # On diminue la taille de la ressource
                    ant.has_resource = True
                    # On donne aux clients l'index de la ressource touchee
                    if not self._first_ant:
                        move_ants[ant_index].append(spotted_resource.index)
                    else:
                        move_ants[ant_index].append(
                            [spotted_resource.index, "first_ant"])
                        self._first_ant = False
                        print("First ant to find resource was color:", ant.color)
                # Si la fourmi est sur son nid
                elif ant.coords_centre == ant.nest:
                    ant.has_resource = False
                    ant.endurance = AntServer.MAX_ENDURANCE
                    ant.tries = 0
                    # Reprendre la couleur d'origine
                    move_ants[ant_index].append("base")
                elif ant.endurance <= 0:
                    move_ants[ant_index].append("black")

        step = 20

        tracemalloc.start()
        TRACEMALLOC_CPT = 0
        TRACEMALLOC_TRIGGER1 = 150
        TRACEMALLOC_TRIGGER2 = 350
        snapshot1 = None
        snapshot2 = None
        top_stats = None

        while self._server.online:

            TRACEMALLOC_CPT += 1
            if TRACEMALLOC_CPT == TRACEMALLOC_TRIGGER1:
                snapshot1 = tracemalloc.take_snapshot()
            elif TRACEMALLOC_CPT == TRACEMALLOC_TRIGGER2:
                snapshot2 = tracemalloc.take_snapshot()
                top_stats = snapshot2.compare_to(snapshot1, "lineno")
                print("[[[[[[[[[[ TOP DIFFERENCES ]]]]]]]]]]")
                for stat in top_stats[:20]:
                    print(stat)

            # temps_sim = perf_counter()

            # liste de coordonnees (x, y), qu'on remet a zero
            pheromones = ["pheromones"]

            temps_ants = perf_counter()

            curr_thread = None
            for i in range(0, number_of_ants, step):
                curr_thread = threading.Thread(
                    target=simulate_ants_in_thread, args=(i, step), daemon=True)
                curr_thread.start()
            if curr_thread is not None:
                # On donne 1s maximum au dernier pour finir
                curr_thread.join(1)

            # il y a bien un ralentissement dans le comportement des fourmis
            print(f"temps_ants : {perf_counter() - temps_ants}")

            # S'il y a de nouvelles pheromones
            if len(pheromones) > 1:
                # On envoie les mouvements des fourmis + les pheromones pour eviter de la latence
                self._server.send_to_all_clients([move_ants, pheromones])

            # Sinon on n'envoie que les positions
            else:
                self._server.send_to_all_clients(move_ants)

            # print("temps_sim :", perf_counter() - temps_sim)

            sleep(self._sleep_time)  # ajout d'une latence
        print("End of the simulation.")
        # faudra afficher le vainqueur ou quoi par là

    def _is_wall(self, x, y):
        """ Retourne True s'il y a un mur à cette position, False sinon """
        return (x, y) in self.objects["wall"]
        # Si on fait un dico associant les sizes avec un set de murs qui font cette size, on peut boucler dessus
        # if "wall" in self.objects:
        #     return (x, y) in self.objects["wall"]
        # return False
        # for wall_size in self.objects["wall"]:
        #   if (x, y) in self.objects["wall"][wall_size]:
        #       return True
        # return False

    # def _is_resource(self, x, y):
    #     """ Retourne l'indice de la ressource à cette position ou None s'il n'y en a pas """
    #     if "resource" in self.objects:
    #         for i, resource in enumerate(self.objects["resource"]):
    #             coords_resource, size = resource[0], resource[1]
    #             offset = size // 2 + 1  # +1 pour l'outline
    #             if (coords_resource[0] - offset <= x <= coords_resource[0] + offset) and (
    #                 coords_resource[1] - offset <= y <= coords_resource[1] + offset) and (
    #                 resource[1] != 0):
    #                     return i  # On retourne l'index de la ressource
    #     return None

    def _is_good_spot(self, x, y, size):
        """
        Retourne True si les coordonnées données en paramètre sont
        disponibles en fonction de la taille donnée, False sinon
        """
        def squared_distance(p1, p2):
            """
            Retourne la distance au carré entre
            les deux points (couples (x, y)).
            """
            return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

        for str_type in self.objects:
            # idée : mettre dans des threads pour calculer les distances au carré parallèlement


            # S'il y a au moins un objet
            if len(self.objects[str_type]):

                # # Generator contenant des tuples de coords
                # all_coords = (obj.coords_centre
                #               for obj in self.objects[str_type])

                """
                Nouvelle idée de logique :
                    dico { distance: objet }
                """

                # TEMPORAIRE, AVANT DE FAIRE UN WALLSERVER :
                if str_type != "wall":
                    # Associe une distance a un objet
                    dist_to_obj = {squared_distance(
                        (x, y), obj.coords_centre): obj for obj in self.objects[str_type]}
                else:
                    dist_to_obj = {squared_distance(
                        (x, y), obj[0]): obj for obj in self.objects[str_type]}
               

                print(f"{dist_to_obj=}")

                min_dist_squared = min(dist_to_obj)
                closest_obj = dist_to_obj[min_dist_squared]

                min_dist = sqrt(min_dist_squared)
                # print(f"{min_dist=}")
                if str_type != "wall":
                    size_closest_obj = closest_obj.size
                    print(f"{size_closest_obj=}")
                    # size_closest_obj = self.objects[str_type][min_dist_index][1]
                else:
                    # IL FAUT POUVOIR RETROUVER LA SIZE ASSOCIÉE AU MUR DE DISTANCE MINIMALE
                    # => on pourra le faire quand on aura des objets WallServer
                    size_closest_obj = 10
                if min_dist <= size_closest_obj:
                    return False
        return True

    def check_all_coords(self, coords_list, size):
        """Vérifie que toutes les coordonnées de la liste sont valides"""
        for i in range(0, len(coords_list) - 1, 2):
            if not self._is_good_spot(coords_list[i], coords_list[i + 1], size):
                return False
        return True

    def add_to_objects(self, str_type, coords, size, width, color):
        """Ajoute une entrée au dictionnaire d'objets de la simulation"""
        # Note : Pour les objets 'wall', les coordonnees sont une liste de couples
        # Si c'est le premier objet de ce type que l'on voit, on init
        if size is None:
            size = width

        # Impossible d'avoir le meme algorithme pour les murs : les coordonnees sont de formes differentes
        # '''
        if str_type == "wall":
            # Generator de couple ((x, y), size)
            self.objects[str_type].update(
                (((coords[i], coords[i + 1]), size) for i in range(0, len(coords), 2)))
            '''
            # On parcourt les coordonnees deux a deux
            for i in range(0, len(coords), 2):
                # On remplit toutes les cases alentour
                x, y = coords[i], coords[i+1]
                for j in range(1, size // 2):
                    # peut-être mettre +1 (mais je crois que non)
                    self.objects["wall"].update(
                        {(x - j, y - j),
                         (x - j, y),
                         (x - j, y + j),
                         (x, y - j),
                         (x, y),
                         (x, y + j),
                         (x + j, y - j),
                         (x + j, y),
                         (x + j, y + j)})
            '''
        elif str_type == "resource":
            self.objects[str_type].add(
                ResourceServer(coords, size, width, color))
        elif str_type == "nest":
            self.objects[str_type].add(NestServer(coords, size, width, color))
        else:
            print(f"[Erreur] le type '{str_type}' n'existe pas")
            raise TypeError
            # Dans tous les cas, on ajoute les nouvelles coords, taille et couleur
            # self.objects[str_type].append((coords, size, width, color))
