# R5.10-Projet_Modelisation

## Hub de lancement (`main.py`)

Un tableau de bord interactif centralise l'accès à l'ensemble des modules, chiffrements et attaques du projet avec une interface visuelle soignée en terminal (couleurs ANSI, arborescences UTF-8, chronométrage et gestion des interruptions Ctrl+C).

Le projet est conçu en **zéro dépendance externe obligatoire** : il fonctionne immédiatement au lancement sur n'importe quelle machine (Linux, macOS, Windows) avec une installation standard de Python 3, sans nécessiter d'environnement virtuel ni d'accès à Internet.

Lancement universel :
```bash
python3 src/main.py
# Ou via le script automatique Linux/macOS :
./run.sh
# Ou sous Windows :
run.bat
```

*(Si vous souhaitez utiliser un environnement virtuel avec NumPy, le fichier `requirements.txt` est également fourni à titre optionnel).*

### Fonctionnement du Hub

Le Hub propose un menu interactif structuré en 3 catégories opérationnelles :

- **Section 1 — Chiffrements élémentaires & Analyses fondamentales** :
  - `[ 1 ] César` : Menu interactif pour chiffrer, déchiffrer avec une clé ou tester les 26 décalages en force brute (`cesar.py`, `attack_cesar_fb.py`).
  - `[ 2 ] Vigenère` : Chiffrement et déchiffrement polyalphabétique avec mot-clé dynamique (`vigenere.py`).
  - `[ 3 ] Substitution` : Chiffrement monoalphabétique avec inclusion complète de l'espace (27 symboles) (`substitution.py`).
  - `[ 4 ] Permutation` : Chiffrement par permutation de positions et gestion du padding d'espaces (`permutation.py`).
  - `[ 5 ] Markov & Digrammes` : Calcul de la matrice stochastique $27 \times 27$ et simulation de texte de Markov (`outils_digrammes.py`).
  - `[ 6 ] Fréquences multilingues` : Analyse statistique des lettres sur 5 langues (FR, EN, ES, DE, IT) (`analyse_frequentielle.py`).

- **Section 2 — Cryptanalyses & Attaques statistiques avancées** :
  - `[ 7 ] Attaque César (Khi-deux χ²)` : Identification analytique directe de la clé sur profils Wikipédia (`attack_cesar_frequentielle.py`).
  - `[ 8 ] Attaque Vigenère (Indice de Coïncidence)` : Déduction de la longueur de clé par IC de Friedman et résolution colonne par colonne (`attack_vigenere_ic.py`).
  - `[ 9 ] Attaque Vigenère (Dictionnaire & Digrammes)` : Recherche de mot-clé guidée par la log-vraisemblance des transitions (`attack_vigenere.py`).
  - `[ 10] Attaque MCMC globale` : Heuristique de Metropolis-Hastings avec score logarithmique et adaptation dynamique des itérations (`1-5.py`).

