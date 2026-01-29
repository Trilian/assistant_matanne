"""
Tests pour les helpers de données
"""

import pytest

from src.utils.helpers.data import (
    safe_get,
    group_by,
    count_by,
    deduplicate,
    flatten,
    partition,
    merge_dicts,
    pick,
    omit,
)


class TestSafeGet:
    """Tests pour safe_get"""

    def test_safe_get_simple(self):
        """Test accès simple"""
        data = {"a": 1}
        assert safe_get(data, "a") == 1

    def test_safe_get_nested(self):
        """Test accès imbriqué"""
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a", "b", "c") == 1

    def test_safe_get_missing(self):
        """Test clé manquante"""
        data = {"a": 1}
        assert safe_get(data, "b") is None

    def test_safe_get_missing_nested(self):
        """Test clé imbriquée manquante"""
        data = {"a": 1}
        assert safe_get(data, "a", "b", "c") is None

    def test_safe_get_default(self):
        """Test valeur par défaut"""
        data = {"a": 1}
        assert safe_get(data, "b", default=0) == 0

    def test_safe_get_none_value(self):
        """Test valeur None"""
        data = {"a": None}
        assert safe_get(data, "a", "b", default=0) == 0


class TestGroupBy:
    """Tests pour group_by"""

    def test_group_by_basic(self):
        """Test groupement basique"""
        items = [
            {"type": "A", "val": 1},
            {"type": "A", "val": 2},
            {"type": "B", "val": 3},
        ]
        result = group_by(items, "type")
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1

    def test_group_by_single_group(self):
        """Test un seul groupe"""
        items = [{"type": "A", "val": 1}, {"type": "A", "val": 2}]
        result = group_by(items, "type")
        assert len(result) == 1
        assert "A" in result

    def test_group_by_empty(self):
        """Test liste vide"""
        result = group_by([], "type")
        assert result == {}


class TestCountBy:
    """Tests pour count_by"""

    def test_count_by_basic(self):
        """Test comptage basique"""
        items = [{"type": "A"}, {"type": "A"}, {"type": "B"}]
        result = count_by(items, "type")
        assert result["A"] == 2
        assert result["B"] == 1

    def test_count_by_empty(self):
        """Test liste vide"""
        result = count_by([], "type")
        assert result == {}


class TestDeduplicate:
    """Tests pour deduplicate"""

    def test_deduplicate_simple(self):
        """Test déduplication simple"""
        result = deduplicate([1, 2, 2, 3])
        assert result == [1, 2, 3]

    def test_deduplicate_with_key(self):
        """Test déduplication avec clé"""
        items = [{"id": 1}, {"id": 1}, {"id": 2}]
        result = deduplicate(items, key=lambda x: x["id"])
        assert len(result) == 2

    def test_deduplicate_strings(self):
        """Test déduplication strings"""
        result = deduplicate(["a", "b", "a", "c"])
        assert result == ["a", "b", "c"]

    def test_deduplicate_preserves_order(self):
        """Test préservation de l'ordre"""
        result = deduplicate([3, 1, 2, 1, 3])
        assert result == [3, 1, 2]


class TestFlatten:
    """Tests pour flatten"""

    def test_flatten_basic(self):
        """Test aplatissement basique"""
        result = flatten([[1, 2], [3, 4], [5]])
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty_sublists(self):
        """Test avec sous-listes vides"""
        result = flatten([[1], [], [2]])
        assert result == [1, 2]

    def test_flatten_empty(self):
        """Test liste vide"""
        result = flatten([])
        assert result == []


class TestPartition:
    """Tests pour partition"""

    def test_partition_basic(self):
        """Test partition basique"""
        matching, not_matching = partition([1, 2, 3, 4], lambda x: x % 2 == 0)
        assert matching == [2, 4]
        assert not_matching == [1, 3]

    def test_partition_all_match(self):
        """Test tous matchent"""
        matching, not_matching = partition([2, 4, 6], lambda x: x % 2 == 0)
        assert matching == [2, 4, 6]
        assert not_matching == []

    def test_partition_none_match(self):
        """Test aucun match"""
        matching, not_matching = partition([1, 3, 5], lambda x: x % 2 == 0)
        assert matching == []
        assert not_matching == [1, 3, 5]


class TestMergeDicts:
    """Tests pour merge_dicts"""

    def test_merge_dicts_basic(self):
        """Test fusion basique"""
        result = merge_dicts({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_merge_dicts_override(self):
        """Test écrasement"""
        result = merge_dicts({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_merge_dicts_multiple(self):
        """Test fusion multiple"""
        result = merge_dicts({"a": 1}, {"b": 2}, {"c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_merge_dicts_empty(self):
        """Test avec dict vide"""
        result = merge_dicts({}, {"a": 1})
        assert result == {"a": 1}


class TestPick:
    """Tests pour pick"""

    def test_pick_basic(self):
        """Test pick basique"""
        result = pick({"a": 1, "b": 2, "c": 3}, ["a", "c"])
        assert result == {"a": 1, "c": 3}

    def test_pick_missing_keys(self):
        """Test clés manquantes"""
        result = pick({"a": 1}, ["a", "b"])
        assert result == {"a": 1}

    def test_pick_all_keys(self):
        """Test toutes les clés"""
        result = pick({"a": 1, "b": 2}, ["a", "b"])
        assert result == {"a": 1, "b": 2}


class TestOmit:
    """Tests pour omit"""

    def test_omit_basic(self):
        """Test omit basique"""
        result = omit({"a": 1, "b": 2, "c": 3}, ["b"])
        assert result == {"a": 1, "c": 3}

    def test_omit_missing_keys(self):
        """Test clés manquantes"""
        result = omit({"a": 1, "b": 2}, ["c"])
        assert result == {"a": 1, "b": 2}

    def test_omit_all_keys(self):
        """Test toutes les clés"""
        result = omit({"a": 1, "b": 2}, ["a", "b"])
        assert result == {}
