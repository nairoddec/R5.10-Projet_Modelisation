"""
Projet Modélisations Mathématiques (R5.10) - Section 1.5 : Attaque MCMC

Principe général :
On veut décoder un texte sans connaître la clé secrète.
Pour cela, on utilise l'algorithme MCMC (Markov Chain Monte Carlo) :
1. On part d'une clé au hasard.
2. À chaque étape, on modifie légèrement la clé (mutation).
3. On regarde si le texte obtenu "ressemble plus" à du français grâce aux paires de lettres (bigrammes).
4. Si c'est meilleur, on garde la clé. Si c'est moins bon, on l'accepte parfois pour éviter de se bloquer.
5. On teste automatiquement la Substitution et la Permutation, puis on affiche le vainqueur.
"""

import math
import random

## Importation des fonctions utiles des autres fichiers
# Statistiques sur les paires de lettres (bigrammes)
from outils_digrammes import statistiques_digrammes 
# Outils de nettoyage et téléchargement Wikipédia
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
# Chiffrement / Déchiffrement par substitution (remplacement de lettres)
from substitution import chiffrer, dechiffrer, extraire_alphabet, generer_cle_aleatoire
# Chiffrement / Déchiffrement par permutation (mélange de positions)
from permutation import dechiffrer_permutation, chiffrer_permutation


def saisir_texte_multiligne(invite) :
    """
    Lit un texte sur une ou plusieurs lignes.
    La saisie se termine en appuyant sur Entrée sur une ligne vide, ou en tapant FIN.
    """
    print(f"{invite}\n(collez votre texte, puis appuyez 2× sur Entrée pour valider) :")
    lignes = []
    while True :
        try :
            ligne = input()
        except EOFError :
            break
        nettoyee = ligne.strip()
        if nettoyee.upper() == "FIN" or (not nettoyee and lignes):
            break
        lignes.append(ligne)
    return "\n".join(lignes)


#  LE SCORE : mesure à quel point un texte "ressemble" à du français

def calculer_score_log(texte_dechiffre, stats_reference) :
    """
    Calcule le score S(k) en utilisant les logarithmes et la fonction d'analyse de digrammes.
    """
    # Le sujet définit S(k) = produit de r(x,y)^f_k(x,y).
    # Un produit de centaines de milliers de facteurs donnerait un nombre
    # impossible à stocker : on passe au logarithme, ce qui le transforme en somme :
    #       log S(k) = somme de f_k(x,y) * log r(x,y)
    # Comme log est croissant, comparer deux scores revient à comparer leurs logs.
    score = 0.0

    # Bigrammes du texte obtenu en déchiffrant avec la clé testée
    stats_texte_actuel = statistiques_digrammes(texte_dechiffre)

    for digramme, donnees in stats_texte_actuel.items() :
        # f_k : nombre de fois où ce bigramme apparaît dans le texte déchiffré
        f_k = donnees["occurrences"]

        # Nombre de fois où il apparaît dans le texte de référence (0 s'il n'y est jamais)
        occurrences_ref = stats_reference.get(digramme, {}).get("occurrences", 0)

        # r(x,y) = 1 + occurrences dans la référence. Le "+1" évite log(0)
        # pour les bigrammes jamais vus dans la référence.
        r_xy = 1 + occurrences_ref

        # Un bigramme fréquent en français (r grand) fait monter le score,
        # et d'autant plus qu'il apparaît souvent dans le texte déchiffré (f_k grand).
        score += f_k * math.log(r_xy)
        
    return score


#  SUBSTITUTION : mutation puis boucle MCMC

