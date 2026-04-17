import pygame
from core.Class.skill_levels import get_max_level

class Batiment:
    TYPE_RESIDENTIEL = "residentiel"
    TYPE_GENERATEUR  = "generateur"
    TYPE_MINE        = "mine"
    TYPE_FARM        = "farm"
    DATA = {
        TYPE_RESIDENTIEL: {
            1: {"population": 1, "cout": 125},
            2: {"population": 3, "cout": 250},
            3: {"population": 5, "cout": 750},
        },
        TYPE_GENERATEUR: {
            1: {"vapeur": 30,  "cout": 200},
            2: {"vapeur": 60,  "cout": 500},
            3: {"vapeur": 120, "cout": 1000},
        },
        TYPE_MINE: {
            1: {"argent": 30,  "cout": 250},
            2: {"argent": 60,  "cout": 600},
            3: {"argent": 120, "cout": 1200},
        },
        TYPE_FARM: {
            1: {"nourriture": 30,  "cout": 150},
            2: {"nourriture": 60,  "cout": 400},
            3: {"nourriture": 120, "cout": 800},
        },
    }

    # Footprint en "petites cases" (style COC) : 3x3 par défaut
    DEFAULT_FOOTPRINT = 3

    def __init__(self, type_batiment, x, y):
        if type_batiment not in Batiment.DATA:
            raise ValueError("Type de batiment invalide")
        self.type = type_batiment
        self.niveau = 1
        self.x = x
        self.y = y
        self.largeur = Batiment.DEFAULT_FOOTPRINT
        self.hauteur = Batiment.DEFAULT_FOOTPRINT

    def get_stats(self):
        return Batiment.DATA[self.type][self.niveau]

    def get_rect_pixel(self, TAILLE_CASE):
        return pygame.Rect(
            self.x * TAILLE_CASE,
            self.y * TAILLE_CASE,
            self.largeur * TAILLE_CASE,
            self.hauteur * TAILLE_CASE
        )

    def get_production(self):
        stats = self.get_stats()
        for key in ("vapeur", "argent", "nourriture", "production"):
            if key in stats:
                return stats[key]
        return 0

    def get_production_type(self):
        stats = self.get_stats()
        for key in ("vapeur", "argent", "nourriture"):
            if key in stats:
                return key
        return None

    def get_population(self):
        stats = self.get_stats()
        return stats.get("population", 0)

    def get_upgrade_cost(self):
        """Returns the cost to reach the next level, or None if at cap or max."""
        if self.niveau >= 3:
            return None
        next_level = self.niveau + 1
        cap = get_max_level(self.type)
        if next_level > cap:
            return None
        return Batiment.DATA[self.type][next_level]["cout"]

    def upgrade(self):
        """Upgrade by one level, respecting the skill-tree cap."""
        if self.niveau >= 3:
            return
        next_level = self.niveau + 1
        cap = get_max_level(self.type)
        if next_level <= cap:
            self.niveau += 1

    def est_max_level(self):
        """True if no more upgrades are available."""
        if self.niveau >= 3:
            return True
        cap = get_max_level(self.type)
        return self.niveau >= cap

    def collision(self, autre):
        return not (
            self.x + self.largeur < autre.x or
            self.x > autre.x + autre.largeur or
            self.y + self.hauteur < autre.y or
            self.y > autre.y + autre.hauteur
        )

    def __str__(self):
        return f"{self.type} (niveau {self.niveau})"

    # pour convertir pour le serveur
    # PAS TOUCHE !!!
    # SINON AU BUCHER !!!!
    def to_dict(self):
        return {
            "type": self.type,
            "niveau": self.niveau,
            "x": self.x,
            "y": self.y,
            "largeur": self.largeur,
            "hauteur": self.hauteur,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["type"], d["x"], d["y"])
        obj.niveau = d.get("niveau", 1)
        # Normalisation : on force le footprint "grille fine" pour éviter
        # les superpositions/collisions incohérentes avec d'anciennes saves.
        obj.largeur = Batiment.DEFAULT_FOOTPRINT
        obj.hauteur = Batiment.DEFAULT_FOOTPRINT
        return obj
