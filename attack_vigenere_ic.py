"""
Variante statistique : attaque de Vigenère SANS dictionnaire de clés,
grâce à l'indice de coïncidence (IC).

Étapes :
  1. Estimer la longueur L de la clé  -> IC moyen des L colonnes du cryptogramme.
  2. Retrouver chaque lettre de la clé -> chaque colonne est un chiffre de César,
     on garde le décalage dont les fréquences ressemblent le plus au français
     (test du khi-deux contre un texte de référence).

Utilisation :
    python attack_vigenere_ic.py                 # pages Wikipédia
"""

import random
import sys
from collections import Counter

from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
from outils_digrammes import extraire_alphabet
from attack_vigenere import chiffrement_vigenere, dechiffrement_vigenere


# ---------------------------------------------------------------------------
# 1. Indice de coïncidence
# ---------------------------------------------------------------------------

def indice_coincidence(texte: str) -> float:
    """IC = somme n_i (n_i - 1) / (N (N - 1)) : proba que 2 caractères tirés
    sans remise dans le texte soient identiques."""
    n = len(texte)
    if n < 2:
        return 0.0
    comptes = Counter(texte)
    return sum(c * (c - 1) for c in comptes.values()) / (n * (n - 1))


def colonnes(texte: str, longueur: int) -> list[str]:
    """Découpe le texte en `longueur` colonnes (caractères de même rang mod L)."""
    return [texte[i::longueur] for i in range(longueur)]


def ic_moyen(texte: str, longueur: int) -> float:
    """IC moyen des colonnes pour une longueur de clé supposée."""
    cols = colonnes(texte, longueur)
    return sum(indice_coincidence(c) for c in cols) / len(cols)


def profil_ic(cryptogramme: str, longueur_max: int = 20) -> dict[int, float]:
    return {L: ic_moyen(cryptogramme, L) for L in range(1, longueur_max + 1)}


def estimer_longueur(profil: dict[int, float], ratio: float = 0.9) -> int:
    """Plus petite longueur dont l'IC atteint 90 % du maximum du profil.
    (Les multiples de la vraie longueur ont aussi un IC élevé : on veut le
    plus petit, pas le plus grand.)"""
    maximum = max(profil.values())
    for L, valeur in profil.items():
        if valeur >= ratio * maximum:
            return L
    return max(profil, key=profil.get)


# ---------------------------------------------------------------------------
# 2. Retrouver la clé une fois L connue
# ---------------------------------------------------------------------------

def frequences_reference(texte_reference: str, alphabet: list[str]) -> dict:
    """Fréquences des caractères (avec +1 pour éviter les zéros)."""
    comptes = Counter(c for c in texte_reference if c in alphabet)
    total = sum(comptes[c] + 1 for c in alphabet)
    return {c: (comptes[c] + 1) / total for c in alphabet}


def khi_deux(colonne: str, freq_ref: dict) -> float:
    """Distance entre les fréquences observées dans la colonne et la référence."""
    n = len(colonne)
    comptes = Counter(colonne)
    return sum(
        (comptes[c] - n * p) ** 2 / (n * p) for c, p in freq_ref.items()
    )


def retrouver_cle(cryptogramme: str, longueur: int, alphabet: list[str],
                  freq_ref: dict) -> str:
    """Pour chaque colonne, essaie les décalages possibles et garde le meilleur."""
    cle = []
    for col in colonnes(cryptogramme, longueur):
        meilleur_decalage, meilleur_score = None, float("inf")
        for lettre in alphabet:
            if lettre == " ":  # une clé ne contient jamais d'espace
                continue
            # on déchiffre la colonne avec une clé d'un seul caractère
            essai = dechiffrement_vigenere(col, lettre, alphabet)
            score = khi_deux(essai, freq_ref)
            if score < meilleur_score:
                meilleur_decalage, meilleur_score = lettre, score
        cle.append(meilleur_decalage)
    return "".join(cle)


# ---------------------------------------------------------------------------
# 3. Affichage et expériences
# ---------------------------------------------------------------------------

