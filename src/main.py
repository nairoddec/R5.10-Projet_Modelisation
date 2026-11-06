#!/usr/bin/env python3
"""
Hub de lancement pour l'ensemble du projet de Modélisation & Cryptographie (R5.10).

Ce script fournit un tableau de bord interactif en ligne de commande permettant
d'accéder à l'ensemble des modules, chiffrements, attaques statistiques, simulations
de Markov, algorithmes MCMC et tests automatisés.

Exécution :
    python3 main.py
"""

import math
import os
import random
import subprocess
import sys
import time 

# Couleurs ANSI
class Color:
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


def clear_console():
    """Efface l'écran du terminal."""
    print("\033[H\033[J", end="")


def pause():
    """Attend que l'utilisateur appuie sur Entrée."""
    print(f"\n  {Color.DIM}Appuyez sur Entrée pour continuer...{Color.RESET}", end="")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass


def executer_script(nom_fichier, description=""):
    """Exécute un script Python dans un sous-processus isolé avec l'interpréteur actif."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), nom_fichier)
    if not os.path.exists(chemin):
        print(f"\n  {Color.RED}Erreur : Le fichier '{nom_fichier}' est introuvable.{Color.RESET}")
        pause()
        return

    print(f"\n  {Color.CYAN}┌─ [LANCEMENT] {Color.BOLD}{description or nom_fichier}{Color.RESET}")
    print(f"  {Color.CYAN}│  Interpréteur : {Color.DIM}{sys.executable}{Color.RESET}")
    print(f"  {Color.CYAN}│  Fichier      : {Color.DIM}{chemin}{Color.RESET}")
    print(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}\n")

    try:
        subprocess.run([sys.executable, chemin])
    except KeyboardInterrupt:
        print(f"\n\n  {Color.YELLOW}Exécution interrompue (Ctrl+C).{Color.RESET}")
    except Exception as e:
        print(f"\n  {Color.RED}Erreur : {e}{Color.RESET}")

    pause()


# =============================================================================
# MODULES INTERACTIFS RAPIDES DU HUB
# =============================================================================

def menu_cesar():
    """Sous-menu interactif pour le Chiffre de César."""
    import cesar
    import attack_cesar_fb

    while True:
        clear_console()
        print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
        print(f"{Color.BOLD}{Color.WHITE}         MODULE CÉSAR - CHIFFREMENT, DÉCHIFFREMENT & FORCE BRUTE{Color.RESET}")
        print(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")
        print(f"  {Color.CYAN}[ 1 ]{Color.RESET} Chiffrer un message avec une clé")
        print(f"  {Color.CYAN}[ 2 ]{Color.RESET} Déchiffrer un message avec une clé connue")
        print(f"  {Color.CYAN}[ 3 ]{Color.RESET} Attaque par force brute (teste les 26 décalages)")
        print(f"  {Color.CYAN}[ 4 ]{Color.RESET} Lancer la démonstration de base (attack_cesar_fb.py)")
        print(f"  {Color.DIM}[ 0 ] Retour au menu principal{Color.RESET}\n")

        choix = input(f"  {Color.BOLD}Votre choix : {Color.RESET}").strip()
        if choix == "0":
            break
        elif choix == "1":
            txt = input("\n  Texte en clair à chiffrer : ").strip().upper()
            try:
                k = int(input("  Clé de décalage (entier 0-25) : ").strip())
                res = cesar.chiffrement_cesar(txt, k)
                print(f"\n  Message chiffré : {Color.BOLD}{res}{Color.RESET}")
            except ValueError:
                print(f"  {Color.RED}Erreur : la clé doit être un entier.{Color.RESET}")
            pause()
        elif choix == "2":
            txt = input("\n  Cryptogramme à déchiffrer : ").strip().upper()
            try:
                k = int(input("  Clé de décalage connue (entier 0-25) : ").strip())
                res = cesar.dechiffrement_cesar(txt, k)
                print(f"\n  Message déchiffré : {Color.BOLD}{res}{Color.RESET}")
            except ValueError:
                print(f"  {Color.RED}Erreur : la clé doit être un entier.{Color.RESET}")
            pause()
        elif choix == "3":
            txt = input("\n  Cryptogramme à attaquer en force brute : ").strip().upper()
            if txt:
                attack_cesar_fb.attaque_force_brute_cesar(txt)
            pause()
        elif choix == "4":
            executer_script("attack_cesar_fb.py", "Démonstration César & Force Brute")


def menu_vigenere():
    """Sous-menu interactif pour le Chiffre de Vigenère."""
    import vigenere

    while True:
        clear_console()
        print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
        print(f"{Color.BOLD}{Color.WHITE}         MODULE VIGENÈRE - CHIFFREMENT & DÉCHIFFREMENT POLYALPHABÉTIQUE{Color.RESET}")
        print(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")
        print(f"  {Color.CYAN}[ 1 ]{Color.RESET} Chiffrer un message avec un mot-clé")
        print(f"  {Color.CYAN}[ 2 ]{Color.RESET} Déchiffrer un message avec un mot-clé")
        print(f"  {Color.DIM}[ 0 ] Retour au menu principal{Color.RESET}\n")

        choix = input(f"  {Color.BOLD}Votre choix : {Color.RESET}").strip()
        if choix == "0":
            break
        elif choix == "1":
            txt = input("\n  Texte en clair à chiffrer : ").strip().upper()
            cle = input("  Mot-clé alphabétique (ex: SECRET) : ").strip().upper()
            if txt and cle and cle.isalpha():
                res = vigenere.chiffrement_vigenere(txt, cle)
                print(f"\n  Message chiffré : {Color.BOLD}{res}{Color.RESET}")
            else:
                print(f"  {Color.RED}Erreur : texte ou clé non valide.{Color.RESET}")
            pause()
        elif choix == "2":
            txt = input("\n  Cryptogramme à déchiffrer : ").strip().upper()
            cle = input("  Mot-clé alphabétique : ").strip().upper()
            if txt and cle and cle.isalpha():
                res = vigenere.dechiffrement_vigenere(txt, cle)
                print(f"\n  Message déchiffré : {Color.BOLD}{res}{Color.RESET}")
            else:
                print(f"  {Color.RED}Erreur : texte ou clé non valide.{Color.RESET}")
            pause()


def demo_crypto01():
    """Démonstration de la résolution de crypto01.txt (Balzac - Substitution)."""
    import importlib
    import outils_digrammes
    import fonction_outils
    mcmc = importlib.import_module("1-5")

    clear_console()
    print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE}         DÉCRYPTAGE CRYPTO01 (SUBSTITUTION MCMC){Color.RESET}")
    print(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")

    if not os.path.exists("crypto01.txt"):
        print(f"  {Color.RED}Erreur : Fichier 'crypto01.txt' introuvable.{Color.RESET}")
        pause()
        return

    with open("crypto01.txt", "r", encoding="utf-8") as f:
        cryptogramme = f.read().strip()

    print(f"  • Source  : crypto01.txt ({len(cryptogramme)} caractères)")
    print(f"  • Extrait : {Color.DIM}{cryptogramme[:80]}...{Color.RESET}\n")

    url_ref = "https://fr.wikipedia.org/wiki/Château"
    try:
        texte_ref = fonction_outils.recuperer_texte_mediawiki(url_ref)
        texte_propre_ref = fonction_outils.nettoyer_texte(texte_ref)
    except Exception:
        texte_propre_ref = (
            "LE CHATEAU EST UNE CONSTRUCTION MEDIEVALE FORTIFIEE DE FRANCE DONT LES TOURS ET LES MURS "
            "PERMETTAIENT DE SE DEFENDRE CONTRE LES ASSAILLANTS DANS L HISTOIRE DU MOYEN AGE"
        ) * 40

    stats_ref = outils_digrammes.statistiques_digrammes(texte_propre_ref)

    nb_iterations = 6000
    print(f"  Lancement MCMC ({nb_iterations} itérations)...\n")

    debut = time.perf_counter()
    solutions = mcmc.attaque_mcmc_substitution(cryptogramme[:1500], stats_ref, iterations=nb_iterations, top_n=3)
    duree = time.perf_counter() - debut

    meilleur_score, meilleure_cle, meilleur_texte = solutions[0]

    print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
    print(f"  {Color.GREEN}Résultat ({duree:.2f} s) :{Color.RESET}")
    print(f"{Color.CYAN}{'─' * 78}{Color.RESET}")
    print(f"  • Texte : Honoré de Balzac - Le Colonel Chabert")
    print(f"  • Score : {Color.YELLOW}{meilleur_score:.2f}{Color.RESET}")
    print(f"  • Extrait déchiffré :\n")
    print(f"  {Color.BOLD}{meilleur_texte[:350]}...{Color.RESET}")
    print(f"{Color.CYAN}{'═' * 78}{Color.RESET}")
    pause()


def demo_crypto02():
    """Démonstration de la résolution de crypto02.txt (Corneille - Permutation l=9)."""
    import importlib
    import outils_digrammes
    import fonction_outils
    mcmc = importlib.import_module("1-5")

    clear_console()
    print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE}         DÉCRYPTAGE CRYPTO02 (PERMUTATION MCMC){Color.RESET}")
    print(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")

    if not os.path.exists("crypto02.txt"):
        print(f"  {Color.RED}Erreur : Fichier 'crypto02.txt' introuvable.{Color.RESET}")
        pause()
        return

    with open("crypto02.txt", "r", encoding="utf-8") as f:
        cryptogramme = f.read().strip()

    print(f"  • Source  : crypto02.txt ({len(cryptogramme)} caractères)")
    print(f"  • Extrait : {Color.DIM}{cryptogramme[:80]}...{Color.RESET}\n")

    url_ref = "https://fr.wikipedia.org/wiki/Château"
    try:
        texte_ref = fonction_outils.recuperer_texte_mediawiki(url_ref)
        texte_propre_ref = fonction_outils.nettoyer_texte(texte_ref)
    except Exception:
        texte_propre_ref = (
            "PIERRE CORNEILLE EST UN DRAMATURGE CLASSIQUE FRANCAIS AUTEUR DE TRAGEDIES CELEBRES "
            "COMME LE CID SCENE PREMIERE ACTE PREMIER DU THEATRE CLASSIQUE"
        ) * 40

    stats_ref = outils_digrammes.statistiques_digrammes(texte_propre_ref)

    l_cible = 9
    iterations = 6000
    print(f"  Lancement MCMC (longueur l = {l_cible}, {iterations} itérations)...\n")

    debut = time.perf_counter()
    reste = len(cryptogramme) % l_cible
    crypto_prepare = cryptogramme if reste == 0 else cryptogramme[:-reste]
    solutions = mcmc.attaque_mcmc_permutation(crypto_prepare[:1200], stats_ref, longueur_cle=l_cible, iterations=iterations, top_n=3)
    duree = time.perf_counter() - debut

    meilleur_score, meilleure_cle, meilleur_texte = solutions[0]

    print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
    print(f"  {Color.GREEN}Résultat ({duree:.2f} s) :{Color.RESET}")
    print(f"{Color.CYAN}{'─' * 78}{Color.RESET}")
    print(f"  • Texte : Pierre Corneille - Le Cid")
    print(f"  • Longueur de clé : {Color.CYAN}l = {l_cible}{Color.RESET}")
    print(f"  • Clé optimale    : {Color.CYAN}{meilleure_cle}{Color.RESET}")
    print(f"  • Score           : {Color.YELLOW}{meilleur_score:.2f}{Color.RESET}")
    print(f"  • Extrait déchiffré :\n")
    print(f"  {Color.BOLD}{meilleur_texte[:350]}...{Color.RESET}")
    print(f"{Color.CYAN}{'═' * 78}{Color.RESET}")
    pause()


# =============================================================================
# MENU PRINCIPAL DU HUB
# =============================================================================

def afficher_banniere():
    """Affiche la bannière d'accueil du Hub."""
    print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE}        HUB PRINCIPAL - PROJET MODÉLISATION & CRYPTOGRAPHIE (R5.10){Color.RESET}")
    print(f"{Color.CYAN}{'═' * 78}{Color.RESET}")


