import json
import ssl
import unicodedata
import urllib.request
from urllib.parse import unquote, urlencode, urlsplit

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

def recuperer_texte_mediawiki(url):
    """Récupère le texte brut d'une page MediaWiki grâce à son API."""
    titre, api_url = extraire_titre_et_api(url)
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

    # Création d'un contexte qui ignore la vérification du certificat SSL
    contexte_ssl = ssl._create_unverified_context()

    with urllib.request.urlopen(requete, timeout=15, context=contexte_ssl) as reponse:
        donnees = json.load(reponse)

    pages = donnees.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        raise ValueError(f"Page MediaWiki introuvable : {titre}")

    return pages[0].get("extract", "")

def est_caractere_analyse(caractere: str) -> bool:
    """Vérifie si le caractère est une lettre alphabétique."""
    return caractere.isalpha()

def nettoyer_texte(texte: str) -> str:
    """Met en majuscules, retire les accents, chiffres et ponctuation."""
    texte = unicodedata.normalize("NFD", texte.upper())

    texte = "".join(
        caractere if est_caractere_analyse(caractere) else " "
        for caractere in texte
        if not unicodedata.combining(caractere)
    )

    return " ".join(texte.split())