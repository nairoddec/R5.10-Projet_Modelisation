from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte

def verifier_cle_permutation(cle: list[int]) -> bool:
    """Vérifie que la clé contient chaque position une seule fois."""
    longueur = len(cle)

    if longueur == 0 or set(cle) != set(range(longueur)):
        raise ValueError(
            "La clé doit contenir tous les entiers de 0 à "
            f"{longueur - 1}, sans doublon."
        )

    return True


def inverser_cle_permutation(cle: list[int]) -> list[int]:
    """Construit la clé inverse."""
    cle_inverse = [0] * len(cle)

    for position_initiale, nouvelle_position in enumerate(cle):
        cle_inverse[nouvelle_position] = position_initiale

    return cle_inverse


def chiffrer_permutation(texte: str, cle: list[int]) -> str:
    """Chiffre le texte par permutation de blocs."""
    longueur = len(cle)

    espaces_manquants = (longueur - len(texte) % longueur) % longueur
    texte += " " * espaces_manquants

    texte_chiffre = []

    for i in range(0, len(texte), longueur):
        bloc = texte[i:i + longueur]
        bloc_melange = [""] * longueur

        for position_initiale, nouvelle_position in enumerate(cle):
            bloc_melange[nouvelle_position] = bloc[position_initiale]

        texte_chiffre.append("".join(bloc_melange))

    return "".join(texte_chiffre)


def dechiffrer_permutation(texte_chiffre: str, cle: list[int]) -> str:
    """Déchiffre avec la permutation inverse."""
    cle_inverse = inverser_cle_permutation(cle)
    return chiffrer_permutation(texte_chiffre, cle_inverse)


if __name__ == "__main__":
    url_cible = "https://fr.wikipedia.org/wiki/Château"
    cle_permutation = [3, 0, 2, 1]

    verifier_cle_permutation(cle_permutation)

    try:
        texte_brut = recuperer_texte_mediawiki(url_cible)
    except Exception as erreur:
        print(f"Impossible de récupérer la page Wikipédia : {erreur}")
        raise SystemExit(1)

    # Même règle que l'analyse fréquentielle :
    # lettres seulement, majuscules, sans accents ni chiffres.
    message_clair = nettoyer_texte(texte_brut)

    cryptogramme = chiffrer_permutation(message_clair, cle_permutation)
    message_retrouve = dechiffrer_permutation(
        cryptogramme,
        cle_permutation,
    ).rstrip()

    print(f"URL utilisée : {url_cible}")
    print(f"Clé utilisée : {cle_permutation}")
    print(f"Longueur du message : {len(message_clair)}")

    print(f"\nExtrait original : {message_clair[:300]}...")
    print(f"\nExtrait chiffré : {cryptogramme[:300]}...")

    if message_clair == message_retrouve:
        print("\nSuccès : le texte déchiffré correspond au texte original.")
    else:
        print("\nErreur : le déchiffrement ne correspond pas.")