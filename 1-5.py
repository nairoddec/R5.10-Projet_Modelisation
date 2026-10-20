import math
import random

## Importation des fonctions
# 1.2
from outils_digrammes import statistiques_digrammes 
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
# 1.3
from substitution import chiffrer, dechiffrer, extraire_alphabet, generer_cle_aleatoire
# 1.4
from permutation import dechiffrer_permutation, chiffrer_permutation


def calculer_score_log(texte_dechiffre, stats_reference) :
    """
    Calcule le score S(k) en utilisant les logarithmes et la fonction d'analyse de digrammes.
    """
    score = 0.0
    stats_texte_actuel = statistiques_digrammes(texte_dechiffre)
    for digramme, donnees in stats_texte_actuel.items() :
        f_k = donnees["occurrences"]
        occurrences_ref = stats_reference.get(digramme, {}).get("occurrences", 0)
        r_xy = 1 + occurrences_ref
        score += f_k * math.log(r_xy)
        
    return score

def muter_substitution(cle_actuelle) :
    """
    Crée un état voisin en échangeant la position de deux lettres chiffrées.
    """
    nouvelle_cle = cle_actuelle.copy()
    lettres_claires = list(nouvelle_cle.keys())
    
    l1, l2 = random.sample(lettres_claires, 2)
    nouvelle_cle[l1], nouvelle_cle[l2] = nouvelle_cle[l2], nouvelle_cle[l1]
    
    return nouvelle_cle

