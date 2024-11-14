

# le problème des symétries a été traité avce une contrainte qui impose que chaque objet i ne puisse être placé que dans une boîte j
#  avec un indice j≤i.  Cela crée un tri implicite où les objets sont placés dans les boîtes dans l'ordre de leurs indices,

# les case vide signifie que j'ai pas pu avoir un resultat

# |                   | nb boites | temps sans gestion symétries | temps avec gestion symmétries |
# | ----------------- | --------- | ---------------------------- | ----------------------------- |
# | u20_00            | 9         | 0.04                         | 0.02                          |
# | u40_00            | 17        | 133.78                       | 26.19                         |
# | u60_00            | 23        |                              | 532                           |
# | u120_00           |           |                              |                               |
# | inst60_non-unif_9 | 14        | 1.17                         | 17.26                         |


from pyscipopt import Model

# Fonction pour lire l'instance depuis un fichier
def lire_instance(fichier):

    with open(fichier, 'r') as file:
        # Lire le nom de l'instance (1ère ligne)
        nom_instance = file.readline().strip()
        
        # Lire la capacité et le nombre d'objets (2ème ligne)
        capacite, nb_objets, _ = map(int, file.readline().split())
        
        # Lire les tailles des objets (lignes suivantes)
        tailles = [int(file.readline().strip()) for _ in range(nb_objets)]
    
    return capacite, tailles

# Charger les données depuis le fichier 

# C pour la capacité
# O pour les taille des objet
C, O = lire_instance('inst60-non-unif_9.bpa')  # Remplacer 'le nom du fichier' par le chemin vers d'autre fichier

# Le modèle :
M = Model()

# Variables :
x = {}
for i in range(len(O)):  # Pour chaque objet
    for j in range(len(O)):  # Pour chaque boîte
        x[i, j] = M.addVar(f"x_{i}_{j}", vtype="B")

# Variables binaires pour les boîtes
B = [M.addVar(f"B_{j}", vtype="B") for j in range(len(O))]  


# Contrainte : chaque objet doit être affecté à une boîte
for i in range(len(O)):
    M.addCons(sum(x[i, j] for j in range(len(O))) == 1)

# Contrainte : La capacité totale dans chaque boîte ne doit pas dépasser C
for j in range(len(O)):
    M.addCons(sum(x[i, j] * O[i] for i in range(len(O))) <= C)

# Contrainte : Si un objet est placé dans la boîte j, la boîte j doit être marquée comme utilisée
for j in range(len(O)):
    for i in range(len(O)):
        M.addCons(x[i, j] <= B[j] ) 

# Contrainte : pour éviter la symétries
for i in range(len(O)):
    for j in range(i + 1, len(O)):  # j commence à i+1 pour imposer i < j
        M.addCons(x[i, j] == 0)

# Fonction objectif : Minimiser le nombre de boîtes utilisées
M.setObjective(sum(B[j] for j in range(len(O))), sense="minimize")

# Résolution :
M.optimize()

# Affichage des résultats :
if M.getStatus() == "optimal":

    print("Solution optimale trouvée :")
    s = M.getBestSol()

    boites_total = 0

    for j in range(len(O)):

        if s[B[j]] > 0.5:  # Si la boîte j est utilisée
            boites_total += 1
            print(f"Boîte {j} est utilisée.")
            for i in range(len(O)):
                
                if s[x[i, j]] > 0.5:  # Si l'objet i est dans la boîte j
                
                    print(f"  Objet {i} avec poids {O[i]} est placé dans la boîte {j}.")
    
    print(f"Nombre total de boîtes utilisées : {boites_total}")
else:
    print("Aucune solution optimale trouvée.")

