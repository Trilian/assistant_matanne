"""
Constantes pour le service de suggestions de recettes.

Contient les dictionnaires de saisons, ingrédients de saison,
types de protéines et scores de pertinence.
"""

# Saisons et mois associés
SAISONS = {
    "printemps": [3, 4, 5],
    "été": [6, 7, 8],
    "automne": [9, 10, 11],
    "hiver": [12, 1, 2],
}

# Ingrédients de saison
INGREDIENTS_SAISON = {
    "printemps": [
        "asperge",
        "radis",
        "épinard",
        "petit pois",
        "fève",
        "carotte nouvelle",
        "fraise",
        "rhubarbe",
        "artichaut",
        "chou-fleur",
        "laitue",
        "cresson",
    ],
    "été": [
        "tomate",
        "courgette",
        "aubergine",
        "poivron",
        "concombre",
        "haricot vert",
        "melon",
        "pastèque",
        "pêche",
        "abricot",
        "cerise",
        "framboise",
        "myrtille",
    ],
    "automne": [
        "champignon",
        "potiron",
        "courge",
        "butternut",
        "châtaigne",
        "noix",
        "pomme",
        "poire",
        "raisin",
        "coing",
        "chou",
        "poireau",
        "céleri",
    ],
    "hiver": [
        "endive",
        "mâche",
        "chou de bruxelles",
        "navet",
        "panais",
        "topinambour",
        "orange",
        "clémentine",
        "kiwi",
        "pamplemousse",
        "pomme de terre",
        "oignon",
    ],
}

# Types de protéines
PROTEINES_POISSON = ["poisson", "saumon", "cabillaud", "thon", "dorade", "bar", "sole", "truite"]
PROTEINES_VIANDE_ROUGE = ["boeuf", "agneau", "veau", "porc", "canard", "gibier"]
PROTEINES_VOLAILLE = ["poulet", "dinde", "pintade"]
PROTEINES_VEGETARIEN = ["tofu", "tempeh", "seitan", "légumineuse", "lentille", "pois chiche"]

# Scores de pertinence
SCORE_INGREDIENT_DISPONIBLE = 10
SCORE_INGREDIENT_PRIORITAIRE = 25  # À consommer vite
SCORE_INGREDIENT_SAISON = 5
SCORE_CATEGORIE_PREFEREE = 15
SCORE_JAMAIS_PREPAREE = 20
SCORE_DIFFICULTE_ADAPTEE = 10
SCORE_TEMPS_ADAPTE = 15
SCORE_VARIETE = 10  # Pas préparée récemment

__all__ = [
    "SAISONS",
    "INGREDIENTS_SAISON",
    "PROTEINES_POISSON",
    "PROTEINES_VIANDE_ROUGE",
    "PROTEINES_VOLAILLE",
    "PROTEINES_VEGETARIEN",
    "SCORE_INGREDIENT_DISPONIBLE",
    "SCORE_INGREDIENT_PRIORITAIRE",
    "SCORE_INGREDIENT_SAISON",
    "SCORE_CATEGORIE_PREFEREE",
    "SCORE_JAMAIS_PREPAREE",
    "SCORE_DIFFICULTE_ADAPTEE",
    "SCORE_TEMPS_ADAPTE",
    "SCORE_VARIETE",
]
