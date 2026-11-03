"""
Fichier de tests unitaires et d'intégration pour l'ensemble du projet R5.10.

Ce fichier couvre :
1. Tests unitaires des modules de chiffrement de base (César, Vigenère).
2. Tests unitaires des outils de nettoyage et d'analyse (Unicode, MediaWiki, fréquences).
3. Tests unitaires de la substitution et de la permutation (bijections, inverses, chiffrement).
4. Tests unitaires de l'analyse stochastique (digrammes, matrice de transitions, Markov, Indice de Coïncidence).
5. Tests unitaires des briques de l'attaque MCMC (score log, mutations valides).
6. Tests d'intégration de bout en bout (Chiffrement -> Cryptanalyse -> Restitution du texte clair).

Exécution :
    python3 -m unittest test_projet.py -v
"""

import importlib
import math
import os
import sys
import time
import unittest
from collections import Counter

# Import des modules du projet
import cesar
import vigenere
import fonction_outils
import analyse_frequentielle
import substitution
import permutation
import outils_digrammes
import attack_cesar_frequentielle
import attack_vigenere_ic

# Import dynamique de 1-5.py (nom de fichier contenant un tiret)
mcmc_module = importlib.import_module("1-5")


# =============================================================================
# COULEURS ANSI & FORMATTEUR D'AFFICHAGE ÉLÉGANT
# =============================================================================

