import random


from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte

def extraire_alphabet(texte: str) -> list[str]:
    """Liste les lettres réellement présentes dans le texte."""
    return list(dict.fromkeys(caractere for caractere in texte if caractere != " "))


def generer_cle_aleatoire(alphabet: list[str]) -> dict[str, str]:
    """Crée une permutation aléatoire de l'alphabet détecté."""
    alphabet_melange = alphabet.copy()
    random.shuffle(alphabet_melange)
    return dict(zip(alphabet, alphabet_melange))


def verifier_cle(cle: dict[str, str], alphabet: list[str]) -> bool:
    """Vérifie que la clé est une permutation de l'alphabet détecté."""
    if set(cle.keys()) != set(alphabet) or set(cle.values()) != set(alphabet):
        raise ValueError("La clé n'est pas une permutation valide de l'alphabet.")
    return True


def inverser_cle(cle: dict[str, str]) -> dict[str, str]:
    """Construit l'inverse de la clé."""
    return {valeur: origine for origine, valeur in cle.items()}


def chiffrer(texte_clair: str, cle: dict[str, str]) -> str:
    """Chiffre les lettres et conserve les espaces."""
    return "".join(cle.get(caractere, caractere) for caractere in texte_clair)


def dechiffrer(texte_chiffre: str, cle: dict[str, str]) -> str:
    """Déchiffre le texte avec la clé connue."""
    return chiffrer(texte_chiffre, inverser_cle(cle))


if __name__ == "__main__":
    url_cible = "https://fr.wikipedia.org/wiki/Château"

    try:
        texte_brut = recuperer_texte_mediawiki(url_cible)
    except Exception as erreur:
        print(f"Impossible de récupérer la page : {erreur}")
        raise SystemExit(1)

    # Même nettoyage que l'analyse fréquentielle :
    # lettres uniquement, majuscules, sans accents ni chiffres.
    message_original = nettoyer_texte(texte_brut)

    if not message_original:
        print("La page ne contient aucune lettre exploitable.")
        raise SystemExit(1)

    alphabet = extraire_alphabet(message_original)
    ma_cle = generer_cle_aleatoire(alphabet)
    verifier_cle(ma_cle, alphabet)

    print(f"URL analysée : {url_cible}")
    print(f"Alphabet détecté : {''.join(alphabet)}")
    print(f"Longueur du message : {len(message_original)} caractères")

    message_chiffre = chiffrer(message_original, ma_cle)
    message_dechiffre = dechiffrer(message_chiffre, ma_cle)

    print(f"\nExtrait original : {message_original[:300]}...")
    print(f"\nExtrait chiffré : {message_chiffre[:300]}...")

    if message_original == message_dechiffre:
        print("\nSuccès : le texte déchiffré est identique au texte original.")
    else:
        print("\nErreur : le déchiffrement ne correspond pas au texte original.")