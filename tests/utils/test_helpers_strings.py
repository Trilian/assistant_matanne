"""
Tests pour src/utils/helpers/strings.py
"""
import pytest
from src.utils.helpers.strings import (
    generate_id,
    normalize_whitespace,
    remove_accents,
    camel_to_snake,
    snake_to_camel,
)


class TestGenerateId:
    """Tests pour generate_id."""

    def test_generate_id_dict(self):
        """Génère ID depuis dict."""
        result = generate_id({"nom": "test", "value": 123})
        assert len(result) == 16
        assert isinstance(result, str)

    def test_generate_id_deterministic(self):
        """Même données = même ID."""
        data = {"a": 1, "b": 2}
        assert generate_id(data) == generate_id(data)

    def test_generate_id_different_data(self):
        """Données différentes = IDs différents."""
        assert generate_id({"a": 1}) != generate_id({"a": 2})

    def test_generate_id_string(self):
        """Génère ID depuis string."""
        result = generate_id("test string")
        assert len(result) == 16


class TestNormalizeWhitespace:
    """Tests pour normalize_whitespace."""

    def test_normalize_multiple_spaces(self):
        """Réduit plusieurs espaces en un seul."""
        assert normalize_whitespace("hello    world") == "hello world"

    def test_normalize_trim(self):
        """Supprime les espaces de début et fin."""
        assert normalize_whitespace("  hello  ") == "hello"

    def test_normalize_tabs_newlines(self):
        """Gère tabs et newlines."""
        assert normalize_whitespace("hello\t\nworld") == "hello world"

    def test_normalize_empty(self):
        """String vide reste vide."""
        assert normalize_whitespace("") == ""

    def test_normalize_single_word(self):
        """Mot seul inchangé."""
        assert normalize_whitespace("hello") == "hello"


class TestRemoveAccents:
    """Tests pour remove_accents."""

    def test_remove_accents_basic(self):
        """Retire les accents basiques."""
        assert remove_accents("café") == "cafe"
        assert remove_accents("crème") == "creme"

    def test_remove_accents_all_vowels(self):
        """Retire les accents sur toutes les voyelles."""
        assert remove_accents("àéîöù") == "aeiou"

    def test_remove_cedilla(self):
        """Retire la cédille."""
        assert remove_accents("français") == "francais"

    def test_remove_tilde(self):
        """Retire le tilde."""
        assert remove_accents("señor") == "senor"

    def test_remove_accents_uppercase(self):
        """Gère les majuscules."""
        assert remove_accents("CAFÉ") == "CAFE"

    def test_no_accents_unchanged(self):
        """Texte sans accent inchangé."""
        assert remove_accents("hello world") == "hello world"


class TestCamelToSnake:
    """Tests pour camel_to_snake."""

    def test_camel_to_snake_basic(self):
        """Conversion basique."""
        assert camel_to_snake("myVariableName") == "my_variable_name"

    def test_camel_to_snake_single_word(self):
        """Mot seul reste en minuscule."""
        assert camel_to_snake("variable") == "variable"

    def test_camel_to_snake_acronym(self):
        """Gère les acronymes."""
        assert camel_to_snake("XMLParser") == "x_m_l_parser"

    def test_camel_to_snake_start_upper(self):
        """PascalCase aussi converti."""
        assert camel_to_snake("MyClassName") == "my_class_name"


class TestSnakeToCamel:
    """Tests pour snake_to_camel."""

    def test_snake_to_camel_basic(self):
        """Conversion basique."""
        assert snake_to_camel("my_variable_name") == "myVariableName"

    def test_snake_to_camel_single_word(self):
        """Mot seul inchangé."""
        assert snake_to_camel("variable") == "variable"

    def test_snake_to_camel_double_underscore(self):
        """Gère les double underscores."""
        result = snake_to_camel("my__double")
        assert "my" in result

    def test_snake_to_camel_numbers(self):
        """Gère les nombres."""
        assert snake_to_camel("item_1_name") == "item1Name"
