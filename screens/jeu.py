import pygame
import math
import os
import threading
from multiplayer.serveur import *
import multiplayer.client as client_module
from multiplayer.client import send_list_client, receive_loop, send_batiment_client, send_liste_batiments_client, \
    send_liste_joueurs_client
from core.Class.batiments import *
import time
import random

stop_event = threading.Event()
batiments = []
players = []
indice = number_connected-1
def on_message_recu(TAILLE_CASE):
    global batiments, players
    while True:
        while len(players) < number_connected:
            new_player(TAILLE_CASE)
        if client_module.result is not None:
            message, type = client_module.result
            if type == "liste_batiments":
                batiments = message
            elif type == "liste_joueurs":
                players = message

def new_player(TAILLE_CASE):
    global players
    player = Player()

    # Spawn du joueur au milieu d'une case
    player.pos = (TAILLE_CASE / 2, TAILLE_CASE / 2)
    players.append(player)

from core.Class.player import Player
from core.Class.batiments import Batiment
from core.Class.npc import Npc
from core.saves import load_save

import core.sounds as sound
from screens.tutorial import run_tutorial
from screens.terminal import Terminal
from screens.utils import collision, calculer_rects_icones, souris_vers_case, joueur_a_portee, dessiner_grille, dessiner_grille_overlay
from screens.game_logic import synchroniser_npcs, calculer_production
from screens.render import dessiner_monde, dessiner_hud


from core.Class.player import Player
from core.Class.batiments import Batiment
from core.Class.npc import Npc
from core.saves import load_save
from screens.GUI.menu_amelioration import afficher_menu_amelioration
import core.sounds as sound
from screens.tutorial import run_tutorial
from screens.terminal import Terminal
#patch pour la farm et autres
def corriger_transparence(surface):
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))
            if color.a < 20:
                surface.set_at((x, y), (0, 0, 0, 0))
    return surface

