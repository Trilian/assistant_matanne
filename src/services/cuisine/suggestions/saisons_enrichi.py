"""
Saisons enrichies — Extension du catalogue INGREDIENTS_SAISON.

Passe de ~50 ingrédients à ~120 avec :
- Sous-catégories (légume, fruit, aromate, produit_mer)
- Croisement stock/saison pour suggestions prioritaires
- Paires de saison classiques (ex: fraise+rhubarbe au printemps)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class IngredientSaisonnier:
    """Ingrédient de saison avec métadonnées."""

    nom: str
    categorie: str  # legume, fruit, aromate, produit_mer, champignon
    pic_mois: list[int] = field(default_factory=list)  # Mois de pleine saison
    bio_local_courant: bool = False  # Facilement trouvable en bio/local


@dataclass
class PaireSaison:
    """Association classique de 2+ ingrédients en saison."""

    ingredients: list[str]
    description: str
    saison: str


@dataclass
class StockSaisonCroise:
    """Résultat du croisement stock × saison."""

    ingredient: str
    en_stock: bool
    de_saison: bool
    categorie: str
    priorite: int  # 3=en stock+de saison, 2=de saison, 1=en stock, 0=ni l'un ni l'autre


# ═══════════════════════════════════════════════════════════
# CATALOGUE ENRICHI (~120 ingrédients de saison)
# ═══════════════════════════════════════════════════════════

INGREDIENTS_SAISON_ENRICHI: dict[str, list[IngredientSaisonnier]] = {
    "printemps": [
        # Légumes
        IngredientSaisonnier("asperge", "legume", [4, 5], True),
        IngredientSaisonnier("radis", "legume", [4, 5], True),
        IngredientSaisonnier("épinard", "legume", [3, 4, 5], True),
        IngredientSaisonnier("petit pois", "legume", [4, 5], True),
        IngredientSaisonnier("fève", "legume", [4, 5], True),
        IngredientSaisonnier("carotte nouvelle", "legume", [4, 5], True),
        IngredientSaisonnier("artichaut", "legume", [3, 4, 5]),
        IngredientSaisonnier("chou-fleur", "legume", [3, 4]),
        IngredientSaisonnier("laitue", "legume", [3, 4, 5], True),
        IngredientSaisonnier("cresson", "legume", [3, 4], True),
        IngredientSaisonnier("navet nouveau", "legume", [4, 5], True),
        IngredientSaisonnier("blette", "legume", [4, 5], True),
        IngredientSaisonnier("oignon nouveau", "legume", [4, 5], True),
        IngredientSaisonnier("roquette", "legume", [3, 4, 5], True),
        IngredientSaisonnier("fenouil", "legume", [4, 5]),
        # Fruits
        IngredientSaisonnier("fraise", "fruit", [4, 5], True),
        IngredientSaisonnier("rhubarbe", "fruit", [4, 5], True),
        IngredientSaisonnier("cerise", "fruit", [5]),
        # Aromates
        IngredientSaisonnier("ciboulette", "aromate", [3, 4, 5], True),
        IngredientSaisonnier("menthe", "aromate", [4, 5], True),
        IngredientSaisonnier("estragon", "aromate", [4, 5], True),
        IngredientSaisonnier("oseille", "aromate", [3, 4, 5], True),
        # Produits de la mer
        IngredientSaisonnier("maquereau", "produit_mer", [3, 4, 5]),
        IngredientSaisonnier("bar", "produit_mer", [3, 4]),
        IngredientSaisonnier("sardine", "produit_mer", [5]),
    ],
    "été": [
        # Légumes
        IngredientSaisonnier("tomate", "legume", [7, 8], True),
        IngredientSaisonnier("courgette", "legume", [6, 7, 8], True),
        IngredientSaisonnier("aubergine", "legume", [7, 8], True),
        IngredientSaisonnier("poivron", "legume", [7, 8], True),
        IngredientSaisonnier("concombre", "legume", [6, 7, 8], True),
        IngredientSaisonnier("haricot vert", "legume", [6, 7, 8], True),
        IngredientSaisonnier("maïs", "legume", [7, 8]),
        IngredientSaisonnier("fenouil", "legume", [6, 7]),
        IngredientSaisonnier("betterave", "legume", [6, 7, 8], True),
        IngredientSaisonnier("céleri branche", "legume", [7, 8]),
        IngredientSaisonnier("brocoli", "legume", [6, 7]),
        IngredientSaisonnier("artichaut violet", "legume", [6, 7]),
        # Fruits
        IngredientSaisonnier("melon", "fruit", [7, 8]),
        IngredientSaisonnier("pastèque", "fruit", [7, 8]),
        IngredientSaisonnier("pêche", "fruit", [7, 8], True),
        IngredientSaisonnier("nectarine", "fruit", [7, 8]),
        IngredientSaisonnier("abricot", "fruit", [6, 7], True),
        IngredientSaisonnier("cerise", "fruit", [6]),
        IngredientSaisonnier("framboise", "fruit", [6, 7, 8], True),
        IngredientSaisonnier("myrtille", "fruit", [7, 8], True),
        IngredientSaisonnier("groseille", "fruit", [6, 7], True),
        IngredientSaisonnier("cassis", "fruit", [7], True),
        IngredientSaisonnier("figue", "fruit", [8]),
        IngredientSaisonnier("prune", "fruit", [7, 8]),
        # Aromates
        IngredientSaisonnier("basilic", "aromate", [6, 7, 8], True),
        IngredientSaisonnier("coriandre", "aromate", [6, 7, 8], True),
        IngredientSaisonnier("aneth", "aromate", [6, 7]),
        IngredientSaisonnier("persil", "aromate", [6, 7, 8], True),
        # Produits de la mer
        IngredientSaisonnier("sardine", "produit_mer", [6, 7, 8]),
        IngredientSaisonnier("thon rouge", "produit_mer", [6, 7]),
        IngredientSaisonnier("dorade", "produit_mer", [7, 8]),
    ],
    "automne": [
        # Légumes
        IngredientSaisonnier("champignon", "champignon", [9, 10, 11], True),
        IngredientSaisonnier("cèpe", "champignon", [9, 10], True),
        IngredientSaisonnier("girolle", "champignon", [9, 10]),
        IngredientSaisonnier("potiron", "legume", [9, 10, 11], True),
        IngredientSaisonnier("courge", "legume", [9, 10, 11], True),
        IngredientSaisonnier("butternut", "legume", [10, 11], True),
        IngredientSaisonnier("potimarron", "legume", [9, 10, 11], True),
        IngredientSaisonnier("chou", "legume", [9, 10, 11], True),
        IngredientSaisonnier("chou-fleur", "legume", [9, 10]),
        IngredientSaisonnier("brocoli", "legume", [9, 10]),
        IngredientSaisonnier("poireau", "legume", [9, 10, 11], True),
        IngredientSaisonnier("céleri", "legume", [9, 10, 11]),
        IngredientSaisonnier("blette", "legume", [9, 10]),
        IngredientSaisonnier("endive", "legume", [10, 11]),
        IngredientSaisonnier("panais", "legume", [10, 11], True),
        IngredientSaisonnier("betterave", "legume", [9, 10]),
        IngredientSaisonnier("épinard", "legume", [9, 10, 11]),
        # Fruits
        IngredientSaisonnier("pomme", "fruit", [9, 10, 11], True),
        IngredientSaisonnier("poire", "fruit", [9, 10, 11], True),
        IngredientSaisonnier("raisin", "fruit", [9, 10]),
        IngredientSaisonnier("figue", "fruit", [9]),
        IngredientSaisonnier("coing", "fruit", [10, 11], True),
        IngredientSaisonnier("châtaigne", "fruit", [10, 11], True),
        IngredientSaisonnier("noix", "fruit", [9, 10, 11], True),
        IngredientSaisonnier("noisette", "fruit", [9, 10], True),
        IngredientSaisonnier("mirabelle", "fruit", [9]),
        # Aromates
        IngredientSaisonnier("thym", "aromate", [9, 10, 11]),
        IngredientSaisonnier("romarin", "aromate", [9, 10, 11]),
        IngredientSaisonnier("sauge", "aromate", [9, 10]),
        # Produits de la mer
        IngredientSaisonnier("moule", "produit_mer", [9, 10, 11]),
        IngredientSaisonnier("huître", "produit_mer", [10, 11]),
        IngredientSaisonnier("coquille saint-jacques", "produit_mer", [10, 11]),
    ],
    "hiver": [
        # Légumes
        IngredientSaisonnier("endive", "legume", [12, 1, 2], True),
        IngredientSaisonnier("mâche", "legume", [12, 1, 2], True),
        IngredientSaisonnier("chou de bruxelles", "legume", [12, 1, 2], True),
        IngredientSaisonnier("navet", "legume", [12, 1, 2], True),
        IngredientSaisonnier("panais", "legume", [12, 1, 2], True),
        IngredientSaisonnier("topinambour", "legume", [12, 1, 2], True),
        IngredientSaisonnier("chou rouge", "legume", [12, 1]),
        IngredientSaisonnier("chou frisé", "legume", [12, 1, 2], True),
        IngredientSaisonnier("pomme de terre", "legume", [12, 1, 2]),
        IngredientSaisonnier("oignon", "legume", [12, 1, 2]),
        IngredientSaisonnier("carotte", "legume", [12, 1, 2]),
        IngredientSaisonnier("céleri-rave", "legume", [12, 1, 2], True),
        IngredientSaisonnier("rutabaga", "legume", [12, 1, 2], True),
        IngredientSaisonnier("salsifis", "legume", [12, 1]),
        IngredientSaisonnier("poireau", "legume", [12, 1, 2], True),
        IngredientSaisonnier("épinard", "legume", [12, 1]),
        # Fruits
        IngredientSaisonnier("orange", "fruit", [12, 1, 2]),
        IngredientSaisonnier("clémentine", "fruit", [12, 1]),
        IngredientSaisonnier("mandarine", "fruit", [12, 1, 2]),
        IngredientSaisonnier("kiwi", "fruit", [12, 1, 2], True),
        IngredientSaisonnier("pamplemousse", "fruit", [1, 2]),
        IngredientSaisonnier("pomme", "fruit", [12, 1, 2], True),
        IngredientSaisonnier("poire", "fruit", [12, 1]),
        IngredientSaisonnier("citron", "fruit", [12, 1, 2]),
        # Aromates
        IngredientSaisonnier("persil", "aromate", [12, 1, 2]),
        IngredientSaisonnier("cerfeuil", "aromate", [12, 1]),
        # Produits de la mer
        IngredientSaisonnier("huître", "produit_mer", [12, 1, 2]),
        IngredientSaisonnier("coquille saint-jacques", "produit_mer", [12, 1]),
        IngredientSaisonnier("moule", "produit_mer", [12]),
        IngredientSaisonnier("lieu noir", "produit_mer", [1, 2]),
    ],
}


# ═══════════════════════════════════════════════════════════
# PAIRES DE SAISON CLASSIQUES
# ═══════════════════════════════════════════════════════════

PAIRES_SAISON: list[PaireSaison] = [
    # Printemps
    PaireSaison(["fraise", "rhubarbe"], "Tarte fraise-rhubarbe", "printemps"),
    PaireSaison(["asperge", "œuf", "parmesan"], "Asperges gratinées", "printemps"),
    PaireSaison(["petit pois", "menthe"], "Petits pois à la menthe", "printemps"),
    PaireSaison(["fève", "pecorino"], "Salade de fèves", "printemps"),
    PaireSaison(["radis", "beurre"], "Radis beurre sel", "printemps"),
    # Été
    PaireSaison(["tomate", "mozzarella", "basilic"], "Caprese", "été"),
    PaireSaison(["courgette", "chèvre", "menthe"], "Tarte courgette-chèvre", "été"),
    PaireSaison(["aubergine", "tomate", "poivron"], "Ratatouille", "été"),
    PaireSaison(["melon", "jambon cru"], "Melon-jambon", "été"),
    PaireSaison(["pêche", "thym"], "Pêches rôties au thym", "été"),
    PaireSaison(["pastèque", "feta", "menthe"], "Salade pastèque-feta", "été"),
    PaireSaison(["concombre", "yaourt", "aneth"], "Tzatziki", "été"),
    # Automne
    PaireSaison(["potiron", "châtaigne"], "Velouté potiron-châtaigne", "automne"),
    PaireSaison(["cèpe", "persil", "ail"], "Cèpes persillés", "automne"),
    PaireSaison(["pomme", "cannelle"], "Tarte aux pommes", "automne"),
    PaireSaison(["butternut", "noisette"], "Butternut rôti aux noisettes", "automne"),
    PaireSaison(["poire", "roquefort", "noix"], "Salade poire-roquefort", "automne"),
    PaireSaison(["endive", "noix", "roquefort"], "Salade d'endives", "automne"),
    # Hiver
    PaireSaison(["endive", "jambon", "béchamel"], "Endives au jambon", "hiver"),
    PaireSaison(["chou", "saucisse", "pomme de terre"], "Potée hivernale", "hiver"),
    PaireSaison(["orange", "chocolat"], "Orangettes", "hiver"),
    PaireSaison(["topinambour", "noisette"], "Velouté topinambour", "hiver"),
    PaireSaison(["panais", "miel"], "Panais rôtis au miel", "hiver"),
    PaireSaison(["céleri-rave", "pomme", "noix"], "Rémoulade de céleri", "hiver"),
]


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def obtenir_saison(dt: date | datetime | None = None) -> str:
    """Détermine la saison pour une date (par défaut: aujourd'hui)."""
    from src.services.cuisine.suggestions.saisons import get_current_season

    return get_current_season(dt)


def obtenir_ingredients_saison_enrichis(
    saison: str | None = None,
    categorie: str | None = None,
    bio_local_seulement: bool = False,
) -> list[IngredientSaisonnier]:
    """
    Retourne les ingrédients enrichis pour une saison.

    Args:
        saison: Nom de saison (auto si None)
        categorie: Filtrer par catégorie (legume, fruit, aromate, produit_mer)
        bio_local_seulement: Filtrer ceux disponibles en bio/local
    """
    if saison is None:
        saison = obtenir_saison()

    ingredients = INGREDIENTS_SAISON_ENRICHI.get(saison, [])

    if categorie:
        ingredients = [i for i in ingredients if i.categorie == categorie]

    if bio_local_seulement:
        ingredients = [i for i in ingredients if i.bio_local_courant]

    return ingredients


def obtenir_paires_saison(saison: str | None = None) -> list[PaireSaison]:
    """Retourne les paires classiques pour la saison."""
    if saison is None:
        saison = obtenir_saison()

    return [p for p in PAIRES_SAISON if p.saison == saison]


def croisement_stock_saison(
    stock_noms: list[str],
    saison: str | None = None,
) -> list[StockSaisonCroise]:
    """
    Croise le stock actuel avec les ingrédients de saison.

    Priorise: en stock + de saison > de saison seul > en stock seul.

    Args:
        stock_noms: Noms des articles en stock
        saison: Saison (auto si None)

    Returns:
        Liste triée par priorité décroissante
    """
    if saison is None:
        saison = obtenir_saison()

    ingredients_saison = INGREDIENTS_SAISON_ENRICHI.get(saison, [])
    saison_noms = {i.nom.lower(): i for i in ingredients_saison}
    stock_lower = {s.lower() for s in stock_noms}

    resultats: list[StockSaisonCroise] = []

    # Tous les ingrédients de saison
    for nom_lower, ing in saison_noms.items():
        en_stock = any(nom_lower in s or s in nom_lower for s in stock_lower)
        priorite = 3 if en_stock else 2
        resultats.append(
            StockSaisonCroise(
                ingredient=ing.nom,
                en_stock=en_stock,
                de_saison=True,
                categorie=ing.categorie,
                priorite=priorite,
            )
        )

    # Articles en stock qui ne sont pas de saison
    noms_inclus = {r.ingredient.lower() for r in resultats}
    for s in stock_noms:
        sl = s.lower()
        if not any(sl in n or n in sl for n in noms_inclus):
            resultats.append(
                StockSaisonCroise(
                    ingredient=s,
                    en_stock=True,
                    de_saison=False,
                    categorie="autre",
                    priorite=1,
                )
            )

    resultats.sort(key=lambda x: x.priorite, reverse=True)
    return resultats


def est_en_pleine_saison(ingredient: str, dt: date | None = None) -> bool:
    """
    Vérifie si un ingrédient est en pleine saison (pic de production).

    Plus précis que is_ingredient_in_season car utilise les mois de pic.
    """
    if dt is None:
        dt = date.today()

    mois = dt.month
    saison = obtenir_saison(dt)
    ingredients = INGREDIENTS_SAISON_ENRICHI.get(saison, [])
    ingredient_lower = ingredient.lower()

    for ing in ingredients:
        if ing.nom.lower() in ingredient_lower or ingredient_lower in ing.nom.lower():
            return mois in ing.pic_mois if ing.pic_mois else True

    return False


__all__ = [
    "IngredientSaisonnier",
    "PaireSaison",
    "StockSaisonCroise",
    "INGREDIENTS_SAISON_ENRICHI",
    "PAIRES_SAISON",
    "obtenir_ingredients_saison_enrichis",
    "obtenir_paires_saison",
    "croisement_stock_saison",
    "est_en_pleine_saison",
]
