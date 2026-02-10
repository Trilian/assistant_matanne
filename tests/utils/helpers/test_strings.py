"""
Tests unitaires pour strings.py

Module: src.utils.helpers.strings
"""

import pytest
from src.utils.helpers.strings import (
    generer_id,
    normaliser_espaces,
    retirer_accents,
    camel_vers_snake,
    snake_vers_camel,
    pluraliser,
    masquer_sensible,
)


class TestStrings:
    """Tests pour le module strings."""

    def test_generer_id(self):
        """Test de la fonction generer_id."""
        id1 = generer_id({"nom": "test"})
        id2 = generer_id({"nom": "test"})
        id3 = generer_id({"nom": "different"})
        assert id1 == id2  # Même données = même ID
        assert id1 != id3  # Données différentes = ID différent
        assert len(id1) == 16

    def test_normaliser_espaces(self):
        """Test de la fonction normaliser_espaces."""
        assert normaliser_espaces("  hello    world  ") == "hello world"
        assert normaliser_espaces("single") == "single"
        assert normaliser_espaces("  ") == ""

    def test_retirer_accents(self):
        """Test de la fonction retirer_accents."""
        assert retirer_accents("café crème") == "cafe creme"
        assert retirer_accents("naïve") == "naive"
        assert retirer_accents("ÉLÉPHANT") == "ELEPHANT"

    def test_camel_vers_snake(self):
        """Test de la fonction camel_vers_snake."""
        assert camel_vers_snake("myVariableName") == "my_variable_name"
        assert camel_vers_snake("simpleCase") == "simple_case"
        assert camel_vers_snake("already_snake") == "already_snake"

    def test_snake_vers_camel(self):
        """Test de la fonction snake_vers_camel."""
        assert snake_vers_camel("my_variable_name") == "myVariableName"
        assert snake_vers_camel("simple_case") == "simpleCase"
        assert snake_vers_camel("single") == "single"

    def test_pluraliser(self):
        """Test de la fonction pluraliser."""
        assert pluraliser("item", 1) == "1 item"
        assert pluraliser("item", 5) == "5 items"
        assert pluraliser("cheval", 2, "chevaux") == "2 chevaux"

    def test_masquer_sensible(self):
        """Test de la fonction masquer_sensible."""
        assert masquer_sensible("1234567890", 4) == "1234******"
        assert masquer_sensible("abc", 4) == "abc"  # Court = pas masqué
        assert masquer_sensible("secret123", 3) == "sec******"
