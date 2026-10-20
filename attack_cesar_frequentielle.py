from collections import Counter
import string

from cesar import chiffrement_cesar, dechiffrement_cesar
from fonction_outils import nettoyer_texte, recuperer_texte_mediawiki
from analyse_frequentielle import saisir_texte_utilisateur

# Alphabet latin usuel de 26 lettres (A à Z)
ALPHABET = list(string.ascii_uppercase)

# Pages Wikipédia de référence par langue pour le calcul dynamique des fréquences
PAGES_REFERENCE_LANGUES = {
    "1": ("Français", "https://fr.wikipedia.org/wiki/Château"),
    "2": ("Anglais", "https://en.wikipedia.org/wiki/Castle"),
    "3": ("Espagnol", "https://es.wikipedia.org/wiki/Castillo"),
    "4": ("Allemand", "https://de.wikipedia.org/wiki/Burg"),
    "5": ("Italien", "https://it.wikipedia.org/wiki/Castello"),
}

# Cache en mémoire pour éviter les téléchargements répétés
_CACHE_FREQUENCES: dict[str, dict[str, float]] = {}


def extraire_frequences_reference(texte_reference: str) -> dict[str, float]:
    """Calcule dynamiquement les fréquences de chaque lettre dans un texte de référence."""
    texte_propre = nettoyer_texte(texte_reference)
    lettres = [c for c in texte_propre if c in ALPHABET]
    total = len(lettres)

    if total == 0:
        return {lettre: 1.0 / len(ALPHABET) for lettre in ALPHABET}

    # Lissage de Laplace (+1) pour éviter les probabilités nulles
    comptes = Counter(lettres)
    total_lisse = total + len(ALPHABET)
    return {lettre: (comptes[lettre] + 1) / total_lisse for lettre in ALPHABET}


def obtenir_frequences_langue(source: str = "1") -> tuple[dict[str, float], str]:
    """Récupère dynamiquement les fréquences depuis la page Wikipédia de référence."""
    if source in PAGES_REFERENCE_LANGUES:
        nom_langue, url = PAGES_REFERENCE_LANGUES[source]
        description = f"{nom_langue} (Wikipédia: {url})"
    elif source.startswith("http"):
        url = source
        description = f"Page ({url})"
    else:
        url = f"https://fr.wikipedia.org/wiki/{source.strip().replace(' ', '_')}"
        description = f"Wikipédia ({url})"

    if url in _CACHE_FREQUENCES:
        return _CACHE_FREQUENCES[url], description

    print(f"Extraction dynamique des statistiques de la langue depuis {url}...")
    texte_brut = recuperer_texte_mediawiki(url)
    freq_ref = extraire_frequences_reference(texte_brut)
    _CACHE_FREQUENCES[url] = freq_ref
    return freq_ref, description




def distance_khi_deux(texte: str, freq_reference: dict[str, float]) -> float:
    """Mesure la distance du Khi-deux (χ²) entre les fréquences observées et la référence.

    Plus la valeur est faible, plus le texte ressemble statistiquement à la langue cible.
    """
    lettres = [c for c in texte if c in ALPHABET]
    n = len(lettres)
    if n == 0:
        return float("inf")

    comptes = Counter(lettres)
    score = 0.0
    for lettre in ALPHABET:
        observe = comptes[lettre]
        attendu = n * freq_reference[lettre]
        score += ((observe - attendu) ** 2) / attendu
    return score


def attaque_frequentielle_cesar(
    texte_chiffre: str,
    freq_ref: dict[str, float] | None = None,
) -> dict:
    """Attaque fréquentielle sur le chiffre de César.

    Principe cryptanalytique :
    1. Compte les occurrences des lettres dans le cryptogramme.
    2. Identifie la lettre chiffrée dominante (C_max).
    3. Déduit immédiatement le décalage sous l'hypothèse principale : C_max -> Lettre_max
       k = (position(C_max) - position(Lettre_max)) mod 26
    4. Évalue et départage l'ensemble des 26 décalages via la distance du Khi-deux (χ²)
       pour garantir la robustesse même sur les textes atypiques ou courts.
    """
    texte_chiffre = nettoyer_texte(texte_chiffre)
    lettres_crypto = [c for c in texte_chiffre if c in ALPHABET]
    if not lettres_crypto:
        raise ValueError("Le cryptogramme ne contient aucune lettre analysable (A-Z).")

    # Si aucune fréquence n'est fournie, charger la référence française par défaut
    if freq_ref is None:
        freq_ref, _ = obtenir_frequences_langue("1")

    lettre_ref_max = max(freq_ref, key=freq_ref.get)

    # 1. Fréquences locales du cryptogramme
    comptes_crypto = Counter(lettres_crypto)
    lettre_crypto_max, occurrences_max = comptes_crypto.most_common(1)[0]

    # 2. Déduction directe de la clé par appariement avec la lettre la plus fréquente
    idx_crypto = ALPHABET.index(lettre_crypto_max)
    idx_ref = ALPHABET.index(lettre_ref_max)
    decalage_direct = (idx_crypto - idx_ref) % 26

    # 3. Validation statistique globale (Khi-deux) pour tous les décalages
    candidats = []
    for decalage in range(26):
        texte_dechiffre = dechiffrement_cesar(texte_chiffre, decalage)
        score_khi2 = distance_khi_deux(texte_dechiffre, freq_ref)
        candidats.append((score_khi2, decalage, texte_dechiffre))

    # Tri par score croissant (le plus petit Khi-deux est le meilleur)
    candidats.sort(key=lambda x: x[0])
    meilleur_score, meilleur_decalage, meilleur_texte = candidats[0]

    return {
        "decalage_direct": decalage_direct,
        "meilleur_decalage": meilleur_decalage,
        "meilleur_texte": meilleur_texte,
        "meilleur_score": meilleur_score,
        "lettre_crypto_max": lettre_crypto_max,
        "occurrences_max": occurrences_max,
        "pourcentage_crypto_max": (occurrences_max / len(lettres_crypto)) * 100,
        "lettre_ref_max": lettre_ref_max,
        "pourcentage_ref_max": freq_ref[lettre_ref_max] * 100,
        "top_lettres_crypto": comptes_crypto.most_common(5),
        "candidats": candidats[:5],
    }


