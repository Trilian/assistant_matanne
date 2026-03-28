"""
Logique d'équilibre nutritionnel pour le planning des repas.

Contient les règles et calculs pour:
- Détermination du type de protéine par jour
- Calcul de l'équilibre hebdomadaire (poisson blanc/gras, vegan, viande rouge)
- Vérification du respect des recommandations nutritionnelles
"""

from src.core.constants import TYPES_PROTEINES

# Mots-clés spécifiques pour la classification poisson blanc / gras
_POISSON_BLANC = {"cabillaud", "merlu", "colin", "sole", "bar", "daurade", "lieu", "lotte"}
_POISSON_GRAS = {"saumon", "thon", "sardine", "maquereau", "hareng", "truite", "anchois"}


def _classifier_poisson(protein_lower: str) -> str:
    """Classifie un poisson en blanc ou gras. Défaut: poisson_blanc."""
    if any(mot in protein_lower for mot in _POISSON_GRAS):
        return "poisson_gras"
    if any(mot in protein_lower for mot in _POISSON_BLANC):
        return "poisson_blanc"
    # "poisson" générique ou "crevette" → poisson_blanc par défaut
    return "poisson_blanc"


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
        poisson_jours: Liste des jours poisson (blanc + gras confondus)
        viande_rouge_jours: Liste des jours viande rouge
        vegetarien_jours: Liste des jours végétariens

    Returns:
        Tuple (type_proteine, raison_emoji)
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
    """
    return {
        "lundi": "poisson",
        "mardi": "viande_rouge",
        "mercredi": "vegetarien",
        "jeudi": "poisson",
        "vendredi": "volaille",
        "samedi": "volaille",
        "dimanche": "volaille",
    }


def calculate_week_balance(repas_list: list[dict]) -> dict:
    """
    Calcule l'équilibre nutritionnel de la semaine.

    Distingue poisson_blanc et poisson_gras.

    Args:
        repas_list: Liste de dicts {type_proteines, ...}

    Returns:
        Dict avec comptage par type de protéine
    """
    balance = {
        "poisson": 0,
        "poisson_blanc": 0,
        "poisson_gras": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
        "autre": 0,
    }

    for repas in repas_list:
        protein = repas.get("type_proteines", "autre")
        if protein is None:
            # Compatibilité test legacy: None est ignoré (pas compté en "autre")
            continue
        if not protein:
            balance["autre"] += 1
            continue

        protein_lower = protein.lower()

        # Vérifier d'abord si c'est un poisson (avant les catégories génériques)
        is_fish = False
        for cat in ("poisson_blanc", "poisson_gras", "poisson"):
            keywords = TYPES_PROTEINES.get(cat, [])
            if any(kw in protein_lower for kw in keywords):
                is_fish = True
                break

        if is_fish:
            fish_type = _classifier_poisson(protein_lower)
            balance[fish_type] += 1
            balance["poisson"] += 1
            continue

        # Autres catégories (viande_rouge, volaille, vegetarien)
        found = False
        for category in ("viande_rouge", "volaille", "vegetarien"):
            keywords = TYPES_PROTEINES.get(category, [])
            if any(kw in protein_lower for kw in keywords):
                balance[category] += 1
                found = True
                break

        if not found:
            balance["autre"] += 1

    return balance


def is_balanced_week(
    repas_list: list[dict],
    poisson_blanc_cible: int = 1,
    poisson_gras_cible: int = 1,
    vegetarien_max: int = 2,
    viande_rouge_max: int = 2,
) -> tuple[bool, list[str]]:
    """
    Vérifie si la semaine est équilibrée.

    Critères paramétrables basés sur les préférences utilisateur.

    Args:
        repas_list: Liste de dicts avec type_proteines
        poisson_blanc_cible: Nombre cible de repas poisson blanc
        poisson_gras_cible: Nombre cible de repas poisson gras
        vegetarien_max: Nombre maximum de repas végétariens
        viande_rouge_max: Nombre maximum de repas viande rouge

    Returns:
        Tuple (is_balanced, list_of_issues)
    """
    balance = calculate_week_balance(repas_list)
    issues = []

    poisson_cible_total = poisson_blanc_cible + poisson_gras_cible
    if balance["poisson"] < poisson_cible_total:
        issues.append(f"Pas assez de poisson ({balance['poisson']}/{poisson_cible_total})")

    if balance["viande_rouge"] > viande_rouge_max:
        issues.append(
            f"Trop de viande rouge ({balance['viande_rouge']}/{viande_rouge_max} max)"
        )

    if balance["vegetarien"] > vegetarien_max:
        issues.append(
            f"Trop de repas végétariens ({balance['vegetarien']}/{vegetarien_max} max)"
        )

    if balance["vegetarien"] < 1:
        issues.append("Pas de repas végétarien")

    # Variété intra-catégorie (batch-friendly: seulement si ≥2x dans la catégorie)
    variety_issues = check_intra_category_variety(repas_list)
    issues.extend(variety_issues)

    return len(issues) == 0, issues


def check_intra_category_variety(repas_list: list[dict]) -> list[str]:
    """Vérifie la variété au sein de chaque catégorie de protéines.

    Règles batch-friendly:
    - Si catégorie n'apparaît qu'1x → pas de contrainte
    - Si catégorie apparaît ≥2x → max 2x la même source (ex: 2 poulet + 1 dinde OK, 3 poulet KO)

    Args:
        repas_list: Liste de dicts avec type_proteines

    Returns:
        Liste de messages d'alerte
    """
    from collections import Counter

    issues = []
    # Grouper les sources brutes par catégorie
    category_sources: dict[str, list[str]] = {}

    for repas in repas_list:
        protein = repas.get("type_proteines", "")
        if not protein:
            continue
        protein_lower = protein.lower()

        # Déterminer la catégorie
        category = "autre"
        for cat_name, keywords in TYPES_PROTEINES.items():
            if any(kw in protein_lower for kw in keywords):
                category = cat_name
                break

        if category == "autre":
            continue

        if category not in category_sources:
            category_sources[category] = []
        category_sources[category].append(protein_lower)

    # Vérifier chaque catégorie
    _labels = {
        "volaille": "volaille",
        "viande_rouge": "viande rouge",
        "poisson_blanc": "poisson blanc",
        "poisson_gras": "poisson gras",
        "vegetarien": "végétarien",
    }
    for category, sources in category_sources.items():
        if len(sources) < 2:
            continue  # Pas de contrainte si 1 seul repas

        counts = Counter(sources)
        for source, count in counts.items():
            if count > 2:
                label = _labels.get(category, category)
                issues.append(
                    f"Trop de {source} ({count}x) dans la catégorie {label} — varier les sources"
                )

    return issues


__all__ = [
    "determine_protein_type",
    "get_default_protein_schedule",
    "calculate_week_balance",
    "is_balanced_week",
    "check_intra_category_variety",
]
