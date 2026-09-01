# Permet de chiffrer et déchiffrer un message avec le chiffre de Vigenère.

def chiffrement_vigenere(texte, cle):
    resultat = ""
    index_cle = 0
    
    for caractere in texte:
        if caractere == ' ':
            resultat += ' '
        else:
            # Récupère la lettre de la clé correspondante
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

# --- Test ---
message = "ATTAQUE A LAUBE"
cle = "SECRET"

chiffre = chiffrement_vigenere(message, cle)
dechiffre = dechiffrement_vigenere(chiffre, cle)

print(f"Message original : {message}")
print(f"Mot-clé : {cle}\n")
print(f"Message chiffré : {chiffre}")
print(f"Message déchiffré : {dechiffre}")