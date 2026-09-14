from collections import Counter
import json
import unicodedata
import urllib.request
from urllib.parse import unquote, urlencode, urlsplit

from fonction_outils import recuperer_texte_mediawiki, nettoyer_texte

def extraire_titre_et_api(url):
    """Vérifie une URL MediaWiki et renvoie le titre et l'URL de son API."""
    morceaux_url = urlsplit(url)

    if not morceaux_url.scheme or not morceaux_url.netloc:
        raise ValueError("L'URL fournie est invalide")
    if "/wiki/" not in morceaux_url.path:
        raise ValueError("L'URL doit être une page MediaWiki (/wiki/Titre)")

    titre = unquote(morceaux_url.path.split("/wiki/", 1)[1])
    if not titre:
        raise ValueError("Le titre de la page MediaWiki est vide")

    api_url = f"{morceaux_url.scheme}://{morceaux_url.netloc}/w/api.php"
    return titre, api_url


def calculer_statistiques(texte):
    """Renvoie les nombres de caractères et leurs fréquences."""
    return {
        "total_avec_espaces": len(texte),
        "total_sans_espaces": len(texte.replace(" ", "")),
        "frequences": Counter(texte),
    }


def afficher_statistiques(url, statistiques, limite=27):
    """Affiche les caractères les plus fréquents."""
    total = statistiques["total_avec_espaces"]
    frequences = statistiques["frequences"]

    print(f"=== Statistiques pour l'URL : {url} ===")
    print(f"Nombre total de caractères (avec espaces) : {total}")
    print(
        "Nombre total de caractères (sans espaces) : "
        f"{statistiques['total_sans_espaces']}"
    )
    print(f"\n--- Top {limite} des caractères les plus fréquents ---")

    for caractere, frequence in frequences.most_common(limite):
        nom_caractere = "'Espace'" if caractere == " " else f"'{caractere}'"
        pourcentage = (frequence / total) * 100 if total else 0
        print(f"{nom_caractere} : {frequence} fois ({pourcentage:.2f}%)")


def analyser_page_web(url, limite=27):
    """Récupère, nettoie, analyse et affiche les statistiques d'une page MediaWiki."""
    try:
        texte_brut = recuperer_texte_mediawiki(url)
        texte_propre = nettoyer_texte(texte_brut)
        statistiques = calculer_statistiques(texte_propre)
        afficher_statistiques(url, statistiques, limite)
        return statistiques
    except Exception as erreur:
        print(f"Une erreur est survenue lors de la récupération : {erreur}")
        return None


if __name__ == "__main__":
    url_cible = "https://fr.wikipedia.org/wiki/Château"
    analyser_page_web(url_cible)