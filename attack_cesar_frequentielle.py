from cesar import (
    chiffrement_cesar,
    dechiffrement_cesar,
)

from analyse_frequentielle import (
    nettoyer_texte,
    calculer_statistiques,
    analyser_page_web,
)


def score_depuis_occurrences(statistiques_texte, statistiques_ref):
    """
    Calcule le score chi carré en comparant le texte essayé 
    avec les statistiques réelles d'une page de référence.
    """
    total_texte = statistiques_texte["total_sans_espaces"]
    occurrences_texte = statistiques_texte["frequences"]
    
    total_ref = statistiques_ref["total_sans_espaces"]
    occurrences_ref = statistiques_ref["frequences"]

    if total_texte == 0 or total_ref == 0:
        return float("inf")

    score = 0

    for lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        observe = occurrences_texte[lettre]
        
        # Probabilité d'apparition de cette lettre dans la page Wikipédia
        proba_ref = occurrences_ref[lettre] / total_ref
        
        # Combien de fois on s'attend à voir cette lettre dans le texte déchiffré
        attendu = total_texte * proba_ref

        if attendu > 0:
            score += (observe - attendu) ** 2 / attendu
        elif observe > 0:
            # Si on attendait 0 occurrence mais qu'il y en a, on pénalise le score
            score += 1000  

    return score


def attaque_frequentielle_cesar(texte_chiffre, statistiques_ref):
    """
    Essaie les 26 décalages possibles en utilisant les stats de référence.
    """
    meilleur_score = float("inf")
    meilleur_decalage = 0
    meilleur_texte = ""

    print("\n--- Attaque fréquentielle de César ---")

    for decalage in range(26):
        texte_essaye = dechiffrement_cesar(texte_chiffre, decalage)
        tableau_occurrences = calculer_statistiques(texte_essaye)
        
        score = score_depuis_occurrences(tableau_occurrences, statistiques_ref)

        print(f"Décalage {decalage:2} | score : {score:8.2f} | {texte_essaye}")

        if score < meilleur_score:
            meilleur_score = score
            meilleur_decalage = decalage
            meilleur_texte = texte_essaye

    return meilleur_decalage, meilleur_texte, meilleur_score


# --- Test ---
if __name__ == "__main__" :
    print("Récupération du corpus de référence (Wikipédia)...")
    url_wiki = "https://fr.wikipedia.org/wiki/Cosplay"
    
    stats_reference = analyser_page_web(url_wiki)
    
    if stats_reference :
        # 2. Préparation du message
        message = (
            "LE CHIFFRE DE CESAR EST SIMPLE A CASSER "
            "AVEC UNE ANALYSE FREQUENTIELLE"
        )
        cle = 3
    
        message = nettoyer_texte(message)
        cryptogramme = chiffrement_cesar(message, cle)
    
        print(f"\nMessage intercepté : {cryptogramme}")
    
        # 3. Lancement de l'attaque
        decalage, texte_dechiffre, score = attaque_frequentielle_cesar(
            cryptogramme, stats_reference
        )
    
        print("\n--- Résultat ---")
        print(f"Décalage trouvé : {decalage}")
        print(f"Texte déchiffré : {texte_dechiffre}")
        print(f"Écart statistique avec le français : {score:.2f} (le score le plus proche de 0 l'emporte)")
    else :
        print("Erreur : Impossible de récupérer les statistiques de référence.")