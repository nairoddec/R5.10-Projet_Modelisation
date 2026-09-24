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



# 1.5.1 : Pourquoi peut-on interpréter cela comme une crédibilité pour la clé-hypothèse k ?

La formule du score S(k)=∏(x,y) r(x,y)^fk(x,y) quantifie directement la ressemblance structurelle entre le texte déchiffré et le français naturel.   

Si la clé-hypothèse k est pertinente, le texte déchiffré contiendra de nombreuses paires de lettres très courantes en français (comme "ES", "LE", "EN"). Pour ces paires, la fréquence de référence r(x,y) est élevée. En l'élevant à la puissance de ses occurrences dans le texte déchiffré fk(x,y), le score global est multiplié par un nombre immense.   

À l'inverse, une mauvaise clé génère des paires improbables (comme "WZ" ou "QK"). Pour ces bigrammes, la valeur r(x,y) sera très faible (proche de 1), ce qui n'augmentera presque pas le score final.   
Le score est donc une mesure directe de "crédibilité" : plus il est élevé, plus le texte généré par la clé respecte les lois statistiques de la langue de référence.




# 1.5.2 : Pourquoi cette chaîne de Markov est-elle irréductible et apériodique ?


Ces deux propriétés mathématiques sont garanties par les mécanismes mêmes de la boucle MCMC :
Irréductibilité : Une chaîne de Markov est irréductible s'il est possible de transiter de n'importe quel état vers n'importe quel autre état en un nombre fini d'étapes. Ici, les états sont les différentes clés. L'algorithme mute par transposition (échange de deux éléments pris au hasard). Puisqu'en algèbre toute permutation peut être décomposée en un produit de transpositions, une suite finie d'échanges permet nécessairement de relier n'importe quelle clé de départ à n'importe quelle autre clé d'arrivée.   

Apériodicité : Une chaîne est apériodique si la séquence de ses états ne s'enferme pas dans des cycles répétitifs de longueur fixe. Dans cet algorithme, la règle de sélection indique qu'en cas de refus (si le tirage U n'est pas inférieur au ratio des scores), la séquence reste dans l'état actuel k. Cette probabilité stricte d'effectuer une transition d'un état vers lui-même (une boucle locale) casse instantanément toute périodicité