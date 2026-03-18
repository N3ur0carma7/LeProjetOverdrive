import pygame

def afficher_currency(ecran, player, image_currency, police_currency):
    rect_ecran = ecran.get_rect()

    marge_x = int(rect_ecran.width * 0.02)
    marge_y = int(rect_ecran.height * 0.02)

    rect_image = image_currency.get_rect()
    rect_image.topright = (
        rect_ecran.right - marge_x,
        rect_ecran.top + marge_y
    )

    ecran.blit(image_currency, rect_image)

    # texte argent
    texte = police_currency.render(str(player.money), True, (255, 215, 0))
    rect_texte = texte.get_rect()

    offset_x = int(rect_image.width * 0.38)

    rect_texte.center = (
        rect_image.left + offset_x,
        rect_image.centery + 2
    )
    ecran.blit(texte, rect_texte)