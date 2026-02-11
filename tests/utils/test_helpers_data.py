"""
Tests pour src/utils/helpers/data.py
"""
import pytest
from src.utils.helpers.data import (
    obtenir_securise,
    grouper_par,
    compter_par,
    dedupliquer,
    aplatir,
    partitionner,
)


class TestObtenirSecurise:
    """Tests pour obtenir_securise."""

    def test_obtenir_securise_existing_key(self):
        """Récupère valeur existante."""
        data = {"name": "test", "value": 42}
        assert obtenir_securise(data, "name") == "test"
        assert obtenir_securise(data, "value") == 42

    def test_obtenir_securise_missing_key(self):
        """Retourne None si clé manquante."""
        data = {"name": "test"}
        assert obtenir_securise(data, "missing") is None

    def test_obtenir_securise_with_default(self):
        """Retourne valeur par défaut si clé manquante."""
        data = {"name": "test"}
        assert obtenir_securise(data, "missing", default="default") == "default"

    def test_obtenir_securise_nested(self):
        """Récupère valeur imbriquée avec clés séparées."""
        # L'API utilise *keys (multiple arguments), pas dot notation
        data = {"user": {"name": "Jean", "age": 30}}
        assert obtenir_securise(data, "user", "name") == "Jean"
        assert obtenir_securise(data, "user", "age") == 30

    def test_obtenir_securise_nested_missing(self):
        """Retourne default si chemin imbriqué invalide."""
        data = {"user": {"name": "Jean"}}
        assert obtenir_securise(data, "user", "email", default="N/A") == "N/A"

    def test_obtenir_securise_empty_dict(self):
        """Dict vide retourne default."""
        assert obtenir_securise({}, "key") is None
        assert obtenir_securise({}, "key", default="empty") == "empty"

    def test_obtenir_securise_deeply_nested(self):
        """Récupère valeur profondément imbriquée."""
        data = {"a": {"b": {"c": {"d": 42}}}}
        assert obtenir_securise(data, "a", "b", "c", "d") == 42


class TestGrouperPar:
    """Tests pour grouper_par."""

    def test_grouper_par_simple(self):
        """Groupe par clé simple."""
        items = [
            {"type": "fruit", "name": "pomme"},
            {"type": "fruit", "name": "poire"},
            {"type": "legume", "name": "carotte"},
        ]
        result = grouper_par(items, "type")
        assert len(result["fruit"]) == 2
        assert len(result["legume"]) == 1

    def test_grouper_par_empty(self):
        """Liste vide retourne dict vide."""
        result = grouper_par([], "key")
        assert result == {}

    def test_grouper_par_single_item(self):
        """Un seul élément."""
        items = [{"type": "A", "value": 1}]
        result = grouper_par(items, "type")
        assert len(result["A"]) == 1


class TestCompterPar:
    """Tests pour compter_par."""

    def test_compter_par_simple(self):
        """Compte par clé."""
        items = [
            {"status": "active"},
            {"status": "active"},
            {"status": "inactive"},
        ]
        result = compter_par(items, "status")
        assert result["active"] == 2
        assert result["inactive"] == 1

    def test_compter_par_empty(self):
        """Liste vide."""
        result = compter_par([], "key")
        assert result == {}


class TestDedupliquer:
    """Tests pour dedupliquer."""

    def test_dedupliquer_simple(self):
        """Supprime doublons simples."""
        items = [1, 2, 2, 3, 3, 3]
        result = dedupliquer(items)
        assert len(result) == 3
        assert set(result) == {1, 2, 3}

    def test_dedupliquer_strings(self):
        """Supprime doublons de strings."""
        items = ["a", "b", "a", "c", "b"]
        result = dedupliquer(items)
        assert len(result) == 3

    def test_dedupliquer_by_key_lambda(self):
        """Supprime doublons par clé avec lambda."""
        # L'API utilise key=lambda, pas key="id"
        items = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "A duplicate"},
        ]
        result = dedupliquer(items, key=lambda x: x["id"])
        assert len(result) == 2

    def test_dedupliquer_empty(self):
        """Liste vide."""
        assert dedupliquer([]) == []


class TestAplatir:
    """Tests pour aplatir."""

    def test_aplatir_nested_lists(self):
        """Aplatit listes imbriquées."""
        nested = [[1, 2], [3, 4], [5]]
        result = aplatir(nested)
        assert result == [1, 2, 3, 4, 5]

    def test_aplatir_empty_sublists(self):
        """Gère sous-listes vides."""
        nested = [[1, 2], [], [3]]
        result = aplatir(nested)
        assert result == [1, 2, 3]

    def test_aplatir_single_list(self):
        """Une seule sous-liste."""
        nested = [[1, 2, 3]]
        result = aplatir(nested)
        assert result == [1, 2, 3]

    def test_aplatir_empty(self):
        """Liste vide."""
        assert aplatir([]) == []


class TestPartitionner:
    """Tests pour partitionner."""

    def test_partitionner_even_odd(self):
        """Partitionne pair/impair."""
        items = [1, 2, 3, 4, 5, 6]
        evens, odds = partitionner(items, lambda x: x % 2 == 0)
        assert evens == [2, 4, 6]
        assert odds == [1, 3, 5]

    def test_partitionner_strings(self):
        """Partitionne par longueur."""
        items = ["a", "abc", "ab", "abcd"]
        short, long = partitionner(items, lambda x: len(x) <= 2)
        assert short == ["a", "ab"]
        assert long == ["abc", "abcd"]

    def test_partitionner_all_true(self):
        """Tous éléments satisfont le prédicat."""
        items = [2, 4, 6]
        trues, falses = partitionner(items, lambda x: x % 2 == 0)
        assert trues == [2, 4, 6]
        assert falses == []

    def test_partitionner_empty(self):
        """Liste vide."""
        trues, falses = partitionner([], lambda x: True)
        assert trues == []
        assert falses == []