def muter_substitution(cle_actuelle) :
    """
    Crée un état voisin en échangeant la position de deux lettres chiffrées.
    """
    # On travaille sur une copie pour ne pas modifier la clé actuelle :
    # si la mutation est refusée, on doit pouvoir revenir à l'ancienne clé.
    nouvelle_cle = cle_actuelle.copy()

    # La clé est un dictionnaire {lettre claire : lettre chiffrée}
    lettres_claires = list(nouvelle_cle.keys())
    
    # On tire 2 lettres claires différentes au hasard...
    l1, l2 = random.sample(lettres_claires, 2)

    # ... et on échange leurs lettres chiffrées (une transposition).
    # La clé reste une permutation valide : chaque lettre chiffrée est toujours utilisée une fois.
    nouvelle_cle[l1], nouvelle_cle[l2] = nouvelle_cle[l2], nouvelle_cle[l1]
    
    return nouvelle_cle

def attaque_mcmc_substitution(cryptogramme, stats_reference, iterations = 15000, top_n = 5) :
    """
    Boucle principale MCMC. Renvoie les 'top_n' meilleures solutions trouvées.
    """
    # Caractères présents dans le cryptogramme (espace inclus) :
    # la clé sera une permutation de cet alphabet.
    alphabet = extraire_alphabet(cryptogramme)
    
    # État initial : une clé aléatoire, et son score
    cle_actuelle = generer_cle_aleatoire(alphabet)
    score_actuel = calculer_score_log(dechiffrer(cryptogramme, cle_actuelle), stats_reference)
    
    # Liste pour stocker les N meilleures solutions sous forme (score, cle, texte, identifiant_cle)
    # (identifiant_cle = la clé écrite en texte, pour détecter les doublons facilement)
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC pour la substitution (Recherche des {top_n} meilleures solutions)\n")
    
    # Chaque tour de boucle = une transition de la chaîne de Markov
    for i in range(iterations) :
        # --- Étape 1 : MUTATION --- on propose une clé voisine, et on la score
        cle_proposee = muter_substitution(cle_actuelle)
        texte_propose = dechiffrer(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        # Différence des logs = log du rapport S(k')/S(k)
        diff_score = score_propose - score_actuel
        
        # --- Étape 2 : SÉLECTION --- règle du sujet : accepter si U < S(k')/S(k)
        if diff_score > 0 :
            # Nouvelle clé meilleure : le rapport S(k')/S(k) est > 1, donc U < rapport
            # est toujours vrai : on accepte sans tirer U.
            accepter = True
        else :
            # Nouvelle clé moins bonne : on l'accepte quand même avec la probabilité
            # exp(diff_score) = S(k')/S(k) (< 1). Plus elle est mauvaise, moins c'est probable.
            # Cela permet de sortir d'un piège (maximum local) au lieu de rester bloqué.
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter :
            # On se déplace vers le nouvel état. Sinon on reste dans l'état actuel.
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
                
        # Suivi de la progression : un affichage toutes les 1000 itérations
        if i % 1000 == 0 :
            # On affiche la meilleure solution du moment
            meilleur_score = top_solutions[0][0]
            texte_apercu = top_solutions[0][2][:50]
            print(f"Itération {i:5d} | Meilleur Score : {meilleur_score:8.2f} | {texte_apercu}...")
            
    # On renvoie la liste complète des tuples (score, cle, texte)
    return [(score, cle, texte) for score, cle, texte, _ in top_solutions]


#  PERMUTATION : mutation puis boucle MCMC

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
    # Une clé de longueur 0 ou 1 n'a aucun voisin différent
    if longueur < 2 :
        return cle_actuelle.copy()

    # On recommence tant que la mutation tirée ne change rien à la clé
    while True :
        # Choix du sous-bloc cle[debut:fin]
        debut = random.randint(0, longueur - 1)
        fin = random.randint(debut + 1, longueur)
        if fin - debut == longueur :
            continue  # bloc = clé entière : déplacement sans effet

        # Le sous-bloc qu'on déplace, et ce qui reste de la clé sans lui
        sous_bloc = cle_actuelle[debut:fin]
        reste = cle_actuelle[:debut] + cle_actuelle[fin:]

        # Position d'insertion dans le reste (différente de la position d'origine)
        position = random.randint(0, len(reste))
        if position == debut :
            continue  # réinsérer au même endroit redonne la même clé

        # On recolle : début du reste + sous-bloc + fin du reste
        return reste[:position] + sous_bloc + reste[position:]

def attaque_mcmc_permutation(cryptogramme, stats_reference, longueur_cle, iterations = 15000, top_n = 5) :
    """
    Boucle principale MCMC pour la permutation. Renvoie les 'top_n' meilleures solutions.
    """
    # État initial : une permutation aléatoire de [0, 1, ..., longueur_cle - 1]
    cle_actuelle = list(range(longueur_cle))
    random.shuffle(cle_actuelle)
    
    # Score de l'état initial (déchiffrement par permutation inverse)
    score_actuel = calculer_score_log(dechiffrer_permutation(cryptogramme, cle_actuelle), stats_reference)
    
    # Même structure que pour la substitution : (score, cle, texte, identifiant_cle)
    top_solutions = [(score_actuel, cle_actuelle.copy(), dechiffrer_permutation(cryptogramme, cle_actuelle), str(cle_actuelle))]
    
    print(f"\nLancement de l'attaque MCMC pour une permutation de longueur {longueur_cle} (Recherche des {top_n} meilleures solutions)\n")
    
    # Même algorithme que pour la substitution : seuls la mutation et le déchiffrement changent
    for i in range(iterations) :
        # Mutation : on déplace un sous-bloc de la clé, puis on score
        cle_proposee = muter_permutation(cle_actuelle)
        texte_propose = dechiffrer_permutation(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        diff_score = score_propose - score_actuel
        
        # Sélection (règle de Metropolis, voir la version substitution)
        if diff_score > 0 :
            accepter = True
        else :
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        if accepter :
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            # Mise à jour du Top N (clés uniques, triées par score décroissant)
            cle_str = str(cle_actuelle)
            if not any(c_str == cle_str for _, _, _, c_str in top_solutions) :
                top_solutions.append((score_actuel, cle_actuelle.copy(), texte_propose, cle_str))
                top_solutions.sort(key=lambda x: x[0], reverse=True)
                top_solutions = top_solutions[:top_n]
                
        # Suivi de la progression : ici on affiche aussi la clé de la meilleure solution
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
    Le nombre d'itérations est adapté à la taille de l'espace des clés (l!).
    """
    # On ne connaît pas la longueur de la clé : on les essaie toutes
    resultats = {}
    for l in range(l_min, l_max + 1) :
        # Le cryptogramme doit être un multiple de l : on tronque le reste
        reste = len(cryptogramme) % l
        crypto_l = cryptogramme if reste == 0 else cryptogramme[:-reste]

        # Adaptation du nombre d'itérations selon la factorielle l! :
        # Inutile de faire 15000 itérations pour l=2 (2 clés) ou l=3 (6 clés)
        nb_permutations = math.factorial(l)
        iter_l = min(iterations, max(60, nb_permutations * 5))

        resultats[l] = attaque_mcmc_permutation(crypto_l, stats_reference, longueur_cle=l,
                                                iterations=iter_l, top_n=top_n)
    return resultats



#  PROGRAMME PRINCIPAL

if __name__ == "__main__" :
    # =========================================================================
    # 1. RÉCUPÉRATION DES STATISTIQUES DE RÉFÉRENCE (La langue française)
    # =========================================================================
    # On télécharge un article Wikipédia pour apprendre les paires de lettres
    # naturelles du français (les bigrammes comme 'ES', 'DE', 'QU', etc.)
    print("\nRécupération de la page Wikipédia de référence (https://fr.wikipedia.org/wiki/Château) pour les statistiques de digrammes")
    texte_brut_ref = recuperer_texte_mediawiki("https://fr.wikipedia.org/wiki/Château")
    stats_digrammes_ref = statistiques_digrammes(nettoyer_texte(texte_brut_ref))
    
    # =========================================================================
    # 2. SAISIE DU TEXTE À ANALYSER
    # =========================================================================
    print("\n" + "="*19)
    print("  SAISIE DU TEXTE  ")
    print("="*19)
    
    # Trois modes possibles : lien Wikipédia, copier-coller, ou fichier texte (ex: crypto01.txt)
    print("1. Fournir une URL Wikipédia")
    print("2. Taper / coller le texte directement")
    print("3. Lire depuis un fichier texte (recommandé pour les longs textes)")
    choix = input("Votre choix [1/2/3] (défaut 2) : ").strip() or "2"
    
    if choix == "1" :
        url_user = input("Entrez l'URL (ex : https://fr.wikipedia.org/wiki/Cryptographie) : ").strip()
        texte_brut_user = recuperer_texte_mediawiki(url_user)
    elif choix == "3" :
        fichier_nom = input("Nom ou chemin du fichier (ex: texte.txt) [défaut texte.txt] : ").strip() or "texte.txt"
        with open(fichier_nom, "r", encoding="utf-8") as f:
            texte_brut_user = f.read()
        print(f"Fichier '{fichier_nom}' chargé avec succès ({len(texte_brut_user)} caractères).")
    else :
        # Saisie directe au clavier
        texte_brut_user = saisir_texte_multiligne("Collez ou tapez votre texte ici :")
        
    # On demande si le texte est déjà codé ou s'il s'agit d'un texte clair à tester
    est_deja_chiffre = input("\nCe texte est-il déjà chiffré ? (o/n) : ").strip().lower()

    if est_deja_chiffre == 'o' :
        # Pour un texte chiffré, on garde les espaces intacts pour ne pas casser l'alignement
        texte_propre_user = texte_brut_user.replace("\r", "").replace("\n", "")
    else :
        # Pour un texte clair, on le nettoie (majuscules A-Z et espaces simples)
        texte_propre_user = nettoyer_texte(texte_brut_user)

    # Avertissement si le texte est trop court (il faut assez de lettres pour les statistiques)
    if len(texte_propre_user) < 300 :
        print("\n[Attention] Votre texte fait moins de 300 caractères. L'attaque MCMC risque de manquer de données statistiques pour converger parfaitement.")

    # On limite la taille pour garder un temps de calcul raisonnable
    texte_cible_sub = texte_propre_user[:5000]   # substitution
    texte_cible_perm = texte_propre_user[:1000]  # permutation
    
    # =========================================================================
    # 3. CHIFFREMENT DE TEST (uniquement si le texte entré était en clair)
    # =========================================================================
    if est_deja_chiffre == 'n' :
        print("\nChiffrement secret du texte en cours pour le test")
        # Substitution aléatoire
        alphabet_test = extraire_alphabet(texte_cible_sub)
        cle_sec_sub = generer_cle_aleatoire(alphabet_test)
        crypto_sub = chiffrer(texte_cible_sub, cle_sec_sub)
        
        # Permutation aléatoire (longueur 4 pour l'exemple)
        longueur_perm_secrete = 4
        cle_sec_perm = list(range(longueur_perm_secrete))
        random.shuffle(cle_sec_perm)
        crypto_perm = chiffrer_permutation(texte_cible_perm, cle_sec_perm)
        print(f"Clé de permutation secrète : {cle_sec_perm}")
    else :
        # Le texte est déjà chiffré : on l'utilise directement
        crypto_sub = texte_cible_sub
        crypto_perm = texte_cible_perm

    # On demande jusqu'à quelle taille de bloc tester pour la permutation
    saisie_l_max = input("Pour l'attaque par permutation, tester les longueurs de clé de 2 jusqu'à ? (ex : 8) : ").strip()
    l_max_perm = int(saisie_l_max) if saisie_l_max else 8


    # =========================================================================
    # 4. LANCEMENT DES ATTAQUES MCMC
    # =========================================================================
    print("\n" + "="*31)
    print("  LANCEMENT DES ATTAQUES MCMC  ")
    print("="*31)
    
    # --- A. Attaque sur l'hypothèse de la Substitution (25 000 itérations) ---
    print(f"\n- [SUBSTITUTION] Cryptogramme analysé (extrait) :\n{crypto_sub[:100]}...\n")
    famille_solutions_sub = attaque_mcmc_substitution(crypto_sub, stats_digrammes_ref, iterations = 25000, top_n = 5)
    
    print("\n= RÉSULTAT SUBSTITUTION")
    for rang, (score, cle, texte) in enumerate(famille_solutions_sub, 1) :
        print(f"[Solution #{rang}] Score : {score:.2f} | Extrait : {texte[:120]}...")

    # --- B. Attaque sur l'hypothèse de la Permutation (test des longueurs de 2 à l_max) ---
    print(f"\n\n- [PERMUTATION] Cryptogramme analysé (extrait) :\n{crypto_perm[:100]}...\n")
    solutions_perm_par_l = attaque_permutation_toutes_longueurs(
        crypto_perm, stats_digrammes_ref, l_min = 2, l_max = l_max_perm, iterations = 15000, top_n = 5)

    # Détail : les 5 meilleures clés pour chaque longueur l testée
    print("\n= RÉSULTAT PERMUTATION (propositions pour chaque longueur l testée)")
    for l, solutions in solutions_perm_par_l.items() :
        print(f"\n- Longueur de clé l = {l}")
        for rang, (score, cle, texte) in enumerate(solutions, 1) :
            print(f"[l = {l} | Solution #{rang}] Score : {score:.2f} | Clé : {cle} | Extrait : {texte[:80]}...")

    # Récapitulatif 
    # Meilleure proposition de chaque longueur, classées par score décroissant :
    # c'est à l'humain de juger laquelle donne un texte lisible.
    print("\n= RÉCAPITULATIF Permutation : Meilleure proposition par longueur")
    for l, solutions in sorted(solutions_perm_par_l.items(), key=lambda kv: kv[1][0][0], reverse = True) :
        score, cle, texte = solutions[0]
        print(f"l = {l} | Score : {score:.2f} | Clé : {cle} | {texte[:80]}...")

    # Récapitulatif final des meilleures clés de substitution
    print("\n= RÉCAPITULATIF Substitution : Meilleures propositions")
    for rang, (score, cle, texte) in enumerate(famille_solutions_sub, 1) :
        print(f"[Solution #{rang}] Score : {score:.2f} | {texte[:80]}...")

    # =========================================================================
    # AFFICHAGE DU MEILLEUR RÉSULTAT GLOBAL (Substitution vs Permutation)
    # =========================================================================
    meilleur_sub = famille_solutions_sub[0]
    meilleure_perm_toutes = max((sols[0] for sols in solutions_perm_par_l.values()), key=lambda x: x[0])

    if meilleur_sub[0] >= meilleure_perm_toutes[0]:
        type_vainqueur = "Substitution"
        score_vainqueur = meilleur_sub[0]
        texte_vainqueur = meilleur_sub[2]
        cle_vainqueur = str(meilleur_sub[1])
    else:
        type_vainqueur = "Permutation"
        score_vainqueur = meilleure_perm_toutes[0]
        texte_vainqueur = meilleure_perm_toutes[2]
        cle_vainqueur = str(meilleure_perm_toutes[1])

    print("\n" + "="*80)
    print(f"Affichage meilleur résultat ({type_vainqueur} | Score = {score_vainqueur:.2f})")
    print("="*80)
    print(f"Clé trouvée : {cle_vainqueur}")
    print("\nExtrait du texte déchiffré :")
    print(texte_vainqueur[:500] + ("..." if len(texte_vainqueur) > 500 else ""))
    print("="*80 + "\n")