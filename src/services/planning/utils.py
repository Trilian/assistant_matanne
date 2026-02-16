"""
Fonctions utilitaires pures pour le service de planning.

Ces fonctions peuvent être testées sans base de données ni dépendances externes.
Elles représentent la logique métier pure extraite du planning.
"""

from datetime import date, datetime, timedelta

from src.modules.shared.constantes import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_LOWER,
    TYPES_PROTEINES,
)

# ═══════════════════════════════════════════════════════════
# DATES ET CALENDRIER
# ═══════════════════════════════════════════════════════════


def get_weekday_names() -> list[str]:
    """
    Retourne la liste des noms de jours de la semaine.

    Returns:
        Liste des jours en français avec majuscule

    Examples:
        >>> get_weekday_names()[0]
        'Lundi'
        >>> len(get_weekday_names())
        7
    """
    return JOURS_SEMAINE.copy()


def get_weekday_name(day_index: int) -> str:
    """
    Retourne le nom du jour pour un index donné.

    Args:
        day_index: Index du jour (0=Lundi, 6=Dimanche)

    Returns:
        Nom du jour

    Examples:
        >>> get_weekday_name(0)
        'Lundi'
        >>> get_weekday_name(4)
        'Vendredi'
    """
    if 0 <= day_index <= 6:
        return JOURS_SEMAINE[day_index]
    return ""


def get_weekday_index(day_name: str) -> int:
    """
    Retourne l'index d'un jour de la semaine.

    Args:
        day_name: Nom du jour (insensible à la casse)

    Returns:
        Index (0-6) ou -1 si non trouvé

    Examples:
        >>> get_weekday_index('Lundi')
        0
        >>> get_weekday_index('vendredi')
        4
    """
    try:
        return JOURS_SEMAINE_LOWER.index(day_name.lower())
    except ValueError:
        return -1


def calculate_week_dates(semaine_debut: date) -> list[date]:
    """
    Calcule les dates de chaque jour de la semaine.

    Args:
        semaine_debut: Date du lundi (début de semaine)

    Returns:
        Liste de 7 dates (lundi à dimanche)

    Examples:
        >>> from datetime import date
        >>> dates = calculate_week_dates(date(2024, 1, 15))  # Lundi
        >>> len(dates)
        7
        >>> dates[6] - dates[0]
        timedelta(days=6)
    """
    return [semaine_debut + timedelta(days=i) for i in range(7)]


def get_week_range(semaine_debut: date) -> tuple[date, date]:
    """
    Retourne les dates de début et fin de semaine.

    Args:
        semaine_debut: Date du lundi

    Returns:
        Tuple (lundi, dimanche)

    Examples:
        >>> start, end = get_week_range(date(2024, 1, 15))
        >>> (end - start).days
        6
    """
    return semaine_debut, semaine_debut + timedelta(days=6)


def get_monday_of_week(dt: date | datetime) -> date:
    """
    Retourne le lundi de la semaine contenant la date.

    Args:
        dt: Date ou datetime

    Returns:
        Date du lundi

    Examples:
        >>> get_monday_of_week(date(2024, 1, 18))  # Jeudi
        date(2024, 1, 15)  # Lundi
    """
    if isinstance(dt, datetime):
        dt = dt.date()

    # weekday(): 0=lundi, 6=dimanche
    return dt - timedelta(days=dt.weekday())


def format_week_label(semaine_debut: date, semaine_fin: date | None = None) -> str:
    """
    Formate un label pour afficher la semaine.

    Args:
        semaine_debut: Date du lundi
        semaine_fin: Date du dimanche (optionnel)

    Returns:
        Label formaté

    Examples:
        >>> format_week_label(date(2024, 1, 15))
        'Semaine du 15/01/2024'
    """
    if semaine_fin is None:
        semaine_fin = semaine_debut + timedelta(days=6)

    return f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}"


# ═══════════════════════════════════════════════════════════
# ÉQUILIBRE NUTRITIONNEL
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# FORMATAGE ET AFFICHAGE
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES COURSES
# ═══════════════════════════════════════════════════════════


def aggregate_ingredients(ingredients_list: list[dict]) -> dict[str, dict]:
    """
    Agrège les quantités d'ingrédients identiques.

    Args:
        ingredients_list: Liste de dicts {nom, quantite, unite, rayon}

    Returns:
        Dict {nom: {quantite, unite, rayon, count}}

    Examples:
        >>> ings = [
        ...     {'nom': 'Tomate', 'quantite': 2, 'unite': 'pcs'},
        ...     {'nom': 'Tomate', 'quantite': 3, 'unite': 'pcs'}
        ... ]
        >>> agg = aggregate_ingredients(ings)
        >>> agg['Tomate']['quantite']
        5
    """
    aggregated = {}

    for ing in ingredients_list:
        nom = ing.get("nom", "")
        if not nom:
            continue

        quantite = ing.get("quantite", 1) or 1
        unite = ing.get("unite", "pcs")
        rayon = ing.get("rayon", ing.get("categorie", "autre"))

        if nom not in aggregated:
            aggregated[nom] = {
                "nom": nom,
                "quantite": quantite,
                "unite": unite,
                "rayon": rayon,
                "count": 1,
            }
        else:
            # Même unité: additionner
            if aggregated[nom]["unite"] == unite:
                aggregated[nom]["quantite"] += quantite
            aggregated[nom]["count"] += 1

    return aggregated


