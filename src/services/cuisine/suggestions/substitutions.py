"""
Service de substitutions d'ingrédients — Base statique + fallback IA.

Propose des substitutions pour les ingrédients manquants basées sur
le stock disponible, les préférences alimentaires et les contraintes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class Substitution:
    """Une substitution possible d'ingrédient."""

    ingredient_original: str
    ingredient_substitut: str
    ratio: float  # ex: 1.0 = même quantité, 0.5 = moitié
    impact_gout: str  # "neutre", "leger", "notable"
    tags: list[str] = field(default_factory=list)  # vegan, sans_lactose, sans_gluten
    note: str = ""


@dataclass
class SubstitutionRecette:
    """Substitution contextualisée pour une recette spécifique."""

    ingredient_manquant: str
    quantite_requise: float
    unite: str
    substitutions: list[Substitution]
    meilleure_en_stock: Substitution | None = None


# ═══════════════════════════════════════════════════════════
# BASE DE SUBSTITUTIONS COURANTES (~80 entrées)
# ═══════════════════════════════════════════════════════════

BASE_SUBSTITUTIONS: dict[str, list[Substitution]] = {
    # Produits laitiers
    "crème fraîche": [
        Substitution("crème fraîche", "yaourt nature", 1.0, "leger", ["sans_lactose_possible"]),
        Substitution("crème fraîche", "lait de coco", 1.0, "notable", ["vegan", "sans_lactose"]),
        Substitution("crème fraîche", "fromage blanc", 1.0, "leger"),
        Substitution("crème fraîche", "crème de soja", 1.0, "leger", ["vegan", "sans_lactose"]),
    ],
    "crème liquide": [
        Substitution(
            "crème liquide", "lait + beurre", 1.0, "neutre", note="200ml lait + 30g beurre"
        ),
        Substitution("crème liquide", "lait de coco", 1.0, "notable", ["vegan", "sans_lactose"]),
        Substitution("crème liquide", "crème de soja", 1.0, "leger", ["vegan", "sans_lactose"]),
    ],
    "beurre": [
        Substitution("beurre", "huile d'olive", 0.75, "notable", ["vegan", "sans_lactose"]),
        Substitution("beurre", "huile de coco", 0.85, "leger", ["vegan", "sans_lactose"]),
        Substitution("beurre", "margarine", 1.0, "neutre", ["sans_lactose"]),
        Substitution("beurre", "compote de pommes", 0.5, "notable", ["vegan"], "Pour pâtisserie"),
        Substitution("beurre", "purée d'avocat", 1.0, "notable", ["vegan"], "Pour pâtisserie"),
    ],
    "lait": [
        Substitution("lait", "lait d'avoine", 1.0, "leger", ["vegan", "sans_lactose"]),
        Substitution("lait", "lait d'amande", 1.0, "leger", ["vegan", "sans_lactose"]),
        Substitution("lait", "lait de soja", 1.0, "leger", ["vegan", "sans_lactose"]),
        Substitution("lait", "lait de coco", 1.0, "notable", ["vegan", "sans_lactose"]),
        Substitution("lait", "eau + crème", 1.0, "leger", note="80% eau + 20% crème"),
    ],
    "fromage râpé": [
        Substitution("fromage râpé", "levure nutritionnelle", 0.3, "notable", ["vegan"]),
        Substitution("fromage râpé", "parmesan", 0.7, "neutre"),
        Substitution("fromage râpé", "chapelure grillée", 0.5, "notable", note="Pour le gratiné"),
    ],
    # Œufs
    "oeuf": [
        Substitution(
            "oeuf", "compote de pommes", 1.0, "leger", ["vegan"], "60g par œuf, pâtisserie"
        ),
        Substitution("oeuf", "banane écrasée", 1.0, "notable", ["vegan"], "1/2 banane par œuf"),
        Substitution(
            "oeuf", "graines de lin + eau", 1.0, "leger", ["vegan"], "1cs + 3cs eau par œuf"
        ),
        Substitution("oeuf", "tofu soyeux", 1.0, "leger", ["vegan"], "60g par œuf"),
        Substitution("oeuf", "yaourt", 1.0, "leger", note="60g par œuf"),
    ],
    "œuf": [
        Substitution("œuf", "compote de pommes", 1.0, "leger", ["vegan"], "60g par œuf"),
        Substitution("œuf", "banane écrasée", 1.0, "notable", ["vegan"], "1/2 banane par œuf"),
        Substitution("œuf", "graines de lin + eau", 1.0, "leger", ["vegan"], "1cs + 3cs eau"),
    ],
    # Farines et féculents
    "farine de blé": [
        Substitution("farine de blé", "farine de riz", 1.0, "leger", ["sans_gluten"]),
        Substitution(
            "farine de blé", "fécule de maïs", 0.5, "neutre", ["sans_gluten"], "Épaississant"
        ),
        Substitution("farine de blé", "farine de sarrasin", 1.0, "notable", ["sans_gluten"]),
        Substitution("farine de blé", "farine d'épeautre", 1.0, "neutre"),
    ],
    "farine": [
        Substitution("farine", "fécule de maïs", 0.5, "neutre", ["sans_gluten"], "Épaississant"),
        Substitution("farine", "farine de riz", 1.0, "leger", ["sans_gluten"]),
    ],
    "chapelure": [
        Substitution("chapelure", "flocons d'avoine mixés", 1.0, "leger"),
        Substitution("chapelure", "semoule fine", 1.0, "leger"),
        Substitution("chapelure", "pain rassis mixé", 1.0, "neutre"),
    ],
    # Sucres
    "sucre": [
        Substitution("sucre", "miel", 0.75, "notable", note="Réduire liquide de 20%"),
        Substitution("sucre", "sirop d'érable", 0.75, "notable", ["vegan"]),
        Substitution("sucre", "compote de pommes", 1.0, "notable", ["vegan"], "Pâtisserie"),
        Substitution("sucre", "sucre de coco", 1.0, "neutre"),
    ],
    "miel": [
        Substitution("miel", "sirop d'érable", 1.0, "leger", ["vegan"]),
        Substitution("miel", "sirop d'agave", 1.0, "leger", ["vegan"]),
        Substitution("miel", "confiture", 1.0, "notable"),
    ],
    # Condiments et assaisonnements
    "moutarde": [
        Substitution("moutarde", "wasabi", 0.3, "notable"),
        Substitution("moutarde", "raifort", 0.5, "notable"),
        Substitution("moutarde", "vinaigre + poivre", 1.0, "leger"),
    ],
    "sauce soja": [
        Substitution("sauce soja", "tamari", 1.0, "neutre", ["sans_gluten"]),
        Substitution("sauce soja", "miso dilué", 1.0, "leger"),
        Substitution("sauce soja", "bouillon + sel", 1.0, "leger"),
    ],
    "vinaigre balsamique": [
        Substitution("vinaigre balsamique", "vinaigre de vin + miel", 1.0, "leger"),
        Substitution("vinaigre balsamique", "jus de citron + sucre", 1.0, "notable"),
    ],
    "vin blanc": [
        Substitution("vin blanc", "bouillon de légumes", 1.0, "leger"),
        Substitution("vin blanc", "jus de citron + eau", 1.0, "notable"),
        Substitution("vin blanc", "vinaigre de cidre dilué", 0.5, "leger"),
    ],
    "vin rouge": [
        Substitution("vin rouge", "bouillon de bœuf", 1.0, "leger"),
        Substitution("vin rouge", "jus de raisin", 1.0, "notable"),
    ],
    # Herbes et épices
    "persil": [
        Substitution("persil", "coriandre", 1.0, "notable"),
        Substitution("persil", "cerfeuil", 1.0, "leger"),
        Substitution("persil", "basilic", 1.0, "notable"),
    ],
    "basilic": [
        Substitution("basilic", "persil", 1.0, "notable"),
        Substitution("basilic", "origan", 0.5, "notable"),
    ],
    "coriandre": [
        Substitution("coriandre", "persil", 1.0, "notable"),
        Substitution("coriandre", "basilic thaï", 1.0, "leger"),
    ],
    # Protéines
    "poulet": [
        Substitution("poulet", "dinde", 1.0, "neutre"),
        Substitution("poulet", "tofu ferme", 1.0, "notable", ["vegan"]),
        Substitution("poulet", "pois chiches", 1.5, "notable", ["vegan"]),
    ],
    "boeuf": [
        Substitution("boeuf", "veau", 1.0, "leger"),
        Substitution("boeuf", "agneau", 1.0, "notable"),
        Substitution("boeuf", "champignons", 1.5, "notable", ["vegan"], "Portobello pour texture"),
        Substitution("boeuf", "lentilles", 1.5, "notable", ["vegan"]),
    ],
    "saumon": [
        Substitution("saumon", "truite", 1.0, "neutre"),
        Substitution("saumon", "cabillaud", 1.0, "leger"),
        Substitution("saumon", "thon", 1.0, "leger"),
    ],
    "lardons": [
        Substitution("lardons", "allumettes de jambon", 1.0, "leger"),
        Substitution("lardons", "champignons émincés", 1.5, "notable", ["vegan"]),
        Substitution("lardons", "tofu fumé émincé", 1.0, "notable", ["vegan"]),
    ],
    # Légumes courants
    "tomate": [
        Substitution("tomate", "poivron rouge", 1.0, "notable"),
        Substitution("tomate", "tomate en conserve", 1.0, "neutre"),
        Substitution("tomate", "coulis de tomate", 0.5, "leger"),
    ],
    "oignon": [
        Substitution("oignon", "échalote", 0.7, "leger"),
        Substitution("oignon", "poireau", 1.0, "leger"),
        Substitution("oignon", "oignon en poudre", 0.1, "leger"),
    ],
    "ail": [
        Substitution("ail", "ail en poudre", 0.2, "leger"),
        Substitution("ail", "échalote", 1.0, "notable"),
    ],
    "courgette": [
        Substitution("courgette", "aubergine", 1.0, "notable"),
        Substitution("courgette", "concombre", 1.0, "notable", note="Cru uniquement"),
    ],
    "pomme de terre": [
        Substitution("pomme de terre", "patate douce", 1.0, "notable"),
        Substitution("pomme de terre", "navet", 1.0, "notable"),
        Substitution("pomme de terre", "céleri-rave", 1.0, "notable"),
    ],
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE RECHERCHE
# ═══════════════════════════════════════════════════════════


def trouver_substitutions(
    ingredient_manquant: str,
    *,
    stock_disponible: list[str] | None = None,
    tags_requis: list[str] | None = None,
) -> list[Substitution]:
    """
    Trouve les substitutions possibles pour un ingrédient manquant.

    Args:
        ingredient_manquant: Nom de l'ingrédient à remplacer
        stock_disponible: Liste des ingrédients en stock (filtrage)
        tags_requis: Tags obligatoires (ex: ["vegan", "sans_gluten"])

    Returns:
        Liste de Substitution triée par pertinence
    """
    ingredient_lower = ingredient_manquant.lower().strip()

    # Chercher correspondance exacte puis partielle
    subs = BASE_SUBSTITUTIONS.get(ingredient_lower, [])

    if not subs:
        # Recherche partielle
        for key, vals in BASE_SUBSTITUTIONS.items():
            if key in ingredient_lower or ingredient_lower in key:
                subs = vals
                break

    if not subs:
        return []

    # Filtrer par tags requis
    if tags_requis:
        subs = [s for s in subs if all(t in s.tags for t in tags_requis)]

    # Filtrer et trier par disponibilité en stock
    if stock_disponible:
        stock_lower = {s.lower() for s in stock_disponible}

        def score_stock(sub: Substitution) -> int:
            sub_lower = sub.ingredient_substitut.lower()
            if any(sub_lower in s or s in sub_lower for s in stock_lower):
                return 100
            return 0

        subs = sorted(subs, key=score_stock, reverse=True)

    return subs


def trouver_meilleure_en_stock(
    ingredient_manquant: str,
    stock_disponible: list[str],
    tags_requis: list[str] | None = None,
) -> Substitution | None:
    """Trouve la meilleure substitution disponible en stock."""
    subs = trouver_substitutions(
        ingredient_manquant,
        stock_disponible=stock_disponible,
        tags_requis=tags_requis,
    )

    stock_lower = {s.lower() for s in stock_disponible}
    for sub in subs:
        sub_lower = sub.ingredient_substitut.lower()
        if any(sub_lower in s or s in sub_lower for s in stock_lower):
            return sub

    return None


def suggerer_substitutions_recette(
    ingredients_manquants: list[dict],
    stock_disponible: list[str],
    tags_requis: list[str] | None = None,
) -> list[SubstitutionRecette]:
    """
    Propose des substitutions pour tous les ingrédients manquants d'une recette.

    Args:
        ingredients_manquants: list de dict {nom, quantite, unite}
        stock_disponible: noms des ingrédients en stock
        tags_requis: contraintes alimentaires

    Returns:
        Liste de SubstitutionRecette
    """
    resultats = []
    for ing in ingredients_manquants:
        nom = ing.get("nom", "")
        subs = trouver_substitutions(
            nom, stock_disponible=stock_disponible, tags_requis=tags_requis
        )
        meilleure = trouver_meilleure_en_stock(nom, stock_disponible, tags_requis)

        resultats.append(
            SubstitutionRecette(
                ingredient_manquant=nom,
                quantite_requise=ing.get("quantite", 0),
                unite=ing.get("unite", ""),
                substitutions=subs[:5],
                meilleure_en_stock=meilleure,
            )
        )

    return resultats


__all__ = [
    "Substitution",
    "SubstitutionRecette",
    "BASE_SUBSTITUTIONS",
    "trouver_substitutions",
    "trouver_meilleure_en_stock",
    "suggerer_substitutions_recette",
]
