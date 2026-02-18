"""
Logique d'équilibre nutritionnel pour le planning des repas.

Contient les règles et calculs pour:
- Détermination du type de protéine par jour
- Calcul de l'équilibre hebdomadaire
- Vérification du respect des recommandations nutritionnelles
"""

from src.core.constants import TYPES_PROTEINES


def determine_protein_type(
    jour_lower: str,
    poisson_jours: list[str],
    viande_rouge_jours: list[str],
    vegetarien_jours: list[str],
) -> tuple[str, str]:
    """
    Détermine le type de protéine pour un jour donné selon les paramètres.

    Args:
        jour_lower: Nom du jour en minuscules
        poisson_jours: Liste des jours poisson
        viande_rouge_jours: Liste des jours viande rouge
        vegetarien_jours: Liste des jours végétariens

    Returns:
        Tuple (type_proteine, raison_emoji)

    Examples:
        >>> determine_protein_type('lundi', ['lundi'], [], [])
        ('poisson', '🐟 Jour poisson')
        >>> determine_protein_type('mercredi', [], [], ['mercredi'])
        ('vegetarien', '🥬 Jour végétarien')
    """
    if jour_lower in [j.lower() for j in poisson_jours]:
        return "poisson", "🐟 Jour poisson"
    elif jour_lower in [j.lower() for j in viande_rouge_jours]:
        return "viande_rouge", "🥩 Jour viande rouge"
    elif jour_lower in [j.lower() for j in vegetarien_jours]:
        return "vegetarien", "🥬 Jour végétarien"
    else:
        return "volaille", "🍗 Jour volaille"


def get_default_protein_schedule() -> dict[str, str]:
    """
    Retourne le planning de protéines par défaut.

    Returns:
        Dict {jour: type_proteine}

    Examples:
        >>> schedule = get_default_protein_schedule()
        >>> schedule['lundi']
        'poisson'
    """
    return {
        "lundi": "poisson",
        "mardi": "viande_rouge",
        "mercredi": "vegetarien",
        "jeudi": "poisson",
        "vendredi": "volaille",
        "samedi": "volaille",
        "dimanche": "viande_rouge",
    }


def calculate_week_balance(repas_list: list[dict]) -> dict:
    """
    Calcule l'équilibre nutritionnel de la semaine.

    Args:
        repas_list: Liste de dicts {type_proteines, ...}

    Returns:
        Dict avec comptage par type de protéine

    Examples:
        >>> repas = [{'type_proteines': 'poisson'}, {'type_proteines': 'volaille'}]
        >>> balance = calculate_week_balance(repas)
        >>> balance['poisson']
        1
    """
    balance = {
        "poisson": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
        "autre": 0,
    }

    for repas in repas_list:
        protein = repas.get("type_proteines", "autre")
        if protein:
            protein_lower = protein.lower()

            # Mapper aux catégories
            found = False
            for category, keywords in TYPES_PROTEINES.items():
                if any(kw in protein_lower for kw in keywords):
                    balance[category] += 1
                    found = True
                    break

            if not found:
                balance["autre"] += 1

    return balance


def is_balanced_week(repas_list: list[dict]) -> tuple[bool, list[str]]:
    """
    Vérifie si la semaine est équilibrée.

    Critères:
    - Au moins 2 repas poisson
    - Maximum 2 repas viande rouge
    - Au moins 1 repas végétarien

    Args:
        repas_list: Liste de dicts avec type_proteines

    Returns:
        Tuple (is_balanced, list_of_issues)

    Examples:
        >>> repas = [{'type_proteines': 'poisson'}] * 3 + [{'type_proteines': 'légumes'}]
        >>> balanced, issues = is_balanced_week(repas)
        >>> balanced
        True
    """
    balance = calculate_week_balance(repas_list)
    issues = []

    if balance["poisson"] < 2:
        issues.append(f"Pas assez de poisson ({balance['poisson']}/2 min)")

    if balance["viande_rouge"] > 2:
        issues.append(f"Trop de viande rouge ({balance['viande_rouge']}/2 max)")

    if balance["vegetarien"] < 1:
        issues.append("Pas de repas végétarien")

    return len(issues) == 0, issues


__all__ = [
    "determine_protein_type",
    "get_default_protein_schedule",
    "calculate_week_balance",
    "is_balanced_week",
]
