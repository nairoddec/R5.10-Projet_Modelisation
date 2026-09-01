from collections import Counter
import re
import urllib.request
from urllib.parse import quote


def analyser_page_web(url):
    try:
        # 1. Récupération de la page web
        headers = {"User-Agent": "Mozilla/5.0"}
        # Encode les caractères non ASCII (ex. « é ») pour former une URL valide.
        url_encodee = quote(url, safe=":/?&=#%")
        requete = urllib.request.Request(url_encodee, headers=headers)

        with urllib.request.urlopen(requete) as reponse:
            # Décodage du contenu en texte brut (UTF-8)
            html_brut = reponse.read().decode("utf-8")

        # 2. Nettoyage du HTML pour ne garder que le texte visible
        # Supprime les balises <script> et <style> et leur contenu
        texte_propre = re.sub(
            r"<script[^>]*>[\s\S]*?</script>|<style[^>]*>[\s\S]*?</style>",
            "",
            html_brut,
        )
        # Supprime toutes les autres balises HTML
        texte_propre = re.sub(r"<[^>]+>", "", texte_propre)
        # Remplace les entités d'espaces multiples par un seul espace
        texte_propre = " ".join(texte_propre.split())
        texte_propre = texte_propre.upper()

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
            
            pourcentage = (frequence / total_caracteres) * 100

            print(
                f"{nom_caractere} : {frequence} fois ({pourcentage:.2f}%)"
            )

    except Exception as e:
        print(f"Une erreur est survenue lors de la récupération : {e}")



#url_cible = "https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal"
url_cible = "https://fr.wikipedia.org/wiki/A"
analyser_page_web(url_cible)