class Color:
    """Codes de couleurs ANSI pour un rendu visuel moderne et soigné."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


CLASS_TITLES = {
    "TestCesar": "1. Chiffrement & Déchiffrement de César (cesar.py)",
    "TestVigenere": "2. Chiffrement polyalphabétique de Vigenère (vigenere.py)",
    "TestFonctionOutils": "3. Nettoyage de texte & API Wikipédia (fonction_outils.py)",
    "TestAnalyseFrequentielle": "4. Analyse fréquentielle des lettres (analyse_frequentielle.py)",
    "TestSubstitution": "5. Chiffrement par substitution générale (substitution.py)",
    "TestPermutation": "6. Chiffrement par permutation par blocs (permutation.py)",
    "TestOutilsDigrammes": "7. Matrice de transition & Modélisation de Markov (outils_digrammes.py)",
    "TestAttaqueCesarFrequentielle": "8. Cryptanalyse fréquentielle de César (attack_cesar_frequentielle.py)",
    "TestVigenereIndiceCoincidence": "9. Attaque Vigenère par Indice de Coïncidence (attack_vigenere_ic.py)",
    "TestMCMCLogique": "10. Heuristique MCMC & Score logarithmique (1-5.py)",
    "TestIntegrationPipelines": "11. Tests d'intégration de bout en bout (Pipelines complets)",
}


SUITE_ORDER = [
    "TestCesar",
    "TestVigenere",
    "TestFonctionOutils",
    "TestAnalyseFrequentielle",
    "TestSubstitution",
    "TestPermutation",
    "TestOutilsDigrammes",
    "TestAttaqueCesarFrequentielle",
    "TestVigenereIndiceCoincidence",
    "TestMCMCLogique",
    "TestIntegrationPipelines",
]


class BaseTestCase(unittest.TestCase):
    """Classe de base fournissant un formatage propre et évitant les coupures de ligne parasites."""

    def shortDescription(self):
        # Empêche standard unittest d'insérer brutalement la docstring sur une nouvelle ligne
        return None

    def __str__(self):
        # Format concis et élégant si exécuté avec 'python3 -m unittest'
        return f"{self._testMethodName} [{self.__class__.__name__}]"


class PrettyTestResult(unittest.TestResult):
    """Collecteur de résultats avec mesure de performance et affichage par catégories."""

    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream or sys.stdout
        self.start_times = {}
        self.current_class = None
        self.successes = 0

    def startTest(self, test):
        super().startTest(test)
        self.start_times[test.id()] = time.perf_counter()
        test_class = test.__class__.__name__
        if test_class != self.current_class:
            if self.current_class is not None:
                self.stream.write(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}\n")
            self.current_class = test_class
            title = CLASS_TITLES.get(test_class, test_class)
            self.stream.write(f"\n  {Color.CYAN}{Color.BOLD}┌─ [SUITE] {title}{Color.RESET}\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes += 1
        elapsed = (time.perf_counter() - self.start_times.get(test.id(), 0)) * 1000
        method_name = test._testMethodName
        self.stream.write(
            f"  {Color.CYAN}│{Color.RESET}  "
            f"{Color.WHITE}{method_name:<50}{Color.RESET} "
            f"[{Color.GREEN}PASS{Color.RESET}]  {Color.DIM}{elapsed:6.2f} ms{Color.RESET}\n"
        )
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        elapsed = (time.perf_counter() - self.start_times.get(test.id(), 0)) * 1000
        method_name = test._testMethodName
        self.stream.write(
            f"  {Color.CYAN}│{Color.RESET}  "
            f"{Color.BOLD}{method_name:<50}{Color.RESET} "
            f"[{Color.RED}FAIL{Color.RESET}]  {Color.DIM}{elapsed:6.2f} ms{Color.RESET}\n"
        )
        self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        elapsed = (time.perf_counter() - self.start_times.get(test.id(), 0)) * 1000
        method_name = test._testMethodName
        self.stream.write(
            f"  {Color.CYAN}│{Color.RESET}  "
            f"{Color.BOLD}{method_name:<50}{Color.RESET} "
            f"[{Color.RED}ERR!{Color.RESET}]  {Color.DIM}{elapsed:6.2f} ms{Color.RESET}\n"
        )
        self.stream.flush()


class PrettyTestRunner:
    """Test runner sobre avec mise en page structurée et mesure de temps."""

    def __init__(self, stream=None, verbosity=1, **kwargs):
        self.stream = stream or sys.stdout

    def _ordonner_suite(self, suite):
        """Réordonne les tests selon la progression logique du projet (1 à 11)."""
        tests_extraits = []

        def extraire(s):
            for element in s:
                if isinstance(element, unittest.TestSuite):
                    extraire(element)
                else:
                    tests_extraits.append(element)

        extraire(suite)

        def cle_tri(t):
            nom_classe = t.__class__.__name__
            rang = SUITE_ORDER.index(nom_classe) if nom_classe in SUITE_ORDER else 999
            return (rang, t._testMethodName)

        tests_extraits.sort(key=cle_tri)
        nouvelle_suite = unittest.TestSuite()
        nouvelle_suite.addTests(tests_extraits)
        return nouvelle_suite

    def run(self, test):
        suite_ordonnee = self._ordonner_suite(test)
        result = PrettyTestResult(self.stream)
        start_time = time.perf_counter()

        self.stream.write(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}\n")
        self.stream.write(
            f"{Color.BOLD}{Color.WHITE}         TESTS UNITAIRES & INTÉGRATION (R5.10){Color.RESET}\n"
        )
        self.stream.write(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")

        suite_ordonnee(result)

        total_time = time.perf_counter() - start_time
        total_tests = result.testsRun
        successes = result.successes
        failures = len(result.failures)
        errors = len(result.errors)

        if result.current_class:
            self.stream.write(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}\n")

        self.stream.write(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}\n")
        self.stream.write(f"{Color.BOLD}{Color.WHITE}                             BILAN{Color.RESET}\n")
        self.stream.write(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")

        pct = (successes / total_tests * 100) if total_tests > 0 else 0
        self.stream.write(f"  • Total des tests : {Color.BOLD}{total_tests}{Color.RESET}\n")
        self.stream.write(
            f"  • Succès          : {Color.GREEN}{Color.BOLD}{successes}{Color.RESET} ({pct:.1f}%)\n"
        )

        if failures > 0:
            self.stream.write(f"  • Échecs          : {Color.RED}{Color.BOLD}{failures}{Color.RESET}\n")
        else:
            self.stream.write(f"  • Échecs          : {Color.DIM}0{Color.RESET}\n")

        if errors > 0:
            self.stream.write(f"  • Erreurs         : {Color.RED}{Color.BOLD}{errors}{Color.RESET}\n")
        else:
            self.stream.write(f"  • Erreurs         : {Color.DIM}0{Color.RESET}\n")

        self.stream.write(f"  • Durée totale    : {Color.YELLOW}{total_time:.3f} s{Color.RESET}\n")
        self.stream.write(f"{Color.CYAN}{'─' * 78}{Color.RESET}\n")

        if result.wasSuccessful():
            self.stream.write(
                f"  {Color.GREEN}{Color.BOLD}Statut : Tous les tests sont validés.{Color.RESET}\n"
            )
        else:
            self.stream.write(
                f"  {Color.RED}{Color.BOLD}Statut : Échec de certains tests.{Color.RESET}\n"
            )
            for t, err in result.failures:
                self.stream.write(f"\n{Color.RED}ÉCHEC sur {t} :{Color.RESET}\n{err}\n")
            for t, err in result.errors:
                self.stream.write(f"\n{Color.RED}ERREUR sur {t} :{Color.RESET}\n{err}\n")

        self.stream.write(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n\n")
        return result


# Branchement automatique du formateur élégant même lors de l'appel 'python3 -m unittest'
import unittest.runner

def _hook_unittest_runner(self, test):
    runner = PrettyTestRunner(stream=self.stream)
    return runner.run(test)

unittest.runner.TextTestRunner.run = _hook_unittest_runner


# =============================================================================
# CLASSES DE TESTS UNITAIRES
# =============================================================================

class TestCesar(BaseTestCase):
    """Tests unitaires du chiffrement et déchiffrement de César."""

    def test_chiffrement_simple(self):
        # Décalage de 3 : 'A' -> 'D', 'B' -> 'E', etc.
        clair = "BONJOUR"
        attendu = "ERQMRXU"
        self.assertEqual(cesar.chiffrement_cesar(clair, 3), attendu)

    def test_preservation_espaces(self):
        texte = "LE CHIFFRE DE CESAR"
        chiffre = cesar.chiffrement_cesar(texte, 5)
        # Les espaces doivent rester des espaces aux mêmes positions
        for i, c in enumerate(texte):
            if c == " ":
                self.assertEqual(chiffre[i], " ")

    def test_reversibilite_cesar(self):
        # Chiffrer puis déchiffrer avec la même clé doit restituer le message exact
        original = "ATTAQUE FREQUENTIELLE SUR CESAR"
        for cle in [1, 7, 13, 25]:
            chiffre = cesar.chiffrement_cesar(original, cle)
            dechiffre = cesar.dechiffrement_cesar(chiffre, cle)
            self.assertEqual(dechiffre, original)

    def test_decalage_modulo(self):
        # Décalage 26 ou 0 ne doit pas modifier le texte
        original = "TEXTE INCHANGE"
        self.assertEqual(cesar.chiffrement_cesar(original, 26), original)
        self.assertEqual(cesar.chiffrement_cesar(original, 0), original)


class TestVigenere(BaseTestCase):
    """Tests unitaires du chiffrement de Vigenère."""

    def test_chiffrement_vigenere_simple(self):
        # Avec la clé 'B' (décalage de 1 partout), équivalent à un César +1
        clair = "ABC"
        self.assertEqual(vigenere.chiffrement_vigenere(clair, "B"), "BCD")

    def test_reversibilite_vigenere(self):
        texte = "MESSAGE SECRET A PROTEGER PAR VIGENERE"
        cle = "POLYALPHABETIQUE"
        chiffre = vigenere.chiffrement_vigenere(texte, cle)
        dechiffre = vigenere.dechiffrement_vigenere(chiffre, cle)
        self.assertEqual(dechiffre, texte)


class TestFonctionOutils(BaseTestCase):
    """Tests des fonctions de nettoyage et manipulation de chaînes."""

    def test_nettoyer_texte_accents_et_majuscules(self):
        brut = "Château & Éléphant, à l'œuvre !"
        propre = fonction_outils.nettoyer_texte(brut)
        # Doit être en majuscules, sans accents, avec 'OE' pour 'Œ', sans ponctuation
        self.assertIn("CHATEAU", propre)
        self.assertIn("ELEPHANT", propre)
        self.assertIn("OEUVRE", propre)
        # Ne doit contenir que des lettres majuscules et des espaces
        for c in propre:
            self.assertTrue(c.isupper() or c == " ", f"Caractère non conforme : {c!r}")

    def test_extraire_titre_et_api(self):
        url = "https://fr.wikipedia.org/wiki/Château"
        titre, api_url = fonction_outils.extraire_titre_et_api(url)
        self.assertEqual(titre, "Château")
        self.assertEqual(api_url, "https://fr.wikipedia.org/w/api.php")

    def test_url_invalide_leve_erreur(self):
        with self.assertRaises(ValueError):
            fonction_outils.extraire_titre_et_api("https://google.com/search?q=test")


class TestAnalyseFrequentielle(BaseTestCase):
    """Tests de comptage statistique des caractères."""

    def test_calculer_statistiques(self):
        texte = "AA BB C"
        stats = analyse_frequentielle.calculer_statistiques(texte)
        self.assertEqual(stats["total_avec_espaces"], 7)
        self.assertEqual(stats["total_sans_espaces"], 5)
        self.assertEqual(stats["frequences"]["A"], 2)
        self.assertEqual(stats["frequences"]["B"], 2)
        self.assertEqual(stats["frequences"][" "], 2)
        self.assertEqual(stats["frequences"]["C"], 1)

    def test_normaliser_multilingue_eszett(self):
        # Le 'ß' allemand doit être préservé sous sa forme majuscule officielle
        texte = "Straße"
        norm = analyse_frequentielle.normaliser_texte_multilingue(texte)
        self.assertIn("STRAẞE", norm)


class TestSubstitution(BaseTestCase):
    """Tests de la substitution monoalphabétique (Section 1.3)."""

    def setUp(self):
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")

    def test_generation_et_verification_cle(self):
        cle = substitution.generer_cle_aleatoire(self.alphabet)
        # La clé doit être valide (permutation complète de l'alphabet)
        self.assertTrue(substitution.verifier_cle(cle, self.alphabet))

    def test_inversion_cle(self):
        cle = substitution.generer_cle_aleatoire(self.alphabet)
        inverse = substitution.inverser_cle(cle)
        # Vérification mathématique : inverse(cle(c)) == c
        for c in self.alphabet:
            self.assertEqual(inverse[cle[c]], c)

    def test_chiffrement_dechiffrement_substitution(self):
        texte = "SUBSTITUTION AVEC ESPACE INCLUS"
        cle = substitution.generer_cle_aleatoire(self.alphabet)
        chiffre = substitution.chiffrer(texte, cle)
        dechiffre = substitution.dechiffrer(chiffre, cle)
        self.assertEqual(dechiffre, texte)


class TestPermutation(BaseTestCase):
    """Tests de la permutation de positions par blocs (Section 1.4)."""

    def test_verification_cle_permutation(self):
        cle_valide = [3, 0, 2, 1]
        self.assertTrue(permutation.verifier_cle_permutation(cle_valide))

        cle_invalide_doublon = [0, 1, 1, 3]
        with self.assertRaises(ValueError):
            permutation.verifier_cle_permutation(cle_invalide_doublon)

        cle_invalide_valeur_trop_grande = [0, 1, 4]
        with self.assertRaises(ValueError):
            permutation.verifier_cle_permutation(cle_invalide_valeur_trop_grande)

    def test_exemple_du_sujet_permutation(self):
        # Exemple donné dans l'énoncé du projet : clé [3, 0, 2, 1] sur 'BONJOUR'
        # 'BONJ' -> 'OJNB'
        # 'OUR ' (avec padding) -> 'U RO'
        # Résultat : 'OJNBU RO'
        cle = [3, 0, 2, 1]
        texte = "BONJOUR"
        chiffre = permutation.chiffrer_permutation(texte, cle)
        self.assertEqual(chiffre, "OJNBU RO")

    def test_reversibilite_permutation(self):
        cle = [2, 0, 4, 1, 3]  # Longueur 5
        texte = "CE TEXTE EST UN TEST DE PERMUTATION PAR BLOCS"
        chiffre = permutation.chiffrer_permutation(texte, cle)
        dechiffre = permutation.dechiffrer_permutation(chiffre, cle)
        # Le déchiffrement doit restituer le texte original (aux espaces de padding près)
        self.assertEqual(dechiffre.rstrip(), texte.rstrip())


class TestOutilsDigrammes(BaseTestCase):
    """Tests de l'analyse des bigrammes et matrice de Markov (Section 1.2)."""

    def test_statistiques_digrammes(self):
        texte = "ABABA"  # Digrammes : 'AB' (2 fois), 'BA' (2 fois)
        stats = outils_digrammes.statistiques_digrammes(texte)
        self.assertEqual(stats["AB"]["occurrences"], 2)
        self.assertEqual(stats["BA"]["occurrences"], 2)
        self.assertEqual(stats["AB"]["pourcentage"], 50.0)

    def test_propriete_stochastique_matrice_transitions(self):
        texte = "LE CHATEAU EST FORT ET LE PONT EST GRAND"
        stats = outils_digrammes.statistiques_digrammes(texte)
        alphabet = outils_digrammes.extraire_alphabet(texte)
        matrice, _, _ = outils_digrammes.construire_matrice_transitions(stats, alphabet)

        # Pour chaque ligne ayant des transitions, la somme des probabilités doit valoir 1
        for i in range(matrice.shape[0]):
            somme_ligne = matrice[i, :].sum()
            if somme_ligne > 0:
                self.assertAlmostEqual(somme_ligne, 1.0, places=5)

    def test_generation_markov(self):
        texte = "UN PETIT EXEMPLE DE TEXTE POUR MARKOV"
        stats = outils_digrammes.statistiques_digrammes(texte)
        alphabet = outils_digrammes.extraire_alphabet(texte)
        matrice, char2idx, idx2char = outils_digrammes.construire_matrice_transitions(stats, alphabet)

        simule = outils_digrammes.generer_texte_markov(matrice, char2idx, idx2char, longueur=40)
        self.assertEqual(len(simule), 40)
        # Doit commencer par un espace (état initial)
        self.assertEqual(simule[0], " ")


