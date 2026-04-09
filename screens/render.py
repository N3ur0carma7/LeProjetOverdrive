import pygame
import math
from screens.utils import collision, souris_vers_case, joueur_a_portee

def dessiner_monde(surface_monde, batiments, images_batiments, camera_x, camera_y, TAILLE_CASE, batiment_selectionne, TYPES_BATIMENTS, player, npcs, image_pnj, dt, zoom):
    from screens.utils import collision, souris_vers_case, joueur_a_portee
    from core.Class.batiments import Batiment

    for B in batiments:
        image = images_batiments[B.type][B.niveau]
        x = B.x * TAILLE_CASE - camera_x + (TAILLE_CASE - image.get_width()) // 2
        y = B.y * TAILLE_CASE - camera_y + (TAILLE_CASE - image.get_height()) // 2
        surface_monde.blit(image, (x, y))

    # fantome
    if batiment_selectionne is not None:
        sx, sy = pygame.mouse.get_pos()
        case = souris_vers_case((sx, sy), camera_x, camera_y, zoom, TAILLE_CASE)
        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
        test_batiment = Batiment(type_batiment, case[0], case[1])
        image = images_batiments[type_batiment][1]
        image_fantome = image.copy()
        if collision(batiments, test_batiment):
            image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        elif not joueur_a_portee(case, player, TAILLE_CASE):
            image_fantome.fill((255, 140, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

        x = case[0] * TAILLE_CASE - camera_x + (TAILLE_CASE - image.get_width()) // 2
        y = case[1] * TAILLE_CASE - camera_y + (TAILLE_CASE - image.get_height()) // 2

        surface_monde.blit(image_fantome, (x, y))

    player.draw_player(surface_monde, camera_x, camera_y)

    for npc in npcs:
        npc.update(dt)
        nx = int(npc.monde_x - camera_x)
        ny = int(npc.monde_y - camera_y)
        sw, sh = surface_monde.get_size()
        if -80 < nx < sw + 80 and -80 < ny < sh + 80:
            npc.dessiner_monde(surface_monde, camera_x, camera_y, image_pnj)

def dessiner_hud(ecran, dims, HAUTEUR_BARRE, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS, TAILLE_ICONE, player, font_argent, hud_or_img, hud_food_img, hud_vapeur_img, save_done_img, save_done_timer):
    pygame.draw.rect(
        ecran,
        (40, 40, 40),
        (0, dims[1] - HAUTEUR_BARRE, dims[0], HAUTEUR_BARRE)
    )

    for i, rect in enumerate(rects_icones):
        couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
        pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

        type_actuel = TYPES_BATIMENTS[i]
        icone = pygame.transform.smoothscale(
            images_batiments[type_actuel][1], (TAILLE_ICONE, TAILLE_ICONE)
        )
        ecran.blit(icone, rect)

    # hud ressources
    hud_font = font_argent
    marge_hud = 2
    hud_y = marge_hud

    ressources_hud = [
        (str(player.money),  (255, 235,  80), hud_or_img),
        (str(player.food),   ( 255, 235,  80), hud_food_img),
        (str(player.vapeur), (255, 235, 80), hud_vapeur_img),
    ]

    for i, (valeur, couleur, img) in enumerate(ressources_hud):
        iw, ih = img.get_size()
        hud_x = dims[0] - marge_hud - (len(ressources_hud) - i) * (iw + marge_hud)
        ecran.blit(img, (hud_x, hud_y))
        texte = hud_font.render(valeur, True, couleur)
        tx = hud_x + (iw - texte.get_width()) // 2 - 13
        ty = hud_y + (ih - texte.get_height()) // 2 + 2
        ecran.blit(texte, (tx, ty))

    if save_done_timer > 0:
        img_w, img_h = save_done_img.get_size()
        x = 10
        y = 10
        ecran.blit(save_done_img, (x, y))