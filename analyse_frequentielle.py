from collections import Counter
import unicodedata

from fonction_outils import recuperer_texte_mediawiki


def normaliser_texte_multilingue(texte):
    """Normalise la casse en préservant les lettres Unicode et leurs signes."""
    texte = unicodedata.normalize("NFC", texte).upper()
    caracteres = []

    for caractere in texte:
        categorie = unicodedata.category(caractere) #Lu pour Lettre majuscule,Nd pour Chiffre décimal, Po pour Ponctuation
        if categorie.startswith(("L", "M")):
            # L = lettre, M = signe combinant (accents et signes d'écriture).
            caracteres.append(caractere)
        else:
            # Les espaces, ponctuations et chiffres séparent les séquences.
            caracteres.append(" ")

    return " ".join("".join(caracteres).split())


def calculer_statistiques(texte):
    """Compte les caractères Unicode, espaces compris."""
    return {
        "total_avec_espaces": len(texte),
        "total_sans_espaces": len(texte.replace(" ", "")),
        "frequences": Counter(texte),
    }


def afficher_statistiques(source, statistiques, limite=27):
    """Affiche les caractères les plus fréquents."""
    total = statistiques["total_avec_espaces"]
    frequences = statistiques["frequences"]

    print(f"=== Statistiques pour : {source} ===")
    print(f"Nombre total de caractères (avec espaces) : {total}")
    print(
        "Nombre total de caractères (sans espaces) : "
        f"{statistiques['total_sans_espaces']}"
    )
    titre = "Tous les caractères" if limite is None else f"Top {limite}"
    print(f"\n--- {titre} les plus fréquents ---")

    for caractere, frequence in frequences.most_common(limite):
        nom_caractere = "'Espace'" if caractere == " " else f"'{caractere}'"
        pourcentage = (frequence / total) * 100 if total else 0
        print(f"{nom_caractere} : {frequence} fois ({pourcentage:.2f}%)")


def saisir_texte_utilisateur(nom):
    """Demande un texte directement ou le récupère depuis une URL MediaWiki."""
    while True:
        choix = input(
            f"\nSource pour {nom} :\n"
            "1. Saisir/coller le texte\n"
            "2. Récupérer une page MediaWiki\n"
            "Votre choix (1 ou 2) : "
        ).strip()
        if choix in {"1", "2"}:
            break
        print("Choix invalide. Entrez 1 ou 2.")

    if choix == "1":
        texte = input(f"Saisissez {nom} sur une ligne :\n")
        return normaliser_texte_multilingue(texte), "texte saisi"

    url = input("URL de la page MediaWiki : ").strip()
    texte = recuperer_texte_mediawiki(url)
    return normaliser_texte_multilingue(texte), url


if __name__ == "__main__":
    try:
        texte, source = saisir_texte_utilisateur("le texte à analyser")
        limite_saisie = input(
            "Nombre de caractères à afficher (27 par défaut, 0 pour tous) : "
        ).strip()
        limite = int(limite_saisie) if limite_saisie else 27
        if limite < 0:
            raise ValueError("Le nombre doit être positif ou nul.")
        if limite == 0:
            limite = None
        statistiques = calculer_statistiques(texte)
        afficher_statistiques(source, statistiques, limite)
    except Exception as erreur:
        print(f"Impossible d'analyser le texte : {erreur}")