from cesar import chiffrement_cesar, dechiffrement_cesar
from analyse_frequentielle import calculer_statistiques
from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte


def lettre_la_plus_frequente(statistiques: dict) -> str:
    """Renvoie la lettre la plus fréquente, sans compter les espaces."""
    frequences = statistiques["frequences"]

    lettres = {
        caractere: occurrence
        for caractere, occurrence in frequences.items()
        if caractere.isalpha()
    }

    if not lettres:
        raise ValueError("Aucune lettre trouvée dans le texte.")

    return max(lettres, key=lettres.get)


def attaque_frequentielle_cesar(
    texte_chiffre: str,
    statistiques_reference: dict,
):
    """
    Estime directement le décalage :
    lettre chiffrée la plus fréquente - lettre de référence la plus fréquente.

    Aucune boucle sur les 26 décalages : ce n'est pas une force brute.
    """
    statistiques_chiffre = calculer_statistiques(texte_chiffre)

    lettre_reference = lettre_la_plus_frequente(statistiques_reference)
    lettre_chiffree = lettre_la_plus_frequente(statistiques_chiffre)

    decalage_estime = (
        ord(lettre_chiffree) - ord(lettre_reference)
    ) % 26

    texte_dechiffre = dechiffrement_cesar(
        texte_chiffre,
        decalage_estime,
    )

    return (
        decalage_estime,
        texte_dechiffre,
        lettre_reference,
        lettre_chiffree,
    )


if __name__ == "__main__":
    # Corpus servant à connaître les fréquences de la langue française.
    url_reference = "https://fr.wikipedia.org/wiki/Château"

    # Page à chiffrer puis attaquer.
    url_message = "https://fr.wikipedia.org/wiki/Château"

    try:
        texte_reference = nettoyer_texte(
            recuperer_texte_mediawiki(url_reference)
        )
        message = nettoyer_texte(
            recuperer_texte_mediawiki(url_message)
        )
    except Exception as erreur:
        print(f"Impossible de récupérer une page Wikipédia : {erreur}")
        raise SystemExit(1)

    stats_reference = calculer_statistiques(texte_reference)

    cle = 3
    cryptogramme = chiffrement_cesar(message, cle)

    print(f"Page de référence : {url_reference}")
    print(f"Page chiffrée : {url_message}")
    print(f"\nExtrait intercepté : {cryptogramme[:300]}...")

    (
        decalage,
        texte_dechiffre,
        lettre_reference,
        lettre_chiffree,
    ) = attaque_frequentielle_cesar(
        cryptogramme,
        stats_reference,
    )

    print("\n--- Résultat de l'attaque fréquentielle ---")
    print(f"Lettre la plus fréquente du corpus : {lettre_reference}")
    print(f"Lettre la plus fréquente du cryptogramme : {lettre_chiffree}")
    print(f"Décalage estimé : {decalage}")
    print(f"Extrait déchiffré : {texte_dechiffre[:300]}...")

    if texte_dechiffre == message:
        print("\nSuccès : le déchiffrement est correct.")
    else:
        print("\nLe résultat est une estimation : sur un texte court, "
              "la lettre la plus fréquente peut ne pas être représentative.")