class TestAttaqueCesarFrequentielle(BaseTestCase):
    """Tests de l'analyse fréquentielle et Khi-deux sur César."""

    def test_lissage_laplace(self):
        # Le lissage doit garantir qu'aucune lettre n'a une probabilité nulle
        corpus = "AAAAA"
        freqs = attack_cesar_frequentielle.extraire_frequences_reference(corpus)
        for c in attack_cesar_frequentielle.ALPHABET:
            self.assertGreater(freqs[c], 0.0)
        # La somme des probabilités doit être égale à 1
        self.assertAlmostEqual(sum(freqs.values()), 1.0, places=5)

    def test_khi_deux_optimal_sur_texte_identique(self):
        # La distance Khi-deux entre un profil et son propre échantillon doit être minimale
        texte = "LE TEXTE DE REFERENCE DU PROJET DE MODELISATION"
        freqs = attack_cesar_frequentielle.extraire_frequences_reference(texte)
        score_bon = attack_cesar_frequentielle.distance_khi_deux(texte, freqs)
        # Un texte brouillé doit avoir un score Khi-deux bien plus élevé
        texte_brouille = "ZZZZ ZZZZZ ZZ ZZZZZZZZZ ZZ ZZZZZZ ZZ ZZZZZZZZZZZZZ"
        score_mauvais = attack_cesar_frequentielle.distance_khi_deux(texte_brouille, freqs)
        self.assertLess(score_bon, score_mauvais)


