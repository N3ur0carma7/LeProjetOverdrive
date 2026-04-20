# ⚙️ Projet Overdrive

> Un city-builder sandbox steampunk avec raids PVE, multijoueur local et arbre de compétences — développé en Python avec Pygame.

---

## 📖 Présentation

**Projet Overdrive** est un jeu de construction et de survie au style steampunk. Le joueur développe son village en posant des bâtiments sur une grille, gère trois ressources (or, nourriture, vapeur) et doit défendre sa base contre des vagues de monstres lors de raids automatiques.

Le jeu supporte un mode **multijoueur en réseau local**, un **arbre de compétences** pour débloquer des améliorations, et un **terminal de développement** intégré pour tester les mécaniques en temps réel.

---

## 🎮 Fonctionnalités

### Construction & gestion
- Pose de bâtiments sur une grille fine (style Clash of Clans)
- 4 types de bâtiments, chacun avec 3 niveaux d'amélioration :
  - 🏠 **Maison** — augmente la population de villageois
  - ⚙️ **Générateur** — produit de la vapeur
  - ⛏️ **Mine** — produit de l'or
  - 🌾 **Ferme** — produit de la nourriture
- Système de population : le nombre de bâtiments de production est limité par les villageois disponibles
- Remboursement partiel à la destruction d'un bâtiment

### Combat & PVE
- Raids automatiques toutes les quelques minutes (4 vagues par raid)
- Attaque au clic sur les monstres avec cooldown
- Coups critiques (chance et multiplicateur configurables)
- Affichage des dégâts flottants avec distinction critique/normal
- Game over avec **pénalité de –30% sur toutes les ressources**

### Progression
- Arbre de compétences pour débloquer les niveaux 2 et 3 des bâtiments
- Statistiques joueur évolutives : PV max, dégâts, défense, régénération

### Multijoueur
- Architecture client/serveur en réseau local (TCP)
- Découverte automatique du serveur par broadcast UDP
- Synchronisation des bâtiments et des positions des joueurs en temps réel

### Interface & confort
- Zoom et déplacement de caméra à la souris
- Barre de construction animée (slide)
- Messages flottants contextuels pour chaque action impossible
- Terminal de développement (`²`) avec commandes : `trigger_raid`, `give_money`, etc.
- Sauvegarde / chargement automatique (JSON)
- Plein écran (`F11`)
- Musique d'ambiance en playlist aléatoire

---


## 🚀 Installation & lancement

### Prérequis

- Python **3.11+**
- [Pygame](https://www.pygame.org/) 2.x

### Installation

```bash
git clone https://github.com/Neurocarma/LeProjetOverdrive.git
cd LeProjetOverdrive

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

pip install pygame
```

### Lancer le jeu

```bash
python main.py
```

> ⚠️ Le jeu doit être lancé depuis la **racine du projet** pour que les chemins vers `assets/` soient correctement résolus.

---

## 🌐 Multijoueur

Le multijoueur fonctionne en **réseau local uniquement**.

1. Un joueur lance le jeu et héberge la partie via le menu **"Rejoindre / Héberger"**
2. Les autres joueurs rejoignent depuis le même réseau local — le serveur est détecté automatiquement par broadcast UDP
3. La synchronisation couvre : positions des joueurs, liste des bâtiments, état du raid

---

## ⌨️ Contrôles

| Action | Contrôle |
|--------|----------|
| Déplacer le joueur | Clic droit |
| Placer un bâtiment | Clic gauche (après sélection) |
| Attaquer un monstre | Clic gauche sur le monstre (à portée) |
| Annuler la sélection | Clic droit |
| Zoom | Molette souris |
| Plein écran | F11 |
| Menu pause / sauvegarde | Échap |
| Terminal développeur | `²` |

---

## 🛠️ Terminal développeur

Le terminal (`²`) est disponible en jeu. Commandes utiles :

```
trigger_raid       — Déclenche un raid immédiatement
give_money <n>     — Donne n pièces d'or au joueur
```

---

## 📦 Technologies

- **Python 3.11+**
- **Pygame 2** — rendu, audio, événements
- **Sockets TCP/UDP** — multijoueur réseau local
- **JSON** — sauvegarde et configuration
- **A\*** — pathfinding du joueur

---

## 👥 Équipe

Projet développé dans le cadre scolaire.

---

## 📄 Licence

Ce projet est à usage éducatif. Assets sonores et visuels soumis à leurs licences respectives.
