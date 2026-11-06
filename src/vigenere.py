# Permet de chiffrer et déchiffrer un message avec le chiffre de Vigenère.
# Chaque lettre est décalée selon la lettre correspondante de la clé (ex: avec CLE : +2, +11, +4).

def chiffrement_vigenere(texte, cle):
    resultat = ""
    index_cle = 0
    
    for caractere in texte:
        if caractere == ' ':
            resultat += ' '
        else:
            # Récupère la lettre de la clé correspondante (en boucle grâce au modulo)
            lettre_cle = cle[index_cle % len(cle)]
            decalage = ord(lettre_cle) - 65
            
            nouveau_code = (ord(caractere) - 65 + decalage) % 26
            resultat += chr(nouveau_code + 65)
            
            # On n'avance dans la clé que si ce n'était pas un espace
            index_cle += 1 
            
    return resultat

def dechiffrement_vigenere(texte_chiffre, cle):
    resultat = ""
    index_cle = 0
    
    for caractere in texte_chiffre:
        if caractere == ' ':
            resultat += ' '
        else:
            lettre_cle = cle[index_cle % len(cle)]
            decalage = ord(lettre_cle) - 65
            
            # Soustraction du décalage pour déchiffrer
            nouveau_code = (ord(caractere) - 65 - decalage) % 26
            resultat += chr(nouveau_code + 65)
            
            index_cle += 1
            
    return resultat
