### R5.10-Projet_Modelisation

## Compte RENDU




## Exemples




## Questions du TD

# Cette chaîne de Markov est-elle irréductible ? apériodique ? Quelle(s) loi(s) stables(s) ?

La chaîne de Markov modélisant les mots est irréductible, car tous les états (les 27 caractères) communiquent entre eux. Dans une langue naturelle comme le français, il existe toujours un chemin de probabilité non nulle permettant d'atteindre n'importe quelle lettre depuis n'importe quelle autre après un certain nombre d'étapes.

Elle est également apériodique, car il existe des transitions directes d'un état vers lui-même. L'existence dans le texte de lettres doubles (comme "LL" ou "EE") ou d'espaces consécutifs crée des boucles locales qui empêchent les transitions de se bloquer dans un cycle temporel prévisible et répétitif. 

Enfin, puisqu'elle est finie, irréductible et apériodique, cette chaîne admet une unique loi stable. Cette loi de probabilité asymptotique correspond très exactement aux fréquences d'apparition individuelles de chaque caractère (les unigrammes) que vous avez calculées lors de l'analyse initiale de la page web. Si le processus de génération tournait à l'infini, la proportion de chaque lettre générée se stabiliserait parfaitement sur cette loi.


# Liens avec le chiffre de César ? Développez une attaque fréquentielle.

Lien avec le chiffre de César :
Le chiffre de César est en réalité un cas particulier du chiffrement par substitution mono-alphabétique. Alors que la substitution générale autorise n'importe quelle permutation aléatoire des 26 lettres de l'alphabet (ce qui offre une immensité de clés possibles), le chiffre de César se limite à un décalage régulier et uniforme de l'alphabet, ce qui ne laisse que 26 clés possibles à tester. Tout chiffre de César est donc une substitution, mais l'inverse n'est pas vrai.  

Développement d'une attaque fréquentielle :
Pour attaquer un chiffrement par substitution classique, on exploite le fait que chaque lettre claire est toujours remplacée par la même lettre chiffrée. L'attaque fréquentielle consiste donc à compter le nombre d'apparitions de chaque lettre dans le cryptogramme, puis à trier ces résultats pour identifier les caractères les plus utilisés. Il suffit ensuite de comparer ces statistiques locales avec les fréquences naturelles de la langue française (que nous avons calculées à l'étape 1.1). Par exemple, la lettre la plus fréquente du texte chiffré a de très fortes chances de correspondre au "E" clair, la suivante au "A", au "S" ou au "I", etc. En procédant par déductions et tâtonnements successifs, on peut reconstituer la quasi-totalité de la clé sans avoir à tester toutes les permutations. 


# Pourquoi est-ce plus difficile à attaquer ?

Le chiffrement par permutation de positions est plus difficile à attaquer qu'une substitution classique car il ne modifie aucune lettre du texte clair, mais se contente de les déplacer. Par conséquent, une attaque fréquentielle basique (qui compte simplement les occurrences de chaque caractère individuel) est totalement inefficace, puisque le cryptogramme conserve exactement les mêmes proportions de lettres que la langue d'origine. 
De plus, pour casser ce chiffrement de manière brute, un attaquant fait face à une double inconnue : il doit deviner non seulement l'ordre exact de la permutation, mais aussi la longueur fixe du bloc qui sert de clé. En éparpillant les caractères, ce procédé détruit la structure locale du texte en cassant les digrammes réguliers (les syllabes et les mots naturels), ce qui justifie précisément l'utilisation d'une méthode probabiliste avancée comme l'algorithme MCMC pour espérer reconstituer le message en évaluant la crédibilité des paires de lettres.


# Pourquoi peut-on interpréter cela comme une crédibilité pour la clé-hypothèse k ?

On peut interpréter la fonction S(k) comme une mesure de crédibilité grâce à la manière dont elle compare le texte déchiffré avec la langue naturelle.
- La formule utilise les statistiques sur le texte obtenu en déchiffrant avec la clé-hypothèse k.   
- Le calcul repose sur la valeur r(x,y), qui représente le nombre d'occurrences d'un bigramme dans un texte de référence (majoré de 1).   - - Cette valeur est élevée à la puissance f_k(x,y), qui correspond au nombre de fois où ce même bigramme apparaît dans le texte déchiffré.   - Par conséquent, si la clé k génère un texte contenant beaucoup de bigrammes qui sont également très fréquents dans le texte de référence (la langue française), la formule va démultiplier le score final.
- À l'inverse, un texte déchiffré rempli de combinaisons de lettres improbables obtiendra un score très faible, ce qui confirme que le score traduit bien la "crédibilité" linguistique de la clé.  


# Pourquoi cette chaîne de Markov est-elle irréductible et apériodique ?

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

