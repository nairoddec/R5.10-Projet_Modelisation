from collections import Counter
import math
import unicodedata

from analyse_frequentielle import (
    calculer_statistiques,
    normaliser_texte_multilingue,
    saisir_texte_utilisateur,
)


def extraire_alphabet_unicode(texte):
    """Construit un alphabet déterministe avec les lettres/signes observés."""
    return sorted({
        caractere
        for caractere in texte
        if unicodedata.category(caractere).startswith(("L", "M"))
    })


def transformer_cesar_unicode(texte, decalage, alphabet):
    """Applique un décalage dans l'alphabet fourni, en gardant les espaces."""
    if not alphabet or len(set(alphabet)) != len(alphabet):
        raise ValueError("L'alphabet doit contenir des symboles uniques.")

    positions = {caractere: index for index, caractere in enumerate(alphabet)}
    resultat = []
    for caractere in texte:
        if caractere in positions:
            nouvel_index = (positions[caractere] + decalage) % len(alphabet)
            resultat.append(alphabet[nouvel_index])
        else:
            resultat.append(caractere)
    return "".join(resultat)


def chiffrer_cesar_unicode(texte, decalage, alphabet=None):
    """Chiffre avec un alphabet Unicode donné ou déduit du texte."""
    texte = normaliser_texte_multilingue(texte)
    alphabet = alphabet or extraire_alphabet_unicode(texte)
    return transformer_cesar_unicode(texte, decalage, alphabet)


def dechiffrer_cesar_unicode(texte_chiffre, decalage, alphabet):
    """Déchiffre un décalage Unicode avec l'alphabet convenu."""
    return transformer_cesar_unicode(texte_chiffre, -decalage, alphabet)


def score_digrammes(texte, statistiques_reference):
    """Évalue la ressemblance des paires de caractères avec la référence."""
    texte_reference = statistiques_reference.get("texte", "")
    if len(texte_reference) < 2:
        raise ValueError("Le texte de référence doit contenir au moins deux caractères.")

    frequences_digrammes = Counter(
        texte_reference[index:index + 2]
        for index in range(len(texte_reference) - 1)
    )
    comptes = Counter(texte[index:index + 2] for index in range(len(texte) - 1))
    total_reference = len(texte_reference) - 1
    taille_vocabulaire = max(len(set(texte_reference)) ** 2, 1)
    denominateur = total_reference + taille_vocabulaire
    return sum(
        occurrences * math.log(
            (frequences_digrammes.get(digramme, 0) + 1) / denominateur
        )
        for digramme, occurrences in comptes.items()
    )


def attaque_frequentielle_cesar(texte_chiffre,statistiques_reference,alphabet=None,):
    """Teste chaque décalage et garde le texte au score de digrammes maximal.

    L'alphabet doit être identique à celui utilisé pour chiffrer. Si aucun
    alphabet n'est fourni, les symboles observés sont triés selon Unicode.
    """
    texte_chiffre = normaliser_texte_multilingue(texte_chiffre)
    texte_reference = statistiques_reference.get("texte")
    if texte_reference is None:
        raise ValueError("Les statistiques de référence doivent inclure le texte.")

    alphabet = alphabet or extraire_alphabet_unicode(texte_chiffre)
    if not alphabet:
        raise ValueError("Le cryptogramme ne contient aucun symbole analysable.")

    candidats = []
    for decalage in range(len(alphabet)):
        texte = dechiffrer_cesar_unicode(texte_chiffre, decalage, alphabet)
        score = score_digrammes(texte, statistiques_reference)
        candidats.append((score, decalage, texte))

    meilleur_score, meilleur_decalage, meilleur_texte = max(
        candidats, key=lambda candidat: (candidat[0], -candidat[1])
    )
    statistiques_chiffre = calculer_statistiques(texte_chiffre)
    lettre_reference = _symbole_le_plus_frequent(statistiques_reference)
    lettre_chiffree = _symbole_le_plus_frequent(statistiques_chiffre)

    return (meilleur_decalage,meilleur_texte,lettre_reference,lettre_chiffree, meilleur_score,
        sorted(candidats, key=lambda candidat: (-candidat[0], candidat[1]))[:5],
    )


