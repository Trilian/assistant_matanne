"""
Convertisseur d'unités culinaires — mesures françaises, anglo-saxonnes, métriques.

Gère cups/tablespoons/teaspoons → ml/g, et les conversions entre
les unités courantes (kg↔g, L↔mL, etc.).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeUnite(Enum):
    """Catégorie d'unité de mesure."""

    VOLUME = "volume"
    POIDS = "poids"
    PIECE = "pièce"
    AUTRE = "autre"


@dataclass
class ResultatConversion:
    """Résultat d'une conversion d'unité."""

    valeur_source: float
    unite_source: str
    valeur_cible: float
    unite_cible: str
    approximation: bool = False  # True si la conversion dépend de la densité


# ═══════════════════════════════════════════════════════════
# TABLES DE CONVERSION
# ═══════════════════════════════════════════════════════════

# Volume → mL (base millilitre)
VOLUME_VERS_ML: dict[str, float] = {
    "ml": 1.0,
    "millilitre": 1.0,
    "cl": 10.0,
    "centilitre": 10.0,
    "dl": 100.0,
    "décilitre": 100.0,
    "l": 1000.0,
    "litre": 1000.0,
    # Anglo-saxons
    "cup": 236.588,
    "tasse": 236.588,
    "tbsp": 14.787,
    "tablespoon": 14.787,
    "cuillère à soupe": 15.0,
    "cs": 15.0,
    "c.à.s": 15.0,
    "cas": 15.0,
    "tsp": 4.929,
    "teaspoon": 4.929,
    "cuillère à café": 5.0,
    "cc": 5.0,
    "c.à.c": 5.0,
    "cac": 5.0,
    "fl oz": 29.574,
    "fluid ounce": 29.574,
    "pint": 473.176,
    "quart": 946.353,
    "gallon": 3785.41,
    # Français spécifiques
    "verre": 200.0,
    "bol": 350.0,
    "louche": 100.0,
}

# Poids → g (base gramme)
POIDS_VERS_G: dict[str, float] = {
    "g": 1.0,
    "gramme": 1.0,
    "kg": 1000.0,
    "kilogramme": 1000.0,
    "mg": 0.001,
    "milligramme": 0.001,
    # Anglo-saxons
    "oz": 28.3495,
    "ounce": 28.3495,
    "lb": 453.592,
    "pound": 453.592,
    "livre": 453.592,
    # Français spécifiques
    "pincée": 0.5,
}

# Unités qui sont des pièces (pas de conversion entre elles)
UNITES_PIECES = {
    "pièce",
    "pc",
    "unité",
    "tranche",
    "feuille",
    "gousse",
    "brin",
    "branche",
    "bouquet",
    "sachet",
    "boîte",
    "conserve",
    "paquet",
    "pot",
}

# Aliases normalisées
_ALIASES: dict[str, str] = {
    "cuillères à soupe": "cuillère à soupe",
    "cuillères à café": "cuillère à café",
    "c. à soupe": "cuillère à soupe",
    "c. à café": "cuillère à café",
    "c.a.s": "c.à.s",
    "c.a.c": "c.à.c",
    "cups": "cup",
    "tasses": "tasse",
    "litres": "litre",
    "grammes": "gramme",
    "kilogrammes": "kilogramme",
    "millilitres": "millilitre",
    "centilitres": "centilitre",
    "onces": "ounce",
    "livres": "livre",
    "verres": "verre",
    "pièces": "pièce",
    "unités": "unité",
    "tranches": "tranche",
    "feuilles": "feuille",
    "gousses": "gousse",
    "brins": "brin",
    "branches": "branche",
    "bouquets": "bouquet",
    "sachets": "sachet",
    "paquets": "paquet",
    "pots": "pot",
}

