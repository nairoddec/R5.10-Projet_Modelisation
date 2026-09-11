def chiffrement_vigenere(texte, cle):
    resultat = ""
    index_cle = 0
    for caractere in texte:
        if caractere == ' ':
            resultat += ' '
        else:
            lettre_cle = cle[index_cle % len(cle)]
            decalage = ord(lettre_cle) - 65
            nouveau_code = (ord(caractere) - 65 + decalage) % 26
            resultat += chr(nouveau_code + 65)
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
            nouveau_code = (ord(caractere) - 65 - decalage) % 26
            resultat += chr(nouveau_code + 65)
            index_cle += 1
    return resultat


def attaque_dictionnaire_vigenere(texte_chiffre, dictionnaire_cles):
    """
    Tente de casser Vigenère en testant une liste de clés.
    Fait appel à votre fonction de déchiffrement.
    """
    # Liste de mots français très courants pour évaluer le déchiffrement
    mots_courants = [" LE ", " LA ", " DE ", " UN ", " ET ", " EST ", " QUE "]
    
    meilleur_score = 0
    meilleure_cle = None
    meilleur_texte = ""
    
    print("Début de l'attaque en force brute...")
    
    for cle_test in dictionnaire_cles:
        # 1. On FAIT APPEL à votre code pour tester cette clé
        texte_essaye = dechiffrement_vigenere(texte_chiffre, cle_test.upper())
        
        # 2. On attribue un "score" (combien de mots français trouve-t-on ?)
        # On ajoute des espaces autour pour s'assurer que ce sont des mots entiers
        texte_avec_espaces = f" {texte_essaye} " 
        score = sum(texte_avec_espaces.count(mot) for mot in mots_courants)
        
        # 3. Si c'est le meilleur score trouvé jusqu'ici, on le sauvegarde
        if score > meilleur_score:
            meilleur_score = score
            meilleure_cle = cle_test
            meilleur_texte = texte_essaye
            
    return meilleure_cle, meilleur_texte

# --- Test de l'attaque ---
if __name__ == "__main__":
    # On simule un message intercepté (chiffré avec la clé "SECRET")
    message_clair = "LE CHIFFRE DE VIGENERE EST PLUS DIFFICILE A CASSER QUE LE CHIFFRE DE CESAR"
    vrai_cle = "PROFESSEUR"
    cryptogramme = chiffrement_vigenere(message_clair, vrai_cle)
    
    print(f"Message intercepté : {cryptogramme}\n")
    
    # Le pirate possède une liste de mots de passe volés ou courants
    dictionnaire_hacker = ["TOTO", "AZERTY", "PROFESSEUR", "SOLEIL", "SECRET", "BATEAU", "MOTDEPASSE"]
    
    # Lancement de l'attaque
    cle_trouvee, texte_trouve = attaque_dictionnaire_vigenere(cryptogramme, dictionnaire_hacker)
    
    print("--- Résultats de l'attaque ---")
    if cle_trouvee:
        print(f" Clé trouvée : {cle_trouvee}")
        print(f" Texte décodé : {texte_trouve}")
    else:
        print("❌ Échec : La clé n'était pas dans le dictionnaire fourni.")
