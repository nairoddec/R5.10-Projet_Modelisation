# Permet de chiffrer et déchiffrer un message avec le chiffre de César.

def chiffrement_cesar(texte, decalage):
    resultat = ""

    for caractere in texte:
        if caractere == " ":
            resultat += " "
        else:
            nouveau_code = (ord(caractere) - 65 + decalage) % 26
            resultat += chr(nouveau_code + 65)

    return resultat


def dechiffrement_cesar(texte_chiffre, decalage):
    return chiffrement_cesar(texte_chiffre, -decalage)


def attaque_force_brute_cesar(texte_chiffre):
    """Affiche les 26 déchiffrements possibles."""
    print("Début de l'attaque en force brute\n")

    for decalage in range(26):
        texte_dechiffre = dechiffrement_cesar(texte_chiffre, decalage)
        print(f"Décalage {decalage:2} : {texte_dechiffre}")


# --- Test ---

if __name__ == "__main__":
    message = "LE CHIFFRE DE CESAR EST SIMPLE A CASSER"
    cle = 8

    chiffre = chiffrement_cesar(message, cle)

    print(f"Message original : {message}")
    print(f"Clé de décalage : {cle}")
    print(f"Message chiffré : {chiffre}\n")

    attaque_force_brute_cesar(chiffre)