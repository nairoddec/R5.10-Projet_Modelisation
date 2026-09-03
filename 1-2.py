import numpy as np

# --- 1. Statistiques des digrammes ---
def statistiques_digrammes(texte) :
    comptes = {}
    total_digrammes = len(texte) - 1
    
    # Sécurité si le texte fait moins de 2 caractères
    if total_digrammes <= 0 :
        return {}
        
    # Extraction et comptage de chaque digramme
    for i in range(total_digrammes) :
        digramme = texte[i : i + 2]
        # .get() récupère la valeur existante ou 0 si le digramme est nouveau
        comptes[digramme] = comptes.get(digramme, 0) + 1
        
    # Tri décroissant et calcul des pourcentages
    statistiques = {}
    # On trie le dictionnaire en fonction de la valeur (le nombre d'occurrences)
    for digramme, occurrences in sorted(comptes.items(), key=lambda item: item[1], reverse = True) :
        statistiques[digramme] = {
            "occurrences": occurrences,
            "pourcentage": round((occurrences / total_digrammes) * 100, 2)
        }
        
    return statistiques

# --- Exemple d'utilisation ---
print("\n--- Statistiques des digrammes ---")
texte_analyse = "BONJOUR TOUT LE MONDE BONJOUR A TOUS LES AMIS"
resultats = statistiques_digrammes(texte_analyse)

for digramme, donnees in resultats.items() :
    print(f"'{digramme}' : {donnees['occurrences']} fois ({donnees['pourcentage']} %)")



# --- 2. Construction de la matrice de transitions 27x27 ---
def construire_matrice_transitions(statistiques) :
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    char_to_idx = {c: i for i, c in enumerate(alphabet)}
    idx_to_char = {i: c for i, c in enumerate(alphabet)}
    
    matrice = np.zeros((27, 27))
    
    # Remplissage de la matrice avec les occurrences des digrammes
    for digramme, donnees in statistiques.items():
        if len(digramme) == 2 and digramme[0] in char_to_idx and digramme[1] in char_to_idx:
            matrice[char_to_idx[digramme[0]], char_to_idx[digramme[1]]] = donnees["occurrences"]
            
    # Normalisation pour que la somme sur chaque ligne soit égale à 1
    sommes_lignes = matrice.sum(axis=1, keepdims=True)
    # Éviter la division par zéro (si une lettre n'a jamais été rencontrée)
    matrice = np.divide(matrice, sommes_lignes, out=np.zeros_like(matrice), where=sommes_lignes!=0)
    
    return matrice, char_to_idx, idx_to_char

# --- Suite de l'exemple d'utilisation ---
matrice_transitions, char2idx, idx2char = construire_matrice_transitions(resultats)

# Affichage de la matrice
print("\n--- Matrice de transitions 27x27 ---")
print(matrice_transitions)



# --- 3. Génération de texte à partir de la chaîne de Markov ---
def generer_texte_markov(matrice, char_to_idx, idx_to_char, longueur=50):
    texte = [" "] # Initialisation obligatoire par "espace"
    
    for _ in range(longueur - 1):
        etat_actuel = texte[-1]
        idx_actuel = char_to_idx[etat_actuel]
        probabilites = matrice[idx_actuel]
        
        # Sécurité : si la ligne est vide de probabilités, on tire de façon uniforme
        if probabilites.sum() == 0:
            probabilites = np.ones(27) / 27
            
        prochain_idx = np.random.choice(27, p=probabilites)
        texte.append(idx_to_char[prochain_idx])
        
    return "".join(texte)

# --- Suite de l'exemple d'utilisation ---
texte_simule = generer_texte_markov(matrice_transitions, char2idx, idx2char, longueur=60)
print("\n--- Génération de texte (Chaîne de Markov) ---")
print(texte_simule)

# Observation qualitative : Sur un corpus très court, le texte boucle sur les mots existants.
# Sur un texte source de la taille d'une page Wikipédia, les mots générés n'existeront pas
# dans le dictionnaire mais respecteront l'alternance consonnes/voyelles du français.

