import threading
from time import sleep
from time import perf_counter # Pour le debug
from math import dist as distance

from .AntServer import AntServer
from .ResourceServer import ResourceServer
from .NestServer import NestServer
from .WallServer import WallServer


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

    __slots__ = ["objects", "_sleep_time", "_first_ant", "_server", "_timeline"]

    @property
    def sleep_time(self):
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, new_time):
        self._sleep_time = round(new_time, 3)

    def __init__(self, server):
        self._server = server

        self.objects = {
            "nest": set(),
            "resource": set(),
            "wall": set()
        }  # Dictionnaire de tous les objets
        self._timeline = []

        self._first_ant = True

        self._sleep_time = 0.05

    def start(self):
        """
        Fonction principale qui lance la simulation
        et calcule le déplacement de chaque fourmi
        """
        all_ants = self._get_all_ants_as_list()
        number_of_ants = len(all_ants)

        self._server.send_to_all_clients(["ants", *(a.to_tuple() for a in all_ants)])

        # liste [delta_x, delta_y] (et parfois une couleur) pour bouger les fourmis
        move_ants = ["move_ants"] + number_of_ants * [None]

        def simulate_ants_in_thread(start, number):
            end = min(start + number, number_of_ants)

            for i in range(start, end):
                ant = all_ants[i]
                ant_index = i + 1  # indice dans move_ants

                x, y = ant.coords_centre  # position actuelle
                if ant.has_resource:
                    pheromones.append((x, y))  # l'ordre n'est pas important
                    # S'il y a un mur mais que la fourmi porte une ressource
                    if self._get_wall(x, y) is not None:
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
                elif self._get_wall(x, y) is not None:
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

                spotted_resource = self._get_resource(new_x, new_y)
                # Si la fourmi touche une ressource
                if (not ant.has_resource) and (
                    spotted_resource is not None) and (
                    spotted_resource.size != 0):
                        # Une fourmi a touche une ressource
                        spotted_resource.shrink_resource() # On reduit la ressource
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

        # step = 20
        step = 40 # test pour voir la diff de perf

        while self._server.online:

            # temps_sim = perf_counter()

            # liste de coordonnees (x, y), qu'on remet a zero
            pheromones = ["pheromones"]

            # temps_ants = perf_counter() # assez rapide

            curr_thread = None
            for i in range(0, number_of_ants, step):
                curr_thread = threading.Thread(
                    target=simulate_ants_in_thread, args=(i, step), daemon=True)
                curr_thread.start()
            if curr_thread is not None:
                # On donne un timeout maximum au dernier pour finir
                curr_thread.join(0.5)
                # curr_thread.join(1)

            # il y a bien un ralentissement dans le comportement des fourmis
            # print(f"temps_ants : {perf_counter() - temps_ants}")

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
        # TODO: afficher la couleur vainqueure a la fin

    # def _is_wall(self, x, y):
    #     """ Retourne True s'il y a un mur à cette position, False sinon """
    #     return (x, y) in self.objects["wall"]
    #     # Si on fait un dico associant les sizes avec un set de murs qui font cette size, on peut boucler dessus
    #     # if "wall" in self.objects:
    #     #     return (x, y) in self.objects["wall"]
    #     # return False
    #     # for wall_size in self.objects["wall"]:
    #     #   if (x, y) in self.objects["wall"][wall_size]:
    #     #       return True
    #     # return False

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
        # Pour chaque liste d'objets
        for objects in self.objects.values():
            # idée : mettre dans des threads pour calculer les distances parallèlement

            # S'il y a au moins un objet
            if len(objects) > 0:
                # On associe une distance au carre a un objet
                all_distances = {distance((x, y), obj.coords_centre): obj for obj in objects}

                min_dist = min(all_distances)
                closest_obj = all_distances[min_dist]

                size_closest_obj = closest_obj.size

                if min_dist <= size_closest_obj:
                    return False
        return True

    def check_all_coords(self, coords_list, size):
        """Vérifie que toutes les coordonnées de la liste sont valides"""
        for i in range(0, len(coords_list), 2):
            if not self._is_good_spot(coords_list[i], coords_list[i+1], size):
                return False
        return True

    def add_to_objects(self, str_type, coords, size, color):
        """Ajoute une entrée au dictionnaire d'objets de la simulation"""
        # Note : Pour les objets 'wall', les coordonnees sont une liste de couples
        new_obj = None

        if str_type == "wall":
            new_obj = []
            for i in range(0, len(coords), 2):
                couple = coords[i], coords[i+1]
                new_obj.append(WallServer(couple, size, color))
            self.objects[str_type].update(new_obj)
        elif str_type == "resource":
            new_obj = ResourceServer(coords, size, color)
            self.objects[str_type].add(new_obj)
        elif str_type == "nest":
            new_obj = NestServer(coords, size, color)
            self.objects[str_type].add(new_obj)
        else:
            raise TypeError(f"[Error] type '{str_type}' does not exist")


        self._timeline.append(new_obj)

    def _get_all_ants_as_list(self):
        """
        Retourne la liste de toutes les fourmis
        (contenues dans les objets NestServer)
        """
        all_ants = []
        for nest in self.objects["nest"]:
            all_ants.extend(nest.ants)
        return all_ants

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

    def cancel_last_object(self):
        raise NotImplementedError("to do: handle walls in the timeline")
    #     if len(self._timeline):
    #         last_object = self._timeline.pop()

    #         object_type = last_object.__class__
    #         print(f"{object_type=}")
    #         if object_type is list:
    #             # On sait que c'est un mur, il faut supprimer tous les objets
    #             # présents dans la liste de l'ensemble WallServer.walls
    #             # (avec une différence ça peut être très facile)

    #         str_type = object_type.__name__[:last_object.__class__.__name__.index("Server")].lower()
    #         print(f"{str_type=}")

    #         objects_set = getattr(object_type, str_type + "s", None)
    #         print(f"{objects_set=}")

    #         objects_set.remove(last_object)

    #         self.objects[str_type].remove(last_object)