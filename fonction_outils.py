# Fonctions utilitaires :
# 1. Téléchargement de texte brut depuis Wikipédia via l'API MediaWiki
# 2. Nettoyage du texte pour ne garder que les 27 caractères usuels (A-Z et espaces)

import json
import ssl
import unicodedata
import urllib.request
from urllib.parse import unquote, urlencode, urlsplit


def extraire_titre_et_api(url: str):
    """Vérifie l'URL Wikipédia et extrait le titre de l'article ainsi que l'adresse de son API."""
    morceaux_url = urlsplit(url)

    if not morceaux_url.scheme or not morceaux_url.netloc:
        raise ValueError("L'URL fournie est invalide")
    if "/wiki/" not in morceaux_url.path:
        raise ValueError("L'URL doit être une page MediaWiki (/wiki/Titre)")

    titre = unquote(morceaux_url.path.split("/wiki/", 1)[1])
    if not titre:
        raise ValueError("Le titre de la page MediaWiki est vide")

    # L'API MediaWiki est accessible sur /w/api.php
    api_url = f"{morceaux_url.scheme}://{morceaux_url.netloc}/w/api.php"
    return titre, api_url


def recuperer_texte_mediawiki(url: str) -> str:
    """Télécharge le contenu textuel brut d'un article Wikipédia (sans le code HTML)."""
    titre, api_url = extraire_titre_et_api(url)
    
    # Paramètres de l'API Wikipédia pour demander le texte brut (explaintext)
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

    # Contexte SSL tolérant pour éviter les blocages de certificats locaux
    contexte_ssl = ssl._create_unverified_context()

    with urllib.request.urlopen(requete, timeout=15, context=contexte_ssl) as reponse:
        donnees = json.load(reponse)

    pages = donnees.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        raise ValueError(f"Page MediaWiki introuvable : {titre}")

    return pages[0].get("extract", "")


def est_caractere_analyse(caractere: str) -> bool:
    """Indique si un caractère est une lettre de l'alphabet."""
    return caractere.isalpha()


def nettoyer_texte(texte: str) -> str:
    """
    Normalise le texte pour l'analyse cryptographique :
    - Remplace les ligatures (ex: Œ -> OE)
    - Enlève les accents (é -> E, à -> A) via la décomposition Unicode NFD
    - Remplace les chiffres et la ponctuation par des espaces
    - Met tout en majuscules et regroupe les espaces consécutifs
    Résultat : un flux propre contenant uniquement les 26 lettres A-Z et des espaces simples.
    """
    texte = texte.upper().replace("Œ", "OE").replace("Æ", "AE")
    texte = unicodedata.normalize("NFD", texte.upper())

    # On ne garde que les lettres alphabétiques et les espaces
    texte = "".join(
        caractere if est_caractere_analyse(caractere) else " "
        for caractere in texte
        if not unicodedata.combining(caractere)
    )

    # Regroupe les espaces multiples en un seul espace
    return " ".join(texte.split())
