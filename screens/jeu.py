import pygame
import math

from core.Class.player import Player
from core.saves import load_save
import os
from multiplayer.serveur import *
from multiplayer.client import send_list_client, CLIENT, recieved_client, send_batiment_client, send_liste_batiments_client, send_liste_joueurs_client
from core.Class.batiments import *
from screens.GUI.menu_amelioration import afficher_menu_amelioration
import time

batiments = []
players = []


def update(client_sock):
    global batiments
    global players
    while True:
        res = recieved_client(client_sock)
        if res is None:
            continue
        data, msg_type = res
        print(msg_type)
        if msg_type == 'liste_batiments':
            print(">>> Donnée reçue (batiments) :", data)
            if not data:
                batiments = []
            else:
                batiments = []
                for B in data:
                    batiments.append(B)
        elif msg_type == 'liste_joueurs':
            print(">>> Donnée reçue (joueurs) :", data)
            if not data:
                players = []
            else:
                players = []
                for P in data:
                    players.append(P)
        time.sleep(0.05)



thread_lance = False

def boucle_jeu(ecran, horloge, FPS):
    global batiments
    global players
    global thread_lance
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    HAUTEUR_BARRE = 100  # barre du bas

    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_CASE = herbe.get_width()

    # Chargement des bâtiments
    images_batiments = {
        Batiment.TYPE_RESIDENTIEL: {
            1: pygame.image.load("assets/buildings/house_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/house_lvl2.png").convert_alpha(),  # Image niveau 2
            3: pygame.image.load("assets/buildings/house_lvl3.png").convert_alpha()  # Image niveau 3
        },
        Batiment.TYPE_MINE: {
            1: pygame.image.load("assets/buildings/mine_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/mine_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/mine_lvl3.png").convert_alpha()
        }
    }

    TYPES_BATIMENTS = [
        Batiment.TYPE_RESIDENTIEL,
        Batiment.TYPE_MINE
    ]

    TAILLE_ICONE = 64

    player = Player()
    players.append(player)
    online = {}
    # Dictionnaire des bâtiments placés
    # clé : (x_case, y_case)
    # valeur : index du bâtiment
    if os.path.exists("save/save.json"):
        if not load_save(batiments, player):
            print("ERREUR CRITIQUE: Lecture du fichier save/save.json")
            return False
    batiment_selectionne = None

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

    # Caméra et zoom
    camera_x, camera_y = 0.0, 0.0
    zoom = 1.0

    ZOOM_MIN = 0.5
    ZOOM_MAX = 3.0
    VITESSE_ZOOM = 0.1

    # Déplacement caméra avec bouton du milieu
    deplacement_camera = False
    derniere_souris = (0, 0)

    # Création de la barre d’icônes
    rects_icones = []
    marge = 20

    for i in range(len(images_batiments)):
        rect = pygame.Rect(
            marge + i * (TAILLE_ICONE + marge),
            HAUTEUR_ECRAN - HAUTEUR_BARRE + (HAUTEUR_BARRE - TAILLE_ICONE) // 2,
            TAILLE_ICONE,
            TAILLE_ICONE
        )
        rects_icones.append(rect)

    def souris_vers_case(pos):
        sx, sy = pos
        mx = camera_x + sx / zoom
        my = camera_y + sy / zoom
        return int(mx // TAILLE_CASE), int(my // TAILLE_CASE)

    # Dessine la grille infinie + l’herbe
    def dessiner_grille(surface):
        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
        debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

        for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
            for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                surface.blit(herbe, (x - camera_x, y - camera_y))
                pygame.draw.rect(
                    surface,
                    (60, 60, 60, 1),
                    (x - camera_x, y - camera_y, TAILLE_CASE, TAILLE_CASE),
                    1
                )



    # Boucle principale du jeu
    en_cours = True
    online_status = False
    while en_cours:
        horloge.tick(FPS)

        if CLIENT is not None and not thread_lance:
            thread_lance = True
            threading.Thread(target=update, args=(CLIENT,), daemon=True).start()

        for event in pygame.event.get():

            # Quitter le jeu
            if event.type == pygame.QUIT:
                return False

            # Menu pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from screens.pause import menu_pause
                if False:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, None, player)
                    pass
                else:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, None, player)
                if not etat_pause:
                    return False
                elif etat_pause == "menu":
                    return True

            # Zoom souris
            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                # Zoom centré sur l’écran
                centre_x = camera_x + LARGEUR_ECRAN / (2 * ancien_zoom)
                centre_y = camera_y + HAUTEUR_ECRAN / (2 * ancien_zoom)

                camera_x = centre_x - LARGEUR_ECRAN / (2 * zoom)
                camera_y = centre_y - HAUTEUR_ECRAN / (2 * zoom)

            # Début déplacement caméra
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                deplacement_camera = True
                derniere_souris = pygame.mouse.get_pos()

            # Fin déplacement caméra
            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                deplacement_camera = False

            # Mouvement caméra
            if event.type == pygame.MOUSEMOTION and deplacement_camera:
                sx, sy = pygame.mouse.get_pos()
                dx = sx - derniere_souris[0]
                dy = sy - derniere_souris[1]
                camera_x -= dx / zoom
                camera_y -= dy / zoom
                derniere_souris = (sx, sy)

            # Clic droit : désélection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                sx, sy = pygame.mouse.get_pos()
                case = souris_vers_case((sx, sy))
                if batiment_selectionne is not None:
                    for B in batiments:
                        if (
                                B.x <= case[0] < B.x + B.largeur and
                                B.y <= case[1] < B.y + B.hauteur
                        ):
                            batiments.remove(B)
                            print(f"envoi en cours {batiments}")
                            send_liste_batiments_client(batiments, CLIENT)
                            break
                if not batiment_selectionne is not None and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
                    case = souris_vers_case((sx, sy))
                    if not player.a_star(case, TAILLE_CASE):
                        print("TA GEULE")
                    print(player.path)
            # Clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sx, sy = pygame.mouse.get_pos()

                # Clic sur la barre d’icônes
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
                        nouveau = Batiment(type_batiment, grid_x, grid_y)

                        if not collision(batiments, nouveau):
                            batiments.append(nouveau)
                            if CLIENT is not None:
                                print(f"envoi en cours {batiments}")
                                send_liste_batiments_client(batiments, CLIENT)

                    else:
                        for B in batiments:
                            rect = B.get_rect_pixel(TAILLE_CASE)
                            rect.x -= camera_x
                            rect.y -= camera_y
                            mx = camera_x + sx / zoom
                            my = camera_y + sy / zoom

                            rect = B.get_rect_pixel(TAILLE_CASE)

                            if rect.collidepoint(mx, my):
                                afficher_menu_amelioration(ecran, B, sx)
                                break


        player.update(TAILLE_CASE)

        # rendu
        ecran.fill((0, 0, 0))

        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        dessiner_grille(surface_monde)

        for B in batiments:
            image = images_batiments[B.type][B.niveau]
            x = B.x * TAILLE_CASE - camera_x + (TAILLE_CASE - image.get_width()) // 2
            y = B.y * TAILLE_CASE - camera_y + (TAILLE_CASE - image.get_height()) // 2
            surface_monde.blit(image, (x, y))

        if batiment_selectionne is not None:
            sx, sy = pygame.mouse.get_pos()
            case = souris_vers_case((sx, sy))
            type_batiment = TYPES_BATIMENTS[batiment_selectionne]
            test_batiment = Batiment(type_batiment, case[0], case[1])
            # On prend l'image du niveau 1 par défaut pour le fantôme
            image = images_batiments[type_batiment][1]
            image_fantome = image.copy()
            # collision = rouge
            if collision(batiments, test_batiment):
                image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

            x = case[0] * TAILLE_CASE - camera_x + (TAILLE_CASE - image.get_width()) // 2
            y = case[1] * TAILLE_CASE - camera_y + (TAILLE_CASE - image.get_height()) // 2

            surface_monde.blit(
                image_fantome,
                (x, y)
            )

        # Dessin du joueur
        player.draw_player(surface_monde, camera_x, camera_y)

        # Application du zoom
        surface_affichee = pygame.transform.smoothscale(
            surface_monde,
            (LARGEUR_ECRAN, HAUTEUR_ECRAN - HAUTEUR_BARRE)
        )
        ecran.blit(surface_affichee, (0, 0))

        # Barre du bas
        pygame.draw.rect(
            ecran,
            (40, 40, 40),
            (0, HAUTEUR_ECRAN - HAUTEUR_BARRE, LARGEUR_ECRAN, HAUTEUR_BARRE)
        )

        # Icônes
        for i, rect in enumerate(rects_icones):
            couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
            pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

            type_actuel = TYPES_BATIMENTS[i]
            # On affiche l'image de niveau 1 dans la barre d'icônes
            icone = pygame.transform.smoothscale(
                images_batiments[type_actuel][1], (TAILLE_ICONE, TAILLE_ICONE)
            )
            ecran.blit(icone, rect)

        pygame.display.flip()

    return True