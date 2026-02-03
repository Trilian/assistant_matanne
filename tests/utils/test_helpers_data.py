"""
Tests pour src/utils/helpers/data.py
"""
import pytest
from src.utils.helpers.data import (
    safe_get,
    group_by,
    count_by,
    deduplicate,
    flatten,
    partition,
)


class TestSafeGet:
    """Tests pour safe_get."""

    def test_safe_get_existing_key(self):
        """Récupère valeur existante."""
        data = {"name": "test", "value": 42}
        assert safe_get(data, "name") == "test"
        assert safe_get(data, "value") == 42

    def test_safe_get_missing_key(self):
        """Retourne None si clé manquante."""
        data = {"name": "test"}
        assert safe_get(data, "missing") is None

    def test_safe_get_with_default(self):
        """Retourne valeur par défaut si clé manquante."""
        data = {"name": "test"}
        assert safe_get(data, "missing", default="default") == "default"

    def test_safe_get_nested(self):
        """Récupère valeur imbriquée avec clés séparées."""
        # L'API utilise *keys (multiple arguments), pas dot notation
        data = {"user": {"name": "Jean", "age": 30}}
        assert safe_get(data, "user", "name") == "Jean"
        assert safe_get(data, "user", "age") == 30

    def test_safe_get_nested_missing(self):
        """Retourne default si chemin imbriqué invalide."""
        data = {"user": {"name": "Jean"}}
        assert safe_get(data, "user", "email", default="N/A") == "N/A"

    def test_safe_get_empty_dict(self):
        """Dict vide retourne default."""
        assert safe_get({}, "key") is None
        assert safe_get({}, "key", default="empty") == "empty"

    def test_safe_get_deeply_nested(self):
        """Récupère valeur profondément imbriquée."""
        data = {"a": {"b": {"c": {"d": 42}}}}
        assert safe_get(data, "a", "b", "c", "d") == 42


class TestGroupBy:
    """Tests pour group_by."""

    def test_group_by_simple(self):
        """Groupe par clé simple."""
        items = [
            {"type": "fruit", "name": "pomme"},
            {"type": "fruit", "name": "poire"},
            {"type": "legume", "name": "carotte"},
        ]
        result = group_by(items, "type")
        assert len(result["fruit"]) == 2
        assert len(result["legume"]) == 1

    def test_group_by_empty(self):
        """Liste vide retourne dict vide."""
        result = group_by([], "key")
        assert result == {}

    def test_group_by_single_item(self):
        """Un seul élément."""
        items = [{"type": "A", "value": 1}]
        result = group_by(items, "type")
        assert len(result["A"]) == 1


class TestCountBy:
    """Tests pour count_by."""

    def test_count_by_simple(self):
        """Compte par clé."""
        items = [
            {"status": "active"},
            {"status": "active"},
            {"status": "inactive"},
        ]
        result = count_by(items, "status")
        assert result["active"] == 2
        assert result["inactive"] == 1

    def test_count_by_empty(self):
        """Liste vide."""
        result = count_by([], "key")
        assert result == {}


class TestDeduplicate:
    """Tests pour deduplicate."""

    def test_deduplicate_simple(self):
        """Supprime doublons simples."""
        items = [1, 2, 2, 3, 3, 3]
        result = deduplicate(items)
        assert len(result) == 3
        assert set(result) == {1, 2, 3}

    def test_deduplicate_strings(self):
        """Supprime doublons de strings."""
        items = ["a", "b", "a", "c", "b"]
        result = deduplicate(items)
        assert len(result) == 3

    def test_deduplicate_by_key_lambda(self):
        """Supprime doublons par clé avec lambda."""
        # L'API utilise key=lambda, pas key="id"
        items = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "A duplicate"},
        ]
        result = deduplicate(items, key=lambda x: x["id"])
        assert len(result) == 2

    def test_deduplicate_empty(self):
        """Liste vide."""
        assert deduplicate([]) == []


class TestFlatten:
    """Tests pour flatten."""

    def test_flatten_nested_lists(self):
        """Aplatit listes imbriquées."""
        nested = [[1, 2], [3, 4], [5]]
        result = flatten(nested)
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty_sublists(self):
        """Gère sous-listes vides."""
        nested = [[1, 2], [], [3]]
        result = flatten(nested)
        assert result == [1, 2, 3]

    def test_flatten_single_list(self):
        """Une seule sous-liste."""
        nested = [[1, 2, 3]]
        result = flatten(nested)
        assert result == [1, 2, 3]

    def test_flatten_empty(self):
        """Liste vide."""
        assert flatten([]) == []


class TestPartition:
    """Tests pour partition."""

    def test_partition_even_odd(self):
        """Partitionne pair/impair."""
        items = [1, 2, 3, 4, 5, 6]
        evens, odds = partition(items, lambda x: x % 2 == 0)
        assert evens == [2, 4, 6]
        assert odds == [1, 3, 5]

    def test_partition_strings(self):
        """Partitionne par longueur."""
        items = ["a", "abc", "ab", "abcd"]
        short, long = partition(items, lambda x: len(x) <= 2)
        assert short == ["a", "ab"]
        assert long == ["abc", "abcd"]

    def test_partition_all_true(self):
        """Tous éléments satisfont le prédicat."""
        items = [2, 4, 6]
        trues, falses = partition(items, lambda x: x % 2 == 0)
        assert trues == [2, 4, 6]
        assert falses == []

    def test_partition_empty(self):
        """Liste vide."""
        trues, falses = partition([], lambda x: True)
        assert trues == []
        assert falses == []
