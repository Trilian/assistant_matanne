"""
Fonctions utilitaires de filtrage et recherche pour les recettes.

Filtrage par temps, difficulté, type, saison et recherche textuelle.
"""

from .utils_calcul import calculer_temps_total

# ═══════════════════════════════════════════════════════════
# FILTRES
# ═══════════════════════════════════════════════════════════


def filtrer_recettes_par_temps(
    recettes: list[dict],
    temps_max: int,
) -> list[dict]:
    """Filtre les recettes par temps total maximum.

    Args:
        recettes: Liste de recettes
        temps_max: Temps maximum en minutes

    Returns:
        Recettes dont le temps total <= temps_max
    """
    return [
        r
        for r in recettes
        if calculer_temps_total(
            r.get("temps_preparation", 0),
            r.get("temps_cuisson", 0),
        )
        <= temps_max
    ]


def filtrer_recettes_par_difficulte(
    recettes: list[dict],
    difficulte: str,
) -> list[dict]:
    """Filtre les recettes par niveau de difficulté.

    Args:
        recettes: Liste de recettes
        difficulte: Niveau de difficulté voulu

    Returns:
        Recettes avec cette difficulté
    """
    return [r for r in recettes if r.get("difficulte") == difficulte]


def filtrer_recettes_par_type(
    recettes: list[dict],
    type_repas: str,
) -> list[dict]:
    """Filtre les recettes par type de repas.

    Args:
        recettes: Liste de recettes
        type_repas: Type de repas voulu

    Returns:
        Recettes de ce type
    """
    return [r for r in recettes if r.get("type_repas") == type_repas]


def filtrer_recettes_par_saison(
    recettes: list[dict],
    saison: str,
) -> list[dict]:
    """Filtre les recettes par saison.

    Args:
        recettes: Liste de recettes
        saison: Saison voulue

    Returns:
        Recettes adaptées à cette saison ou toute_année
    """
    return [r for r in recettes if r.get("saison") in [saison, "toute_année"]]


# ═══════════════════════════════════════════════════════════
# RECHERCHE
# ═══════════════════════════════════════════════════════════


def rechercher_par_nom(
    recettes: list[dict],
    terme: str,
) -> list[dict]:
    """Recherche des recettes par nom.

    Args:
        recettes: Liste de recettes
        terme: Terme de recherche (insensible à la casse)

    Returns:
        Recettes dont le nom contient le terme
    """
    terme_lower = terme.lower()
    return [r for r in recettes if terme_lower in r.get("nom", "").lower()]


def rechercher_par_ingredient(
    recettes: list[dict],
    ingredient: str,
) -> list[dict]:
    """Recherche des recettes contenant un ingrédient.

    Args:
        recettes: Liste de recettes
        ingredient: Nom de l'ingrédient (insensible à la casse)

    Returns:
        Recettes contenant cet ingrédient
    """
    ingredient_lower = ingredient.lower()
    result = []

    for r in recettes:
        for ing in r.get("ingredients", []):
            if ingredient_lower in ing.get("nom", "").lower():
                result.append(r)
                break

    return result


__all__ = [
    "filtrer_recettes_par_temps",
    "filtrer_recettes_par_difficulte",
    "filtrer_recettes_par_type",
    "filtrer_recettes_par_saison",
    "rechercher_par_nom",
    "rechercher_par_ingredient",
]