def sort_ingredients_by_rayon(ingredients: dict[str, dict] | list[dict]) -> list[dict]:
    """
    Trie les ingrédients par rayon puis par quantité.

    Args:
        ingredients: Dict ou liste d'ingrédients

    Returns:
        Liste triée

    Examples:
        >>> ings = {'Tomate': {'rayon': 'legumes', 'quantite': 5}}
        >>> sorted_ings = sort_ingredients_by_rayon(ings)
        >>> sorted_ings[0]['nom']
        'Tomate'
    """
    if isinstance(ingredients, dict):
        items = list(ingredients.values())
    else:
        items = ingredients

    return sorted(items, key=lambda x: (x.get("rayon", "zzz"), -x.get("quantite", 0)))


def get_rayon_order() -> list[str]:
    """
    Retourne l'ordre des rayons en supermarché.

    Returns:
        Liste ordonnée des rayons
    """
    return [
        "fruits_legumes",
        "legumes",
        "fruits",
        "boucherie",
        "poissonnerie",
        "charcuterie",
        "cremerie",
        "epicerie",
        "conserves",
        "surgeles",
        "boissons",
        "hygiene",
        "autre",
    ]


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def validate_planning_dates(semaine_debut: date, semaine_fin: date) -> tuple[bool, str]:
    """
    Valide les dates d'un planning.

    Args:
        semaine_debut: Date de début
        semaine_fin: Date de fin

    Returns:
        Tuple (is_valid, error_message)

    Examples:
        >>> validate_planning_dates(date(2024, 1, 15), date(2024, 1, 21))
        (True, '')
    """
    if semaine_fin < semaine_debut:
        return False, "La date de fin doit être après la date de début"

    diff = (semaine_fin - semaine_debut).days
    if diff != 6:
        return False, f"Un planning doit couvrir exactement 7 jours (trouvé: {diff + 1})"

    # Vérifier que c'est un lundi
    if semaine_debut.weekday() != 0:
        return False, "La semaine doit commencer un lundi"

    return True, ""


def validate_meal_selection(
    selection: dict[str, int], available_recipes: list[int]
) -> tuple[bool, list[str]]:
    """
    Valide la sélection de recettes pour un planning.

    Args:
        selection: Dict {jour_index: recette_id}
        available_recipes: Liste des IDs de recettes disponibles

    Returns:
        Tuple (is_valid, list_of_errors)

    Examples:
        >>> validate_meal_selection({'jour_0': 1, 'jour_1': 2}, [1, 2, 3])
        (True, [])
    """
    errors = []

    for jour_key, recette_id in selection.items():
        if recette_id not in available_recipes:
            errors.append(f"Recette {recette_id} non trouvée pour {jour_key}")

    return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE PROMPT IA
# ═══════════════════════════════════════════════════════════


def build_planning_prompt_context(
    semaine_debut: date, preferences: dict | None = None, constraints: list[str] | None = None
) -> str:
    """
    Construit le contexte pour le prompt de génération IA.

    Args:
        semaine_debut: Date de début
        preferences: Préférences utilisateur
        constraints: Contraintes supplémentaires

    Returns:
        Contexte formaté pour le prompt
    """
    prefs = preferences or {}
    consts = constraints or []

    lines = [
        f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
        "Durée: 7 jours (Lundi à Dimanche)",
    ]

    if prefs.get("nb_personnes"):
        lines.append(f"Nombre de personnes: {prefs['nb_personnes']}")

    if prefs.get("budget"):
        lines.append(f"Budget: {prefs['budget']}")

    if prefs.get("allergies"):
        lines.append(f"Allergies: {', '.join(prefs['allergies'])}")

    if prefs.get("preferences_cuisine"):
        lines.append(f"Préférences: {', '.join(prefs['preferences_cuisine'])}")

    for constraint in consts:
        lines.append(f"Contrainte: {constraint}")

    return "\n".join(lines)


def parse_ai_planning_response(response: list[dict]) -> list[dict]:
    """
    Parse et valide la réponse de l'IA pour le planning.

    Args:
        response: Liste de dicts {jour, dejeuner, diner}

    Returns:
        Liste validée et normalisée

    Examples:
        >>> resp = [{'jour': 'Lundi', 'dejeuner': 'Pâtes', 'diner': 'Salade'}]
        >>> parsed = parse_ai_planning_response(resp)
        >>> parsed[0]['jour']
        'Lundi'
    """
    parsed = []

    for item in response:
        jour = item.get("jour", "")

        # Valider le jour
        if jour not in JOURS_SEMAINE:
            # Tenter de normaliser
            for j in JOURS_SEMAINE:
                if j.lower() == jour.lower():
                    jour = j
                    break

        parsed.append(
            {
                "jour": jour,
                "dejeuner": item.get("dejeuner", "Non défini"),
                "diner": item.get("diner", "Non défini"),
            }
        )

    return parsed


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Dates
    "get_weekday_names",
    "get_weekday_name",
    "get_weekday_index",
    "calculate_week_dates",
    "get_week_range",
    "get_monday_of_week",
    "format_week_label",
    # Équilibre
    "determine_protein_type",
    "get_default_protein_schedule",
    "calculate_week_balance",
    "is_balanced_week",
    # Formatage
    "format_meal_for_display",
    "format_planning_summary",
    "group_meals_by_type",
    # Courses
    "aggregate_ingredients",
    "sort_ingredients_by_rayon",
    "get_rayon_order",
    # Validation
    "validate_planning_dates",
    "validate_meal_selection",
    # IA
    "build_planning_prompt_context",
    "parse_ai_planning_response",
]
