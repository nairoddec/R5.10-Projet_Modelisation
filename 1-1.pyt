from collections import Counter
import json
import urllib.request
from urllib.parse import unquote, urlencode, urlsplit


def analyser_page_web(url):
    try:
        # 1. Récupération du texte brut par l'API MediaWiki
        morceaux_url = urlsplit(url)
        if "/wiki/" not in morceaux_url.path:
            raise ValueError("L'URL doit être une page MediaWiki (/wiki/Titre)")

        titre = unquote(morceaux_url.path.split("/wiki/", 1)[1])
        if not titre:
            raise ValueError("Le titre de la page MediaWiki est vide")

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

        texte_propre = pages[0].get("extract", "").upper()

        # 3. Calcul des statistiques
        total_caracteres = len(texte_propre)
        total_sans_espaces = len(texte_propre.replace(" ", ""))

        # Compte l'occurrence de chaque caractère
        compteur = Counter(texte_propre)

        # 4. Affichage des résultats
        print(f"=== Statistiques pour l'URL : {url} ===")
        print(f"Nombre total de caractères (avec espaces) : {total_caracteres}")
        print(f"Nombre total de caractères (sans espaces) : {total_sans_espaces}")
        print("\n--- Top 15 des caractères les plus fréquents ---")

        # Tri et affichage des 15 caractères les plus utilisés
        for caractere, frequence in compteur.most_common(15):
            # Remplacement visuel pour les espaces pour plus de clarté
            nom_caractere = (
                f"'{caractere}'" if caractere != " " else "'Espace' "
            )
            
            pourcentage = (frequence / total_caracteres) * 100 if total_caracteres else 0

            print(
                f"{nom_caractere} : {frequence} fois ({pourcentage:.2f}%)"
            )

    except Exception as e:
        print(f"Une erreur est survenue lors de la récupération : {e}")



#url_cible = "https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal"
url_cible = "https://fr.wikipedia.org/wiki/A"
analyser_page_web(url_cible)