class TestVigenereIndiceCoincidence(BaseTestCase):
    """Tests de l'attaque Vigenère par Indice de Coïncidence (IC)."""

    def test_indice_coincidence_francais_vs_uniforme(self):
        # En français naturel, l'IC est proche de 0.074.
        # Sur un texte uniforme (aléatoire), l'IC est proche de 1/26 ≈ 0.038.
        texte_francais = "CETTE PHRASE PERMET DE MESURER L INDICE DE COINCIDENCE DU FRANCAIS" * 10
        ic_fr = attack_vigenere_ic.indice_coincidence(texte_francais.replace(" ", ""))
        self.assertGreater(ic_fr, 0.05)

    def test_decoupage_colonnes(self):
        texte = "ABCDEFGHI"
        cols = attack_vigenere_ic.colonnes(texte, 3)
        self.assertEqual(cols, ["ADG", "BEH", "CFI"])


class TestMCMCLogique(BaseTestCase):
    """Tests des mécanismes internes de l'algorithme MCMC (Section 1.5)."""

    def setUp(self):
        self.ref_texte = "LE CHATEAU EST ANCIEN ET GRAND AVEC DE BELLES TOURS"
        self.stats_ref = outils_digrammes.statistiques_digrammes(self.ref_texte)

    def test_score_log_discrimine_sens(self):
        # Un texte cohérent avec la référence doit avoir un meilleur score log qu'un charabia
        texte_coherent = "LE CHATEAU EST GRAND"
        texte_charabia = "ZX QKJXWW QZ JKXQZ"

        score_bon = mcmc_module.calculer_score_log(texte_coherent, self.stats_ref)
        score_mauvais = mcmc_module.calculer_score_log(texte_charabia, self.stats_ref)
        self.assertGreater(score_bon, score_mauvais)

    def test_mutation_substitution_preserve_bijection(self):
        alphabet = list("ABCDE ")
        cle_initiale = dict(zip(alphabet, alphabet))
        cle_mutee = mcmc_module.muter_substitution(cle_initiale)
        # La clé mutée doit rester une permutation valide sans perte de lettres
        self.assertEqual(set(cle_mutee.keys()), set(alphabet))
        self.assertEqual(set(cle_mutee.values()), set(alphabet))

    def test_mutation_permutation_preserve_positions(self):
        cle = [0, 1, 2, 3, 4, 5, 6]
        cle_mutee = mcmc_module.muter_permutation(cle)
        # La clé mutée doit rester une permutation exacte de [0..6]
        self.assertEqual(sorted(cle_mutee), cle)


