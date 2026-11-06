# Analyse fréquentielle des caractères dans un texte.
# Permet de compter le nombre d'apparitions de chaque lettre et d'afficher
# un histogramme textuel des fréquences (utilisé pour les langues naturelles).

from collections import Counter
import unicodedata

from fonction_outils import recuperer_texte_mediawiki


def normaliser_texte_multilingue(texte: str) -> str:
    """Normalise la casse en préservant les lettres de toute langue (français, allemand, etc.)."""
    # Préserve le 'ß' allemand sous sa majuscule officielle 'ẞ' (U+1E9E)
    texte = texte.replace("ß", "ẞ")
    texte = unicodedata.normalize("NFC", texte).upper()
    caracteres = []

    for caractere in texte:
        categorie = unicodedata.category(caractere)
        # 'L' pour Letter (lettres), 'M' pour Mark (accents combinés)
        if categorie.startswith(("L", "M")):
            caracteres.append(caractere)
        else:
            caracteres.append(" ")

    return " ".join("".join(caracteres).split())


def calculer_statistiques(texte: str) -> dict:
    """Compte le nombre total de caractères et les occurrences de chaque lettre."""
    return {
        "total_avec_espaces": len(texte),
        "total_sans_espaces": len(texte.replace(" ", "")),
        "frequences": Counter(texte),  # Dictionnaire {caractère: nombre_d_apparitions}
    }


def afficher_statistiques(source: str, statistiques: dict, limite: int = 27) -> None:
    """Affiche le classement des lettres les plus fréquentes avec une barre visuelle."""
    total = statistiques["total_avec_espaces"]
    frequences = statistiques["frequences"]

    print(f"\n=== Statistiques pour : {source} ===")
    print(f"Total caractères (avec espaces) : {total}")
    print(f"Total caractères (sans espaces) : {statistiques['total_sans_espaces']}")
    print(f"Nombre de caractères distincts  : {len(frequences)}")

    titre = "Tous les caractères" if limite is None else f"Top {limite}"
    print(f"\n--- {titre} les plus fréquents ---")

    # Affiche chaque lettre avec son pourcentage et une barre en blocs █
    for caractere, frequence in frequences.most_common(limite):
        nom_caractere = "'Espace'" if caractere == " " else f"'{caractere}'"
        pourcentage = (frequence / total) * 100 if total else 0
        barre = "█" * int(pourcentage / 2)
        print(f"{nom_caractere:<10} : {frequence:5d} fois ({pourcentage:5.2f}%) {barre}")


def saisir_texte_utilisateur(nom: str) -> tuple[str, str]:
    """Invite l'utilisateur à entrer un texte (soit par copier-coller multiligne, soit via une page Wikipédia)."""
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
        print(f"Collez {nom} ci-dessous")
        print("(puis appuyez 2× sur Entrée pour valider) :")
        lignes = []
        while True:
            ligne = input()
            if not ligne.strip():
                break
            lignes.append(ligne)
        texte = " ".join(lignes)
        return normaliser_texte_multilingue(texte), "texte saisi"

    # Option 2 : Téléchargement depuis Wikipédia
    url = input("URL de la page MediaWiki (ex: https://fr.wikipedia.org/wiki/Château) : ").strip()
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