def afficher_profil(profil: dict[int, float], ic_fr: float, ic_alea: float,
                    fichier_png: str = "profil_ic_vigenere.png") -> None:
    """Graphique matplotlib si disponible, sinon barres en texte."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 4))
        plt.bar(list(profil), list(profil.values()), color="steelblue")
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
        print("matplotlib absent : affichage texte")
    for L, valeur in profil.items():
        print(f"L={L:2d} | {valeur:.4f} | {'#' * int(valeur * 600)}")


def experience_longueur_texte(message_clair: str, alphabet: list[str],
                              ic_fr: float, ic_alea: float,
                              longueur_cle: int = 8, essais: int = 40) -> None:
    """Taux de réussite de l'estimation de L selon la taille du cryptogramme."""
    print(f"\n--- Réussite de l'estimation de L (clé de longueur {longueur_cle}) ---")
    lettres = [c for c in alphabet if c != " "]
    for taille in (100, 200, 400, 800, 1600, 3200):
        if taille > len(message_clair):
            break
        reussites = 0
        for _ in range(essais):
            debut = random.randint(0, len(message_clair) - taille)
            extrait = message_clair[debut:debut + taille]
            cle = "".join(random.choice(lettres) for _ in range(longueur_cle))
            crypto = chiffrement_vigenere(extrait, cle, alphabet)
            profil = profil_ic(crypto, 20)
            if estimer_longueur(profil) == longueur_cle:
                reussites += 1
        print(f"{taille:5d} caractères : {reussites}/{essais} ({100 * reussites / essais:.0f} %)")


def charger_textes(arguments: list[str]) -> tuple[str, str]:
    """Renvoie (texte du message, texte de référence)."""
    if len(arguments) >= 2:
        with open(arguments[0], encoding="utf-8") as f1, \
             open(arguments[1], encoding="utf-8") as f2:
            return f1.read(), f2.read()
    url_message = "https://fr.wikipedia.org/wiki/Cathédrale"
    url_reference = "https://fr.wikipedia.org/wiki/Château"
    return (recuperer_texte_mediawiki(url_message),
            recuperer_texte_mediawiki(url_reference))


if __name__ == "__main__":
    random.seed(42)
    try:
        brut_message, brut_reference = charger_textes(sys.argv[1:])
    except Exception as erreur:
        print(f"Impossible de charger les textes : {erreur}")
        raise SystemExit(1)

    message_clair = nettoyer_texte(brut_message)
    texte_reference = nettoyer_texte(brut_reference)
    alphabet = extraire_alphabet(message_clair)

    ic_fr = indice_coincidence(texte_reference)
    ic_alea = 1 / len(alphabet)
    print(f"Alphabet : {len(alphabet)} caractères | longueur du clair : {len(message_clair)}")
    print(f"IC du français (référence) : {ic_fr:.4f}")
    print(f"IC d'un texte aléatoire    : {ic_alea:.4f}  (= 1/{len(alphabet)})")

    # Clé volontairement absente de tout dictionnaire
    vraie_cle = "MODELISATION"
    cryptogramme = chiffrement_vigenere(message_clair, vraie_cle, alphabet)
    print(f"\nClé secrète : {vraie_cle} (longueur {len(vraie_cle)})")
    print(f"Extrait chiffré : {cryptogramme[:100]}...")

    # Étape 1 : longueur
    profil = profil_ic(cryptogramme, 20)
    afficher_profil(profil, ic_fr, ic_alea)
    longueur = estimer_longueur(profil)
    print(f"\nLongueur de clé estimée : {longueur}")

    # Étape 2 : clé
    freq_ref = frequences_reference(texte_reference, alphabet)
    cle_trouvee = retrouver_cle(cryptogramme, longueur, alphabet, freq_ref)
    print(f"Clé retrouvée : {cle_trouvee}")
    print(f"Extrait déchiffré : "
          f"{dechiffrement_vigenere(cryptogramme, cle_trouvee, alphabet)[:200]}...")

    # Expérience : combien de texte faut-il ?
    experience_longueur_texte(message_clair, alphabet, ic_fr, ic_alea)
