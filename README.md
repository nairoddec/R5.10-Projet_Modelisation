# R5.10-Projet_Modelisation

# 1.2 : Cette chaîne de Markov est-elle irréductible ? apériodique ? Quelle(s) loi(s) stables(s) ?

La chaîne de Markov modélisant les mots est irréductible, car tous les états (les 27 caractères) communiquent entre eux. Dans une langue naturelle comme le français, il existe toujours un chemin de probabilité non nulle permettant d'atteindre n'importe quelle lettre depuis n'importe quelle autre après un certain nombre d'étapes.

Elle est également apériodique, car il existe des transitions directes d'un état vers lui-même. L'existence dans le texte de lettres doubles (comme "LL" ou "EE") ou d'espaces consécutifs crée des boucles locales qui empêchent les transitions de se bloquer dans un cycle temporel prévisible et répétitif. 

Enfin, puisqu'elle est finie, irréductible et apériodique, cette chaîne admet une unique loi stable. Cette loi de probabilité asymptotique correspond très exactement aux fréquences d'apparition individuelles de chaque caractère (les unigrammes) que vous avez calculées lors de l'analyse initiale de la page web. Si le processus de génération tournait à l'infini, la proportion de chaque lettre générée se stabiliserait parfaitement sur cette loi.


# 1.3 : Liens avec le chiffre de César ? Développez une attaque fréquentielle.

Lien avec le chiffre de César :
Le chiffre de César est en réalité un cas particulier du chiffrement par substitution mono-alphabétique. Alors que la substitution générale autorise n'importe quelle permutation aléatoire des 26 lettres de l'alphabet (ce qui offre une immensité de clés possibles), le chiffre de César se limite à un décalage régulier et uniforme de l'alphabet, ce qui ne laisse que 26 clés possibles à tester. Tout chiffre de César est donc une substitution, mais l'inverse n'est pas vrai.  
Développement d'une attaque fréquentielle :
Pour attaquer un chiffrement par substitution classique, on exploite le fait que chaque lettre claire est toujours remplacée par la même lettre chiffrée. L'attaque fréquentielle consiste donc à compter le nombre d'apparitions de chaque lettre dans le cryptogramme, puis à trier ces résultats pour identifier les caractères les plus utilisés. Il suffit ensuite de comparer ces statistiques locales avec les fréquences naturelles de la langue française (que nous avons calculées à l'étape 1.1). Par exemple, la lettre la plus fréquente du texte chiffré a de très fortes chances de correspondre au "E" clair, la suivante au "A", au "S" ou au "I", etc. En procédant par déductions et tâtonnements successifs, on peut reconstituer la quasi-totalité de la clé sans avoir à tester toutes les permutations. 


# 1.4 : Pourquoi est-ce plus difficile à attaquer ?

Le chiffrement par permutation de positions est plus difficile à attaquer qu'une substitution classique car il ne modifie aucune lettre du texte clair, mais se contente de les déplacer. Par conséquent, une attaque fréquentielle basique (qui compte simplement les occurrences de chaque caractère individuel) est totalement inefficace, puisque le cryptogramme conserve exactement les mêmes proportions de lettres que la langue d'origine. 
De plus, pour casser ce chiffrement de manière brute, un attaquant fait face à une double inconnue : il doit deviner non seulement l'ordre exact de la permutation, mais aussi la longueur fixe du bloc qui sert de clé. En éparpillant les caractères, ce procédé détruit la structure locale du texte en cassant les digrammes réguliers (les syllabes et les mots naturels), ce qui justifie précisément l'utilisation d'une méthode probabiliste avancée comme l'algorithme MCMC pour espérer reconstituer le message en évaluant la crédibilité des paires de lettres.

