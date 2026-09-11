"""
Analyse de digrammes et génération de texte par chaîne de Markov.
"""

from collections import Counter

import numpy as np

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ0123456789 .,;:!?'-\"()"


def normaliser_texte(texte: str) -> str:
    texte = texte.upper()
    texte = "".join(c for c in texte if c in ALPHABET)
    texte = " ".join(texte.split())
    return texte


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


def construire_matrice_transitions(statistiques: dict) -> tuple[np.ndarray, dict, dict]:
    taille = len(ALPHABET)
    char_to_idx = {c: i for i, c in enumerate(ALPHABET)}
    idx_to_char = {i: c for i, c in enumerate(ALPHABET)}
    matrice = np.zeros((taille, taille))

    for digramme, donnees in statistiques.items():
        if len(digramme) == 2 and digramme[0] in char_to_idx and digramme[1] in char_to_idx:
            matrice[char_to_idx[digramme[0]], char_to_idx[digramme[1]]] = donnees["occurrences"]

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
    texte_brut = "Bonjour tout le monde, outils de digrammes !"
    texte_analyse = normaliser_texte(texte_brut)

    print("\n--- Texte normalisé ---")
    print(texte_analyse)

    print("\n--- Statistiques des digrammes ---")
    resultats = statistiques_digrammes(texte_analyse)
    for digramme, donnees in resultats.items():
        print(f"'{digramme}' : {donnees['occurrences']} fois ({donnees['pourcentage']} %)")

    print("\n--- Matrice de transitions ---")
    matrice_transitions, char2idx, idx2char = construire_matrice_transitions(resultats)
    afficher_matrice_transitions(matrice_transitions, idx2char)

    print("\n--- Génération de texte (Chaîne de Markov) ---")
    texte_simule = generer_texte_markov(matrice_transitions, char2idx, idx2char, longueur=60)
    print(texte_simule)


if __name__ == "__main__":
    main()