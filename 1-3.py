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