- **Section 3 — Validation & Démonstrations en direct (Conditions réelles d'oral)** :
  - `[ 11] Tests unitaires & d'intégration` : Lancement de la suite complète de 29 tests automatisés (`test_projet.py`).
  - `[ 12] Démo Express crypto01.txt` : Déchiffrement direct en direct par MCMC substitution du roman *Le Colonel Chabert* d'Honoré de Balzac.
  - `[ 13] Démo Express crypto02.txt` : Déchiffrement direct en direct par MCMC permutation ($l=9$) de la pièce *Le Cid* de Pierre Corneille.

---

## Compte RENDU

Ce projet porte sur la modélisation stochastique appliquée à la cryptanalyse de chiffrements classiques (César, Vigenère, substitution monoalphabétique et permutation de positions).

La méthode centrale repose sur l'algorithme **MCMC (Markov Chain Monte Carlo)** avec l'échantillonneur de **Metropolis-Hastings** :
- **Fonction score $S(k)$** : Mesure à quel point le texte déchiffré avec une clé candidate $k$ « ressemble » à du français naturel, en exploitant les fréquences des transitions de digrammes (paires de caractères consécutifs).
- **Exploration stochastique** : Face à des espaces d'états gigantesques ($27! \approx 1{,}08 \times 10^{28}$ pour la substitution), l'algorithme effectue une marche aléatoire guidée. En autorisant avec une probabilité contrôlée des transitions vers des clés de score inférieur, la chaîne échappe aux pièges des maximums locaux et converge vers la clé optimale.


## Exemples

- **Exemple 1 — Substitution monoalphabétique (`crypto01.txt`)** :
  - Extrait chiffré : `DTGTYS XS QWRPWA RS ATRTGSR ADWQSYU W BWXWBS RW ATBUSJJS...`
  - Résultat de l'attaque MCMC : Le texte clair est reconstitué en moins de 3 000 itérations avec un score dépassant 6 000. Il s'agit du roman *Le Colonel Chabert* d'Honoré de Balzac : `HONORE DE BALZAC LE COLONEL CHABERT A MADAME LA COMTESSE...`
- **Exemple 2 — Permutation par blocs (`crypto02.txt`)** :
  - Extrait chiffré : `CRPE IRE EIONLREL  C EDL I E ATRCEP E MECIRS IRN MEPE...`
  - Résultat de l'attaque MCMC : Le pic de score apparaît nettement pour une longueur de bloc $l = 9$ (clé `[2, 5, 3, 6, 1, 8, 7, 4, 0]`, score $\approx 4\,342$ contre $\approx 3\,500$ pour les autres longueurs). Le texte clair reconstruit correspond à la pièce *Le Cid* de Pierre Corneille : `PIERRE CORNEILLE LE CID ACTE PREMIER SCENE PREMIERE...`
- **Sensibilité aux espaces et longueur de clé (7, 8 ou 9)** :
  - Dans une permutation, l'espace est une position physique au même titre qu'une lettre. La présence d'espaces multiples consécutifs, d'espaces insécables ou de caractères de padding en fin de bloc modifie l'alignement modulaire. Si un cryptogramme est tronqué ou si les espaces sont altérés, la longueur apparente peut sembler flotter. Le programme teste systématiquement chaque longueur de clé de façon indépendante, garantissant de trouver la longueur qui maximise la vraisemblance linguistique sans biais préalable.


## Questions du TD

### Cette chaîne de Markov est-elle irréductible ? apériodique ? Quelle(s) loi(s) stables(s) ?

La chaîne de Markov modélisant les mots est irréductible, car tous les états (les 27 caractères) communiquent entre eux. Dans une langue naturelle comme le français, il existe toujours un chemin de probabilité non nulle permettant d'atteindre n'importe quelle lettre depuis n'importe quelle autre après un certain nombre d'étapes.

Elle est également apériodique, car il existe des transitions directes d'un état vers lui-même. L'existence dans le texte de lettres doubles (comme "LL" ou "EE") ou d'espaces consécutifs crée des boucles locales qui empêchent les transitions de se bloquer dans un cycle temporel prévisible et répétitif. 

Enfin, puisqu'elle est finie, irréductible et apériodique, cette chaîne admet une unique loi stable. Cette loi de probabilité asymptotique correspond très exactement aux fréquences d'apparition individuelles de chaque caractère (les unigrammes) que vous avez calculées lors de l'analyse initiale de la page web. Si le processus de génération tournait à l'infini, la proportion de chaque lettre générée se stabiliserait parfaitement sur cette loi.


### Liens avec le chiffre de César ? Développez une attaque fréquentielle.

Lien avec le chiffre de César :
Le chiffre de César est en réalité un cas particulier du chiffrement par substitution mono-alphabétique. Alors que la substitution générale autorise n'importe quelle permutation aléatoire des 26 lettres de l'alphabet (ce qui offre une immensité de clés possibles), le chiffre de César se limite à un décalage régulier et uniforme de l'alphabet, ce qui ne laisse que 26 clés possibles à tester. Tout chiffre de César est donc une substitution, mais l'inverse n'est pas vrai.  

Développement d'une attaque fréquentielle :
Pour attaquer un chiffrement par substitution classique, on exploite le fait que chaque lettre claire est toujours remplacée par la même lettre chiffrée. L'attaque fréquentielle consiste donc à compter le nombre d'apparitions de chaque lettre dans le cryptogramme, puis à trier ces résultats pour identifier les caractères les plus utilisés. Il suffit ensuite de comparer ces statistiques locales avec les fréquences naturelles de la langue française (que nous avons calculées à l'étape 1.1). Par exemple, la lettre la plus fréquente du texte chiffré a de très fortes chances de correspondre au "E" clair, la suivante au "A", au "S" ou au "I", etc. En procédant par déductions et tâtonnements successifs, on peut reconstituer la quasi-totalité de la clé sans avoir à tester toutes les permutations. 


### Pourquoi est-ce plus difficile à attaquer ?

Le chiffrement par permutation de positions est plus difficile à attaquer qu'une substitution classique car il ne modifie aucune lettre du texte clair, mais se contente de les déplacer. Par conséquent, une attaque fréquentielle basique (qui compte simplement les occurrences de chaque caractère individuel) est totalement inefficace, puisque le cryptogramme conserve exactement les mêmes proportions de lettres que la langue d'origine. 
De plus, pour casser ce chiffrement de manière brute, un attaquant fait face à une double inconnue : il doit deviner non seulement l'ordre exact de la permutation, mais aussi la longueur fixe du bloc qui sert de clé. En éparpillant les caractères, ce procédé détruit la structure locale du texte en cassant les digrammes réguliers (les syllabes et les mots naturels), ce qui justifie précisément l'utilisation d'une méthode probabiliste avancée comme l'algorithme MCMC pour espérer reconstituer le message en évaluant la crédibilité des paires de lettres.


### Pourquoi peut-on interpréter cela comme une crédibilité pour la clé-hypothèse k ?

On peut interpréter la fonction S(k) comme une mesure de crédibilité grâce à la manière dont elle compare le texte déchiffré avec la langue naturelle.
- La formule utilise les statistiques sur le texte obtenu en déchiffrant avec la clé-hypothèse k.
- Le calcul repose sur la valeur r(x,y), qui représente le nombre d'occurrences d'un bigramme dans un texte de référence (majoré de 1).
- Cette valeur est élevée à la puissance f_k(x,y), qui correspond au nombre de fois où ce même bigramme apparaît dans le texte déchiffré.
- Par conséquent, si la clé k génère un texte contenant beaucoup de bigrammes qui sont également très fréquents dans le texte de référence (la langue française), la formule va démultiplier le score final.
- À l'inverse, un texte déchiffré rempli de combinaisons de lettres improbables obtiendra un score très faible, ce qui confirme que le score traduit bien la "crédibilité" linguistique de la clé.  


### Pourquoi cette chaîne de Markov est-elle irréductible et apériodique ?

La chaîne de Markov construite par l'algorithme MCMC possède ces deux propriétés mathématiques essentielles pour garantir sa convergence :
- Elle est irréductible : Une chaîne est irréductible s'il est possible d'atteindre n'importe quel état (n'importe quelle clé) depuis n'importe quel autre état de départ.
    - L'algorithme propose un état voisin en effectuant une petite modification sur la clé actuelle k.
    - Pour la substitution, cette mutation se fait par transposition, c'est-à-dire par l'échange de deux lettres chiffrées prises au hasard.
    - Pour la permutation, on mute en déplaçant un sous-bloc.
    - Mathématiquement, une suite finie de ces petites opérations successives permet de reconstituer absolument toutes les permutations possibles de l'espace des clés. Aucun état n'est donc inaccessible.
- Elle est apériodique : Une chaîne est périodique si elle est forcée de revenir à un état selon un nombre de cycles régulier. L'apériodicité ici est assurée par l'étape de sélection.
    - L'algorithme calcule le score de la nouvelle clé et utilise un tirage au sort $U$ pour décider de la transition.
    - Si la condition d'acceptation n'est pas remplie, le programme refuse la mutation, c'est-à-dire qu'il reste dans l'état k actuel.
    - Cette probabilité non nulle de stagner sur place (une transition de l'état k vers lui-même) brise instantanément toute forme de périodicité, empêchant la séquence de s'enfermer dans un cycle répétitif.


## Explorations statistiques

- **Profils de référence multilingues dynamiques** : Téléchargement et extraction à la volée de corpus Wikipédia pour 5 langues (Français, Anglais, Espagnol, Allemand, Italien). Zéro constante codée en dur dans le code source : les distributions empiriques de fréquences s'adaptent dynamiquement à la langue choisie.
- **Test d'adéquation du Khi-deux ($\chi^2$) de Pearson** : Implémentation d'un discriminateur statistique comparant les effectifs observés $O_c$ aux effectifs théoriques attendus $E_c = N \cdot p_c$ sur les 26 lettres de l'alphabet. Ce test sert de fonction de coût pour départager automatiquement les clés candidates.
- **Indice de Coïncidence (IC) de Friedman** : Analyse statistique dans `attack_vigenere_ic.py` calculant la probabilité que deux lettres tirées au hasard dans le texte soient identiques ($IC = \frac{\sum n_i(n_i - 1)}{N(N - 1)}$). Cette métrique permet d'estimer avec précision la période de la clé d'un chiffre polyalphabétique sans force brute.
- **Étude de convergence de l'algorithme MCMC** :
  - Pour la substitution : observation d'une montée rapide du score log dès les premières 3 000 itérations, suivie d'une phase de stabilisation fine.
  - Pour la permutation : mise en évidence d'un contraste franc entre les longueurs de blocs incorrectes (qui stagnent sur un plateau bas de score vers 4 300) et la longueur exacte (qui produit un pic net dépassant 5 100, comme observé sur *Germinal* à $l = 9$).


## Variantes

- **Attaque fréquentielle directe vs Force brute (César)** : Au lieu d'itérer aveuglément sur les 26 décalages, déduction analytique directe en complexité $\mathcal{O}(1)$ en reliant la lettre chiffrée dominante $C_{\max}$ au pic naturel de la langue $L_{\max}$ par la relation modulaire $k = (\text{index}(C_{\max}) - \text{index}(L_{\max})) \pmod{26}$.
- **Substitution avec inclusion de l'espace (alphabet à 27 caractères)** : Extension complète du sujet intégrant l'espace comme un caractère interchangeable au même titre que les lettres A–Z. Cette variante supprime les repères visuels des mots clairs, augmentant la complexité de l'espace de recherche ($27! \approx 1{,}08 \times 10^{28}$ clés possibles).
- **Opérateurs de mutation adaptés** :
  - *Pour la substitution* : mutation par transposition de 2 lettres choisies aléatoirement dans l'alphabet de déchiffrement.
  - *Pour la permutation* : mutation par découpage et translation d'un sous-bloc contigu de taille variable, garantissant une meilleure explorabilité de l'espace combinatoire que de simples inversions de positions contiguës.
- **Cryptanalyse de Vigenère** :
  - Variante par dictionnaire évaluant chaque mot-clé par log-vraisemblance sur la matrice de transition des digrammes (`attack_vigenere.py`).
  - Variante analytique complète couplant recherche de la période par Indice de Coïncidence et résolution colonne par colonne par minimisation du $\chi^2$ (`attack_vigenere_ic.py`).


## Choix d'implémentation

- **Adaptation dynamique du nombre d'itérations selon la longueur de clé ($l!$)** : Pour une permutation de longueur $l=2$ (seulement 2 clés possibles : `[0, 1]` et `[1, 0]`) ou $l=3$ (6 clés), effectuer 15 000 itérations est inutile et coûteux. Le programme adapte automatiquement le nombre d'itérations selon la taille de l'espace combinatoire : $\min(\text{iterations}, \max(60, l! \times 5))$, rendant l'évaluation des petites longueurs quasi-instantanée.
- **Synthèse automatisée du meilleur résultat global** : À la fin de l'exécution, le script compare les meilleurs scores obtenus entre la substitution et toutes les longueurs de permutation testées, et affiche directement le verdict avec le format standardisé : `Affichage meilleur résultat (Substitution/Permutation | Score = …)`.
- **Passage du score en échelle logarithmique ($\log S(k)$)** : La formule théorique $S(k) = \prod_{(x,y)} r(x,y)^{f_k(x,y)}$ impliquant des produits de puissances astronomiques, elle mène inévitablement à un débordement de capacité numérique (overflow). Le calcul est transformé en somme de logarithmes $\log S(k) = \sum f_k(x,y) \cdot \ln(r(x,y))$, rendant l'algorithme numériquement stable.
- **Lissage additif de Laplace ($+1$)** : Application systématique d'une constante de lissage sur les effectifs de référence ($r(x,y) = 1 + \text{occ}$) et les probabilités de lettres, empêchant toute divergence mathématique par $\ln(0)$ ou division par zéro lors des tests d'adéquation.
- **Mémoïsation et mise en cache mémoire** : Utilisation d'un dictionnaire de cache (`_CACHE_FREQUENCES`) pour conserver les statistiques des pages Wikipédia une fois téléchargées, évitant ainsi les requêtes réseau superflues et accélérant les exécutions ultérieures.
- **Mémorisation du Top-N des meilleures clés uniques** : La chaîne de Markov conservant une probabilité d'accepter des transitions vers des états moins crédibles (pour échapper aux optimums locaux), l'algorithme maintient une mémoire tampon des 5 meilleures solutions distinctes rencontrées au fil de la trajectoire pour ne jamais perdre l'optimum global.
- **Contournement de la limite système de saisie (`MAX_CANON`)** : Sur macOS et systèmes POSIX, le buffer d'entrée canonique du terminal est restreint à 1 024 octets, bloquant la touche Entrée lors du collage de cryptogrammes longs. Le code propose une option de chargement direct par fichier texte (`texte.txt`, `crypto01.txt`, `crypto02.txt`) ainsi qu'une saisie multiligne avec validation assouplie.
- **Portabilité universelle et zéro dépendance obligatoire** : La matrice stochastique de transitions $27 \times 27$ dispose d'une implémentation hybride pure Python (`MatriceTransitions`) et d'un tirage pondéré natif (`random.choices`). Si NumPy est présent, il est exploité ; s'il est absent, le projet fonctionne immédiatement à 100% de ses capacités sans nécessiter d'installation externe ni d'environnement virtuel, garantissant un démarrage instantané lors des évaluations orales.


## Tests unitaires et d'intégration

Une suite complète de 29 tests automatisés est fournie dans `test_projet.py` pour valider l'ensemble des modules :
- **Chiffrements de base** : Réversibilité et cas limites pour César et Vigenère.
- **Normalisation et outils** : Suppression d'accents, ligatures (Œ, Æ), préservation multilingue (ß), API Wikipédia.
- **Substitution et Permutation** : Conservation des bijections, validité des clés inverses, exemple de l'énoncé.
- **Modélisation de Markov** : Calcul des digrammes, normalisation stochastique de la matrice (somme par ligne = 1), simulation.
- **Algorithme MCMC** : Pertinence de la fonction score log, conservation de la validité des clés après mutation.
- **Intégration de bout en bout** : Pipeline complet d'attaque fréquentielle César et vérification de l'intégrité des fichiers cryptogrammes fournis (`crypto01.txt`, `crypto02.txt`).

Exécution de la suite de tests (avec affichage soigné, chronométrage et couleurs) :
```bash
python3 src/test_projet.py
```
