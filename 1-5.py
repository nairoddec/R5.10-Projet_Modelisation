import math
import random

# Importation de tes propres fonctions (adapte les noms de fichiers si besoin)
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
from substitution import chiffrer, dechiffrer, extraire_alphabet, generer_cle_aleatoire
from permutation import dechiffrer_permutation, chiffrer_permutation
# On importe la fonction de ton exercice 1.2
from outils_digrammes import statistiques_digrammes 

def calculer_score_log(texte_dechiffre, stats_reference):
    """
    Calcule le score S(k) en utilisant les logarithmes et la fonction d'analyse de digrammes.
    """
    score = 0.0
    stats_texte_actuel = statistiques_digrammes(texte_dechiffre)
    for digramme, donnees in stats_texte_actuel.items():
        f_k = donnees["occurrences"]
        occurrences_ref = stats_reference.get(digramme, {}).get("occurrences", 0)
        r_xy = 1 + occurrences_ref
        score += f_k * math.log(r_xy)
        
    return score

def muter_substitution(cle_actuelle):
    """
    Crée un état voisin en échangeant la position de deux lettres chiffrées.
    """
    nouvelle_cle = cle_actuelle.copy()
    lettres_claires = list(nouvelle_cle.keys())
    
    l1, l2 = random.sample(lettres_claires, 2)
    nouvelle_cle[l1], nouvelle_cle[l2] = nouvelle_cle[l2], nouvelle_cle[l1]
    
    return nouvelle_cle

