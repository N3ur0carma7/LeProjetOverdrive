import pygame
import math

def collision(batiments, nouveau):
    for b in batiments:
        if (
                nouveau.x < b.x + b.largeur and
                nouveau.x + nouveau.largeur > b.x and
                nouveau.y < b.y + b.hauteur and
                nouveau.y + nouveau.hauteur > b.y
        ):
            return True
    return False

def calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE, slide_offset=0):
    """
    slide_offset : décalage vertical vers le bas (0 = visible, HAUTEUR_BARRE = caché).
    """
    rects = []
    marge = 20
    for i in range(4):
        rect = pygame.Rect(
            marge + i * (TAILLE_ICONE + marge),
            dims[1] - HAUTEUR_BARRE + (HAUTEUR_BARRE - TAILLE_ICONE) // 2 + slide_offset,
            TAILLE_ICONE,
            TAILLE_ICONE
        )
        rects.append(rect)
    return rects

def souris_vers_case(pos, camera_x, camera_y, zoom, TAILLE_CASE):
    sx, sy = pos
    mx = camera_x + sx / zoom
    my = camera_y + sy / zoom
    return int(mx // TAILLE_CASE), int(my // TAILLE_CASE)

def joueur_a_portee(case, player, TAILLE_CASE, distance_max=2, largeur=1, hauteur=1):
    """
    case: (x, y) en coordonnées grille.
    largeur/hauteur: footprint de la cible en cases (permet 3x3, etc.).
    Vérifie la distance jusqu'à la case la plus proche dans le rectangle cible.
    """
    joueur_case_x = int(player.pos[0] // TAILLE_CASE)
    joueur_case_y = int(player.pos[1] // TAILLE_CASE)

    x0, y0 = case
    x1 = x0 + max(1, int(largeur)) - 1
    y1 = y0 + max(1, int(hauteur)) - 1

    nearest_x = min(max(joueur_case_x, x0), x1)
    nearest_y = min(max(joueur_case_y, y0), y1)

    dx = abs(joueur_case_x - nearest_x)
    dy = abs(joueur_case_y - nearest_y)
    return dx <= distance_max and dy <= distance_max

def dessiner_grille(surface, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, herbe, TAILLE_CASE):
    # Sol "steampunk" : couleur unie (pas d'image de fond)
    # (équivalent visuel à l'ancien remplissage case-par-case, mais beaucoup plus rapide)
    surface.fill((58, 44, 32))

def dessiner_grille_overlay(surface, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, TAILLE_CASE):
    # Ligne de grille plus "cuivre/bronze"
    couleur_grille = (92, 72, 44)
    epaisseur = 1 if zoom < 1.0 else 2

    debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
    debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE
    largeur_vue = dims[0] / zoom
    hauteur_vue = (dims[1] - HAUTEUR_BARRE) / zoom

    x_fin = debut_x + int(largeur_vue) + TAILLE_CASE
    y_fin = debut_y + int(hauteur_vue) + TAILLE_CASE

    for x in range(debut_x, x_fin + 1, TAILLE_CASE):
        screen_x = int((x - camera_x) * zoom)
        pygame.draw.line(surface, couleur_grille, (screen_x, 0), (screen_x, dims[1] - HAUTEUR_BARRE), epaisseur)

    for y in range(debut_y, y_fin + 1, TAILLE_CASE):
        screen_y = int((y - camera_y) * zoom)
        pygame.draw.line(surface, couleur_grille, (0, screen_y), (dims[0], screen_y), epaisseur)

def dessiner_grille_overlay_ecran(ecran, camera_x, camera_y, dims, hauteur_ui, zoom, TAILLE_CASE):
    """
    Dessine la grille directement en pixels écran (après scaling du monde).
    Ça évite les artefacts quand on scale une grille fine à des zooms non entiers.
    hauteur_ui: hauteur (en px écran) occupée par l'UI en bas (on ne dessine pas dessus).
    """
    couleur_grille = (150, 120, 84)
    epaisseur = 1

    w, h = int(dims[0]), int(dims[1])
    h_monde = max(0, h - int(hauteur_ui))
    if h_monde <= 0:
        return

    # Espacement en pixels écran entre deux lignes de grille.
    step = TAILLE_CASE * zoom
    if step <= 2:
        # Si trop serré, la grille devient du bruit visuel.
        return

    # Position de la première ligne en pixels écran (offset de caméra), puis itération.
    # On utilise round() pour "snap" au pixel et éviter le scintillement.
    offset_x = (-camera_x * zoom) % step
    offset_y = (-camera_y * zoom) % step

    x = offset_x
    while x <= w:
        sx = int(round(x))
        pygame.draw.line(ecran, couleur_grille, (sx, 0), (sx, h_monde), epaisseur)
        x += step

    y = offset_y
    while y <= h_monde:
        sy = int(round(y))
        pygame.draw.line(ecran, couleur_grille, (0, sy), (w, sy), epaisseur)
        y += step


def dessiner_grille_overlay_monde(surface_monde, camera_x, camera_y, TAILLE_CASE):
    """
    Variante "monde" (sans zoom) : dessine la grille directement sur surface_monde
    pour qu'elle passe derrière le joueur / les sprites.
    """
    # Grille simple (sans lignes "majeures")
    couleur_grille = (150, 120, 84)
    epaisseur = 1

    largeur_vue, hauteur_vue = surface_monde.get_size()
    debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
    debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

    x_fin = debut_x + int(largeur_vue) + TAILLE_CASE
    y_fin = debut_y + int(hauteur_vue) + TAILLE_CASE

    for x in range(debut_x, x_fin + 1, TAILLE_CASE):
        sx = int(x - camera_x)
        pygame.draw.line(surface_monde, couleur_grille, (sx, 0), (sx, hauteur_vue), epaisseur)

    for y in range(debut_y, y_fin + 1, TAILLE_CASE):
        sy = int(y - camera_y)
        pygame.draw.line(surface_monde, couleur_grille, (0, sy), (largeur_vue, sy), epaisseur)