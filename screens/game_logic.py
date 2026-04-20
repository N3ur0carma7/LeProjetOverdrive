import pygame
from core.Class.npc import Npc

_fullscreen = False

def toggle_fullscreen():
    global _fullscreen
    _fullscreen = not _fullscreen
    if _fullscreen:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

def synchroniser_npcs(batiments, npcs, player, TAILLE_CASE):
    from core.Class.batiments import Batiment
    population_attendue = {}
    for b in batiments:
        if b.type == Batiment.TYPE_RESIDENTIEL:
            population_attendue[id(b)] = b.get_population()

    npcs_par_maison = {}
    for npc in list(npcs):
        cle = id(npc.maison)
        if cle not in npcs_par_maison:
            npcs_par_maison[cle] = []
        npcs_par_maison[cle].append(npc)

    maisons_valides = {id(b) for b in batiments if b.type == Batiment.TYPE_RESIDENTIEL}
    for npc in list(npcs):
        if id(npc.maison) not in maisons_valides:
            npcs.remove(npc)

    for b in batiments:
        if b.type != Batiment.TYPE_RESIDENTIEL:
            continue
        cle = id(b)
        actuels = npcs_par_maison.get(cle, [])
        attendus = population_attendue.get(cle, 0)

        while len(actuels) < attendus:
            npc = Npc(b, TAILLE_CASE, player)
            npcs.append(npc)
            actuels.append(npc)

        while len(actuels) > attendus:
            npc = actuels.pop()
            if npc in npcs:
                npcs.remove(npc)

    lieux_travail = [b for b in batiments if b.type != Batiment.TYPE_RESIDENTIEL]
    for i, npc in enumerate(npcs):
        if lieux_travail:
            npc.assigner_travail(lieux_travail[i % len(lieux_travail)])
        else:
            npc.assigner_travail(None)

def calculer_production(batiments, player, dt, acc_argent, acc_food, acc_vapeur):
    # Production des batiments selon leur type de ressource
    # Si food == 0, seule la farm continue de produire
    food_ok = player.food > 0
    for b in batiments:
        rtype = b.get_production_type()
        val = b.get_production() * dt / 60.0
        if rtype == "nourriture":
            acc_food += val
        elif not food_ok:
            pass  # production stoppee tant que food == 0
        elif rtype == "argent":
            acc_argent += val
        elif rtype == "vapeur":
            acc_vapeur += val

    gains_argent = int(acc_argent)
    if gains_argent > 0:
        player.money += gains_argent
        acc_argent -= gains_argent

    gains_food = int(acc_food)
    if gains_food > 0:
        player.food += gains_food
        acc_food -= gains_food

    gains_vapeur = int(acc_vapeur)
    if gains_vapeur > 0:
        player.vapeur += gains_vapeur
        acc_vapeur -= gains_vapeur

    return acc_argent, acc_food, acc_vapeur