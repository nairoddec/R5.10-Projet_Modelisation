# Permet d'établir les digrammes, c'est-à-dire les groupes de 2 caractères consécutifs.

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
texte_analyse = "BONJOUR TOUT LE MONDE BONJOUR A TOUS LES AMIS"
resultats = statistiques_digrammes(texte_analyse)

for digramme, donnees in resultats.items() :
    print(f"'{digramme}' : {donnees['occurrences']} fois ({donnees['pourcentage']} %)")