def boucle_jeu(ecran, horloge, FPS, online: bool, dev_mode: bool = False):
    global batiments, indice
    global players
    HAUTEUR_BARRE = 100
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    dims = [LARGEUR_ECRAN, HAUTEUR_ECRAN]  # mutable pour mise a jour au resize



    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_CASE = herbe.get_width()

    images_batiments = {
        Batiment.TYPE_RESIDENTIEL: {
            1: pygame.image.load("assets/buildings/house_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/house_lvl2.png").convert_alpha(),  # Image niveau 2
            3: pygame.image.load("assets/buildings/house_lvl3.png").convert_alpha()  # Image niveau 3
        },
        Batiment.TYPE_GENERATEUR: {
            1: pygame.image.load("assets/buildings/generateur_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/generateur_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/generateur_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_MINE: {
            1: pygame.image.load("assets/buildings/mine_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/mine_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/mine_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_FARM: {
            1: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl1.png").convert_alpha()),
            2: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl2.png").convert_alpha()),
            3: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl3.png").convert_alpha())
        }
    }

    TYPES_BATIMENTS = [
        Batiment.TYPE_RESIDENTIEL,
        Batiment.TYPE_GENERATEUR,
        Batiment.TYPE_MINE,
        Batiment.TYPE_FARM,
    ]

    TAILLE_ICONE = 64
    batiments = []
    npcs = []


    image_pnj = pygame.image.load("assets/pnj.png").convert_alpha()
    font_argent = pygame.font.Font("assets/fonts/Minecraft.ttf", 15)
    hud_or_img     = pygame.image.load("assets/or.png").convert_alpha()
    hud_food_img   = pygame.image.load("assets/food.png").convert_alpha()
    hud_vapeur_img = pygame.image.load("assets/vapeur.png").convert_alpha()
    save_done_img = pygame.image.load("assets/save_done.png").convert_alpha()
    new_player(TAILLE_CASE)
    # Dictionnaire des bâtiments placés
    # clé : (x_case, y_case)
    # valeur : index du bâtiment
    is_new_game = not os.path.exists("save/save.json")
    if not dev_mode and os.path.exists("save/save.json"):
        if not load_save(batiments, players[indice]):
            print("ERREUR CRITIQUE: Lecture du fichier save/save.json")
            return False

    if dev_mode:
        players[indice].money = 5000
        players[indice].food = 5000
        players[indice].vapeur = 5000

    synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)

    # Camera et zoom
    camera_x = players[indice].pos[0] - dims[0] / 2
    camera_y = players[indice].pos[1] - (dims[1] - HAUTEUR_BARRE) / 2
    zoom = 1.0
    #tuto
    if is_new_game and not dev_mode:
        def _draw_tuto_background():
            ecran.fill((0, 0, 0))
            lw, lh = dims[0], dims[1]
            largeur_vue = lw / 1.0
            hauteur_vue = (lh - HAUTEUR_BARRE) / 1.0
            surf_tuto = pygame.Surface(
                (math.ceil(largeur_vue), math.ceil(hauteur_vue))
            ).convert()
            couleur_grille = (20, 80, 20)
            epaisseur = 2
            debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
            debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE
            for ty in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
                for tx in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                    surf_tuto.blit(herbe, (tx - camera_x, ty - camera_y))
                    pygame.draw.rect(surf_tuto, couleur_grille,
                        (tx - camera_x, ty - camera_y, TAILLE_CASE, TAILLE_CASE), epaisseur)
            players[indice].draw_player(surf_tuto, camera_x, camera_y)
            ecran.blit(surf_tuto, (0, 0))
            pygame.draw.rect(
                ecran, (40, 40, 40),
                (0, dims[1] - HAUTEUR_BARRE, dims[0], HAUTEUR_BARRE)
            )

        result = run_tutorial(ecran, horloge, FPS, draw_background_fn=_draw_tuto_background)
        if result is False:
            stop_event.set()
            return False

    batiment_selectionne = None

    terminal = Terminal()

    ZOOM_MIN = 0.3
    ZOOM_MAX = 2.5
    VITESSE_ZOOM = 0.1

    deplacement_camera = False
    derniere_souris = (0, 0)

    rects_icones = calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE)
    en_cours = True
    acc_argent   = 0.0  # mine → money
    acc_food     = 0.0  # farm → food
    acc_vapeur   = 0.0  # generateur → vapeur
    save_done_timer = 0.0

    ambient_playlist = list(range(len(sound.ambient_musics)))
    random.shuffle(ambient_playlist)
    current_playlist_index = 0
    ambient_delay_timer = 0.0
    update = threading.Thread(target=on_message_recu, args=(TAILLE_CASE,), daemon=True)
    update.start()
    #if client_module.CLIENT is not None and online:
    #    send_liste_batiments_client(batiments, client_module.CLIENT)
    #if client_module.CLIENT is not None and online:
    #    send_liste_joueurs_client(players, client_module.CLIENT)
    while en_cours:
        dt = horloge.tick(FPS) / 1000.0
        save_done_timer = max(0, save_done_timer - dt)

        if not pygame.mixer.music.get_busy():
            if ambient_delay_timer > 0:
                ambient_delay_timer -= dt
            else:
                index = ambient_playlist[current_playlist_index]
                sound.play_ambient(index, loop=0)
                current_playlist_index += 1
                if current_playlist_index >= len(ambient_playlist):
                    random.shuffle(ambient_playlist)
                    current_playlist_index = 0
                ambient_delay_timer = 3.0 

        acc_argent, acc_food, acc_vapeur = calculer_production(batiments, players[indice], dt, acc_argent, acc_food, acc_vapeur)


        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop_event.set()
                return False

            if event.type == pygame.VIDEORESIZE:
                dims[0], dims[1] = event.w, event.h
                rects_icones[:] = calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE)

            # ── Terminal : touche ² pour ouvrir/fermer ──────────────────────
            if event.type == pygame.KEYDOWN and event.unicode == "²":
                terminal.toggle()
                continue

            # Si le terminal est ouvert, il consomme tous les events clavier/souris
            if terminal.handle_event(event, players[indice], batiments):
                continue
            # ───────────────────────────────────────────────────────────────

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from screens.pause import menu_pause
                screenshot = ecran.copy()
                if online:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, online, players[indice], screenshot)
                    pass
                else:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, online, players[indice], screenshot)
                if etat_pause == "jeu_save_done":
                    save_done_timer = 1.5  # show for 1.5 seconds
                elif not etat_pause:
                    stop_event.set()
                    return False
                elif etat_pause == "menu":
                    stop_event.set()
                    return True

            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                centre_x = camera_x + dims[0] / (2 * ancien_zoom)
                centre_y = camera_y + dims[1] / (2 * ancien_zoom)

                camera_x = centre_x - dims[0] / (2 * zoom)
                camera_y = centre_y - dims[1] / (2 * zoom)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                deplacement_camera = True
                derniere_souris = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                deplacement_camera = False

            if event.type == pygame.MOUSEMOTION and deplacement_camera:
                sx, sy = pygame.mouse.get_pos()
                dx = sx - derniere_souris[0]
                dy = sy - derniere_souris[1]
                camera_x -= dx / zoom
                camera_y -= dy / zoom
                derniere_souris = (sx, sy)

