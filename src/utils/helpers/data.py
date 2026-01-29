"""
Helpers - Manipulation de données
"""

from collections import Counter, defaultdict
from collections.abc import Callable
from typing import Any


def safe_get(data: dict, *keys, default=None) -> Any:
    """
    Récupère valeur nested avec fallback

    Examples:
        >>> safe_get({"a": {"b": {"c": 1}}}, "a", "b", "c")
        1
        >>> safe_get({"a": 1}, "b", "c", default=0)
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


def group_by(items: list[dict], key: str) -> dict[Any, list[dict]]:
    """
    Regroupe items par clé

    Examples:
        >>> items = [{"type": "A", "val": 1}, {"type": "A", "val": 2}, {"type": "B", "val": 3}]
        >>> group_by(items, "type")
        {"A": [{"type": "A", "val": 1}, {"type": "A", "val": 2}], "B": [{"type": "B", "val": 3}]}
    """
    grouped = defaultdict(list)
    for item in items:
        group_key = item.get(key)
        grouped[group_key].append(item)
    return dict(grouped)


def count_by(items: list[dict], key: str) -> dict[Any, int]:
    """
    Compte items par clé

    Examples:
        >>> items = [{"type": "A"}, {"type": "A"}, {"type": "B"}]
        >>> count_by(items, "type")
        {"A": 2, "B": 1}
    """
    return dict(Counter(item.get(key) for item in items))


def deduplicate(items: list[Any], key: Callable | None = None) -> list[Any]:
    """
    Déduplique une liste

    Examples:
        >>> deduplicate([1, 2, 2, 3])
        [1, 2, 3]
        >>> deduplicate([{"id": 1}, {"id": 1}, {"id": 2}], key=lambda x: x["id"])
        [{"id": 1}, {"id": 2}]
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


def flatten(nested_list: list[list[Any]]) -> list[Any]:
    """
    Aplatit une liste de listes

    Examples:
        >>> flatten([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested_list for item in sublist]


def partition(items: list[Any], predicate: Callable) -> tuple[list[Any], list[Any]]:
    """
    Partitionne liste selon prédicat

    Returns:
        (items_matching, items_not_matching)

    Examples:
        >>> partition([1, 2, 3, 4], lambda x: x % 2 == 0)
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


def merge_dicts(*dicts: dict) -> dict:
    """
    Fusionne plusieurs dicts (dernier gagne)

    Examples:
        >>> merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        {"a": 3, "b": 2}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def pick(data: dict, keys: list[str]) -> dict:
    """
    Extrait uniquement les clés spécifiées

    Examples:
        >>> pick({"a": 1, "b": 2, "c": 3}, ["a", "c"])
        {"a": 1, "c": 3}
    """
    return {k: v for k, v in data.items() if k in keys}


def omit(data: dict, keys: list[str]) -> dict:
    """
    Exclut les clés spécifiées

    Examples:
        >>> omit({"a": 1, "b": 2, "c": 3}, ["b"])
        {"a": 1, "c": 3}
    """
    return {k: v for k, v in data.items() if k not in keys}
