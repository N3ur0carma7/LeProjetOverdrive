"""
Système de messages flottants.
Utilisation :
    from screens.floating_messages import FloatingMessageManager
    msg = FloatingMessageManager()
    msg.add("Trop loin !", x, y)   # message rouge par défaut
    msg.add("OK !", x, y, color=(80, 255, 80))
    # dans la boucle :
    msg.update(dt)
    msg.draw(ecran)
"""

import pygame
import math

_FONT = None
_FONT_SMALL = None

def _get_fonts():
    global _FONT, _FONT_SMALL
    if _FONT is None:
        try:
            _FONT       = pygame.font.Font("assets/fonts/Minecraft.ttf", 15)
            _FONT_SMALL = pygame.font.Font("assets/fonts/Minecraft.ttf", 12)
        except Exception:
            _FONT       = pygame.font.SysFont("arial", 15, bold=True)
            _FONT_SMALL = pygame.font.SysFont("arial", 12)
    return _FONT, _FONT_SMALL


class _FloatingMsg:
    DURATION = 1.8
    RISE     = 60  #pixel par seconde vers le haut

    def __init__(self, text: str, x: int, y: int, color=(230, 60, 60), small=False):
        self.text     = text
        self.x        = float(x)
        self.y        = float(y)
        self.color    = color
        self.small    = small
        self.timer    = 0.0
        self.alive    = True

    def update(self, dt: float):
        self.timer += dt
        self.y     -= self.RISE * dt
        if self.timer >= self.DURATION:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        font, font_small = _get_fonts()
        f = font_small if self.small else font

        # opacité
        ratio = self.timer / self.DURATION
        if ratio < 0.15:
            alpha = int(255 * (ratio / 0.15))
        elif ratio > 0.6:
            alpha = int(255 * (1.0 - (ratio - 0.6) / 0.4))
        else:
            alpha = 255

        # légère oscillation horizontale
        ox = int(math.sin(self.timer * 6) * 2)

        txt_surf = f.render(self.text, True, self.color)

        # ombre
        shadow = f.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(int(alpha * 0.6))
        txt_surf.set_alpha(alpha)

        cx = int(self.x) - txt_surf.get_width() // 2
        cy = int(self.y) - txt_surf.get_height() // 2

        surface.blit(shadow, (cx + ox + 1, cy + 1))
        surface.blit(txt_surf, (cx + ox, cy))


class FloatingMessageManager:
    """Gère une liste de messages flottants."""

    # Couleurs prédéfinies pour les cas récurrents
    COLOR_ERROR   = (230,  60,  60)   # rouge  — action impossible
    COLOR_WARNING = (255, 165,   0)   # orange — ressources insuffisantes
    COLOR_INFO    = (100, 200, 255)   # bleu   — info neutre
    COLOR_SUCCESS = ( 80, 220,  80)   # vert   — succès

    def __init__(self):
        self._messages: list[_FloatingMsg] = []

    def add(self, text: str, x: int, y: int,
            color=None, small: bool = False):
        """Ajoute un message flottant à la position écran (x, y)."""
        if color is None:
            color = self.COLOR_ERROR
        # Décaler légèrement si plusieurs messages sur le même spot
        offset = len(self._messages) * 6
        self._messages.append(_FloatingMsg(text, x, y - offset, color, small))

    def error(self, text: str, x: int, y: int):
        self.add(text, x, y, self.COLOR_ERROR)

    def warning(self, text: str, x: int, y: int):
        self.add(text, x, y, self.COLOR_WARNING)

    def info(self, text: str, x: int, y: int):
        self.add(text, x, y, self.COLOR_INFO)

    def success(self, text: str, x: int, y: int):
        self.add(text, x, y, self.COLOR_SUCCESS)

    def update(self, dt: float):
        for m in self._messages:
            m.update(dt)
        self._messages = [m for m in self._messages if m.alive]

    def draw(self, surface: pygame.Surface):
        for m in self._messages:
            m.draw(surface)