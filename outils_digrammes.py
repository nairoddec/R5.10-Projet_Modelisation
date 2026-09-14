"""
Analyse de digrammes et génération de texte par chaîne de Markov.
"""

from collections import Counter
from analyse_frequentielle import recuperer_texte_mediawiki
from fonction_outils import est_caractere_analyse, nettoyer_texte

import unicodedata


import numpy as np




def extraire_alphabet(texte: str) -> list[str]:
    """Construit l'alphabet depuis les caractères réellement présents."""
    return list(dict.fromkeys(texte))


def statistiques_digrammes(texte: str) -> dict:
    total_digrammes = len(texte) - 1
    if total_digrammes <= 0:
        return {}

    comptes = Counter(texte[i:i + 2] for i in range(total_digrammes))

    statistiques = {}
    for digramme, occurrences in comptes.most_common():
        statistiques[digramme] = {
            "occurrences": occurrences,
            "pourcentage": round((occurrences / total_digrammes) * 100, 2),
        }
    return statistiques


def construire_matrice_transitions(
    statistiques: dict,
    alphabet: list[str],
) -> tuple[np.ndarray, dict, dict]:
    taille = len(alphabet)
    char_to_idx = {c: i for i, c in enumerate(alphabet)}
    idx_to_char = {i: c for i, c in enumerate(alphabet)}
    matrice = np.zeros((taille, taille))

    for digramme, donnees in statistiques.items():
        if len(digramme) == 2:
            i = char_to_idx[digramme[0]]
            j = char_to_idx[digramme[1]]
            matrice[i, j] = donnees["occurrences"]

    sommes_lignes = matrice.sum(axis=1, keepdims=True)
    matrice = np.divide(
        matrice, sommes_lignes,
        out=np.zeros_like(matrice),
        where=sommes_lignes != 0,
    )
    return matrice, char_to_idx, idx_to_char


def afficher_matrice_transitions(
    matrice: np.ndarray,
    idx_to_char: dict,
    seuil: float = 0.0,
) -> None:
    taille = matrice.shape[0]

    colonnes_utilisees = [
        j for j in range(taille) if matrice[:, j].sum() > seuil
    ]
    lignes_utilisees = [
        i for i in range(taille) if matrice[i, :].sum() > seuil
    ]

    def etiquette(c: str) -> str:
        return "␣" if c == " " else c

    largeur = 6
    entete = " " * largeur + "".join(
        f"{etiquette(idx_to_char[j]):>{largeur}}" for j in colonnes_utilisees
    )
    print(entete)

    for i in lignes_utilisees:
        ligne = f"{etiquette(idx_to_char[i]):<{largeur}}"
        for j in colonnes_utilisees:
            valeur = matrice[i, j]
            ligne += f"{valeur:>{largeur}.2f}" if valeur > 0 else f"{'.':>{largeur}}"
        print(ligne)

def generer_texte_markov(
    matrice: np.ndarray,
    char_to_idx: dict,
    idx_to_char: dict,
    longueur: int = 50,
) -> str:
    taille = len(char_to_idx)
    texte = [" "]
    for _ in range(longueur - 1):
        etat_actuel = texte[-1]
        idx_actuel = char_to_idx[etat_actuel]
        probabilites = matrice[idx_actuel]

        if probabilites.sum() == 0:
            probabilites = np.ones(taille) / taille
        else:
            probabilites = probabilites / probabilites.sum()

        prochain_idx = np.random.choice(taille, p=probabilites)
        texte.append(idx_to_char[prochain_idx])
    return "".join(texte)


def main() -> None:
    url_cible = "https://fr.wikipedia.org/wiki/Château"

    try:
        texte_brut = recuperer_texte_mediawiki(url_cible)
    except Exception as erreur:
        print(f"Impossible de récupérer la page Wikipédia : {erreur}")
        return

    texte_analyse = nettoyer_texte(texte_brut)
    alphabet = extraire_alphabet(texte_analyse)

    print("\n--- Texte normalisé ---")
    print(texte_analyse[:500] + "..." if len(texte_analyse) > 500 else texte_analyse)

    print("\n--- Alphabet détecté ---")
    print(alphabet)

    print("\n--- Statistiques des digrammes ---")
    resultats = statistiques_digrammes(texte_analyse)
    for digramme, donnees in resultats.items():
        print(
            f"'{digramme}' : {donnees['occurrences']} fois "
            f"({donnees['pourcentage']} %)"
        )

    print("\n--- Matrice de transitions ---")
    matrice_transitions, char2idx, idx2char = construire_matrice_transitions(
        resultats,
        alphabet,
    )
    afficher_matrice_transitions(matrice_transitions, idx2char)

    print("\n--- Génération de texte (Chaîne de Markov) ---")
    texte_simule = generer_texte_markov(
        matrice_transitions,
        char2idx,
        idx2char,
        longueur=60,
    )
    print(texte_simule)


if __name__ == "__main__":
    main()