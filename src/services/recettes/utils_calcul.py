"""
Fonctions utilitaires de calcul pour les recettes.

Temps, quantités, statistiques et scoring.
"""

from .utils import ROBOTS_COMPATIBLES

# ═══════════════════════════════════════════════════════════
# CALCULS DE TEMPS
# ═══════════════════════════════════════════════════════════


def calculer_temps_total(temps_preparation: int, temps_cuisson: int) -> int:
    """Calcule le temps total de la recette.

    Args:
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes

    Returns:
        Temps total en minutes
    """
    return temps_preparation + temps_cuisson


def estimer_temps_robot(
    temps_cuisson: int,
    robot_type: str,
) -> int:
    """Estime le temps de cuisson adapté pour un robot.

    Args:
        temps_cuisson: Temps de cuisson original
        robot_type: Type de robot culinaire

    Returns:
        Temps de cuisson estimé pour le robot
    """
    info = ROBOTS_COMPATIBLES.get(robot_type, {"temps_reduction": 1.0})
    reduction = info.get("temps_reduction", 1.0)
    return int(temps_cuisson * reduction)


def formater_temps(minutes: int) -> str:
    """Formate une durée en minutes en format lisible.

    Args:
        minutes: Durée en minutes

    Returns:
        Format "Xh Ymin" ou "Ymin"
    """
    if minutes < 60:
        return f"{minutes}min"

    heures = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{heures}h"
    return f"{heures}h {mins}min"


# ═══════════════════════════════════════════════════════════
# AJUSTEMENT DES PORTIONS
# ═══════════════════════════════════════════════════════════


def ajuster_quantite_ingredient(
    quantite_base: float,
    portions_base: int,
    portions_cible: int,
) -> float:
    """Ajuste la quantité d'un ingrédient pour un nombre de portions différent.

    Args:
        quantite_base: Quantité originale
        portions_base: Nombre de portions originales
        portions_cible: Nombre de portions voulues

    Returns:
        Quantité ajustée
    """
    if portions_base <= 0:
        return quantite_base

    ratio = portions_cible / portions_base
    return round(quantite_base * ratio, 2)


def ajuster_ingredients(
    ingredients: list[dict],
    portions_base: int,
    portions_cible: int,
) -> list[dict]:
    """Ajuste tous les ingrédients pour un nombre de portions différent.

    Args:
        ingredients: Liste des ingrédients avec quantite
        portions_base: Nombre de portions originales
        portions_cible: Nombre de portions voulues

    Returns:
        Liste des ingrédients ajustés
    """
    if portions_base == portions_cible:
        return ingredients

    ajustes = []
    for ing in ingredients:
        ajuste = ing.copy()
        if "quantite" in ajuste:
            ajuste["quantite"] = ajuster_quantite_ingredient(
                ajuste["quantite"],
                portions_base,
                portions_cible,
            )
        ajustes.append(ajuste)

    return ajustes


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_stats_recettes(recettes: list[dict]) -> dict:
    """Calcule des statistiques sur une collection de recettes.

    Args:
        recettes: Liste de recettes

    Returns:
        Dictionnaire de statistiques
    """
    if not recettes:
        return {
            "total": 0,
            "temps_moyen_preparation": 0,
            "temps_moyen_cuisson": 0,
            "temps_moyen_total": 0,
            "par_difficulte": {},
            "par_type": {},
            "par_saison": {},
        }

    temps_prep = [r.get("temps_preparation", 0) for r in recettes]
    temps_cuisson = [r.get("temps_cuisson", 0) for r in recettes]
    temps_totaux = [
        calculer_temps_total(r.get("temps_preparation", 0), r.get("temps_cuisson", 0))
        for r in recettes
    ]

    # Comptage par catégorie
    par_difficulte = {}
    par_type = {}
    par_saison = {}

    for r in recettes:
        diff = r.get("difficulte", "inconnu")
        par_difficulte[diff] = par_difficulte.get(diff, 0) + 1

        type_r = r.get("type_repas", "inconnu")
        par_type[type_r] = par_type.get(type_r, 0) + 1

        saison = r.get("saison", "inconnu")
        par_saison[saison] = par_saison.get(saison, 0) + 1

    return {
        "total": len(recettes),
        "temps_moyen_preparation": sum(temps_prep) / len(temps_prep),
        "temps_moyen_cuisson": sum(temps_cuisson) / len(temps_cuisson),
        "temps_moyen_total": sum(temps_totaux) / len(temps_totaux),
        "par_difficulte": par_difficulte,
        "par_type": par_type,
        "par_saison": par_saison,
    }


def calculer_score_recette(
    recette: dict,
    criteres: dict | None = None,
) -> float:
    """Calcule un score de pertinence pour une recette.

    Args:
        recette: Dictionnaire recette
        criteres: Critères de scoring {temps_max, difficulte_preferee, etc}

    Returns:
        Score de 0 à 100
    """
    score = 50.0  # Base

    if criteres is None:
        return score

    # Bonus pour temps < temps_max
    if "temps_max" in criteres:
        temps_total = calculer_temps_total(
            recette.get("temps_preparation", 0),
            recette.get("temps_cuisson", 0),
        )
        if temps_total <= criteres["temps_max"]:
            score += 20

    # Bonus pour difficulté préférée
    if "difficulte_preferee" in criteres:
        if recette.get("difficulte") == criteres["difficulte_preferee"]:
            score += 15

    # Bonus pour type de repas
    if "type_repas" in criteres:
        if recette.get("type_repas") == criteres["type_repas"]:
            score += 10

    # Bonus pour saison actuelle
    if "saison" in criteres:
        saison_recette = recette.get("saison", "")
        if saison_recette == criteres["saison"] or saison_recette == "toute_année":
            score += 5

    return min(100.0, score)


__all__ = [
    "calculer_temps_total",
    "estimer_temps_robot",
    "formater_temps",
    "ajuster_quantite_ingredient",
    "ajuster_ingredients",
    "calculer_stats_recettes",
    "calculer_score_recette",
]
