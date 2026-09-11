import math

from outils_digrammes import (
    statistiques_digrammes,
    construire_matrice_transitions,
)

print("\n")
print("\n--- Attaque de Vigenère par analyse des digrammes ---")

def chiffrement_vigenere(texte, cle):
    resultat = ""
    index_cle = 0

    for caractere in texte:
        if caractere == " ":
            resultat += " "
        else:
            lettre_cle = cle[index_cle % len(cle)]
            decalage = ord(lettre_cle) - ord("A")
            nouveau_code = (ord(caractere) - ord("A") + decalage) % 26
            resultat += chr(nouveau_code + ord("A"))
            index_cle += 1

    return resultat


def dechiffrement_vigenere(texte_chiffre, cle):
    resultat = ""
    index_cle = 0

    for caractere in texte_chiffre:
        if caractere == " ":
            resultat += " "
        else:
            lettre_cle = cle[index_cle % len(cle)]
            decalage = ord(lettre_cle) - ord("A")
            nouveau_code = (ord(caractere) - ord("A") - decalage) % 26
            resultat += chr(nouveau_code + ord("A"))
            index_cle += 1

    return resultat


def score_digrammes(texte, matrice, char_to_idx):
    """
    Calcule la probabilité des digrammes du texte.
    Plus le score est grand, plus le texte ressemble au français.
    """
    score = 0
    epsilon = 0.0001

    for i in range(len(texte) - 1):
        lettre1 = texte[i]
        lettre2 = texte[i + 1]

        if lettre1 in char_to_idx and lettre2 in char_to_idx:
            probabilite = matrice[
                char_to_idx[lettre1],
                char_to_idx[lettre2]
            ]

            score += math.log(probabilite + epsilon)

    return score


def attaque_dictionnaire_vigenere(texte_chiffre, dictionnaire_cles):
    """Teste les clés et sélectionne le texte le plus français selon ses digrammes."""

    # Texte français servant à construire la matrice de transitions.
    texte_reference = (
        "LE CHIFFRE DE VIGENERE EST UN CHIFFREMENT POLYALPHABETIQUE "
        "IL UTILISE UNE CLE POUR DECALER CHAQUE LETTRE DU MESSAGE "
        "LE TEXTE CLAIR EST TRANSFORME EN TEXTE CHIFFRE "
        "LES LETTRES ET LES ESPACES FORMENT DES DIGRAMMES EN FRANCAIS"
    )

    # Fonctions provenant de outils_digrammes.py (anciennement 1-2.py).
    statistiques = statistiques_digrammes(texte_reference)
    matrice, char_to_idx, _ = construire_matrice_transitions(statistiques)

    meilleur_score = float("-inf")
    meilleure_cle = None
    meilleur_texte = ""

    print("Début de l'attaque par analyse des digrammes...\n")

    for cle_test in dictionnaire_cles:
        cle_test = cle_test.upper()
        texte_essaye = dechiffrement_vigenere(texte_chiffre, cle_test)

        score = score_digrammes(texte_essaye, matrice, char_to_idx)

        print(f"Clé testée : {cle_test:12} | Score : {score:.2f}")

        if score > meilleur_score:
            meilleur_score = score
            meilleure_cle = cle_test
            meilleur_texte = texte_essaye

    return meilleure_cle, meilleur_texte, meilleur_score


# --- Test de l'attaque ---

if __name__ == "__main__":
    message_clair = (
        "LE CHIFFRE DE VIGENERE EST PLUS DIFFICILE A CASSER "
        "QUE LE CHIFFRE DE CESAR"
    )
    vrai_cle = "PROFESSEUR"

    cryptogramme = chiffrement_vigenere(message_clair, vrai_cle)

    print(f"Message intercepté : {cryptogramme}\n")

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
    )

    print("\n--- Résultats de l'attaque ---")
    print(f"Clé trouvée : {cle_trouvee}")
    print(f"Texte décodé : {texte_trouve}")
    print(f"Score des digrammes : {score:.2f}")