def _symbole_le_plus_frequent(statistiques):
    frequences = statistiques["frequences"]
    symboles = {
        caractere: nombre
        for caractere, nombre in frequences.items()
        if unicodedata.category(caractere).startswith(("L", "M"))
    }
    return max(symboles, key=symboles.get) if symboles else "(aucun)"


def _saisir_alphabet(texte_chiffre):
    alphabet_auto = extraire_alphabet_unicode(texte_chiffre)
    print("\nOrdre de l'alphabet utilisé pour le chiffrement :")
    print("1. Saisir l'alphabet dans son ordre exact")
    print("2. Déduire un ordre Unicode des symboles présents")
    choix = input("Votre choix (1 ou 2, défaut 2) : ").strip() or "2"

    if choix == "1":
        alphabet_saisi = normaliser_texte_multilingue(
            input("Saisissez les symboles de l'alphabet, sans séparateur : ")
        ).replace(" ", "")
        alphabet = list(alphabet_saisi)
        if len(set(alphabet)) != len(alphabet):
            raise ValueError("L'alphabet saisi contient des doublons.")
        symboles_manquants = set(alphabet_auto) - set(alphabet)
        if symboles_manquants:
            raise ValueError(
                "L'alphabet ne contient pas tous les symboles du cryptogramme."
            )
        return alphabet

    if choix != "2":
        raise ValueError("Choix invalide : entrez 1 ou 2.")
    return alphabet_auto


def _chiffrer_texte():
    texte_clair, source = saisir_texte_utilisateur("le texte à chiffrer")
    if not texte_clair:
        raise ValueError("Le texte à chiffrer doit contenir des caractères.")

    alphabet = _saisir_alphabet(texte_clair)
    decalage = int(input("Décalage à appliquer (entier) : ").strip())
    texte_chiffre = chiffrer_cesar_unicode(texte_clair, decalage, alphabet)

    print(f"\nSource : {source}")
    print(f"Décalage : {decalage}")
    print(f"Texte chiffré :\n{texte_chiffre}")


def _attaquer_cryptogramme():
    texte_reference, source_reference = saisir_texte_utilisateur(
        "le texte de référence (même langue que le message clair)"
    )
    texte_chiffre, source_cryptogramme = saisir_texte_utilisateur(
        "le cryptogramme"
    )
    if not texte_reference or not texte_chiffre:
        raise ValueError("Les deux textes doivent contenir des caractères.")

    alphabet = _saisir_alphabet(texte_chiffre)
    statistiques_reference = calculer_statistiques(texte_reference)
    statistiques_reference["texte"] = texte_reference

    (
        decalage,
        texte_dechiffre,
        symbole_reference,
        symbole_chiffre,
        score,
        meilleurs_candidats,
    ) = attaque_frequentielle_cesar(
        texte_chiffre,
        statistiques_reference,
        alphabet,
    )

    print(f"\nRéférence : {source_reference}")
    print(f"Cryptogramme : {source_cryptogramme}")
    print(f"Symbole le plus fréquent dans la référence : {symbole_reference}")
    print(f"Symbole le plus fréquent dans le cryptogramme : {symbole_chiffre}")
    print(f"Décalage estimé : {decalage} (score {score:.2f})")
    print(f"\nTexte déchiffré estimé :\n{texte_dechiffre}")
    print("\nMeilleurs décalages :")
    for score_candidat, decalage_candidat, texte_candidat in meilleurs_candidats:
        apercu = texte_candidat[:100]
        print(f"Décalage {decalage_candidat}: score {score_candidat:.2f} | {apercu}")


def main():
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