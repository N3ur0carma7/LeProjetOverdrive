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

def dessiner_hud(ecran, dims, HAUTEUR_BARRE, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS, TAILLE_ICONE, player, font_argent, hud_or_img, hud_food_img, hud_vapeur_img, save_done_img, save_done_timer, barre_ouverte=True, slide_offset=0, btn_batiments_rect=None, skill_btn_rect=None):
    if slide_offset < HAUTEUR_BARRE:
        barre_surf = pygame.Surface((dims[0], HAUTEUR_BARRE), pygame.SRCALPHA)
        barre_surf.fill((30, 30, 30, 210))
        ecran.blit(barre_surf, (0, dims[1] - HAUTEUR_BARRE + slide_offset))

    for i, rect in enumerate(rects_icones):
        couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
        pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

        type_actuel = TYPES_BATIMENTS[i]
        icone = pygame.transform.smoothscale(
            images_batiments[type_actuel][1], (TAILLE_ICONE, TAILLE_ICONE)
        )
        ecran.blit(icone, rect)

    # bouton toggle barre bâtiments
    BTN_SIZE = 80
    BTN_MARGE = 12
    btn_x = dims[0] - BTN_SIZE - BTN_MARGE
    btn_y = dims[1] - BTN_SIZE - BTN_MARGE

    # Fond du bouton : vert = ouvrir, orange = fermer
    btn_couleur = (160, 90, 30) if barre_ouverte else (40, 140, 40)
    pygame.draw.rect(ecran, btn_couleur, pygame.Rect(btn_x, btn_y, BTN_SIZE, BTN_SIZE), border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(btn_x, btn_y, BTN_SIZE, BTN_SIZE), 3, border_radius=10)

    btn_font = pygame.font.Font("assets/fonts/Minecraft.ttf", 11)
    label = "CLOSE" if barre_ouverte else "BUILD"
    lbl_surf = btn_font.render(label, True, (255, 255, 255))
    lbl_x = btn_x + (BTN_SIZE - lbl_surf.get_width()) // 2
    lbl_y = btn_y + (BTN_SIZE - lbl_surf.get_height()) // 2
    ecran.blit(lbl_surf, (lbl_x, lbl_y))

    if btn_batiments_rect is not None:
        btn_batiments_rect.update(btn_x, btn_y, BTN_SIZE, BTN_SIZE)

    # bouton skill tree
    skill_btn_x = btn_x - BTN_SIZE - BTN_MARGE
    skill_btn_y = btn_y
    skill_btn_couleur = (100, 100, 200)  # Bleu pour skills
    pygame.draw.rect(ecran, skill_btn_couleur, pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE), border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE), 3, border_radius=10)

    skill_label = "SKILLS"
    skill_lbl_surf = btn_font.render(skill_label, True, (255, 255, 255))
    skill_lbl_x = skill_btn_x + (BTN_SIZE - skill_lbl_surf.get_width()) // 2
    skill_lbl_y = skill_btn_y + (BTN_SIZE - skill_lbl_surf.get_height()) // 2
    ecran.blit(skill_lbl_surf, (skill_lbl_x, skill_lbl_y))

    if skill_btn_rect is not None:
        skill_btn_rect.update(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE)

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