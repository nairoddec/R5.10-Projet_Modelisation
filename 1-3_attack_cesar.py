def chiffrement_cesar(texte, decalage):
    """Chiffre un texte composé de lettres majuscules avec César."""
    resultat = ""

    for caractere in texte:
        if caractere == " ":
            resultat += " "
        else:
            nouveau_code = (ord(caractere) - 65 + decalage) % 26
            resultat += chr(nouveau_code + 65)

    return resultat


def dechiffrement_cesar(texte_chiffre, decalage):
    """Déchiffre un texte César en retirant le décalage."""
    resultat = ""

    for caractere in texte_chiffre:
        if caractere == " ":
            resultat += " "
        else:
            nouveau_code = (ord(caractere) - 65 - decalage) % 26
            resultat += chr(nouveau_code + 65)

    return resultat


def attaque_force_brute_cesar(texte_chiffre):
    """Teste les 26 décalages possibles du chiffre de César."""
    mots_courants = [" LE ", " LA ", " DE ", " UN ", " ET ", " EST ", " QUE "]
    meilleur_score = -1
    meilleur_decalage = None
    meilleur_texte = ""

    print("Début de l'attaque en force brute...")

    for decalage_test in range(26):
        # On fait appel à la fonction de déchiffrement pour chaque décalage.
        texte_essaye = dechiffrement_cesar(texte_chiffre, decalage_test)

        # On compte les mots français fréquents trouvés dans le résultat.
        texte_avec_espaces = f" {texte_essaye} "
        score = sum(texte_avec_espaces.count(mot) for mot in mots_courants)

        if score > meilleur_score:
            meilleur_score = score
            meilleur_decalage = decalage_test
            meilleur_texte = texte_essaye

    return meilleur_decalage, meilleur_texte


# --- Test de l'attaque ---
if __name__ == "__main__":
    message_clair = "LE CHIFFRE DE CESAR EST SIMPLE A CASSER QUE LE CHIFFRE DE VIGENERE"
    vrai_decalage = 3
    cryptogramme = chiffrement_cesar(message_clair, vrai_decalage)

    print(f"Message intercepté : {cryptogramme}\n")

    decalage_trouve, texte_trouve = attaque_force_brute_cesar(cryptogramme)

    print("\n--- Résultats de l'attaque ---")
    print(f"Décalage trouvé : {decalage_trouve}")
    print(f"Texte décodé : {texte_trouve}")