import math
import pygame
from core.Class.batiments import Batiment  # Ajustez le chemin selon votre structure


class Tourelle(Batiment):
    def __init__(self, x, y, type_batiment="tourelle"):
        super().__init__(x, y, type_batiment)
        self.portee = 200  # Range
        self.degats = 15  # Degats
        self.cadence_tir = 1.0  # cooldown
        self.dernier_tir = 0  # dernier tir

    def update_attaque(self, liste_ennemis):

        temps_actuel = pygame.time.get_ticks()

        if temps_actuel - self.dernier_tir < self.cadence_tir * 1000:
            return

        cible_la_plus_proche = None
        distance_min = self.portee


        taille_case = 64
        tourelle_x = self.x * taille_case + taille_case // 2
        tourelle_y = self.y * taille_case + taille_case // 2

        for ennemi in liste_ennemis:

            dx = ennemi.x - tourelle_x
            dy = ennemi.y - tourelle_y
            distance = math.hypot(dx, dy)

            if distance < distance_min:
                distance_min = distance
                cible_la_plus_proche = ennemi

        if cible_la_plus_proche is not None:

            if hasattr(cible_la_plus_proche, "recevoir_degats"):
                cible_la_plus_proche.recevoir_degats(self.degats)
            else:
                cible_la_plus_proche.pv -= self.degats


            self.dernier_tir = temps_actuel

