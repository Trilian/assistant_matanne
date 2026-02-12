"""
Tests pour src/utils/helpers/strings.py
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


class TestGenererId:
    """Tests pour generer_id."""

    def test_generer_id_dict(self):
        """Génère ID depuis dict."""
        result = generer_id({"nom": "test", "value": 123})
        assert len(result) == 16
        assert isinstance(result, str)

    def test_generer_id_deterministic(self):
        """Même données = même ID."""
        data = {"a": 1, "b": 2}
        assert generer_id(data) == generer_id(data)

    def test_generer_id_different_data(self):
        """Données différentes = IDs différents."""
        assert generer_id({"a": 1}) != generer_id({"a": 2})

    def test_generer_id_string(self):
        """Génère ID depuis string."""
        result = generer_id("test string")
        assert len(result) == 16


class TestNormaliserEspaces:
    """Tests pour normaliser_espaces."""

    def test_normaliser_multiple_spaces(self):
        """Réduit plusieurs espaces en un seul."""
        assert normaliser_espaces("hello    world") == "hello world"

    def test_normaliser_trim(self):
        """Supprime les espaces de début et fin."""
        assert normaliser_espaces("  hello  ") == "hello"

    def test_normaliser_tabs_newlines(self):
        """Gère tabs et newlines."""
        assert normaliser_espaces("hello\t\nworld") == "hello world"

    def test_normaliser_empty(self):
        """String vide reste vide."""
        assert normaliser_espaces("") == ""

    def test_normaliser_single_word(self):
        """Mot seul inchangé."""
        assert normaliser_espaces("hello") == "hello"


class TestRetirerAccents:
    """Tests pour retirer_accents."""

    def test_retirer_accents_basic(self):
        """Retire les accents basiques."""
        assert retirer_accents("café") == "cafe"
        assert retirer_accents("crème") == "creme"

    def test_retirer_accents_all_vowels(self):
        """Retire les accents sur toutes les voyelles."""
        assert retirer_accents("Ã éîÃ¶ù") == "aeiou"

    def test_retirer_cedilla(self):
        """Retire la cédille."""
        assert retirer_accents("français") == "francais"

    def test_retirer_tilde(self):
        """Retire le tilde."""
        assert retirer_accents("seÃ±or") == "senor"

    def test_retirer_accents_uppercase(self):
        """Gère les majuscules."""
        assert retirer_accents("CAFÃ‰") == "CAFE"

    def test_no_accents_unchanged(self):
        """Texte sans accent inchangé."""
        assert retirer_accents("hello world") == "hello world"


class TestCamelVersSnake:
    """Tests pour camel_vers_snake."""

    def test_camel_vers_snake_basic(self):
        """Conversion basique."""
        assert camel_vers_snake("myVariableName") == "my_variable_name"

    def test_camel_vers_snake_single_word(self):
        """Mot seul reste en minuscule."""
        assert camel_vers_snake("variable") == "variable"

    def test_camel_vers_snake_acronym(self):
        """Gère les acronymes."""
        assert camel_vers_snake("XMLParser") == "x_m_l_parser"

    def test_camel_vers_snake_start_upper(self):
        """PascalCase aussi converti."""
        assert camel_vers_snake("MyClassName") == "my_class_name"


class TestSnakeVersCamel:
    """Tests pour snake_vers_camel."""

    def test_snake_vers_camel_basic(self):
        """Conversion basique."""
        assert snake_vers_camel("my_variable_name") == "myVariableName"

    def test_snake_vers_camel_single_word(self):
        """Mot seul inchangé."""
        assert snake_vers_camel("variable") == "variable"

    def test_snake_vers_camel_double_underscore(self):
        """Gère les double underscores."""
        result = snake_vers_camel("my__double")
        assert "my" in result

    def test_snake_vers_camel_numbers(self):
        """Gère les nombres."""
        assert snake_vers_camel("item_1_name") == "item1Name"


class TestPluraliser:
    """Tests pour pluraliser."""

    def test_pluraliser_singular(self):
        """Count 1 = singulier."""
        assert pluraliser("item", 1) == "1 item"

    def test_pluraliser_plural(self):
        """Count > 1 = pluriel."""
        assert pluraliser("item", 5) == "5 items"

    def test_pluraliser_zero(self):
        """Count 0 = pluriel."""
        assert pluraliser("item", 0) == "0 items"

    def test_pluraliser_custom_plural(self):
        """Pluriel personnalisé."""
        assert pluraliser("cheval", 2, "chevaux") == "2 chevaux"


class TestMasquerSensible:
    """Tests pour masquer_sensible."""

    def test_masquer_basic(self):
        """Masque les caractères après visible_count."""
        assert masquer_sensible("1234567890", 4) == "1234******"

    def test_masquer_short_text(self):
        """Texte court (< visible_count) = pas masqué."""
        assert masquer_sensible("abc", 4) == "abc"

    def test_masquer_exact_count(self):
        """Texte exact = partiellement masqué."""
        assert masquer_sensible("secret123", 3) == "sec******"
