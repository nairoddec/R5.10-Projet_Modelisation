"""
Variante statistique : attaque de Vigenère SANS dictionnaire de clés,
grâce à l'indice de coïncidence (IC).

Étapes :
  1. Estimer la longueur L de la clé  -> IC moyen des L colonnes du cryptogramme.
  2. Retrouver chaque lettre de la clé -> chaque colonne est un chiffre de César,
     on garde le décalage dont les fréquences ressemblent le plus au français
     (test du khi-deux contre un texte de référence).

Utilisation :
    python attack_vigenere_ic.py
Le programme demande ensuite :
  - la page Wikipédia de référence (titre ou URL, Entrée = valeur par défaut) ;
  - la clé secrète de Vigenère à utiliser pour chiffrer le message.
"""

# Counter compte combien de fois chaque élément apparaît dans une séquence.
# Exemple : Counter("ABAC") -> {'A': 2, 'B': 1, 'C': 1}
from collections import Counter

# Outils du projet réutilisés :
#  - recuperer_texte_mediawiki : télécharge le texte d'une page Wikipédia
#  - nettoyer_texte            : majuscules, sans accents ni ponctuation
#  - extraire_alphabet         : liste des caractères présents dans un texte
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
from outils_digrammes import extraire_alphabet
# Chiffrement / déchiffrement de Vigenère déjà écrits pour l'attaque par
# dictionnaire. normaliser_cle nettoie une clé (majuscules, sans espaces).
from attack_vigenere import (chiffrement_vigenere, dechiffrement_vigenere,
                             normaliser_cle)


# 1. Indice de coïncidence

def indice_coincidence(texte: str) -> float :
    """IC = somme n_i (n_i - 1) / (N (N - 1)) : proba que 2 caractères tirés
    sans remise dans le texte soient identiques."""
    # n = N dans la formule : nombre total de caractères du texte
    n = len(texte)
    # Avec moins de 2 caractères, N(N-1) vaudrait 0 : on évite la division par 0
    if n < 2 :
        return 0.0
    # comptes[c] = n_i : nombre d'occurrences de chaque caractère c
    comptes = Counter(texte)
    # Numérateur : somme des n_i (n_i - 1) = nombre de paires de positions
    # qui portent le même caractère.
    # Dénominateur : N (N - 1) = nombre total de paires de positions.
    return sum(c * (c - 1) for c in comptes.values()) / (n * (n - 1))


def colonnes(texte: str, longueur: int) -> list[str]:
    """Découpe le texte en `longueur` colonnes (caractères de même rang mod L)."""
    # texte[i::longueur] : on part du caractère i puis on avance de `longueur`
    # en `longueur`. Exemple : colonnes("ABCDEFG", 3) -> ["ADG", "BE", "CF"]
    # Si `longueur` est la vraie longueur de la clé, tous les caractères d'une
    # colonne ont été chiffrés avec la même lettre de clé.
    return [texte[i::longueur] for i in range(longueur)]


def ic_moyen(texte: str, longueur: int) -> float:
    """IC moyen des colonnes pour une longueur de clé supposée."""
    # On découpe en colonnes, on calcule l'IC de chacune, puis la moyenne.
    cols = colonnes(texte, longueur)
    return sum(indice_coincidence(c) for c in cols) / len(cols)


def profil_ic(cryptogramme: str, longueur_max: int = 20) -> dict[int, float]:
    # Pour chaque longueur L de 1 à longueur_max, on calcule l'IC moyen des
    # colonnes. Résultat : un dictionnaire {L: IC moyen}, qui sert à tracer
    # le graphique. Un pic indique une longueur de clé probable.
    return {L: ic_moyen(cryptogramme, L) for L in range(1, longueur_max + 1)}


def estimer_longueur(profil: dict[int, float], ratio: float = 0.9) -> int:
    """Plus petite longueur dont l'IC atteint 90 % du maximum du profil.
    (Les multiples de la vraie longueur ont aussi un IC élevé : on veut le
    plus petit, pas le plus grand.)"""
    # Le plus grand IC observé dans le profil
    maximum = max(profil.values())
    # Le dictionnaire est parcouru dans l'ordre croissant de L : on renvoie
    # donc la PREMIÈRE longueur dont l'IC est proche du maximum.
    for L, valeur in profil.items():
        if valeur >= ratio * maximum:
            return L
    # Filet de sécurité : le maximum lui-même vérifie la condition ci-dessus,
    # donc on n'arrive normalement jamais ici.
    return max(profil, key=profil.get)


# 2. Retrouver la clé une fois L connue

