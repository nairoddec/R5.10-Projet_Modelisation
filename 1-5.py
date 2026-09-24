import math
import random

# Importation de tes propres fonctions (adapte les noms de fichiers si besoin)
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
from substitution import chiffrer, dechiffrer, extraire_alphabet, generer_cle_aleatoire
from permutation import dechiffrer_permutation, chiffrer_permutation
# On importe la fonction de ton exercice 1.2
from outils_digrammes import statistiques_digrammes 

def calculer_score_log(texte, stats_reference):
    """
    Calcule le score de crédibilité d'un texte déchiffré en utilisant les logarithmes.
    """
    score = 0.0
    
    for i in range(len(texte) - 1):
        xy = texte[i:i+2] # Récupère le digramme (ex: "ES")
        
        # On va chercher le nombre d'occurrences de "xy" dans le vrai français.
        # .get(xy, {}) renvoie un dico vide si le digramme n'existe pas du tout.
        occurrences = stats_reference.get(xy, {}).get("occurrences", 0)
        
        # Formule du sujet : r(x,y) = 1 + occurrences
        r_xy = 1 + occurrences
        
        score += math.log(r_xy)
        
    return score

def muter_substitution(cle_actuelle):
    """
    Crée un état voisin en échangeant la position de deux lettres chiffrées.
    """
    nouvelle_cle = cle_actuelle.copy()
    lettres_claires = list(nouvelle_cle.keys())
    
    # Pioche deux lettres au hasard
    l1, l2 = random.sample(lettres_claires, 2)
    
    # Échange (transposition)
    nouvelle_cle[l1], nouvelle_cle[l2] = nouvelle_cle[l2], nouvelle_cle[l1]
    
    return nouvelle_cle

