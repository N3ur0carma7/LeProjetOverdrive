import math
import pygame

# ---------------------------------------------------------------------------
# Spritesheets player
# Chaque frame fait 48px de large x 48px de haut.
# Les images sont des bandes horizontales de frames.
# ---------------------------------------------------------------------------

FRAME_W = 48   # largeur d'une frame
FRAME_H = 48   # hauteur d'une frame

# Nombre de frames par animation (width / 48)
ANIM_FRAMES = {
    "idle":         4,   # 192 / 48
    "run":          6,   # 288 / 48
    "hand_cannon":  6,   # 288 / 48
    "hit":          3,   # 144 / 48
    "death":        6,   # 288 / 48
}

# FPS par animation
ANIM_FPS = {
    "idle":        8,
    "run":        10,
    "hand_cannon": 12,
    "hit":         10,
    "death":        8,
}


class Player:
    _sheets: dict = {}   # {name: pygame.Surface}

    START_MONEY      = 1000
    START_FOOD       = 200
    START_VAPEUR     = 300
    START_CAP_MONEY  = 1000
    START_CAP_FOOD   = 200
    START_CAP_VAPEUR = 300

    @classmethod
    def load_sprites(cls):
        if cls._sheets:
            return
        for name in ANIM_FRAMES:
            cls._sheets[name] = pygame.image.load(
                f"assets/player_sprites/{name}.png"
            ).convert_alpha()

    # ------------------------------------------------------------------
    def __init__(self):
        self.hp_max       = 100
        self.hp           = 100
        self.crit_chance  = 20
        self.crit_damage  = 20
        self.raw_damage   = 10
        self.defense      = 0
        self.health_regen = 1
        self.money        = Player.START_MONEY
        self.food         = Player.START_FOOD
        self.vapeur       = Player.START_VAPEUR
        self.cap_money   = Player.START_CAP_MONEY
        self.cap_food     = Player.START_CAP_FOOD
        self.cap_vapeur   = Player.START_CAP_VAPEUR
        self.pos    = (0, 0)
        self.path   = []

        # Animation
        self.direction  = "right"   # "right" | "left"
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.is_moving  = False

        # Attaque
        self._attack_anim_active   = False
        self._attack_anim_timer    = 0.0
        self._attack_anim_duration = ANIM_FRAMES["hand_cannon"] / ANIM_FPS["hand_cannon"]

        self.sprite_height = 128

        self.speed = 420
        self.size  = 40

    def recalculate_storage(self, batiments_list):
        cap_or = Player.START_CAP_MONEY
        cap_food = Player.START_CAP_FOOD
        cap_vapeur = Player.START_CAP_VAPEUR
        for b in batiments_list:
            storage = b.get_storage()
            if storage > 0:
                rtype = b.type
                if rtype == Batiment.TYPE_STOCKAGE_OR:
                    cap_or = storage
                elif rtype == Batiment.TYPE_STOCKAGE_NOUR:
                    cap_food = storage
                elif rtype == Batiment.TYPE_STOCKAGE_VAPEUR:
                    cap_vapeur = storage
        self.cap_money = cap_or
        self.cap_food = cap_food
        self.cap_vapeur = cap_vapeur
    def trigger_attack_anim(self):
        """Declenche l'animation hand_cannon pour un cycle complet."""
        self._attack_anim_active = True
        self._attack_anim_timer  = self._attack_anim_duration
        self.anim_state  = "hand_cannon"
        self.anim_frame  = 0
        self.anim_timer  = 0.0

    def hurt(self, raw_damage: int):
        damage = raw_damage / (self.defense * 0.05 + 1)
        self.hp -= damage
        if self.hp <= 0:
            return None
        return damage

    # ------------------------------------------------------------------
    # Pathfinding
    # ------------------------------------------------------------------
    def heuristique(self, start, dest):
        dx = abs(start[0] - dest[0])
        dy = abs(start[1] - dest[1])
        d1 = 1.0
        d2 = math.sqrt(2)
        # Heuristique "octile" (8 directions) : admissible avec coûts 1 et sqrt(2)
        return d1 * (dx + dy) + (d2 - 2 * d1) * min(dx, dy)

    def reconstruire_path(self, came_from, current):
        chemin = [current]
        while current in came_from:
            current = came_from[current]
            chemin.append(current)
        chemin.reverse()
        return chemin

    def a_star(self, dest, taille_case):
        start = (int(self.pos[0] // taille_case), int(self.pos[1] // taille_case))
        open_set   = [start]
        closed_set = set()
        came_from  = {}
        g_score    = {start: 0}
        f_score    = {start: self.heuristique(start, dest)}

        while open_set:
            current = min(open_set, key=lambda c: f_score.get(c, float("inf")))
            if current == dest:
                self.path = self.reconstruire_path(came_from, current)
                return True
            open_set.remove(current)
            closed_set.add(current)
            for dx, dy in (
                (1, 0), (0, 1), (-1, 0), (0, -1),
                (1, 1), (-1, 1), (-1, -1), (1, -1),
            ):
                voisin = (current[0] + dx, current[1] + dy)
                if voisin in closed_set:
                    continue
                step_cost = math.sqrt(2) if (dx != 0 and dy != 0) else 1.0
                tentative_g = g_score[current] + step_cost
                if voisin not in open_set:
                    open_set.append(voisin)
                elif tentative_g >= g_score.get(voisin, float("inf")):
                    continue
                came_from[voisin] = current
                g_score[voisin]   = tentative_g
                f_score[voisin]   = tentative_g + self.heuristique(voisin, dest)
        return False

    # ------------------------------------------------------------------
    def update(self, taille_case, dt=1/60):
        if not self.path:
            self.is_moving = False
            return

        next_case = self.path[0]
        target_x  = next_case[0] * taille_case + taille_case / 2
        target_y  = next_case[1] * taille_case + taille_case / 2
        dx = target_x - self.pos[0]
        dy = target_y - self.pos[1]
        distance = math.hypot(dx, dy)

        if abs(dx) >= abs(dy):
            self.direction = "right" if dx > 0 else "left"

        self.is_moving = True
        step = self.speed * dt

        if distance < step:
            self.pos = (target_x, target_y)
            self.path.pop(0)
            if not self.path:
                self.is_moving = False
                self.anim_frame = 0
                self.anim_timer = 0.0
            return

        dx /= distance
        dy /= distance
        self.pos = (self.pos[0] + dx * step, self.pos[1] + dy * step)

    # ------------------------------------------------------------------
    def update_anim(self, dt):
        if self._attack_anim_active:
            self._attack_anim_timer -= dt
            if self._attack_anim_timer <= 0:
                self._attack_anim_active = False
                self.anim_state = "run" if self.is_moving else "idle"
                self.anim_frame = 0
                self.anim_timer = 0.0
            else:
                self._advance_frame("hand_cannon", dt)
            return

        self.anim_state = "run" if self.is_moving else "idle"
        self._advance_frame(self.anim_state, dt)

    def _advance_frame(self, state, dt):
        fps       = ANIM_FPS[state]
        nb_frames = ANIM_FRAMES[state]
        self.anim_timer += dt
        if self.anim_timer >= 1.0 / fps:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % nb_frames
        self.anim_state = state

    # ------------------------------------------------------------------
    def draw_player(self, surface, camera_x, camera_y):
        Player.load_sprites()

        sheet = Player._sheets[self.anim_state]
        frame = min(self.anim_frame, ANIM_FRAMES[self.anim_state] - 1)

        # Rect source : chaque frame fait FRAME_W x FRAME_H
        src_rect = pygame.Rect(frame * FRAME_W, 0, FRAME_W, FRAME_H)

        scale = self.sprite_height / FRAME_H
        dst_w = int(FRAME_W * scale)
        dst_h = self.sprite_height

        sub    = sheet.subsurface(src_rect)
        scaled = pygame.transform.scale(sub, (dst_w, dst_h))

        if self.direction == "left":
            scaled = pygame.transform.flip(scaled, True, False)

        draw_x = int(self.pos[0] - camera_x) - dst_w // 2
        draw_y = int(self.pos[1] - camera_y) - dst_h // 2

        surface.blit(scaled, (draw_x, draw_y))
        return True

    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            "hp_max": self.hp_max, "hp": self.hp,
            "crit_chance": self.crit_chance, "crit_damage": self.crit_damage,
            "raw_damage": self.raw_damage, "defense": self.defense,
            "health_regen": self.health_regen, "money": self.money,
            "food": self.food, "vapeur": self.vapeur,
            "cap_money": self.cap_money,
            "cap_food": self.cap_food,
            "cap_vapeur": self.cap_vapeur,
            "pos": self.pos, "path": self.path,
            "speed": self.speed, "size": self.size,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        obj.hp_max       = d.get("hp_max",       100)
        obj.hp           = d.get("hp",            100)
        obj.crit_chance  = d.get("crit_chance",    20)
        obj.crit_damage  = d.get("crit_damage",    10)
        obj.raw_damage   = d.get("raw_damage",      1)
        obj.defense      = d.get("defense",         0)
        obj.health_regen = d.get("health_regen",    1)
        obj.money        = d.get("money",        1000)
        obj.food         = d.get("food",            200)
        obj.vapeur       = d.get("vapeur",          300)
        obj.cap_money   = d.get("cap_money",       1000)
        obj.cap_food    = d.get("cap_food",          200)
        obj.cap_vapeur   = d.get("cap_vapeur",        300)
        obj.pos          = d.get("pos",          (0, 0))
        obj.path         = d.get("path",           [])
        obj.speed        = d.get("speed",         420)
        obj.size         = d.get("size",           40)
        return obj
