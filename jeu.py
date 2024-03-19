import streamlit as st
import numpy as np

# Taille du plateau de jeu
TAILLE_PLATEAU = 10

# Initialisation de l'état du jeu
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if 'targets' not in st.session_state:
    st.session_state.targets = []

if 'result_message' not in st.session_state:
    st.session_state.result_message = ""

if 'shot_count' not in st.session_state:
    st.session_state.shot_count = 0

if 'button_state' not in st.session_state:
    st.session_state.button_state = np.zeros((TAILLE_PLATEAU, TAILLE_PLATEAU))

if 'destroyed_targets' not in st.session_state:
    st.session_state.destroyed_targets = set()

# Logique du jeu
def generate_target(taille_plateau):
    targets = []
    occupied = set()
    for longueur in range(1, 5):  # Longueurs de 1 à 4
        valide = False
        while not valide:
            orientation = np.random.choice(['horizontal', 'vertical'])
            if orientation == 'horizontal':
                ligne = np.random.randint(0, taille_plateau)
                colonne = np.random.randint(0, taille_plateau - longueur + 1)
                if all((ligne, colonne + i) not in occupied for i in range(longueur)) and \
                   all((ligne + 1, colonne + i) not in occupied for i in range(longueur)):
                    targets.append((ligne, colonne, longueur, orientation))
                    occupied.update((ligne, colonne + i) for i in range(longueur))
                    occupied.update((ligne + 1, colonne + i) for i in range(longueur))
                    valide = True
            else:  # orientation == 'vertical'
                ligne = np.random.randint(0, taille_plateau - longueur)
                colonne = np.random.randint(0, taille_plateau)
                if all((ligne + i, colonne) not in occupied for i in range(longueur)) and \
                   all((ligne + i, colonne + 1) not in occupied for i in range(longueur)):
                    targets.append((ligne, colonne, longueur, orientation))
                    occupied.update((ligne + i, colonne) for i in range(longueur))
                    occupied.update((ligne + i, colonne + 1) for i in range(longueur))
                    valide = True
    return targets

# Logique du jeu
def play_battleship(ligne, colonne):
    st.session_state.shot_count += 1  # Incrémenter le nombre de coups
    target_hit = False
    for target in st.session_state.targets:
        ligne_cible, colonne_cible, longueur, orientation = target
        if orientation == 'horizontal':
            if ligne == ligne_cible and colonne in range(colonne_cible, colonne_cible + longueur):
                target_hit = True
                st.session_state.result_message = f"Vous avez touché une cible de longueur {longueur} !"
                st.session_state.destroyed_targets.add(target)
        else:  # orientation == 'vertical'
            if colonne == colonne_cible and ligne in range(ligne_cible, ligne_cible + longueur):
                target_hit = True
                st.session_state.result_message = f"Vous avez touché une cible de longueur {longueur} !"
                st.session_state.destroyed_targets.add(target)
    
    if target_hit:
        # Vérifier si toutes les cibles sont détruites
        if len(st.session_state.destroyed_targets) == len(st.session_state.targets):
            st.session_state.game_started = False  # Fin du jeu
            st.session_state.result_message += f" Jeu terminé ! Vous avez utilisé {st.session_state.shot_count} coups."

    if not target_hit:
        st.session_state.result_message = "Vous n'avez touché aucune cible."
    
    st.session_state.button_state[ligne, colonne] = 1  # Désactiver le bouton après le clic

    
    # Vérifier si toutes les cibles sont détruites
    if len(st.session_state.destroyed_targets) == len(st.session_state.targets):
        st.session_state.game_started = False  # Fin du jeu
        st.session_state.result_message += f" Jeu terminé ! Vous avez utilisé {st.session_state.shot_count} coups."

    st.session_state.button_state[ligne, colonne] = 1  # Désactiver le bouton après le clic


# Application Streamlit
st.title("Jeu de Bataille Navale")

# Menu principal
if not st.session_state.game_started:
    st.write("""
    ## Règles du jeu
    - Cliquez sur les boutons sur le plateau de jeu pour sélectionner votre position de tir.
    - Détruisez les cibles en utilisant le moins de coups possible, la longueur des cibles varie de un à quatre.
    - Si vous touchez tous les cibles, vous gagnez le jeu !
    """)
    start_game = st.button("Commencer le jeu")

    if start_game:
        st.session_state.game_started = True
        st.session_state.shot_count = 0
        st.session_state.targets = generate_target(TAILLE_PLATEAU)
        st.session_state.result_message = ""
        st.session_state.destroyed_targets = set()
        st.session_state.button_state = np.zeros((TAILLE_PLATEAU, TAILLE_PLATEAU))

# Interface du plateau de jeu
if st.session_state.game_started:
    st.write("### Plateau de jeu")
    for i in range(TAILLE_PLATEAU):
        cols = st.columns(TAILLE_PLATEAU)
        for j in range(TAILLE_PLATEAU):
            button_placeholder = cols[j].empty()
            button_key = f"button_{i}_{j}"  # Utiliser une clé unique
            if st.session_state.button_state[i, j] == 0:
                if button_placeholder.button("", key=button_key):
                    play_battleship(i, j)
            if st.session_state.button_state[i, j] == 1:
                target_mark = "X"
                for target in st.session_state.targets:
                    ligne_cible, colonne_cible, longueur, orientation = target
                    if orientation == 'horizontal':
                        if i == ligne_cible and j in range(colonne_cible, colonne_cible + longueur):
                            target_mark = "✓"
                    else:  # orientation == 'vertical'
                        if j == colonne_cible and i in range(ligne_cible, ligne_cible + longueur):
                            target_mark = "✓"
                button_placeholder.markdown(target_mark)

# Affichage des informations en temps réel
    st.write("### Informations en temps réel")
    st.write(f"Nombre de coups : {st.session_state.shot_count}")
    st.write(f"Nombre de cibles détruites : {len(st.session_state.destroyed_targets)}/{len(st.session_state.targets)}")

# Affichage du résultat du jeu dans le menu principal
if st.session_state.result_message:
    st.write("""
    ## Résultat du jeu
    """)
    st.write(st.session_state.result_message)

# Bouton de redémarrage
if st.session_state.game_started or st.session_state.result_message:
    if st.button("Redémarrer"):
        st.session_state.game_started = False
        st.session_state.targets = generate_target(TAILLE_PLATEAU)
        st.session_state.button_state = np.zeros((TAILLE_PLATEAU, TAILLE_PLATEAU))
        st.session_state.result_message = ""
        st.session_state.destroyed_targets = set()