def attaque_mcmc_substitution(cryptogramme, stats_reference, iterations = 15000, top_n = 5) :
    """
    Boucle principale MCMC. Renvoie les 'top_n' meilleures solutions trouvées.
    """
    alphabet = extraire_alphabet(cryptogramme)
    
    cle_actuelle = generer_cle_aleatoire(alphabet)
    score_actuel = calculer_score_log(dechiffrer(cryptogramme, cle_actuelle), stats_reference)
    
    # Liste pour stocker les N meilleures solutions sous forme (score, cle, texte, identifiant_cle)
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC pour la substitution (Recherche des {top_n} meilleures solutions)\n")
    
    for i in range(iterations) :
        cle_proposee = muter_substitution(cle_actuelle)
        texte_propose = dechiffrer(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        diff_score = score_propose - score_actuel
        
        if diff_score > 0 :
            accepter = True
        else :
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter :
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            # Gestion du Top N des solutions uniques
            cle_str = str(cle_actuelle)
            # On vérifie si cette clé n'est pas déjà dans notre top
            if not any(c_str == cle_str for _, _, _, c_str in top_solutions) :
                top_solutions.append((score_actuel, cle_actuelle.copy(), texte_propose, cle_str))
                # Tri par score décroissant
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                # On ne garde que les N meilleures
                top_solutions = top_solutions[:top_n]
                
        if i % 1000 == 0 :
            # On affiche la meilleure solution du moment
            meilleur_score = top_solutions[0][0]
            texte_apercu = top_solutions[0][2][:50]
            print(f"Itération {i:5d} | Meilleur Score : {meilleur_score:8.2f} | {texte_apercu}...")
            
    # On renvoie la liste complète des tuples (score, cle, texte)
    return [(score, cle, texte) for score, cle, texte, _ in top_solutions]


def muter_permutation(cle_actuelle) :
    """
    Crée un état voisin en déplaçant un sous-bloc de la clé :
    on découpe un morceau contigu de la clé (de 1 à longueur-1 éléments),
    on le retire, puis on le réinsère à une autre position.
    Exemple : [3, 0, 2, 1, 4] -> on prend le sous-bloc [0, 2] et on le
    replace à la fin : [3, 1, 4, 0, 2].
    (Un sous-bloc de taille 1 correspond au déplacement d'un seul élément.)
    """
    longueur = len(cle_actuelle)
    if longueur < 2 :
        return cle_actuelle.copy()

    while True :
        # Choix du sous-bloc cle[debut:fin]
        debut = random.randint(0, longueur - 1)
        fin = random.randint(debut + 1, longueur)
        if fin - debut == longueur :
            continue  # bloc = clé entière : déplacement sans effet

        sous_bloc = cle_actuelle[debut:fin]
        reste = cle_actuelle[:debut] + cle_actuelle[fin:]

        # Position d'insertion dans le reste (différente de la position d'origine)
        position = random.randint(0, len(reste))
        if position == debut :
            continue

        return reste[:position] + sous_bloc + reste[position:]

def attaque_mcmc_permutation(cryptogramme, stats_reference, longueur_cle, iterations = 15000, top_n = 5) :
    """
    Boucle principale MCMC pour la permutation. Renvoie les 'top_n' meilleures solutions.
    """
    cle_actuelle = list(range(longueur_cle))
    random.shuffle(cle_actuelle)
    
    score_actuel = calculer_score_log(dechiffrer_permutation(cryptogramme, cle_actuelle), stats_reference)
    
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer_permutation(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC pour une permutation de longueur {longueur_cle} (Recherche des {top_n} meilleures solutions)\n")
    
    for i in range(iterations) :
        cle_proposee = muter_permutation(cle_actuelle)
        texte_propose = dechiffrer_permutation(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        diff_score = score_propose - score_actuel
        
        if diff_score > 0 :
            accepter = True
        else :
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter :
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            cle_str = str(cle_actuelle)
            if not any(c_str == cle_str for _, _, _, c_str in top_solutions) :
                top_solutions.append((score_actuel, cle_actuelle.copy(), texte_propose, cle_str))
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                top_solutions = top_solutions[:top_n]
                
        if i % 1000 == 0 :
            meilleur_score = top_solutions[0][0]
            meilleure_cle_apercu = top_solutions[0][1]
            texte_apercu = top_solutions[0][2][:50]
            print(f"Itération {i:5d} | Score : {meilleur_score:8.2f} | Clé : {meilleure_cle_apercu} | {texte_apercu}...")
            
    return [(score, cle, texte) for score, cle, texte, _ in top_solutions]


def attaque_permutation_toutes_longueurs(cryptogramme, stats_reference, l_min = 2, l_max = 8, iterations = 15000, top_n = 5) :
    """
    Lance l'attaque MCMC pour chaque longueur de clé l = l_min, ..., l_max
    (comme demandé dans le sujet : l = 2, puis l = 3, etc.).
    Renvoie un dictionnaire {l: liste des top_n solutions (score, cle, texte)}.
    L'humain choisit ensuite entre toutes les propositions.
    """
    resultats = {}
    for l in range(l_min, l_max + 1) :
        # Le cryptogramme doit être un multiple de l : on tronque le reste
        reste = len(cryptogramme) % l
        crypto_l = cryptogramme if reste == 0 else cryptogramme[:-reste]
        resultats[l] = attaque_mcmc_permutation(crypto_l, stats_reference, longueur_cle=l,
                                                iterations=iterations, top_n=top_n)
    return resultats


if __name__ == "__main__" :
    # 1. RÉCUPÉRATION DES STATISTIQUES DE RÉFÉRENCE
    print("\nRécupération de la page Wikipédia de référence (https://fr.wikipedia.org/wiki/Château) pour les statistiques de digrammes")
    texte_brut_ref = recuperer_texte_mediawiki("https://fr.wikipedia.org/wiki/Château") # grâce à fonction_outils.py
    stats_digrammes_ref = statistiques_digrammes(nettoyer_texte(texte_brut_ref)) # grâce à outils_digrammes.py
    
    # 2. SAISIE DU TEXTE À ANALYSER
    print("\n" + "="*19)
    print("  SAISIE DU TEXTE  ")
    print("="*19)
    
    choix = input("Voulez-vous fournir une URL Wikipédia (1) ou taper/coller le texte directement (2) ? [1/2] : ").strip()
    
    if choix == "1" :
        url_user = input("Entrez l'URL (ex : https://fr.wikipedia.org/wiki/Cryptographie) : ").strip()
        texte_brut_user = recuperer_texte_mediawiki(url_user)
    else :
        texte_brut_user = input("Collez ou tapez votre texte ici : ")
        
    est_deja_chiffre = input("\nCe texte est-il déjà chiffré ? (o/n) : ").strip().lower()

    if est_deja_chiffre == 'o' :
        # IMPORTANT : on NE nettoie PAS un cryptogramme. Dans une permutation (ou une
        # substitution avec espace), les espaces sont des caractères du cryptogramme :
        # nettoyer_texte() fusionnerait les espaces consécutifs et décalerait les blocs.
        texte_propre_user = texte_brut_user.replace("\r", "").replace("\n", "")
    else :
        # Conversion en texte brut (27 caractères : majuscules, espaces, sans accents)
        texte_propre_user = nettoyer_texte(texte_brut_user)

    if len(texte_propre_user) < 300 :
        print("\n[Attention] Votre texte fait moins de 300 caractères. L'attaque MCMC risque de manquer de données statistiques pour converger parfaitement.")


    # On limite la longueur
    texte_cible_sub = texte_propre_user[:10000]
    texte_cible_perm = texte_propre_user[:1000]
    
    # 3. CHIFFREMENT DU TEXTE POUR LE TEST (si nécessaire)
    if est_deja_chiffre == 'n' :
        print("\nChiffrement secret du texte en cours pour le test")
        # Substitution
        alphabet_test = extraire_alphabet(texte_cible_sub)
        cle_sec_sub = generer_cle_aleatoire(alphabet_test)
        crypto_sub = chiffrer(texte_cible_sub, cle_sec_sub)
        
        # Permutation (longueur 4 fixée pour la simulation, mais l'attaque ne la connaît pas :
        # elle testera toutes les longueurs de l_min à l_max)
        longueur_perm_secrete = 4
        cle_sec_perm = list(range(longueur_perm_secrete))
        random.shuffle(cle_sec_perm)
        crypto_perm = chiffrer_permutation(texte_cible_perm, cle_sec_perm)
        print(f"Clé de permutation secrète : {cle_sec_perm}")
    else :
        crypto_sub = texte_cible_sub
        crypto_perm = texte_cible_perm

    saisie_l_max = input("Pour l'attaque par permutation, tester les longueurs de clé de 2 jusqu'à ? (ex : 8) : ").strip()
    l_max_perm = int(saisie_l_max) if saisie_l_max else 8


    # 4. LANCEMENT DES ATTAQUES MCMC
    print("\n" + "="*31)
    print("  LANCEMENT DES ATTAQUES MCMC  ")
    print("="*31)
    
    print(f"\n- [SUBSTITUTION] Cryptogramme analysé (extrait) :\n{crypto_sub[:100]}...\n")
    famille_solutions_sub = attaque_mcmc_substitution(crypto_sub, stats_digrammes_ref, iterations = 25000, top_n = 5)
    
    print("\n= RÉSULTAT SUBSTITUTION")
    for rang, (score, cle, texte) in enumerate(famille_solutions_sub, 1) :
        print(f"[Solution #{rang}] Score : {score:.2f} | Extrait : {texte[:120]}...")

    print(f"\n\n- [PERMUTATION] Cryptogramme analysé (extrait) :\n{crypto_perm[:100]}...\n")
    solutions_perm_par_l = attaque_permutation_toutes_longueurs(
        crypto_perm, stats_digrammes_ref, l_min = 2, l_max = l_max_perm, iterations = 15000, top_n = 5)

    print("\n= RÉSULTAT PERMUTATION (propositions pour chaque longueur l testée)")
    for l, solutions in solutions_perm_par_l.items() :
        print(f"\n- Longueur de clé l = {l}")
        for rang, (score, cle, texte) in enumerate(solutions, 1) :
            print(f"[l = {l} | Solution #{rang}] Score : {score:.2f} | Clé : {cle} | Extrait : {texte[:80]}...")

    # Récapitulatif 
    print("\n= RÉCAPITULATIF Permutation : Meilleure proposition par longueur")
    for l, solutions in sorted(solutions_perm_par_l.items(), key=lambda kv: kv[1][0][0], reverse = True) :
        score, cle, texte = solutions[0]
        print(f"l = {l} | Score : {score:.2f} | Clé : {cle} | {texte[:80]}...")

    print("\n= RÉCAPITULATIF Substitution : Meilleures propositions")
    for rang, (score, cle, texte) in enumerate(famille_solutions_sub, 1) :
        print(f"[Solution #{rang}] Score : {score:.2f} | {texte[:80]}...")