def afficher_menu():
    """Affiche les cartes d'options organisées par catégories."""
    print(f"\n  {Color.CYAN}{Color.BOLD}┌─ [SECTION 1] CHIFFREMENTS & ANALYSES FONDAMENTALES{Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 1 ]{Color.RESET} {Color.WHITE}{'César (Chiffrement, Déchiffrement, Force brute)':<48}{Color.RESET} {Color.DIM}(cesar.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 2 ]{Color.RESET} {Color.WHITE}{'Vigenère (Chiffrement polyalphabétique)':<48}{Color.RESET} {Color.DIM}(vigenere.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 3 ]{Color.RESET} {Color.WHITE}{'Substitution générale avec espace (27 symboles)':<48}{Color.RESET} {Color.DIM}(substitution.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 4 ]{Color.RESET} {Color.WHITE}{'Permutation par blocs de positions':<48}{Color.RESET} {Color.DIM}(permutation.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 5 ]{Color.RESET} {Color.WHITE}{'Matrice de transition 27x27 & Chaîne de Markov':<48}{Color.RESET} {Color.DIM}(outils_digrammes.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 6 ]{Color.RESET} {Color.WHITE}{'Analyse fréquentielle des lettres & Multilingue':<48}{Color.RESET} {Color.DIM}(analyse_frequentielle.py){Color.RESET}")
    print(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}")

    print(f"\n  {Color.CYAN}{Color.BOLD}┌─ [SECTION 2] CRYPTANALYSES & ATTAQUES STATISTIQUES{Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 7 ]{Color.RESET} {Color.WHITE}{'Attaque César par Khi-deux (χ²)':<48}{Color.RESET} {Color.DIM}(attack_cesar_frequentielle.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 8 ]{Color.RESET} {Color.WHITE}{'Attaque Vigenère par Indice de Coïncidence':<48}{Color.RESET} {Color.DIM}(attack_vigenere_ic.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 9 ]{Color.RESET} {Color.WHITE}{'Attaque Vigenère par Dictionnaire & Digrammes':<48}{Color.RESET} {Color.DIM}(attack_vigenere.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.YELLOW}[ 10]{Color.RESET} {Color.WHITE}{'Attaque MCMC (Substitution & Permutation)':<48}{Color.RESET} {Color.DIM}(1-5.py){Color.RESET}")
    print(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}")

    print(f"\n  {Color.CYAN}{Color.BOLD}┌─ [SECTION 3] VALIDATION & DÉMONSTRATIONS{Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[ 11]{Color.RESET} {Color.BOLD}{'Tests unitaires et d’intégration (29 tests)':<48}{Color.RESET} {Color.DIM}(test_projet.py){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[ 12]{Color.RESET} {Color.BOLD}{'Déchiffrement crypto01.txt (Balzac)':<48}{Color.RESET} {Color.DIM}(Substitution MCMC){Color.RESET}")
    print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[ 13]{Color.RESET} {Color.BOLD}{'Déchiffrement crypto02.txt (Le Cid)':<48}{Color.RESET} {Color.DIM}(Permutation l=9){Color.RESET}")
    print(f"  {Color.CYAN}└{'─' * 74}{Color.RESET}")

    print(f"\n  {Color.DIM}[ 0 ] Quitter{Color.RESET}\n")


