"""
Formatage pour l'affichage des plannings.

Contient les fonctions pour:
- Formatage des repas pour l'UI
- Génération de résumés
- Groupement des données
"""


def format_meal_for_display(repas: dict) -> dict:
    """
    Formate un repas pour l'affichage dans l'UI.

    Args:
        repas: Dict avec id, type_repas, recette_nom, etc.

    Returns:
        Dict formaté pour l'affichage

    Examples:
        >>> repas = {'id': 1, 'type_repas': 'dejeuner', 'recette_nom': 'Pâtes'}
        >>> formatted = format_meal_for_display(repas)
        >>> formatted['display_type']
        'Déjeuner'
    """
    type_repas = repas.get("type_repas", "")

    # Capitaliser le type
    display_type = type_repas.replace("-", " ").replace("_", " ").title()

    # Emoji par type
    emoji_map = {
        "petit-dejeuner": "🌅",
        "dejeuner": "☀️",
        "gouter": "🍪",
        "diner": "🌙",
    }
    emoji = emoji_map.get(type_repas.lower().replace(" ", "-"), "🍽️")

    return {
        "id": repas.get("id"),
        "display_type": display_type,
        "emoji": emoji,
        "recette_nom": repas.get("recette_nom", repas.get("notes", "Non défini")),
        "recette_id": repas.get("recette_id"),
        "prepare": repas.get("prepare", False),
        "notes": repas.get("notes", ""),
    }


def format_planning_summary(planning_data: dict) -> str:
    """
    Génère un résumé textuel du planning.

    Args:
        planning_data: Dict complet du planning

    Returns:
        Résumé formaté

    Examples:
        >>> data = {'nom': 'Planning 15/01', 'repas_par_jour': {'2024-01-15': [1,2]}}
        >>> summary = format_planning_summary(data)
        >>> 'Planning 15/01' in summary
        True
    """
    nom = planning_data.get("nom", "Planning")
    repas_par_jour = planning_data.get("repas_par_jour", {})

    total_repas = sum(len(repas) for repas in repas_par_jour.values())
    jours_remplis = len([j for j, r in repas_par_jour.items() if r])

    return f"{nom} - {jours_remplis} jours, {total_repas} repas"


def group_meals_by_type(repas_list: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les repas par type.

    Args:
        repas_list: Liste de repas

    Returns:
        Dict {type_repas: [repas]}

    Examples:
        >>> meals = [{'type_repas': 'dejeuner'}, {'type_repas': 'diner'}]
        >>> grouped = group_meals_by_type(meals)
        >>> len(grouped['dejeuner'])
        1
    """
    grouped = {}

    for repas in repas_list:
        type_repas = repas.get("type_repas", "autre")
        if type_repas not in grouped:
            grouped[type_repas] = []
        grouped[type_repas].append(repas)

    return grouped


__all__ = [
    "format_meal_for_display",
    "format_planning_summary",
    "group_meals_by_type",
]
