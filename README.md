# 🤖 robot-flower-princess API

Une API REST développée avec FastAPI pour un jeu de plateau inspiré du film d'animation Disney Wall-E.

## 📖 Description

Le jeu consiste à aider Wall-E (un robot) à livrer une fleur à une princesse sur un plateau 2D. Le joueur doit naviguer à travers des obstacles (déchets) qu'il peut nettoyer, ramasser la fleur et la livrer à destination.

### 🎮 Règles du jeu

- **Objectif** : Livrer la fleur à la princesse
- **Plateau** : Grille 2D configurable (3x3 à 50x50)
- **Éléments** :
  - 🤖 **Robot (R)** : Contrôlé par le joueur, démarre en haut à gauche
  - 👑 **Princesse (P)** : Destination finale, positionnée en bas à droite
  - 🌸 **Fleur (F)** : À ramasser et livrer, position aléatoire
  - 🗑️ **Déchet (D)** : Obstacles nettoyables (~30% du plateau)
  - ⬜ **Vide (V)** : Cases libres

### 🎯 Mécaniques de jeu

- **Mouvement** : Une case à la fois (haut, bas, gauche, droite)
- **Transport** : Le robot peut porter la fleur en se déplaçant
- **Nettoyage** : Les déchets peuvent être nettoyés (impossible en portant la fleur)
- **Victoire** : Déposer la fleur sur la case de la princesse
- **Défaite** : Effectuer un mouvement invalide

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Installation des dépendances

```bash
# Cloner le projet
git clone https://github.com/remi-picard/robot-flower-princess.git
cd robot-flower-princess

# Installer les dépendances
pip install fastapi uvicorn

# Ou avec requirements.txt
pip install -r requirements.txt
```

### Lancer le serveur

```bash
# Méthode 1 : Directement
python main.py

# Méthode 2 : Avec Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Méthode 3 : Mode développement
uvicorn main:app --reload

# Méthode 4 : Pull l'image Docker Hub
docker run --rm -p 8000:8000 picardremi/robot-flower-princess:master
```

L'API sera accessible sur : `http://localhost:8000`

Documentation interactive : `http://localhost:8000/docs`