# =============================================================================
# TESTS D'INTÉGRATION (Pipelines complets du projet)
# =============================================================================

class TestIntegrationPipelines(BaseTestCase):
    """Tests d'intégration validant les chaînes complètes de cryptanalyse."""

    def test_integration_attaque_cesar(self):
        """Pipeline complet César : Chiffrement -> Attaque fréquentielle -> Restitution."""
        texte_clair = (
            "L ANALYSE FREQUENTIELLE REPOSE SUR LE FAIT QUE LA LETTRE E "
            "EST LA PLUS FREQUENTE DANS LA LANGUE FRANCAISE DE MANIERE NATURELLE"
        )
        decalage_secret = 11
        cryptogramme = cesar.chiffrement_cesar(texte_clair, decalage_secret)

        # Profil de référence simulé (français avec 'E' dominant)
        freq_ref = {c: 0.01 for c in attack_cesar_frequentielle.ALPHABET}
        freq_ref["E"] = 0.15
        freq_ref["A"] = 0.08
        freq_ref["S"] = 0.08
        freq_ref["I"] = 0.07

        # Lancement de l'attaque analytique
        resultats = attack_cesar_frequentielle.attaque_frequentielle_cesar(cryptogramme, freq_ref)

        # La clé trouvée doit être exactement le décalage secret (11)
        self.assertEqual(resultats["decalage_direct"], decalage_secret)
        self.assertEqual(resultats["meilleur_decalage"], decalage_secret)
        self.assertEqual(resultats["meilleur_texte"], texte_clair)

    def test_integration_fichiers_crypto_disponibles(self):
        """Vérifie que les cryptogrammes de test fournis existent et sont analysables."""
        for nom in ["crypto01.txt", "crypto02.txt"]:
            self.assertTrue(os.path.exists(nom), f"Le fichier {nom} est manquant.")
            with open(nom, "r", encoding="utf-8") as f:
                contenu = f.read().strip()
            self.assertGreater(len(contenu), 500, f"Le fichier {nom} est trop court.")


if __name__ == "__main__":
    unittest.main(testRunner=PrettyTestRunner)