#clic droit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if batiment_selectionne is not None:
                    batiment_selectionne = None
                    print("Sélection annulée")

                else:
                    sx, sy = pygame.mouse.get_pos()
                    case = souris_vers_case((sx, sy), camera_x, camera_y, zoom, TAILLE_CASE)

                    if sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
                        if not players[indice].a_star(case, TAILLE_CASE):
                            print("Chemin bloqué")
                        if client_module.CLIENT is not None and online:
                            send_liste_joueurs_client(players, client_module.CLIENT)



# Clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sx, sy = pygame.mouse.get_pos()

                clic_barre = False
                for i, rect in enumerate(rects_icones):
                    if rect.collidepoint(sx, sy):
                        batiment_selectionne = None if batiment_selectionne == i else i
                        clic_barre = True
                        break


                # Placement du bâtiment sur la grille
                if not clic_barre and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
                    mx = camera_x + sx / zoom
                    my = camera_y + sy / zoom

                    if batiment_selectionne is not None:
                        grid_x = int(mx // TAILLE_CASE)
                        grid_y = int(my // TAILLE_CASE)

                        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
                        image_ref = images_batiments[type_batiment][1]
                        nouveau = Batiment(type_batiment, grid_x, grid_y)

                        cout = Batiment.DATA[type_batiment][1]["cout"]

                        # Limite : nb batiments de production <= nb total de villageois
                        nb_villageois = sum(b.get_population() for b in batiments if b.type == Batiment.TYPE_RESIDENTIEL)
                        nb_production = sum(1 for b in batiments if b.type != Batiment.TYPE_RESIDENTIEL)
                        production_pleine = (type_batiment != Batiment.TYPE_RESIDENTIEL and nb_production >= nb_villageois)

                        if not joueur_a_portee((grid_x, grid_y), players[indice], TAILLE_CASE):
                            print("Trop loin : rapprochez-vous de la case (2 cases max)")
                        elif production_pleine:
                            print("Pas assez de villageois pour ce batiment de production")
                        elif not collision(batiments, nouveau) and players[indice].money >= cout:
                            players[indice].money -= cout
                            batiments.append(nouveau)
                            sound.son_placement.play()
                            synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)
                            if client_module.CLIENT is not None and online:
                                print(f"envoi en cours {batiments}")
                                send_liste_batiments_client(batiments, client_module.CLIENT)

                    else:
                        for B in batiments:
                            rect = B.get_rect_pixel(TAILLE_CASE)
                            rect.x -= camera_x
                            rect.y -= camera_y
                            mx = camera_x + sx / zoom
                            my = camera_y + sy / zoom

                            rect = B.get_rect_pixel(TAILLE_CASE)

                            if rect.collidepoint(mx, my):
                                if not joueur_a_portee((B.x, B.y), players[indice], TAILLE_CASE):
                                    print("Trop loin : rapprochez-vous du bâtiment (2 cases max)")
                                    break
                                resultat = afficher_menu_amelioration(ecran, B, sx, players[indice])

                                if resultat == "supprimer":
                                    batiments.remove(B)
                                    cashback = 0
                                    for k in range(B.niveau):
                                        cashback += Batiment.DATA[B.type][1+k]["cout"]
                                    players[indice].money += cashback
                                    if client_module.CLIENT is not None and online:
                                        send_liste_batiments_client(batiments, client_module.CLIENT)
                                elif resultat == "upgrade":
                                    if client_module.CLIENT is not None and online:
                                        send_liste_batiments_client(batiments, client_module.CLIENT)

                                synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)

                                break
                #Boutton SELL pour vendre les batiments quand c'est selectionné
                mode_sell = False


        players[indice].update(TAILLE_CASE, dt)
        players[indice].update_anim(dt)

        ecran.fill((0, 0, 0))

        largeur_vue = dims[0] / zoom
        hauteur_vue = (dims[1] - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        dessiner_grille(surface_monde, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, herbe, TAILLE_CASE)

        dessiner_monde(surface_monde, batiments, images_batiments, camera_x, camera_y, TAILLE_CASE, batiment_selectionne, TYPES_BATIMENTS, players[indice], npcs, image_pnj, dt, zoom)

        surface_affichee = pygame.transform.scale(
            surface_monde,
            (dims[0], dims[1] - HAUTEUR_BARRE)
        )

        ecran.blit(surface_affichee, (0, 0))
        dessiner_grille_overlay(ecran, camera_x, camera_y, dims, HAUTEUR_BARRE, zoom, TAILLE_CASE)

        dessiner_hud(ecran, dims, HAUTEUR_BARRE, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS, TAILLE_ICONE, players[indice], font_argent, hud_or_img, hud_food_img, hud_vapeur_img, save_done_img, save_done_timer)

        terminal.draw(ecran, dt)

        pygame.display.flip()
    stop_event.set()
    sound.stop_ambient()
    return True