def attaque_mcmc_substitution(cryptogramme, stats_reference, iterations=15000):
    """
    Boucle principale de la chaîne de Markov Monte-Carlo.
    """
    alphabet = extraire_alphabet(cryptogramme)
    
    # 1. État initial k
    cle_actuelle = generer_cle_aleatoire(alphabet)
    score_actuel = calculer_score_log(dechiffrer(cryptogramme, cle_actuelle), stats_reference)
    
    meilleure_cle = cle_actuelle
    meilleur_score = score_actuel
    
    print("\nLancement de l'attaque MCMC (Patientez quelques secondes)...\n")
    
    # 2. Boucle de transitions
    for i in range(iterations):
        # A. Mutation (état k')
        cle_proposee = muter_substitution(cle_actuelle)
        
        # B. Évaluation
        texte_propose = dechiffrer(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        # C. Règle de sélection
        diff_score = score_propose - score_actuel
        
        if diff_score > 0:
            accepter = True
        else:
            # Si le score est moins bon, on l'accepte avec une probabilité mathématique
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        # D. Transition
        if accepter:
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            # Sauvegarde absolue
            if score_actuel > meilleur_score:
                meilleur_score = score_actuel
                meilleure_cle = cle_actuelle.copy()
                
        # Affichage régulier
        if i % 1000 == 0:
            texte_apercu = dechiffrer(cryptogramme, meilleure_cle)[:50]
            print(f"Itération {i:5d} | Score : {meilleur_score:8.2f} | {texte_apercu}...")
            
    return meilleure_cle, dechiffrer(cryptogramme, meilleure_cle)


def muter_permutation(cle_actuelle):
    """
    Crée un état voisin en déplaçant un sous-bloc (ici, échange de 2 positions).
    """
    nouvelle_cle = cle_actuelle.copy()
    longueur = len(nouvelle_cle)
    
    # Pioche deux indices au hasard
    i, j = random.sample(range(longueur), 2)
    
    # Échange les valeurs à ces indices
    nouvelle_cle[i], nouvelle_cle[j] = nouvelle_cle[j], nouvelle_cle[i]
    
    return nouvelle_cle

def attaque_mcmc_permutation(cryptogramme, stats_reference, longueur_cle, iterations=15000):
    """
    Boucle principale MCMC adaptée à la permutation pour une longueur l fixée.
    """
    # 1. État initial k (une liste de 0 à l-1, mélangée)
    cle_actuelle = list(range(longueur_cle))
    random.shuffle(cle_actuelle)
    
    score_actuel = calculer_score_log(dechiffrer_permutation(cryptogramme, cle_actuelle), stats_reference)
    
    meilleure_cle = cle_actuelle.copy()
    meilleur_score = score_actuel
    
    print(f"\nLancement de l'attaque MCMC pour une permutation de longueur {longueur_cle}...")
    
    # 2. Boucle de transitions
    for i in range(iterations):
        # A. Mutation
        cle_proposee = muter_permutation(cle_actuelle)
        
        # B. Évaluation
        texte_propose = dechiffrer_permutation(cryptogramme, cle_proposee)
        score_propose = calculer_score_log(texte_propose, stats_reference)
        
        # C. Sélection
        diff_score = score_propose - score_actuel
        
        if diff_score > 0:
            accepter = True
        else:
            U = random.uniform(0, 1)
            accepter = U < math.exp(diff_score)
            
        # D. Transition
        if accepter:
            cle_actuelle = cle_proposee
            score_actuel = score_propose
            
            # Sauvegarde absolue
            if score_actuel > meilleur_score:
                meilleur_score = score_actuel
                meilleure_cle = cle_actuelle.copy()
                
        # Affichage
        if i % 1000 == 0:
            texte_apercu = dechiffrer_permutation(cryptogramme, meilleure_cle)[:50]
            print(f"Itération {i:5d} | Score : {meilleur_score:8.2f} | Clé : {meilleure_cle} | {texte_apercu}...")
            
    return meilleure_cle, dechiffrer_permutation(cryptogramme, meilleure_cle)






if __name__ == "__main__":
    # --- 1. PRÉPARATION COMMUNE ---
    print("Récupération de la page Wikipédia de référence...")
    texte_brut_ref = recuperer_texte_mediawiki("https://fr.wikipedia.org/wiki/Château")
    texte_ref = nettoyer_texte(texte_brut_ref)
    
    print("Calcul des statistiques des digrammes...")
    stats_digrammes_ref = statistiques_digrammes(texte_ref)
    
    
    # --- 2. TEST : ATTAQUE PAR SUBSTITUTION ---
    print("\n" + "="*50)
    print("   TEST 1 : ATTAQUE MCMC PAR SUBSTITUTION")
    print("="*50)
    
    message_secret_sub = "CECI EST UN MESSAGE SECRET QUE NOUS ALLONS TENTER DE DECHIFFRER AVEC NOTRE SUPER ALGORITHME MCMC"
    alphabet_test = extraire_alphabet(message_secret_sub)
    cle_secrete_sub = generer_cle_aleatoire(alphabet_test)
    cryptogramme_sub = chiffrer(message_secret_sub, cle_secrete_sub)
    
    print(f"Cryptogramme à casser :\n{cryptogramme_sub}\n")
    
    cle_trouvee_sub, texte_trouve_sub = attaque_mcmc_substitution(cryptogramme_sub, stats_digrammes_ref, iterations=15000)
    
    print("\n--- RÉSULTAT FINAL SUBSTITUTION ---")
    print(texte_trouve_sub)


    # --- 3. TEST : ATTAQUE PAR PERMUTATION ---
    print("\n\n" + "="*50)
    print("   TEST 2 : ATTAQUE MCMC PAR PERMUTATION")
    print("="*50)
    
    message_secret_perm = "L ALGORITHME DOIT AUSSI ETRE CAPABLE DE RETROUVER L ORDRE DES BLOCS POUR LA PERMUTATION"
    longueur_l = 4
    # On définit une clé secrète de longueur 4 (ex: [2, 0, 3, 1])
    cle_secrete_perm = list(range(longueur_l))
    random.shuffle(cle_secrete_perm) 
    
    cryptogramme_perm = chiffrer_permutation(message_secret_perm, cle_secrete_perm)
    
    print(f"Clé secrète utilisée : {cle_secrete_perm}")
    print(f"Cryptogramme à casser :\n{cryptogramme_perm}\n")
    
    cle_trouvee_perm, texte_trouve_perm = attaque_mcmc_permutation(cryptogramme_perm, stats_digrammes_ref, longueur_cle=longueur_l, iterations=10000)
    
    print("\n--- RÉSULTAT FINAL PERMUTATION ---")
    print(f"Clé trouvée : {cle_trouvee_perm}")
    print(f"Texte déchiffré : {texte_trouve_perm}")