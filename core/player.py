import math
import random
import pygame
import heapq

from discord.ext.commands.parameters import empty


class Player:
    def __init__(self):
        self.hp_max = 100
        self.hp = 100
        self.crit_chance = 20
        self.crit_damage = 10
        self.raw_damage = 1
        self.defense = 0
        self.health_regen = 1
        self.money = 0


        self.pos = (0, 0)
        self.path = []

        self.speed = 10
        self.size = 40
    def hurt(self, raw_damage: int) -> float | None:
        """
        :param raw_damage: dégats du monstre attaquant le joueur
        :return: nombre de dégats pris par le joueur ou None si le joueur est mort
        """
        damage = raw_damage / (self.defense * 0.05 + 1)
        self.hp -= damage
        if self.hp <= 0:
            return None
        else:
            return damage

    def heuristique(self, start: tuple, dest: tuple):
        """
        :param start: coodonnées de départ
        :param dest: coordonnées de destination
        :return: Entier représentant la distance Manhattan du départ jusqu'à la destination
        """
        return abs(start[0] - dest[0]) + abs(start[1] - dest[1])

    def reconstruire_path(self, came_from, current):

        chemin = [current]

        while current in came_from:
            current = came_from[current]
            chemin.append(current)
        chemin.reverse()
        return chemin

    def a_star(self, dest: tuple, batiments: list, taille_case: int):
        """
        :param dest: coordonnées de destination
        :param batiments: liste de coordonnées des batiments sur la carte
        :return: True si il existe un chemin allant de la position du joueur à la destination, False sinon
        """
        start = (
            int(self.pos[0] // taille_case),
            int(self.pos[1] // taille_case)
        )
        open_set = [start]
        closed_set = set()

        came_from = dict()
        g_score = dict()
        f_score = dict()

        g_score[start] = 0
        f_score[start] = self.heuristique(start, dest)

        while open_set:
            current = min(open_set, key=lambda case: f_score.get(case, float('inf')))

            if current == dest:
                self.path = self.reconstruire_path(came_from, current)
                return True

            open_set.remove(current)
            closed_set.add(current)

            voisins = [
                (current[0] + 1, current[1]),
                (current[0], current[1] + 1),
                (current[0] - 1, current[1]),
                (current[0], current[1] - 1),
            ]

            for voisin in voisins:
                if voisin in batiments:
                    continue

                if voisin in closed_set:
                    continue

                tentative_g = g_score[current] + 1
                if voisin not in open_set:
                    open_set.append(voisin)
                elif tentative_g >= g_score[voisin]:
                    continue

                came_from[voisin] = current

                g_score[voisin] = tentative_g
                f_score[voisin] = g_score[voisin] + self.heuristique(voisin, dest)
        return False

    def update(self, taille_case: int):
        if not self.path:
            return

        next_case = self.path[0]

        target_x = next_case[0] * taille_case + taille_case / 2
        target_y = next_case[1] * taille_case + taille_case / 2

        dx = target_x - self.pos[0]
        dy = target_y - self.pos[1]

        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.pos = (target_x, target_y)

            self.path.pop(0)

            return

        dx /= distance
        dy /= distance


        self.pos = (self.pos[0] + dx * self.speed, self.pos[1] + dy * self.speed)


    def draw_player(self, surface, camera_x, camera_y) -> bool:
        """
        :param surface: la map
        :param camera_x: la position x de la caméra
        :param camera_y: la position y de la caméra
        :return: True si le joueur s'est correctement déplacé, False sinon.
        """
        x = self.pos[0] - camera_x
        y = self.pos[1] - camera_y

        pygame.draw.circle(surface, (220, 50, 50), (int(x), int(y)), self.size)
        return True
