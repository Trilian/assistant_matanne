"""
Tests pour les validators communs
"""

import pytest

from src.utils.validators.common import (
    is_valid_email,
    is_valid_phone,
    clamp,
    validate_range,
    validate_string_length,
    validate_required_fields,
    validate_choice,
)


class TestIsValidEmail:
    """Tests pour is_valid_email"""

    def test_valid_email_basic(self):
        """Test email valide basique"""
        assert is_valid_email("test@example.com") is True

    def test_valid_email_with_dots(self):
        """Test email avec points"""
        assert is_valid_email("test.name@example.com") is True

    def test_valid_email_with_plus(self):
        """Test email avec +"""
        assert is_valid_email("test+tag@example.com") is True

    def test_invalid_email_no_at(self):
        """Test email sans @"""
        assert is_valid_email("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Test email sans domaine"""
        assert is_valid_email("test@") is False

    def test_invalid_email_simple(self):
        """Test email invalide simple"""
        assert is_valid_email("invalid") is False


class TestIsValidPhone:
    """Tests pour is_valid_phone"""

    def test_valid_phone_french(self):
        """Test téléphone français valide"""
        assert is_valid_phone("0612345678", "FR") is True

    def test_valid_phone_with_spaces(self):
        """Test téléphone avec espaces"""
        assert is_valid_phone("06 12 34 56 78", "FR") is True

    def test_valid_phone_with_prefix(self):
        """Test téléphone avec préfixe international"""
        assert is_valid_phone("+33 6 12 34 56 78", "FR") is True

    def test_invalid_phone_too_short(self):
        """Test téléphone trop court"""
        assert is_valid_phone("061234", "FR") is False

    def test_invalid_phone_unknown_country(self):
        """Test pays inconnu"""
        assert is_valid_phone("0612345678", "XX") is False


class TestClamp:
    """Tests pour clamp"""

    def test_clamp_in_range(self):
        """Test valeur dans la plage"""
        assert clamp(5, 0, 10) == 5

    def test_clamp_below_min(self):
        """Test valeur sous le min"""
        assert clamp(-5, 0, 10) == 0

    def test_clamp_above_max(self):
        """Test valeur au-dessus du max"""
        assert clamp(15, 0, 10) == 10

    def test_clamp_at_min(self):
        """Test valeur égale au min"""
        assert clamp(0, 0, 10) == 0

    def test_clamp_at_max(self):
        """Test valeur égale au max"""
        assert clamp(10, 0, 10) == 10


class TestValidateRange:
    """Tests pour validate_range"""

    def test_validate_range_valid(self):
        """Test valeur valide"""
        is_valid, error = validate_range(5, 0, 10)
        assert is_valid is True
        assert error == ""

    def test_validate_range_below_min(self):
        """Test valeur sous le min"""
        is_valid, error = validate_range(-5, 0, 10)
        assert is_valid is False
        assert ">" in error

    def test_validate_range_above_max(self):
        """Test valeur au-dessus du max"""
        is_valid, error = validate_range(15, 0, 10)
        assert is_valid is False
        assert "<" in error

    def test_validate_range_no_min(self):
        """Test sans min"""
        is_valid, error = validate_range(5, max_val=10)
        assert is_valid is True

    def test_validate_range_no_max(self):
        """Test sans max"""
        is_valid, error = validate_range(5, min_val=0)
        assert is_valid is True

    def test_validate_range_invalid_value(self):
        """Test valeur invalide"""
        is_valid, error = validate_range("invalid", 0, 10)
        assert is_valid is False
        assert "nombre" in error


class TestValidateStringLength:
    """Tests pour validate_string_length"""

    def test_validate_string_length_valid(self):
        """Test longueur valide"""
        is_valid, error = validate_string_length("test", min_length=1, max_length=10)
        assert is_valid is True

    def test_validate_string_length_too_short(self):
        """Test trop court"""
        is_valid, error = validate_string_length("ab", min_length=5)
        assert is_valid is False
        assert "au moins" in error

    def test_validate_string_length_too_long(self):
        """Test trop long"""
        is_valid, error = validate_string_length("abcdefghij", max_length=5)
        assert is_valid is False
        assert "maximum" in error

    def test_validate_string_length_not_string(self):
        """Test non-string"""
        is_valid, error = validate_string_length(123, min_length=1)
        assert is_valid is False
        assert "texte" in error


class TestValidateRequiredFields:
    """Tests pour validate_required_fields"""

    def test_validate_required_fields_all_present(self):
        """Test tous les champs présents"""
        data = {"nom": "Test", "email": "test@example.com"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is True
        assert missing == []

    def test_validate_required_fields_some_missing(self):
        """Test certains champs manquants"""
        data = {"nom": "Test"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False
        assert "email" in missing

    def test_validate_required_fields_empty_value(self):
        """Test valeur vide"""
        data = {"nom": "Test", "email": ""}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False
        assert "email" in missing

    def test_validate_required_fields_none_value(self):
        """Test valeur None"""
        data = {"nom": "Test", "email": None}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False
        assert "email" in missing


class TestValidateChoice:
    """Tests pour validate_choice"""

    def test_validate_choice_valid(self):
        """Test choix valide"""
        is_valid, error = validate_choice("A", ["A", "B", "C"])
        assert is_valid is True
        assert error == ""

    def test_validate_choice_invalid(self):
        """Test choix invalide"""
        is_valid, error = validate_choice("D", ["A", "B", "C"])
        assert is_valid is False
        assert "doit être dans" in error

    def test_validate_choice_numbers(self):
        """Test avec nombres"""
        is_valid, error = validate_choice(1, [1, 2, 3])
        assert is_valid is True

