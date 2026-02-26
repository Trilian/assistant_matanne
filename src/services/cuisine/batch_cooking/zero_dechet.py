"""
Service Zéro Déchet pour Batch Cooking — Maximiser l'utilisation.

Analyse les ingrédients restants après un batch cooking et propose
des idées pour utiliser épluchures, fanes, restes de prep.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class AstuceDechets:
    """Astuce pour valoriser un déchet alimentaire."""

    dechet: str
    idee: str
    difficulte: str = "facile"  # facile, moyen, avancé
    temps_min: int = 10
    categorie: str = ""  # compost, recette, conservation


@dataclass
class BilanZeroDechet:
    """Bilan zéro déchet d'une session batch cooking."""

    ingredients_utilises: int = 0
    ingredients_total: int = 0
    astuces: list[AstuceDechets] = field(default_factory=list)
    score_pourcentage: float = 0.0
    badge: str = ""


# ═══════════════════════════════════════════════════════════
# BASE DE CONNAISSANCES ZÉRO DÉCHET
# ═══════════════════════════════════════════════════════════

ASTUCES_DECHETS: dict[str, list[AstuceDechets]] = {
    "épluchures de légumes": [
        AstuceDechets(
            "épluchures de légumes",
            "Bouillon de légumes : faire mijoter 30min avec eau et aromates",
            "facile",
            35,
            "recette",
        ),
        AstuceDechets(
            "épluchures de légumes",
            "Chips d'épluchures : four 180°C avec huile d'olive et sel",
            "facile",
            20,
            "recette",
        ),
        AstuceDechets("épluchures de légumes", "Compost pour le jardin", "facile", 2, "compost"),
    ],
    "fanes de carottes": [
        AstuceDechets(
            "fanes de carottes",
            "Pesto de fanes : mixer avec ail, parmesan, huile d'olive, pignons",
            "facile",
            10,
            "recette",
        ),
        AstuceDechets(
            "fanes de carottes",
            "Soupe verte : avec pomme de terre et crème",
            "facile",
            25,
            "recette",
        ),
    ],
    "fanes de radis": [
        AstuceDechets(
            "fanes de radis",
            "Velouté de fanes : cuire avec pomme de terre, mixer, crème",
            "facile",
            25,
            "recette",
        ),
        AstuceDechets(
            "fanes de radis",
            "Pesto de fanes de radis : comme un pesto classique",
            "facile",
            10,
            "recette",
        ),
    ],
    "pain rassis": [
        AstuceDechets(
            "pain rassis",
            "Chapelure maison : mixer et conserver au sec",
            "facile",
            5,
            "conservation",
        ),
        AstuceDechets(
            "pain rassis", "Pain perdu : œufs + lait + sucre, poêle", "facile", 15, "recette"
        ),
        AstuceDechets(
            "pain rassis",
            "Croûtons : cubes dorés au four avec huile et herbes",
            "facile",
            15,
            "recette",
        ),
        AstuceDechets(
            "pain rassis", "Panure pour gratins et légumes farcis", "facile", 5, "recette"
        ),
    ],
    "os et carcasses": [
        AstuceDechets(
            "os et carcasses",
            "Fond de volaille/bouillon : mijoter 2-4h avec légumes et aromates",
            "moyen",
            240,
            "recette",
        ),
        AstuceDechets(
            "os et carcasses",
            "Rillettes : effilocher la viande restante sur les os",
            "moyen",
            30,
            "recette",
        ),
    ],
    "eau de cuisson": [
        AstuceDechets(
            "eau de cuisson", "Eau de pâtes pour lier les sauces", "facile", 1, "recette"
        ),
        AstuceDechets(
            "eau de cuisson",
            "Eau de légumes pour arroser les plantes (une fois refroidie)",
            "facile",
            1,
            "compost",
        ),
        AstuceDechets(
            "eau de cuisson",
            "Aquafaba (eau de pois chiches) : remplace le blanc d'œuf",
            "moyen",
            1,
            "recette",
        ),
    ],
    "parures de viande": [
        AstuceDechets("parures de viande", "Farce pour légumes farcis", "moyen", 20, "recette"),
        AstuceDechets("parures de viande", "Base de ragu ou bolognaise", "moyen", 45, "recette"),
    ],
    "tiges de brocoli": [
        AstuceDechets(
            "tiges de brocoli", "Râper pour un coleslaw de tiges", "facile", 10, "recette"
        ),
        AstuceDechets(
            "tiges de brocoli",
            "Cuire avec les fleurettes — même goût, texture légèrement différente",
            "facile",
            0,
            "recette",
        ),
    ],
    "croûtes de fromage": [
        AstuceDechets(
            "croûtes de fromage",
            "Dans la soupe : ajouter en fin de cuisson pour parfumer",
            "facile",
            5,
            "recette",
        ),
        AstuceDechets(
            "croûtes de fromage",
            "Parmesan : congeler les croûtes pour les soupes futures",
            "facile",
            2,
            "conservation",
        ),
    ],
    "blanc de poireau": [
        AstuceDechets(
            "blanc de poireau", "Fondue de poireaux : beurre + crème", "facile", 15, "recette"
        ),
    ],
    "vert de poireau": [
        AstuceDechets("vert de poireau", "Bouillon aromatique", "facile", 30, "recette"),
        AstuceDechets(
            "vert de poireau", "Velouté vert avec pomme de terre", "facile", 25, "recette"
        ),
    ],
    "citron pressé": [
        AstuceDechets(
            "citron pressé",
            "Zester avant de presser — congeler les zestes",
            "facile",
            5,
            "conservation",
        ),
        AstuceDechets(
            "citron pressé",
            "Nettoyer le plan de travail — dégraissant naturel",
            "facile",
            2,
            "autre",
        ),
    ],
    "herbes flétries": [
        AstuceDechets(
            "herbes flétries",
            "Beurre aux herbes : mixer avec du beurre mou, congeler",
            "facile",
            10,
            "conservation",
        ),
        AstuceDechets(
            "herbes flétries",
            "Huile parfumée : macérer dans de l'huile d'olive",
            "facile",
            5,
            "conservation",
        ),
        AstuceDechets(
            "herbes flétries",
            "Glaçons d'herbes : mixer avec un peu d'eau, congeler en bac",
            "facile",
            10,
            "conservation",
        ),
    ],
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def trouver_astuces(dechet: str) -> list[AstuceDechets]:
    """
    Trouve des astuces pour un déchet alimentaire.

    Args:
        dechet: Description du déchet

    Returns:
        Liste d'astuces
    """
    dechet_lower = dechet.lower()

    # Correspondance exacte
    if dechet_lower in ASTUCES_DECHETS:
        return ASTUCES_DECHETS[dechet_lower]

    # Correspondance partielle
    for key, astuces in ASTUCES_DECHETS.items():
        if key in dechet_lower or dechet_lower in key:
            return astuces

    # Recherche par mot-clé
    for key, astuces in ASTUCES_DECHETS.items():
        mots_key = set(key.split())
        mots_dechet = set(dechet_lower.split())
        if mots_key & mots_dechet:
            return astuces

    return []


def calculer_bilan_zero_dechet(
    ingredients_utilises: list[str],
    ingredients_total: list[str],
    dechets_identifies: list[str] | None = None,
) -> BilanZeroDechet:
    """
    Calcule le bilan zéro déchet d'une session.

    Args:
        ingredients_utilises: Ingrédients effectivement utilisés
        ingredients_total: Tous les ingrédients disponibles
        dechets_identifies: Déchets identifiés (épluchures, etc.)

    Returns:
        BilanZeroDechet avec score et astuces
    """
    nb_utilises = len(ingredients_utilises)
    nb_total = max(len(ingredients_total), 1)
    score = round(nb_utilises / nb_total * 100, 1)

    # Collecter astuces pour les déchets identifiés
    astuces = []
    if dechets_identifies:
        for dechet in dechets_identifies:
            astuces.extend(trouver_astuces(dechet))

    # Badge
    if score >= 100:
        badge = "🏆 Zéro Déchet Parfait"
    elif score >= 90:
        badge = "🌟 Éco-Champion"
    elif score >= 75:
        badge = "🌱 Éco-Conscient"
    elif score >= 50:
        badge = "🔄 En Progrès"
    else:
        badge = "📖 Apprenti"

    return BilanZeroDechet(
        ingredients_utilises=nb_utilises,
        ingredients_total=nb_total,
        astuces=astuces,
        score_pourcentage=score,
        badge=badge,
    )


def obtenir_toutes_astuces() -> dict[str, list[AstuceDechets]]:
    """Retourne la base complète d'astuces zéro déchet."""
    return ASTUCES_DECHETS.copy()


__all__ = [
    "AstuceDechets",
    "BilanZeroDechet",
    "ASTUCES_DECHETS",
    "trouver_astuces",
    "calculer_bilan_zero_dechet",
    "obtenir_toutes_astuces",
]
