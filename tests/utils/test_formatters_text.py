"""
Tests pour les formatters de texte
"""

import pytest

from src.utils.formatters.text import (
    truncate,
    clean_text,
    slugify,
    extract_number,
    capitalize_first,
)


class TestTruncate:
    """Tests pour truncate"""

    def test_truncate_short_text(self):
        """Test texte court"""
        result = truncate("Court", length=10)
        assert result == "Court"

    def test_truncate_exact_length(self):
        """Test longueur exacte"""
        result = truncate("1234567890", length=10)
        assert result == "1234567890"

    def test_truncate_long_text(self):
        """Test texte long"""
        result = truncate("Un texte trÃ¨s long qui dÃ©passe", length=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test suffixe personnalisÃ©"""
        result = truncate("Un texte long", length=10, suffix="â€¦")
        assert result.endswith("â€¦")

    def test_truncate_no_suffix(self):
        """Test sans suffixe"""
        result = truncate("Un texte long", length=10, suffix="")
        assert len(result) == 10


class TestCleanText:
    """Tests pour clean_text"""

    def test_clean_text_basic(self):
        """Test nettoyage basique"""
        result = clean_text("Texte normal")
        assert result == "Texte normal"

    def test_clean_text_html_tags(self):
        """Test suppression balises HTML"""
        result = clean_text("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_clean_text_braces(self):
        """Test suppression accolades"""
        result = clean_text("{malicious}")
        assert "{" not in result
        assert "}" not in result

    def test_clean_text_empty(self):
        """Test chaÃ®ne vide"""
        assert clean_text("") == ""

    def test_clean_text_none(self):
        """Test None"""
        assert clean_text(None) is None


class TestSlugify:
    """Tests pour slugify"""

    def test_slugify_basic(self):
        """Test basique"""
        result = slugify("Tarte aux Pommes")
        assert result == "tarte-aux-pommes"

    def test_slugify_accents(self):
        """Test accents"""
        result = slugify("CrÃ¨me brÃ»lÃ©e")
        assert result == "creme-brulee"

    def test_slugify_special_chars(self):
        """Test caractÃ¨res spÃ©ciaux"""
        result = slugify("Test & Test (2)")
        assert "&" not in result
        assert "(" not in result

    def test_slugify_multiple_spaces(self):
        """Test espaces multiples"""
        result = slugify("Tarte   aux   pommes")
        assert "--" not in result

    def test_slugify_numbers(self):
        """Test avec nombres"""
        result = slugify("Recette 123")
        assert "123" in result


class TestExtractNumber:
    """Tests pour extract_number"""

    def test_extract_number_basic(self):
        """Test basique"""
        result = extract_number("2.5 kg")
        assert result == 2.5

    def test_extract_number_comma(self):
        """Test virgule franÃ§aise"""
        result = extract_number("Prix: 10,50â‚¬")
        assert result == 10.5

    def test_extract_number_integer(self):
        """Test entier"""
        result = extract_number("QuantitÃ©: 5")
        assert result == 5.0

    def test_extract_number_negative(self):
        """Test nombre nÃ©gatif"""
        result = extract_number("-15.5")
        assert result == -15.5

    def test_extract_number_no_number(self):
        """Test sans nombre"""
        result = extract_number("Pas de nombre")
        assert result is None

    def test_extract_number_empty(self):
        """Test chaÃ®ne vide"""
        result = extract_number("")
        assert result is None

    def test_extract_number_none(self):
        """Test None"""
        result = extract_number(None)
        assert result is None


class TestCapitalizeFirst:
    """Tests pour capitalize_first"""

    def test_capitalize_first_basic(self):
        """Test basique"""
        result = capitalize_first("tomate")
        assert result == "Tomate"

    def test_capitalize_first_uppercase(self):
        """Test majuscules"""
        result = capitalize_first("TOMATE")
        assert result == "Tomate"

    def test_capitalize_first_mixed(self):
        """Test mixte"""
        result = capitalize_first("tOMate")
        assert result == "Tomate"

    def test_capitalize_first_single_char(self):
        """Test un caractÃ¨re"""
        result = capitalize_first("a")
        assert result == "A"

    def test_capitalize_first_empty(self):
        """Test chaÃ®ne vide"""
        result = capitalize_first("")
        assert result == ""

    def test_capitalize_first_none(self):
        """Test None"""
        result = capitalize_first(None)
        assert result is None

