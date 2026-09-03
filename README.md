# R5.10-Projet_Modelisation

# 1.2 : Cette chaîne de Markov est-elle irréductible ? apériodique ? Quelle(s) loi(s) stables(s) ?

La chaîne de Markov modélisant les mots est irréductible, car tous les états (les 27 caractères) communiquent entre eux. Dans une langue naturelle comme le français, il existe toujours un chemin de probabilité non nulle permettant d'atteindre n'importe quelle lettre depuis n'importe quelle autre après un certain nombre d'étapes.

Elle est également apériodique, car il existe des transitions directes d'un état vers lui-même. L'existence dans le texte de lettres doubles (comme "LL" ou "EE") ou d'espaces consécutifs crée des boucles locales qui empêchent les transitions de se bloquer dans un cycle temporel prévisible et répétitif. 

Enfin, puisqu'elle est finie, irréductible et apériodique, cette chaîne admet une unique loi stable. Cette loi de probabilité asymptotique correspond très exactement aux fréquences d'apparition individuelles de chaque caractère (les unigrammes) que vous avez calculées lors de l'analyse initiale de la page web. Si le processus de génération tournait à l'infini, la proportion de chaque lettre générée se stabiliserait parfaitement sur cette loi.