def attaque_mcmc_substitution(cryptogramme, stats_reference, iterations=15000, top_n=5):
    """
    Boucle principale MCMC. Renvoie les 'top_n' meilleures solutions trouvées.
    """
    alphabet = extraire_alphabet(cryptogramme)
    
    cle_actuelle = generer_cle_aleatoire(alphabet)
    score_actuel = calculer_score_log(dechiffrer(cryptogramme, cle_actuelle), stats_reference)
    
    # Liste pour stocker les N meilleures solutions sous forme (score, cle, texte, identifiant_cle)
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC (Recherche des {top_n} meilleures solutions)...\n")
    
    for i in range(iterations):
        cle_proposee = muter_substitution(cle_actuelle)
        texte_propose = dechiffrer(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        diff_score = score_propose - score_actuel
        
        if diff_score > 0:
            accepter = True
        else:
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter:
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            # Gestion du Top N des solutions uniques
            cle_str = str(cle_actuelle)
            # On vérifie si cette clé n'est pas déjà dans notre top
            if not any(c_str == cle_str for _, _, _, c_str in top_solutions):
                top_solutions.append((score_actuel, cle_actuelle.copy(), texte_propose, cle_str))
                # Tri par score décroissant
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                # On ne garde que les N meilleures
                top_solutions = top_solutions[:top_n]
                
        if i % 1000 == 0:
            # On affiche la meilleure solution du moment
            meilleur_score = top_solutions[0][0]
            texte_apercu = top_solutions[0][2][:50]
            print(f"Itération {i:5d} | Meilleur Score : {meilleur_score:8.2f} | {texte_apercu}...")
            
    # On renvoie la liste complète des tuples (score, cle, texte)
    return [(score, cle, texte) for score, cle, texte, _ in top_solutions]


def muter_permutation(cle_actuelle):
    """
    Crée un état voisin en déplaçant un sous-bloc (échange de 2 positions).
    """
    nouvelle_cle = cle_actuelle.copy()
    longueur = len(nouvelle_cle)
    
    i, j = random.sample(range(longueur), 2)
    nouvelle_cle[i], nouvelle_cle[j] = nouvelle_cle[j], nouvelle_cle[i]
    
    return nouvelle_cle

def attaque_mcmc_permutation(cryptogramme, stats_reference, longueur_cle, iterations=15000, top_n=5):
    """
    Boucle principale MCMC pour la permutation. Renvoie les 'top_n' meilleures solutions.
    """
    cle_actuelle = list(range(longueur_cle))
    random.shuffle(cle_actuelle)
    
    score_actuel = calculer_score_log(dechiffrer_permutation(cryptogramme, cle_actuelle), stats_reference)
    
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer_permutation(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC pour une permutation de longueur {longueur_cle}...")
    
    for i in range(iterations):
        cle_proposee = muter_permutation(cle_actuelle)
        texte_propose = dechiffrer_permutation(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        diff_score = score_propose - score_actuel
        
        if diff_score > 0:
            accepter = True
        else:
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter:
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            cle_str = str(cle_actuelle)
            if not any(c_str == cle_str for _, _, _, c_str in top_solutions):
                top_solutions.append((score_actuel, cle_actuelle.copy(), texte_propose, cle_str))
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                top_solutions = top_solutions[:top_n]
                
        if i % 1000 == 0:
            meilleur_score = top_solutions[0][0]
            meilleure_cle_apercu = top_solutions[0][1]
            texte_apercu = top_solutions[0][2][:50]
            print(f"Itération {i:5d} | Score : {meilleur_score:8.2f} | Clé : {meilleure_cle_apercu} | {texte_apercu}...")
            
    return [(score, cle, texte) for score, cle, texte, _ in top_solutions]


if __name__ == "__main__":
    # --- 1. PRÉPARATION COMMUNE (Statistiques de référence) ---
    print("Récupération de la page Wikipédia de référence pour les statistiques (français)...")
    texte_brut_ref = recuperer_texte_mediawiki("https://fr.wikipedia.org/wiki/Château")
    stats_digrammes_ref = statistiques_digrammes(nettoyer_texte(texte_brut_ref))
    
    # --- 2. SAISIE UTILISATEUR ---
    print("\n" + "="*50)
    print("   SAISIE DU TEXTE À DÉCHIFFRER")
    print("="*50)
    
    choix = input("Voulez-vous fournir une URL Wikipédia (1) ou taper/coller le texte directement (2) ? [1/2] : ").strip()
    
    if choix == "1":
        url_user = input("Entrez l'URL (ex: https://fr.wikipedia.org/wiki/Cryptographie) : ").strip()
        texte_brut_user = recuperer_texte_mediawiki(url_user)
    else:
        texte_brut_user = input("Collez ou tapez votre texte ici : ").strip()
        
    # Conversion en texte brut (27 caractères : majuscules, espaces, sans accents)
    texte_propre_user = nettoyer_texte(texte_brut_user)
    
    if len(texte_propre_user) < 300:
        print("\n[Attention] Votre texte fait moins de 300 caractères. L'attaque MCMC risque de manquer de données statistiques pour converger parfaitement.")
        
    est_deja_chiffre = input("\nCe texte est-il DÉJÀ chiffré (cryptogramme) ? (o/n) : ").strip().lower()

    # On limite la longueur à ~800 caractères max pour que le calcul reste rapide (et suffisant)
    texte_cible = texte_propre_user[:800]
    
    # --- 3. PRÉPARATION DES CRYPTOGRAMMES ---
    if est_deja_chiffre == 'n':
        print("\n[Simulation] Chiffrement secret du texte en cours pour le test...")
        # Substitution
        alphabet_test = extraire_alphabet(texte_cible)
        cle_sec_sub = generer_cle_aleatoire(alphabet_test)
        crypto_sub = chiffrer(texte_cible, cle_sec_sub)
        
        # Permutation (longueur 4 fixée pour la simulation)
        longueur_perm = 4
        cle_sec_perm = list(range(longueur_perm))
        random.shuffle(cle_sec_perm)
        crypto_perm = chiffrer_permutation(texte_cible, cle_sec_perm)
    else:
        crypto_sub = texte_cible
        longueur_perm = int(input("Pour l'attaque par permutation, quelle longueur de clé tester ? (ex: 4) : ").strip())
        
        # Si le cryptogramme n'est pas un multiple exact de la longueur, on le tronque proprement 
        # pour éviter l'erreur de padding lors du déchiffrement par bloc
        reste = len(texte_cible) % longueur_perm
        crypto_perm = texte_cible if reste == 0 else texte_cible[:-reste]


    # --- 4. EXÉCUTION DES ATTAQUES ---
    print("\n" + "="*50)
    print("   LANCEMENT DES ATTAQUES MCMC")
    print("="*50)
    
    print(f"\n[SUBSTITUTION] Cryptogramme analysé (extrait) :\n{crypto_sub[:100]}...\n")
    famille_solutions_sub = attaque_mcmc_substitution(crypto_sub, stats_digrammes_ref, iterations=25000, top_n=5)
    
    print("\n--- RÉSULTAT SUBSTITUTION ---")
    for rang, (score, cle, texte) in enumerate(famille_solutions_sub, 1):
        print(f"[Solution #{rang}] Score: {score:.2f} | Extrait: {texte[:120]}...")

    print(f"\n\n[PERMUTATION] Cryptogramme analysé (extrait) :\n{crypto_perm[:100]}...\n")
    famille_solutions_perm = attaque_mcmc_permutation(crypto_perm, stats_digrammes_ref, longueur_cle=longueur_perm, iterations=15000, top_n=5)
    
    print("\n--- RÉSULTAT PERMUTATION ---")
    for rang, (score, cle, texte) in enumerate(famille_solutions_perm, 1):
        print(f"[Solution #{rang}] Score: {score:.2f} | Clé: {cle} | Extrait: {texte[:100]}...")