# Densités approximatives (g/mL) pour conversion volume↔poids
DENSITES: dict[str, float] = {
    # Liquides
    "eau": 1.0,
    "lait": 1.03,
    "huile": 0.92,
    "huile d'olive": 0.92,
    "vinaigre": 1.01,
    "miel": 1.42,
    "sirop d'érable": 1.32,
    "sauce soja": 1.10,
    "crème liquide": 1.01,
    "crème fraîche": 1.05,
    # Poudres et solides
    "farine": 0.55,
    "farine de blé": 0.55,
    "sucre": 0.85,
    "sucre glace": 0.56,
    "cassonade": 0.83,
    "sel": 1.20,
    "sel fin": 1.20,
    "cacao": 0.42,
    "levure chimique": 0.90,
    "maïzena": 0.50,
    "fécule": 0.50,
    "riz": 0.85,
    "semoule": 0.70,
    "flocons d'avoine": 0.34,
    "noix de coco râpée": 0.34,
    "amande en poudre": 0.47,
    "chapelure": 0.50,
    "parmesan râpé": 0.45,
    "fromage râpé": 0.40,
    "beurre": 0.91,
    "beurre fondu": 0.91,
    "confiture": 1.30,
    "nutella": 1.20,
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def normaliser_unite(unite: str) -> str:
    """Normalise une unité en sa forme canonique."""
    u = unite.lower().strip().rstrip(".")
    return _ALIASES.get(u, u)


def type_unite(unite: str) -> TypeUnite:
    """Détermine le type d'une unité."""
    u = normaliser_unite(unite)
    if u in VOLUME_VERS_ML:
        return TypeUnite.VOLUME
    if u in POIDS_VERS_G:
        return TypeUnite.POIDS
    if u in UNITES_PIECES:
        return TypeUnite.PIECE
    return TypeUnite.AUTRE


def convertir(
    valeur: float,
    unite_source: str,
    unite_cible: str,
    ingredient: str | None = None,
) -> ResultatConversion | None:
    """
    Convertit une quantité d'une unité à une autre.

    Args:
        valeur: Quantité source
        unite_source: Unité d'origine
        unite_cible: Unité cible
        ingredient: Nom de l'ingrédient (pour les conversions volume↔poids)

    Returns:
        ResultatConversion ou None si conversion impossible

    Examples:
        >>> convertir(2, "cup", "ml")
        ResultatConversion(valeur_source=2, unite_source='cup', valeur_cible=473.18, ...)
        >>> convertir(500, "g", "lb")
        ResultatConversion(valeur_source=500, unite_source='g', valeur_cible=1.1, ...)
        >>> convertir(1, "cup", "g", "farine")
        ResultatConversion(valeur_source=1, ... valeur_cible=130.12, ..., approximation=True)
    """
    us = normaliser_unite(unite_source)
    uc = normaliser_unite(unite_cible)

    type_s = type_unite(us)
    type_c = type_unite(uc)

    # Même type → conversion directe
    if type_s == type_c == TypeUnite.VOLUME:
        factor_s = VOLUME_VERS_ML.get(us)
        factor_c = VOLUME_VERS_ML.get(uc)
        if factor_s is not None and factor_c is not None:
            ml = valeur * factor_s
            resultat = ml / factor_c
            return ResultatConversion(valeur, unite_source, round(resultat, 2), unite_cible)

    if type_s == type_c == TypeUnite.POIDS:
        factor_s = POIDS_VERS_G.get(us)
        factor_c = POIDS_VERS_G.get(uc)
        if factor_s is not None and factor_c is not None:
            g = valeur * factor_s
            resultat = g / factor_c
            return ResultatConversion(valeur, unite_source, round(resultat, 2), unite_cible)

    # Volume ↔ Poids (nécessite ingrédient)
    if ingredient and type_s != type_c:
        ingredient_lower = ingredient.lower()
        densite = _trouver_densite(ingredient_lower)

        if densite is not None:
            if type_s == TypeUnite.VOLUME and type_c == TypeUnite.POIDS:
                factor_s = VOLUME_VERS_ML.get(us)
                factor_c = POIDS_VERS_G.get(uc)
                if factor_s is not None and factor_c is not None:
                    ml = valeur * factor_s
                    g = ml * densite
                    resultat = g / factor_c
                    return ResultatConversion(
                        valeur, unite_source, round(resultat, 2), unite_cible, approximation=True
                    )

            if type_s == TypeUnite.POIDS and type_c == TypeUnite.VOLUME:
                factor_s = POIDS_VERS_G.get(us)
                factor_c = VOLUME_VERS_ML.get(uc)
                if factor_s is not None and factor_c is not None:
                    g = valeur * factor_s
                    ml = g / densite
                    resultat = ml / factor_c
                    return ResultatConversion(
                        valeur, unite_source, round(resultat, 2), unite_cible, approximation=True
                    )

    return None


def _trouver_densite(ingredient: str) -> float | None:
    """Trouve la densité pour un ingrédient (recherche partielle)."""
    # Exact
    if ingredient in DENSITES:
        return DENSITES[ingredient]
    # Partiel
    for nom, d in DENSITES.items():
        if nom in ingredient or ingredient in nom:
            return d
    return None


def convertir_texte(texte_quantite: str, unite_cible: str, ingredient: str | None = None) -> str:
    """
    Convertit un texte de quantité (ex: "2 cups") vers une unité cible.

    Args:
        texte_quantite: Ex: "2 cups", "500g", "3 c.à.s"
        unite_cible: Unité souhaitée
        ingredient: Nom de l'ingrédient (optionnel)

    Returns:
        Texte converti ou le texte original si impossible
    """
    import re

    # Parser "valeur unite" — gère "2.5 cups", "500g", "3 c.à.s"
    match = re.match(r"([\d.,]+)\s*(.+)", texte_quantite.strip())
    if not match:
        return texte_quantite

    try:
        valeur = float(match.group(1).replace(",", "."))
    except ValueError:
        return texte_quantite

    unite_source = match.group(2).strip()
    resultat = convertir(valeur, unite_source, unite_cible, ingredient)

    if resultat:
        approx = " (≈)" if resultat.approximation else ""
        return f"{resultat.valeur_cible} {unite_cible}{approx}"

    return texte_quantite


def lister_unites_disponibles() -> dict[str, list[str]]:
    """Retourne les unités disponibles par catégorie."""
    return {
        "volume": sorted(set(VOLUME_VERS_ML.keys())),
        "poids": sorted(set(POIDS_VERS_G.keys())),
        "pièce": sorted(UNITES_PIECES),
    }


__all__ = [
    "TypeUnite",
    "ResultatConversion",
    "VOLUME_VERS_ML",
    "POIDS_VERS_G",
    "DENSITES",
    "convertir",
    "convertir_texte",
    "normaliser_unite",
    "type_unite",
    "lister_unites_disponibles",
]