def frequences_reference(texte_reference: str, alphabet: list[str]) -> dict:
    """Fréquences des caractères (avec +1 pour éviter les zéros)."""
    # Effectif de chaque caractère dans le texte de référence
    comptes = Counter(c for c in texte_reference if c in alphabet)
    # On ajoute 1 à l'effectif de chaque caractère (lissage) : un caractère
    # absent de la référence n'aura pas une fréquence nulle, ce qui ferait
    # diviser par zéro dans le khi-deux.
    total = sum(comptes[c] + 1 for c in alphabet)
    # Fréquence de chaque caractère : la somme vaut bien 1
    return {c: (comptes[c] + 1) / total for c in alphabet}


def khi_deux(colonne: str, freq_ref: dict) -> float:
    """Distance entre les fréquences observées dans la colonne et la référence."""
    # n = nombre de caractères de la colonne
    n = len(colonne)
    comptes = Counter(colonne)
    # Pour chaque caractère : (observé - attendu)² / attendu
    #  - observé = comptes[c] : combien de fois c apparaît dans la colonne
    #  - attendu = n * p      : combien de fois on l'attendrait si la colonne
    #                           suivait les fréquences de référence
    # Plus la somme est petite, plus la colonne ressemble au français.
    return sum(
        (comptes[c] - n * p) ** 2 / (n * p) for c, p in freq_ref.items()
    )


def retrouver_cle(cryptogramme: str, longueur: int, alphabet: list[str],
                  freq_ref: dict) -> str:
    """Pour chaque colonne, essaie les décalages possibles et garde le meilleur."""
    cle = []
    # Chaque colonne a été chiffrée avec une seule lettre de la clé :
    # on retrouve donc la clé lettre par lettre, colonne par colonne.
    for col in colonnes(cryptogramme, longueur):
        # Le meilleur score démarre à l'infini : le premier essai sera retenu
        meilleur_decalage, meilleur_score = None, float("inf")
        for lettre in alphabet:
            if lettre == " ":  # une clé ne contient jamais d'espace
                continue
            # on déchiffre la colonne avec une clé d'un seul caractère
            essai = dechiffrement_vigenere(col, lettre, alphabet)
            # Si c'est la bonne lettre, le texte obtenu a les fréquences du
            # français, donc un khi-deux petit.
            score = khi_deux(essai, freq_ref)
            # On garde la lettre qui donne le plus petit khi-deux
            if score < meilleur_score:
                meilleur_decalage, meilleur_score = lettre, score
        cle.append(meilleur_decalage)
    # Les lettres retenues, mises bout à bout, forment la clé complète
    return "".join(cle)


# 3. Affichage

def afficher_profil(profil: dict[int, float], ic_fr: float, ic_alea: float,
                    fichier_png: str = "profil_ic_vigenere.png") -> None:
    """Graphique matplotlib si disponible, sinon barres en texte."""
    try:
        import matplotlib
        # "Agg" : moteur qui écrit seulement dans un fichier (aucune fenêtre
        # ne s'ouvre). C'est pourquoi le graphique est à ouvrir à la main.
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 4))
        # Une barre par longueur L supposée, de hauteur IC moyen
        plt.bar(list(profil), list(profil.values()), color="steelblue")
        # Deux repères horizontaux : IC d'un texte français (vert) et IC d'un
        # texte où tous les caractères seraient équiprobables (rouge)
        plt.axhline(ic_fr, color="green", linestyle="--", label="IC français")
        plt.axhline(ic_alea, color="red", linestyle="--", label="IC aléatoire")
        plt.xticks(list(profil))
        plt.xlabel("Longueur de clé supposée L")
        plt.ylabel("IC moyen des colonnes")
        plt.legend()
        plt.tight_layout()
        plt.savefig(fichier_png, dpi=150)
        print(f"Graphique enregistré dans {fichier_png}")
    except ImportError:
        # matplotlib n'est pas installé : on se contente de l'affichage texte
        print("matplotlib absent : affichage texte")
    # Affichage texte : une ligne par L, avec une barre de '#' proportionnelle
    # à l'IC (la valeur est multipliée par 600 pour que la barre soit lisible)
    for L, valeur in profil.items():
        print(f"L={L:2d} | {valeur:.4f} | {'#' * int(valeur * 600)}")


# 4. Saisies utilisateur

URL_MESSAGE = "https://fr.wikipedia.org/wiki/Cathédrale"   # texte à chiffrer
REFERENCE_PAR_DEFAUT = "Château"                           # texte de référence


def construire_url(saisie: str) -> str:
    """Accepte une URL complète ou simplement un titre de page Wikipédia."""
    saisie = saisie.strip()
    # Déjà une URL : on la garde telle quelle
    if saisie.startswith("http"):
        return saisie
    # Sinon c'est un titre : "Château fort" -> .../wiki/Château_fort
    return "https://fr.wikipedia.org/wiki/" + saisie.replace(" ", "_")


