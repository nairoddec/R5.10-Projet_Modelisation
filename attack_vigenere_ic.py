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

from collections import Counter

from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
from outils_digrammes import extraire_alphabet
from attack_vigenere import (chiffrement_vigenere, dechiffrement_vigenere,
                             normaliser_cle)


# 1. Indice de coïncidence

def indice_coincidence(texte: str) -> float :
    """IC = somme n_i (n_i - 1) / (N (N - 1)) : proba que 2 caractères tirés
    sans remise dans le texte soient identiques."""
    n = len(texte)
    if n < 2 :
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


# 2. Retrouver la clé une fois L connue

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


# 3. Affichage

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


# 4. Saisies utilisateur

URL_MESSAGE = "https://fr.wikipedia.org/wiki/Cathédrale"   # texte à chiffrer
REFERENCE_PAR_DEFAUT = "Château"                           # texte de référence


def construire_url(saisie: str) -> str:
    """Accepte une URL complète ou simplement un titre de page Wikipédia."""
    saisie = saisie.strip()
    if saisie.startswith("http"):
        return saisie
    return "https://fr.wikipedia.org/wiki/" + saisie.replace(" ", "_")


def demander_reference() -> str:
    """Demande la page Wikipédia servant de texte de référence."""
    saisie = input(f"Page Wikipédia de référence (titre ou URL) "
                   f"[Entrée = {REFERENCE_PAR_DEFAUT}] : ").strip()
    return construire_url(saisie or REFERENCE_PAR_DEFAUT)


def demander_cle(alphabet: list[str]) -> str:
    """Demande une clé et la redemande tant qu'elle n'est pas utilisable."""
    while True:
        saisie = input("Clé secrète de Vigenère (lettres uniquement) : ")
        cle = normaliser_cle(saisie)
        if not cle:
            print("  Clé vide ou sans lettre : recommence.")
            continue
        inconnus = sorted({c for c in cle if c not in alphabet})
        if inconnus:
            print(f"  Caractères absents de l'alphabet du message : {inconnus}")
            continue
        if cle != saisie:
            print(f"  Clé normalisée : {cle}")
        return cle


if __name__ == "__main__":
    url_reference = demander_reference()
    try:
        texte_reference = nettoyer_texte(recuperer_texte_mediawiki(url_reference))
        message_clair = nettoyer_texte(recuperer_texte_mediawiki(URL_MESSAGE))
    except Exception as erreur:
        print(f"Impossible de charger les textes : {erreur}")
        raise SystemExit(1)

    if url_reference.rstrip("/").lower() == URL_MESSAGE.lower():
        print("Attention : la référence est la même page que le message, "
              "le résultat sera trop favorable.")

    alphabet = extraire_alphabet(message_clair)
    vraie_cle = demander_cle(alphabet)

    ic_fr = indice_coincidence(texte_reference)
    ic_alea = 1 / len(alphabet)
    print(f"\nAlphabet : {len(alphabet)} caractères | longueur du clair : {len(message_clair)}")
    print(f"IC du français (référence) : {ic_fr:.4f}")
    print(f"IC d'un texte aléatoire    : {ic_alea:.4f}  (= 1/{len(alphabet)})")

    cryptogramme = chiffrement_vigenere(message_clair, vraie_cle, alphabet)
    print(f"\nClé secrète : {vraie_cle} (longueur {len(vraie_cle)})")
    print(f"Extrait chiffré : {cryptogramme[:100]}...")

    # Étape 1 : longueur (on teste au moins jusqu'à 2 fois la longueur de la clé)
    profil = profil_ic(cryptogramme, max(20, 2 * len(vraie_cle)))
    afficher_profil(profil, ic_fr, ic_alea)
    longueur = estimer_longueur(profil)
    print(f"\nLongueur de clé estimée : {longueur}")

    # Étape 2 : clé
    freq_ref = frequences_reference(texte_reference, alphabet)
    cle_trouvee = retrouver_cle(cryptogramme, longueur, alphabet, freq_ref)
    print(f"Clé retrouvée : {cle_trouvee}")
    print(f"Extrait déchiffré : "
          f"{dechiffrement_vigenere(cryptogramme, cle_trouvee, alphabet)[:200]}...")