def boucle_principale():
    """Boucle interactive de contrôle du Hub."""
    while True:
        clear_console()
        afficher_banniere()
        afficher_menu()

        try:
            choix = input(f"  {Color.BOLD}{Color.CYAN}Choix [0-13] : {Color.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            choix = "0"

        if choix == "0":
            clear_console()
            print(f"\n{Color.CYAN}{'═' * 78}{Color.RESET}")
            print(f"  Fermeture du hub.")
            print(f"{Color.CYAN}{'═' * 78}{Color.RESET}\n")
            sys.exit(0)

        elif choix == "1":
            menu_cesar()
        elif choix == "2":
            menu_vigenere()
        elif choix == "3":
            executer_script("substitution.py", "Substitution avec Espace (Section 1.3)")
        elif choix == "4":
            executer_script("permutation.py", "Permutation par Blocs (Section 1.4)")
        elif choix == "5":
            executer_script("outils_digrammes.py", "Matrice de Transition & Markov (Section 1.2)")
        elif choix == "6":
            executer_script("analyse_frequentielle.py", "Analyse Fréquentielle Multilingue (Section 1.1)")
        elif choix == "7":
            executer_script("attack_cesar_frequentielle.py", "Attaque Fréquentielle César (Khi-deux)")
        elif choix == "8":
            executer_script("attack_vigenere_ic.py", "Attaque Vigenère par Indice de Coïncidence")
        elif choix == "9":
            executer_script("attack_vigenere.py", "Attaque Vigenère par Dictionnaire & Digrammes")
        elif choix == "10":
            executer_script("1-5.py", "Attaque MCMC (Substitution & Permutation)")
        elif choix == "11":
            executer_script("test_projet.py", "Tests Unitaires & d'Intégration (29 tests)")
        elif choix == "12":
            demo_crypto01()
        elif choix == "13":
            demo_crypto02()
        else:
            print(f"\n  {Color.RED}Option invalide : '{choix}'. Entrez un nombre de 0 à 13.{Color.RESET}")
            pause()


if __name__ == "__main__":
    try:
        boucle_principale()
    except KeyboardInterrupt:
        print("\n\nFermeture du hub.\n")
