import math

from analyse_frequentielle import recuperer_texte_mediawiki, nettoyer_texte
from outils_digrammes import (
    statistiques_digrammes,
    construire_matrice_transitions,
    extraire_alphabet,
)
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte



def normaliser_cle(cle: str) -> str:
    """Applique le même nettoyage que pour le texte, sans espaces."""
    return nettoyer_texte(cle).replace(" ", "")


def chiffrement_vigenere(
    texte: str,
    cle: str,
    alphabet: list[str],
) -> str:
    """Chiffre un texte avec Vigenère et un alphabet détecté dynamiquement."""
    positions = {caractere: index for index, caractere in enumerate(alphabet)}
    cle = normaliser_cle(cle)

    if not cle or any(caractere not in positions for caractere in cle):
        raise ValueError("La clé contient des caractères absents de l'alphabet.")

    resultat = []
    index_cle = 0

    for caractere in texte:
        if caractere not in positions:
            resultat.append(caractere)
            continue

        decalage = positions[cle[index_cle % len(cle)]]
        nouvelle_position = (positions[caractere] + decalage) % len(alphabet)

        resultat.append(alphabet[nouvelle_position])
        index_cle += 1

    return "".join(resultat)


def dechiffrement_vigenere(
    texte_chiffre: str,
    cle: str,
    alphabet: list[str],
) -> str:
    """Déchiffre un texte chiffré avec Vigenère."""
    positions = {caractere: index for index, caractere in enumerate(alphabet)}
    cle = normaliser_cle(cle)

    if not cle or any(caractere not in positions for caractere in cle):
        raise ValueError("La clé contient des caractères absents de l'alphabet.")

    resultat = []
    index_cle = 0

    for caractere in texte_chiffre:
        if caractere not in positions:
            resultat.append(caractere)
            continue

        decalage = positions[cle[index_cle % len(cle)]]
        nouvelle_position = (positions[caractere] - decalage) % len(alphabet)

        resultat.append(alphabet[nouvelle_position])
        index_cle += 1

    return "".join(resultat)


def score_digrammes(
    texte: str,
    matrice,
    char_to_idx: dict[str, int],
) -> float:
    """Plus le score est élevé, plus le texte ressemble au texte de référence."""
    score = 0
    epsilon = 0.0001

    for i in range(len(texte) - 1):
        caractere_1 = texte[i]
        caractere_2 = texte[i + 1]

        if caractere_1 in char_to_idx and caractere_2 in char_to_idx:
            probabilite = matrice[
                char_to_idx[caractere_1],
                char_to_idx[caractere_2],
            ]
            score += math.log(probabilite + epsilon)

    return score


def attaque_dictionnaire_vigenere(
    texte_chiffre: str,
    dictionnaire_cles: list[str],
    texte_reference: str,
    alphabet: list[str],
):
    """Teste chaque clé possible et retient le meilleur score de digrammes."""
    statistiques = statistiques_digrammes(texte_reference)
    matrice, char_to_idx, _ = construire_matrice_transitions(
        statistiques,
        alphabet,
    )

    meilleur_score = float("-inf")
    meilleure_cle = None
    meilleur_texte = ""

    print("\n--- Attaque par analyse des digrammes ---")

    for cle_test in dictionnaire_cles:
        cle_test = normaliser_cle(cle_test)

        if not cle_test or any(c not in alphabet for c in cle_test):
            print(f"Clé ignorée : {cle_test!r} (caractère absent de l'alphabet)")
            continue

        texte_essaye = dechiffrement_vigenere(
            texte_chiffre,
            cle_test,
            alphabet,
        )
        score = score_digrammes(texte_essaye, matrice, char_to_idx)

        print(f"Clé testée : {cle_test:12} | Score : {score:.2f}")

        if score > meilleur_score:
            meilleur_score = score
            meilleure_cle = cle_test
            meilleur_texte = texte_essaye

    return meilleure_cle, meilleur_texte, meilleur_score


if __name__ == "__main__":
    url_cible = "https://fr.wikipedia.org/wiki/Château"
    vraie_cle = "PROFESSEUR"

    try:
        texte_brut = recuperer_texte_mediawiki(url_cible)
    except Exception as erreur:
        print(f"Impossible de récupérer la page Wikipédia : {erreur}")
        raise SystemExit(1)

    # Lettres seulement, sans chiffres et sans accents,
    # selon la fonction définie dans analyse_frequentielle.py.
    message_clair = nettoyer_texte(texte_brut)
    alphabet = extraire_alphabet(message_clair)

    cryptogramme = chiffrement_vigenere(
        message_clair,
        vraie_cle,
        alphabet,
    )

    print(f"URL utilisée : {url_cible}")
    print(f"Alphabet détecté : {''.join(alphabet)}")
    print(f"Longueur du texte : {len(message_clair)}")
    print(f"\nExtrait chiffré : {cryptogramme[:300]}...")

    dictionnaire_hacker = [
        "TOTO",
        "AZERTY",
        "PROFESSEUR",
        "SOLEIL",
        "SECRET",
        "BATEAU",
        "MOTDEPASSE",
    ]

    cle_trouvee, texte_trouve, score = attaque_dictionnaire_vigenere(
        cryptogramme,
        dictionnaire_hacker,
        message_clair,
        alphabet,
    )

    print("\n--- Résultats ---")
    print(f"Clé trouvée : {cle_trouvee}")
    print(f"Score : {score:.2f}")
    print(f"Extrait déchiffré : {texte_trouve[:300]}...")