def _chiffrer_texte() -> None:
    """Chiffre un texte avec une clé César choisie par l'utilisateur."""
    texte_clair, source = saisir_texte_utilisateur("le texte à chiffrer")
    texte_propre = nettoyer_texte(texte_clair)
    if not texte_propre:
        raise ValueError("Le texte à chiffrer ne contient aucune lettre.")

    decalage_saisi = input("\nDécalage à appliquer (entier de 0 à 25) : ").strip()
    decalage = int(decalage_saisi) % 26

    texte_chiffre = chiffrement_cesar(texte_propre, decalage)

    print(f"\nSource        : {source}")
    print(f"Décalage (clé): {decalage}")
    print(f"Texte chiffré :\n{texte_chiffre}")


def _attaquer_cryptogramme() -> None:
    """Lance l'attaque fréquentielle sur un message chiffré."""
    texte_chiffre, source_crypto = saisir_texte_utilisateur("le cryptogramme")
    texte_chiffre = nettoyer_texte(texte_chiffre)
    if not texte_chiffre:
        raise ValueError("Le cryptogramme ne contient aucune lettre.")

    print("\nChoix de la langue de référence (extraction dynamique Wikipédia) :")
    print("1. Français (fr) [par défaut]")
    print("2. Anglais (en)")
    print("3. Espagnol (es)")
    print("4. Allemand (de)")
    print("5. Italien (it)")
    print("6. Page Wikipédia personnalisée (URL ou titre)")
    choix_langue = input("Votre choix (1 à 6, défaut 1) : ").strip() or "1"

    if choix_langue == "6":
        source_ref = input("URL ou titre Wikipédia personnalisé : ").strip() or "Château"
    else:
        source_ref = choix_langue

    freq_ref, description_ref = obtenir_frequences_langue(source_ref)
    resultats = attaque_frequentielle_cesar(texte_chiffre, freq_ref)

    largeur = 72
    print("\n" + "=" * largeur)
    print("        RÉSULTATS DE L'ATTAQUE FRÉQUENTIELLE SUR CÉSAR")
    print("=" * largeur)
    print(f" Cryptogramme : {source_crypto} ({len(texte_chiffre)} caractères)")
    print(f" Référence    : {description_ref}")

    print("\n 1. ANALYSE FRÉQUENTIELLE DU CRYPTOGRAMME :")
    top_str = ", ".join(f"'{c}' ({n} fois)" for c, n in resultats["top_lettres_crypto"])
    print(f"    Lettres les plus fréquentes : {top_str}")
    print(
        f"    Lettre chiffrée dominante   : '{resultats['lettre_crypto_max']}' "
        f"({resultats['pourcentage_crypto_max']:.1f}% des lettres)"
    )
    print(
        f"    Lettre attendue pour {description_ref.split()[0]} : '{resultats['lettre_ref_max']}' "
        f"({resultats['pourcentage_ref_max']:.1f}% mesuré)"
    )

    print("\n 2. DÉDUCTION IMMÉDIATE DE LA CLÉ (Hypothèse principale) :")
    print(
        f"    Formule : Décalage = (ord('{resultats['lettre_crypto_max']}') "
        f"- ord('{resultats['lettre_ref_max']}')) mod 26"
    )
    print(f"    => Décalage estimé : {resultats['decalage_direct']}")

    print("\n 3. VALIDATION GLOBALE PAR LE TEST DU KHI-DEUX (χ²) :")
    print("    Rang   Clé    Score χ² (plus petit = meilleur)   Aperçu du texte")
    print("    ────   ───    ────────────────────────────────   ───────────────")
    for rang, (score, d, txt) in enumerate(resultats["candidats"], 1):
        marqueur = " <== RETENU" if d == resultats["meilleur_decalage"] else ""
        apercu = txt[:35] + ("..." if len(txt) > 35 else "")
        print(f"     {rang:2d}.   {d:2d}     χ² = {score:8.2f}                   {apercu}{marqueur}")

    print("\n 4. MESSAGE DÉCHIFFRÉ FINAL :")
    print("-" * largeur)
    print(resultats["meilleur_texte"])
    print("-" * largeur + "\n")


def main() -> None:
    print("1. Chiffrer un texte avec César")
    print("2. Attaquer un cryptogramme par analyse fréquentielle")
    choix = input("Votre choix (1 ou 2) : ").strip()

    if choix == "1":
        _chiffrer_texte()
    elif choix == "2":
        _attaquer_cryptogramme()
    else:
        raise ValueError("Choix invalide : entrez 1 ou 2.")


if __name__ == "__main__":
    try:
        main()
    except Exception as erreur:
        print(f"Impossible d'effectuer l'opération : {erreur}")