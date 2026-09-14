import json
import unicodedata
import urllib.request
from urllib.parse import unquote, urlencode, urlsplit


def est_caractere_analyse(caractere: str) -> bool:
    return caractere.isalpha()


def nettoyer_texte(texte: str) -> str:
    """Majuscules, lettres uniquement, sans accents ni chiffres."""
    texte = unicodedata.normalize("NFD", texte.upper())

    texte = "".join(
        caractere if est_caractere_analyse(caractere) else " "
        for caractere in texte
        if not unicodedata.combining(caractere)
    )

    return " ".join(texte.split())


def recuperer_texte_mediawiki(url: str) -> str:
    """Récupère le texte brut d'une page Wikipédia/MediaWiki."""
    morceaux_url = urlsplit(url)

    if not morceaux_url.scheme or not morceaux_url.netloc:
        raise ValueError("L'URL fournie est invalide")

    if "/wiki/" not in morceaux_url.path:
        raise ValueError("L'URL doit contenir /wiki/Titre")

    titre = unquote(morceaux_url.path.split("/wiki/", 1)[1])
    api_url = f"{morceaux_url.scheme}://{morceaux_url.netloc}/w/api.php"

    parametres = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "titles": titre,
        "format": "json",
        "formatversion": "2",
    }

    requete = urllib.request.Request(
        f"{api_url}?{urlencode(parametres)}",
        headers={"User-Agent": "AnalyseurTexte/1.0"},
    )

    with urllib.request.urlopen(requete, timeout=15) as reponse:
        donnees = json.load(reponse)

    pages = donnees.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        raise ValueError(f"Page MediaWiki introuvable : {titre}")

    return pages[0].get("extract", "")