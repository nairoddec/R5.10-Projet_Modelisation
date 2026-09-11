def verifier_cle_permutation(cle):
    """
    Vérifie que la clé est une liste contenant tous les entiers 
    de 0 à (longueur_cle - 1) sans doublon.
    """
    longueur = len(cle)
    if set(cle) != set(range(longueur)):
        raise ValueError(f"La clé n'est pas valide. Elle doit contenir tous les entiers de 0 à {longueur - 1}.")
    return True

def inverser_cle_permutation(cle):
    """
    Construit la clé inverse. Si l'indice 0 va à l'indice 3, 
    la clé inverse fera en sorte que l'indice 3 retourne à l'indice 0.
    """
    longueur = len(cle)
    cle_inverse = [0] * longueur
    for position_initiale, nouvelle_position in enumerate(cle):
        cle_inverse[nouvelle_position] = position_initiale
    return cle_inverse

def chiffrer_permutation(texte, cle):
    """
    Chiffre le texte en le découpant en blocs et en déplaçant les caractères.
    """
    longueur = len(cle)
    
    # 1. Padding : On ajoute des espaces à la fin si le texte 
    # n'est pas un multiple de la longueur de la clé.
    espaces_manquants = (longueur - (len(texte) % longueur)) % longueur
    texte += " " * espaces_manquants
    
    texte_chiffre = []
    
    # 2. Découpage et mélange par blocs
    for i in range(0, len(texte), longueur):
        bloc = texte[i : i + longueur]
        bloc_melange = [''] * longueur
        
        for position_initiale, nouvelle_position in enumerate(cle):
            bloc_melange[nouvelle_position] = bloc[position_initiale]
            
        texte_chiffre.append("".join(bloc_melange))
        
    return "".join(texte_chiffre)

def dechiffrer_permutation(texte_chiffre, cle):
    """
    Déchiffre un texte chiffré par permutation en utilisant l'inverse de la clé.
    """
    cle_inverse = inverser_cle_permutation(cle)
    # Déchiffrer revient exactement à chiffrer avec la clé inverse !
    return chiffrer_permutation(texte_chiffre, cle_inverse)


# --- Test avec l'exemple du sujet ---
if __name__ == "__main__":
    message_clair = "BONJOUR"
    cle_permutation = [3, 0, 2, 1] # Correspond à la clé 3021 du PDF
    
    verifier_cle_permutation(cle_permutation)
    
    cryptogramme = chiffrer_permutation(message_clair, cle_permutation)
    message_retrouve = dechiffrer_permutation(cryptogramme, cle_permutation)
    
    print(f"Message original : '{message_clair}'")
    print(f"Clé utilisée     : {cle_permutation}")
    print(f"Cryptogramme     : '{cryptogramme}'") # Doit afficher 'OJNBU RO'
    print(f"Message décodé   : '{message_retrouve}'")