def demander_reference() -> str:
    """Demande la page Wikipédia servant de texte de référence."""
    saisie = input(f"Page Wikipédia de référence (titre ou URL) "
                   f"[Entrée = {REFERENCE_PAR_DEFAUT}] : ").strip()
    # Si l'utilisateur appuie sur Entrée, saisie est une chaîne vide (donc
    # "fausse") : "or" renvoie alors la valeur par défaut.
    return construire_url(saisie or REFERENCE_PAR_DEFAUT)


def demander_cle(alphabet: list[str]) -> str:
    """Demande une clé et la redemande tant qu'elle n'est pas utilisable."""
    while True:
        saisie = input("Clé secrète de Vigenère (lettres uniquement) : ")
        # Même nettoyage que pour le texte : "clé!" devient "CLE"
        cle = normaliser_cle(saisie)
        # Rien d'exploitable après nettoyage : on redemande
        if not cle:
            print("  Clé vide ou sans lettre : recommence.")
            continue
        # Caractères de la clé qui n'existent pas dans l'alphabet du message
        # (le chiffrement repose sur la position des caractères dans l'alphabet)
        inconnus = sorted({c for c in cle if c not in alphabet})
        if inconnus:
            print(f"  Caractères absents de l'alphabet du message : {inconnus}")
            continue
        # On informe l'utilisateur si la clé a été modifiée par le nettoyage
        if cle != saisie:
            print(f"  Clé normalisée : {cle}")
        # return fait sortir de la boucle : la clé est valide
        return cle


# Ce bloc ne s'exécute que si on lance ce fichier directement (pas si un autre fichier l'importe).
if __name__ == "__main__":
    # Chargement des textes 
    url_reference = demander_reference()
    try:
        # Texte de référence : sert à mesurer l'IC du français et les fréquences
        texte_reference = nettoyer_texte(recuperer_texte_mediawiki(url_reference))
        # Message à chiffrer puis à attaquer
        message_clair = nettoyer_texte(recuperer_texte_mediawiki(URL_MESSAGE))
    except Exception as erreur:
        # Réseau coupé, page introuvable... : on arrête proprement
        print(f"Impossible de charger les textes : {erreur}")
        raise SystemExit(1)

    # Si la référence est la même page que le message, les fréquences viennent
    # du texte lui-même : l'attaque est alors trop facile.
    if url_reference.rstrip("/").lower() == URL_MESSAGE.lower():
        print("Attention : la référence est la même page que le message, "
              "le résultat sera trop favorable.")

    # Alphabet et clé
    # L'alphabet est construit à partir du message (hypothèse classique :
    # l'attaquant connaît l'alphabet, seule la clé est secrète).
    alphabet = extraire_alphabet(message_clair)
    vraie_cle = demander_cle(alphabet)

    # Valeurs de repère
    # IC du français : mesuré sur le texte de référence
    ic_fr = indice_coincidence(texte_reference)
    # IC "aléatoire" : formule théorique (aucun texte généré). 
    # Si les N caractères étaient équiprobables, N * (1/N)² = 1/N.
    ic_alea = 1 / len(alphabet)
    print(f"\nAlphabet : {len(alphabet)} caractères | longueur du clair : {len(message_clair)}")
    print(f"IC du français (référence) : {ic_fr:.4f}")
    print(f"IC d'un texte aléatoire    : {ic_alea:.4f}  (= 1/{len(alphabet)})")

    # Chiffrement
    cryptogramme = chiffrement_vigenere(message_clair, vraie_cle, alphabet)
    print(f"\nClé secrète : {vraie_cle} (longueur {len(vraie_cle)})")
    print(f"Extrait chiffré : {cryptogramme[:100]}...")

    # Étape 1 : trouver la longueur de la clé
    # (on teste au moins jusqu'à 2 fois la longueur de la clé, pour que les
    # multiples de la vraie longueur apparaissent aussi sur le graphique)
    profil = profil_ic(cryptogramme, max(20, 2 * len(vraie_cle)))
    afficher_profil(profil, ic_fr, ic_alea)
    longueur = estimer_longueur(profil)
    print(f"\nLongueur de clé estimée : {longueur}")

    # Étape 2 : retrouver les lettres de la clé
    freq_ref = frequences_reference(texte_reference, alphabet)
    cle_trouvee = retrouver_cle(cryptogramme, longueur, alphabet, freq_ref)
    print(f"Clé retrouvée : {cle_trouvee}")
    # Vérification visuelle : si la clé est bonne, le texte est lisible
    print(f"Extrait déchiffré : "
          f"{dechiffrement_vigenere(cryptogramme, cle_trouvee, alphabet)[:200]}...")