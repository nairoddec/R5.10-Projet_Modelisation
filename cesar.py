# Permet de chiffrer et déchiffrer un message avec le chiffre de César.

def chiffrement_cesar(texte, decalage):
    resultat = ""
    for caractere in texte:
        if caractere == ' ':
            resultat += ' '
        else:
            nouveau_code = (ord(caractere) - 65 + decalage) % 26
            resultat += chr(nouveau_code + 65)
    return resultat

def dechiffrement_cesar(texte_chiffre, decalage):
    return chiffrement_cesar(texte_chiffre, -decalage)


