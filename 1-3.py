import string
import random

# L'alphabet de référence
ALPHABET = list(string.ascii_uppercase)

def generer_cle_aleatoire():
    """Définit une clé de chiffrement (permutation aléatoire)."""
    alphabet_melange = ALPHABET.copy()
    random.shuffle(alphabet_melange)
    return dict(zip(ALPHABET, alphabet_melange))

def verifier_cle(cle):
    """Vérifie que la clé contient bien une permutation des 26 lettres."""
    if set(cle.keys()) != set(ALPHABET) or set(cle.values()) != set(ALPHABET):
         raise ValueError("La clé n'est pas une permutation valide de 26 lettres.")
    return True

def inverser_cle(cle):
    """Construit l'inverse de la clé de chiffrement."""
    return {valeur: cle_origine for cle_origine, valeur in cle.items()}

def chiffrer(texte_clair, cle):
    """Applique la clé à un texte clair (conserve l'espace)."""
    return "".join(cle.get(caractere, caractere) for caractere in texte_clair)

def dechiffrer(texte_chiffre, cle):
    """Déchiffre un texte avec une clé connue."""
    cle_inverse = inverser_cle(cle)
    return chiffrer(texte_chiffre, cle_inverse)


if __name__ == "__main__":
    # 1. Le message clair (en majuscules, selon notre alphabet)
    message_original = "ATTAQUE FREQUENTIELLE SUR WIKIPEDIA"
    print(f"Message original : '{message_original}'")
    print("-" * 50)

    # 2. Génération et vérification de la clé
    ma_cle = generer_cle_aleatoire()
    verifier_cle(ma_cle)
    # Affiche un extrait de la clé (les 5 premières substitutions) pour vérifier
    extrait_cle = {k: ma_cle[k] for k in list(ma_cle)[:5]}
    print(f"Clé générée (début) : {extrait_cle} ...")
    print("-" * 50)

    # 3. Chiffrement
    message_chiffre = chiffrer(message_original, ma_cle)
    print(f"Message chiffré : '{message_chiffre}'")

    # 4. Déchiffrement
    message_dechiffre = dechiffrer(message_chiffre, ma_cle)
    print(f"Message déchiffré : '{message_dechiffre}'")
    print("-" * 50)

    # 5. Vérification finale
    if message_original == message_dechiffre:
        print("Succès ! L'algorithme de substitution fonctionne parfaitement.")
    else:
        print("Erreur : Le texte déchiffré ne correspond pas à l'original.")
