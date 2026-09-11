# R5.10-Projet_Modelisation

# 1.2 : Cette chaîne de Markov est-elle irréductible ? apériodique ? Quelle(s) loi(s) stables(s) ?

La chaîne de Markov modélisant les mots est irréductible, car tous les états (les 27 caractères) communiquent entre eux. Dans une langue naturelle comme le français, il existe toujours un chemin de probabilité non nulle permettant d'atteindre n'importe quelle lettre depuis n'importe quelle autre après un certain nombre d'étapes.

Elle est également apériodique, car il existe des transitions directes d'un état vers lui-même. L'existence dans le texte de lettres doubles (comme "LL" ou "EE") ou d'espaces consécutifs crée des boucles locales qui empêchent les transitions de se bloquer dans un cycle temporel prévisible et répétitif. 

Enfin, puisqu'elle est finie, irréductible et apériodique, cette chaîne admet une unique loi stable. Cette loi de probabilité asymptotique correspond très exactement aux fréquences d'apparition individuelles de chaque caractère (les unigrammes) que vous avez calculées lors de l'analyse initiale de la page web. Si le processus de génération tournait à l'infini, la proportion de chaque lettre générée se stabiliserait parfaitement sur cette loi.

# 1.2 : Pourquoi est-ce plus difficile à attaquer ?

Voici les éléments d'analyse que tu peux apporter à ton compte-rendu :Destruction de l'analyse fréquentielle simple : Dans une substitution classique (comme César ou ton script 1-3.py), la lettre 'E' est remplacée par une autre lettre, mais cette nouvelle lettre devient la plus fréquente du texte. Avec la permutation, aucune lettre n'est modifiée. Si tu comptes les lettres du cryptogramme, tu trouveras exactement les mêmes proportions que dans la langue française classique. L'attaque par comptage direct des unigrammes devient donc totalement inutile.  Double inconnue : Pour casser ce code de manière brute, l'attaquant doit deviner deux choses : la longueur du bloc de permutation (qui est arbitraire) et l'ordre exact de la permutation au sein de ce bloc.  Destruction des digrammes : Les lettres sont arrachées à leur contexte immédiat, brisant ainsi les syllabes et les mots. C'est précisément pour cela que l'algorithme MCMC (partie 1.5) sera redoutable : il va évaluer la "crédibilité" des paires de lettres (bigrammes) pour remettre de l'ordre dans le chaos.