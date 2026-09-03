import numpy as np

def statistiques_digrammes(texte) :
    comptes = {}
    total_digrammes = len(texte) - 1
    
    if total_digrammes <= 0 :
        return {}
        
    for i in range(total_digrammes) :
        digramme = texte[i : i + 2]
        comptes[digramme] = comptes.get(digramme, 0) + 1
        
    statistiques = {}
    for digramme, occurrences in sorted(comptes.items(), key=lambda item: item[1], reverse = True) :
        statistiques[digramme] = {
            "occurrences": occurrences,
            "pourcentage": round((occurrences / total_digrammes) * 100, 2)
        }
        
    return statistiques

print("\n--- Statistiques des digrammes ---")
texte_analyse = "BONJOUR TOUT LE MONDE BONJOUR A TOUS LES AMIS"
resultats = statistiques_digrammes(texte_analyse)

for digramme, donnees in resultats.items() :
    print(f"'{digramme}' : {donnees['occurrences']} fois ({donnees['pourcentage']} %)")



def construire_matrice_transitions(statistiques) :
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    char_to_idx = {c: i for i, c in enumerate(alphabet)}
    idx_to_char = {i: c for i, c in enumerate(alphabet)}
    
    matrice = np.zeros((27, 27))
    
    for digramme, donnees in statistiques.items():
        if len(digramme) == 2 and digramme[0] in char_to_idx and digramme[1] in char_to_idx:
            matrice[char_to_idx[digramme[0]], char_to_idx[digramme[1]]] = donnees["occurrences"]
            
    sommes_lignes = matrice.sum(axis=1, keepdims=True)
    matrice = np.divide(matrice, sommes_lignes, out=np.zeros_like(matrice), where=sommes_lignes!=0)
    
    return matrice, char_to_idx, idx_to_char

matrice_transitions, char2idx, idx2char = construire_matrice_transitions(resultats)
print("\n--- Matrice de transitions 27x27 ---")
print(matrice_transitions)



def generer_texte_markov(matrice, char_to_idx, idx_to_char, longueur=50):
    texte = [" "] 
    
    for _ in range(longueur - 1):
        etat_actuel = texte[-1]
        idx_actuel = char_to_idx[etat_actuel]
        probabilites = matrice[idx_actuel]
        
        if probabilites.sum() == 0:
            probabilites = np.ones(27) / 27
            
        prochain_idx = np.random.choice(27, p=probabilites)
        texte.append(idx_to_char[prochain_idx])
        
    return "".join(texte)

texte_simule = generer_texte_markov(matrice_transitions, char2idx, idx2char, longueur=60)
print("\n--- Génération de texte (Chaîne de Markov) ---")
print(texte_simule)

