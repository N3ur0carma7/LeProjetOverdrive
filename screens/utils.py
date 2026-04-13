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

def joueur_a_portee(case, player, TAILLE_CASE, distance_max=2):
    joueur_case_x = int(player.pos[0] // TAILLE_CASE)
    joueur_case_y = int(player.pos[1] // TAILLE_CASE)
    dx = abs(joueur_case_x - case[0])
    dy = abs(joueur_case_y - case[1])
    return dx <= distance_max and dy <= distance_max

def dessiner_grille(surface, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, herbe, TAILLE_CASE):
    largeur_vue = dims[0] / zoom
    hauteur_vue = (dims[1] - HAUTEUR_BARRE) / zoom

    debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
    debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

    for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
        for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
            surface.blit(herbe, (x - camera_x, y - camera_y))

def dessiner_grille_overlay(surface, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, TAILLE_CASE):
    couleur_grille = (20, 80, 20)
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