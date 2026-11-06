"""
Analyse de digrammes et génération de texte par chaîne de Markov (Section 1.2 du sujet).

Principe :
1. On compte les paires de 2 caractères consécutifs (digrammes : 'ES', 'DE', etc.).
2. On construit une matrice de transitions 27x27 (probabilité de passer d'une lettre à la suivante).
3. On utilise cette matrice pour générer du texte aléatoire qui ressemble superficiellement à du français.
"""

from collections import Counter
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte
import random
import unicodedata

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    np = None
    HAVE_NUMPY = False


class LigneMatrice(list):
    """Ligne ou tranche de matrice avec méthodes statistiques compatibles NumPy."""
    def sum(self) -> float:
        return sum(self)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return LigneMatrice([x / other if other != 0 else 0.0 for x in self])
        return NotImplemented


class MatriceTransitions:
    """Matrice 2D native autonome (permet de fonctionner sans installer NumPy)."""
    def __init__(self, data: list[list[float]]):
        self._data = data
        self.shape = (len(data), len(data[0]) if data else 0)

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            r, c = item
            if isinstance(r, int) and isinstance(c, int):
                return self._data[r][c]
            elif isinstance(r, int) and isinstance(c, slice):
                indices = range(*c.indices(self.shape[1]))
                return LigneMatrice([self._data[r][idx] for idx in indices])
            elif isinstance(r, slice) and isinstance(c, int):
                indices = range(*r.indices(self.shape[0]))
                return LigneMatrice([self._data[idx][c] for idx in indices])
            elif isinstance(r, slice) and isinstance(c, slice):
                r_indices = range(*r.indices(self.shape[0]))
                c_indices = range(*c.indices(self.shape[1]))
                return MatriceTransitions([[self._data[ri][ci] for ci in c_indices] for ri in r_indices])
        elif isinstance(item, int):
            return LigneMatrice(self._data[item])
        raise IndexError(f"Indice de matrice non pris en charge : {item}")

    def __setitem__(self, item, value):
        if isinstance(item, tuple) and len(item) == 2:
            self._data[item[0]][item[1]] = float(value)
        elif isinstance(item, int):
            self._data[item] = [float(x) for x in value]
        else:
            raise IndexError(f"Affectation non prise en charge : {item}")

    def sum(self, axis=None, keepdims=False):
        if axis is None:
            return sum(sum(r) for r in self._data)
        elif axis == 1:
            res = [sum(r) for r in self._data]
            return [[s] for s in res] if keepdims else res
        elif axis == 0:
            res = [sum(self._data[r][c] for r in range(self.shape[0])) for c in range(self.shape[1])]
            return [res] if keepdims else res
        raise ValueError(f"Axe non supporté : {axis}")

    def __len__(self):
        return self.shape[0]

    def __iter__(self):
        for row in self._data:
            yield LigneMatrice(row)


def extraire_alphabet(texte: str) -> list[str]:
    """Construit l'alphabet depuis les caractères réellement présents dans le texte."""
    return list(dict.fromkeys(texte))


def statistiques_digrammes(texte: str) -> dict:
    """Compte les apparitions de chaque paire de lettres consécutives (digrammes)."""
    total_digrammes = len(texte) - 1
    if total_digrammes <= 0:
        return {}

    # On extrait chaque paire de deux lettres consécutives (texte[i:i+2])
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
):
    """
    Construit la matrice de transitions 27x27 de la chaîne de Markov.
    La case (i, j) contient la probabilité qu'une lettre 'j' suive la lettre 'i'.
    Chaque ligne est normalisée pour que sa somme soit égale à 1.
    Fonctionne avec NumPy si disponible, ou en Python standard natif.
    """
    taille = len(alphabet)
    char_to_idx = {c: i for i, c in enumerate(alphabet)}
    idx_to_char = {i: c for i, c in enumerate(alphabet)}

    if HAVE_NUMPY:
        matrice = np.zeros((taille, taille))
        for digramme, donnees in statistiques.items():
            if len(digramme) == 2 and digramme[0] in char_to_idx and digramme[1] in char_to_idx:
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
    else:
        donnees_matrice = [[0.0] * taille for _ in range(taille)]
        for digramme, donnees in statistiques.items():
            if len(digramme) == 2 and digramme[0] in char_to_idx and digramme[1] in char_to_idx:
                i = char_to_idx[digramme[0]]
                j = char_to_idx[digramme[1]]
                donnees_matrice[i][j] = float(donnees["occurrences"])

        for i in range(taille):
            somme_ligne = sum(donnees_matrice[i])
            if somme_ligne > 0:
                donnees_matrice[i] = [val / somme_ligne for val in donnees_matrice[i]]

        matrice = MatriceTransitions(donnees_matrice)
        return matrice, char_to_idx, idx_to_char


def afficher_matrice_transitions(
    matrice,
    idx_to_char: dict,
    seuil: float = 0.0,
) -> None:
    """Affiche la matrice sous forme de tableau lisible dans la console."""
    taille = matrice.shape[0]

    colonnes_utilisees = [
        j for j in range(taille) if (matrice[:, j].sum() if hasattr(matrice[:, j], 'sum') else sum(matrice[:, j])) > seuil
    ]
    lignes_utilisees = [
        i for i in range(taille) if (matrice[i, :].sum() if hasattr(matrice[i, :], 'sum') else sum(matrice[i, :])) > seuil
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
    matrice,
    char_to_idx: dict,
    idx_to_char: dict,
    longueur: int = 50,
) -> str:
    """
    Génère un texte aléatoire selon la chaîne de Markov.
    On part de l'espace (début de mot) puis on tire chaque lettre suivante
    selon les probabilités de la ligne courante de la matrice.
    """
    taille = len(char_to_idx)
    texte = [" "]
    for _ in range(longueur - 1):
        etat_actuel = texte[-1]
        idx_actuel = char_to_idx[etat_actuel]
        probabilites = matrice[idx_actuel]

        somme_p = sum(probabilites) if not hasattr(probabilites, 'sum') else probabilites.sum()
        if somme_p == 0:
            p_normalisees = [1.0 / taille] * taille
        else:
            p_normalisees = [p / somme_p for p in probabilites]

        if HAVE_NUMPY and isinstance(matrice, np.ndarray):
            prochain_idx = int(np.random.choice(taille, p=p_normalisees))
        else:
            prochain_idx = random.choices(range(taille), weights=p_normalisees)[0]

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
