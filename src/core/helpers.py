"""
Helpers centralisés - Manipulation de données, statistiques, strings.

Ce module consolide les fonctions utilitaires précédemment dans:
- utils/helpers/data.py
- utils/helpers/food.py
- utils/helpers/stats.py
- utils/helpers/strings.py

Note: Les fonctions de dates sont dans core/date_utils.py

Usage:
    from src.core.helpers import grouper_par, calculer_moyenne, generer_id
"""

import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from collections.abc import Callable
from typing import Any

# ═══════════════════════════════════════════════════════════
# MANIPULATION DE DONNÉES
# ═══════════════════════════════════════════════════════════


def obtenir_securise(data: dict, *keys, default=None) -> Any:
    """
    Récupère valeur nested avec fallback.

    Examples:
        >>> obtenir_securise({"a": {"b": {"c": 1}}}, "a", "b", "c")
        1
        >>> obtenir_securise({"a": 1}, "b", "c", default=0)
        0
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result


def grouper_par(items: list[dict], key: str) -> dict[Any, list[dict]]:
    """
    Regroupe items par clé.

    Examples:
        >>> items = [{"type": "A", "val": 1}, {"type": "A", "val": 2}]
        >>> grouper_par(items, "type")
        {"A": [{"type": "A", "val": 1}, {"type": "A", "val": 2}]}
    """
    grouped = defaultdict(list)
    for item in items:
        group_key = item.get(key)
        grouped[group_key].append(item)
    return dict(grouped)


def compter_par(items: list[dict], key: str) -> dict[Any, int]:
    """
    Compte items par clé.

    Examples:
        >>> items = [{"type": "A"}, {"type": "A"}, {"type": "B"}]
        >>> compter_par(items, "type")
        {"A": 2, "B": 1}
    """
    return dict(Counter(item.get(key) for item in items))


def dedupliquer(items: list[Any], key: Callable | None = None) -> list[Any]:
    """
    Déduplique une liste.

    Examples:
        >>> dedupliquer([1, 2, 2, 3])
        [1, 2, 3]
        >>> dedupliquer([{"id": 1}, {"id": 1}], key=lambda x: x["id"])
        [{"id": 1}]
    """
    if not key:
        return list(dict.fromkeys(items))

    seen = set()
    result = []
    for item in items:
        item_key = key(item)
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    return result


def aplatir(nested_list: list[list[Any]]) -> list[Any]:
    """
    Aplatit une liste de listes.

    Examples:
        >>> aplatir([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested_list for item in sublist]


def partitionner(items: list[Any], predicate: Callable) -> tuple[list[Any], list[Any]]:
    """
    Partitionne liste selon prédicat.

    Returns:
        (items_matching, items_not_matching)

    Examples:
        >>> partitionner([1, 2, 3, 4], lambda x: x % 2 == 0)
        ([2, 4], [1, 3])
    """
    matching = []
    not_matching = []

    for item in items:
        if predicate(item):
            matching.append(item)
        else:
            not_matching.append(item)

    return matching, not_matching


def fusionner_dicts(*dicts: dict) -> dict:
    """
    Fusionne plusieurs dicts (dernier gagne).

    Examples:
        >>> fusionner_dicts({"a": 1}, {"b": 2}, {"a": 3})
        {"a": 3, "b": 2}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def extraire(data: dict, keys: list[str]) -> dict:
    """
    Extrait uniquement les clés spécifiées.

    Examples:
        >>> extraire({"a": 1, "b": 2, "c": 3}, ["a", "c"])
        {"a": 1, "c": 3}
    """
    return {k: v for k, v in data.items() if k in keys}


def omettre(data: dict, keys: list[str]) -> dict:
    """
    Exclut les clés spécifiées.

    Examples:
        >>> omettre({"a": 1, "b": 2, "c": 3}, ["b"])
        {"a": 1, "c": 3}
    """
    return {k: v for k, v in data.items() if k not in keys}


def trier_donnees(items: list[dict], key: str, reverse: bool = False) -> list[dict]:
    """
    Trie une liste de dicts par clé.

    Examples:
        >>> trier_donnees([{"val": 3}, {"val": 1}], "val")
        [{"val": 1}, {"val": 3}]
    """
    return sorted(items, key=lambda x: x.get(key), reverse=reverse)


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_moyenne(values: list[float]) -> float:
    """
    Calcule moyenne.

    Examples:
        >>> calculer_moyenne([1, 2, 3, 4, 5])
        3.0
    """
    return sum(values) / len(values) if values else 0.0


def calculer_mediane(values: list[float]) -> float:
    """
    Calcule médiane.

    Examples:
        >>> calculer_mediane([1, 2, 3, 4, 5])
        3.0
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    if n % 2 == 0:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    else:
        return sorted_values[n // 2]


def calculer_variance(values: list[float]) -> float:
    """
    Calcule variance.

    Examples:
        >>> calculer_variance([1, 2, 3, 4, 5])
        2.0
    """
    if not values or len(values) < 2:
        return 0.0

    return statistics.variance(values)


def calculer_ecart_type(values: list[float]) -> float:
    """
    Calcule écart-type.

    Examples:
        >>> calculer_ecart_type([1, 2, 3, 4, 5])
        1.4142135623730951
    """
    if not values or len(values) < 2:
        return 0.0

    return statistics.stdev(values)


def calculer_percentile(values: list[float], percentile: int) -> float:
    """
    Calcule un percentile.

    Args:
        values: Liste de valeurs
        percentile: 0-100

    Examples:
        >>> calculer_percentile([1, 2, 3, 4, 5], 50)
        3.0
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * percentile / 100

    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = index - lower

    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def calculer_mode(values: list) -> Any:
    """
    Calcule le mode (valeur la plus fréquente).

    Examples:
        >>> calculer_mode([1, 2, 2, 3, 3, 3])
        3
    """
    if not values:
        return None

    try:
        return statistics.mode(values)
    except statistics.StatisticsError:
        return None


def calculer_etendue(values: list[float]) -> float:
    """
    Calcule l'étendue (max - min).

    Examples:
        >>> calculer_etendue([1, 2, 3, 4, 5])
        4.0
    """
    if not values:
        return 0.0

    return max(values) - min(values)


def moyenne_mobile(values: list[float], window: int) -> list[float]:
    """
    Calcule moyenne mobile.

    Examples:
        >>> moyenne_mobile([1, 2, 3, 4, 5], 3)
        [2.0, 3.0, 4.0]
    """
    if len(values) < window:
        return []

    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i : i + window]
        result.append(sum(window_values) / window)

    return result


# ═══════════════════════════════════════════════════════════
# STRINGS
# ═══════════════════════════════════════════════════════════


def generer_id(data: Any) -> str:
    """
    Génère ID unique basé sur données.

    Examples:
        >>> generer_id({"nom": "test", "value": 123})
        "a1b2c3d4e5f6g7h8"
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]


def normaliser_espaces(text: str) -> str:
    """
    Normalise espaces (single space, trim).

    Examples:
        >>> normaliser_espaces("  hello    world  ")
        "hello world"
    """
    return " ".join(text.split())


def retirer_accents(text: str) -> str:
    """
    Retire les accents d'un texte.

    Examples:
        >>> retirer_accents("café crème")
        "cafe creme"
    """
    replacements = {
        "à": "a",
        "á": "a",
        "â": "a",
        "ä": "a",
        "ã": "a",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "ì": "i",
        "í": "i",
        "î": "i",
        "ï": "i",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "ö": "o",
        "õ": "o",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
        "ñ": "n",
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
        result = result.replace(old.upper(), new.upper())

    return result


def camel_vers_snake(text: str) -> str:
    """
    Convertit camelCase en snake_case.

    Examples:
        >>> camel_vers_snake("myVariableName")
        "my_variable_name"
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def snake_vers_camel(text: str) -> str:
    """
    Convertit snake_case en camelCase.

    Examples:
        >>> snake_vers_camel("my_variable_name")
        "myVariableName"
    """
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def pluraliser(word: str, count: int, plural_form: str | None = None) -> str:
    """
    Pluralise un mot selon le nombre.

    Examples:
        >>> pluraliser("item", 1)
        "1 item"
        >>> pluraliser("item", 5)
        "5 items"
        >>> pluraliser("cheval", 2, "chevaux")
        "2 chevaux"
    """
    if count == 1:
        return f"{count} {word}"

    if plural_form:
        return f"{count} {plural_form}"

    if word.endswith("y"):
        return f"{count} {word[:-1]}ies"
    elif word.endswith("s"):
        return f"{count} {word}es"
    else:
        return f"{count} {word}s"


def masquer_sensible(text: str, visible_chars: int = 4) -> str:
    """
    Masque données sensibles.

    Examples:
        >>> masquer_sensible("1234567890", 4)
        "1234******"
    """
    if len(text) <= visible_chars:
        return text

    visible = text[:visible_chars]
    masked = "*" * (len(text) - visible_chars)
    return visible + masked


# ═══════════════════════════════════════════════════════════
# FOOD HELPERS
# ═══════════════════════════════════════════════════════════


def convertir_unite(valeur: float, unite_source: str, unite_cible: str) -> float | None:
    """
    Convertit une unité de mesure vers une autre.

    Examples:
        >>> convertir_unite(1000, "ml", "L")
        1.0
        >>> convertir_unite(1, "kg", "g")
        1000.0
    """
    conversions = {
        # Volume
        ("ml", "L"): 0.001,
        ("L", "ml"): 1000,
        ("cl", "ml"): 10,
        ("ml", "cl"): 0.1,
        ("cl", "L"): 0.01,
        ("L", "cl"): 100,
        # Poids
        ("g", "kg"): 0.001,
        ("kg", "g"): 1000,
        ("mg", "g"): 0.001,
        ("g", "mg"): 1000,
    }
    key = (
        unite_source.lower(),
        unite_cible.upper() if unite_cible.upper() in ["L"] else unite_cible.lower(),
    )
    if key in conversions:
        return valeur * conversions[key]
    return None


def multiplier_portion(portion_originale: int, portion_cible: int, ingredients: dict) -> dict:
    """
    Multiplie les quantités d'ingrédients pour adapter une recette.

    Examples:
        >>> multiplier_portion(4, 8, {"sucre": 200})
        {"sucre": 400}
    """
    if portion_originale <= 0:
        return ingredients
    multiplicateur = portion_cible / portion_originale
    return {ing: qte * multiplicateur for ing, qte in ingredients.items()}


def extraire_ingredient(texte: str) -> dict | None:
    """
    Extrait les infos d'ingrédient depuis un texte.

    Examples:
        >>> extraire_ingredient("200g de farine")
        {"quantite": 200, "unite": "g", "nom": "farine"}
    """
    match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)?\s*(?:de\s+)?(.+)", texte.strip())
    if match:
        return {
            "quantite": float(match.group(1)),
            "unite": match.group(2) or "",
            "nom": match.group(3).strip(),
        }
    return None


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Data
    "obtenir_securise",
    "grouper_par",
    "compter_par",
    "dedupliquer",
    "aplatir",
    "partitionner",
    "fusionner_dicts",
    "extraire",
    "omettre",
    "trier_donnees",
    # Stats
    "calculer_moyenne",
    "calculer_mediane",
    "calculer_variance",
    "calculer_ecart_type",
    "calculer_percentile",
    "calculer_mode",
    "calculer_etendue",
    "moyenne_mobile",
    # Strings
    "generer_id",
    "normaliser_espaces",
    "retirer_accents",
    "camel_vers_snake",
    "snake_vers_camel",
    "pluraliser",
    "masquer_sensible",
    # Food
    "convertir_unite",
    "multiplier_portion",
    "extraire_ingredient",
]
