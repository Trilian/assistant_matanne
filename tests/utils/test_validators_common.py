"""
Tests pour src/utils/validators/common.py
"""
import pytest
from src.utils.validators.common import (
    is_valid_email,
    is_valid_phone,
    clamp,
    validate_range,
    validate_string_length,
)


class TestIsValidEmail:
    """Tests pour is_valid_email."""

    def test_valid_email_simple(self):
        """Email simple valide."""
        assert is_valid_email("test@example.com") is True

    def test_valid_email_subdomain(self):
        """Email avec sous-domaine."""
        assert is_valid_email("user@mail.example.com") is True

    def test_valid_email_plus_sign(self):
        """Email avec +."""
        assert is_valid_email("user+tag@example.com") is True

    def test_invalid_email_no_at(self):
        """Sans @ invalide."""
        assert is_valid_email("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Sans domaine invalide."""
        assert is_valid_email("test@") is False

    def test_invalid_email_empty(self):
        """Email vide invalide."""
        assert is_valid_email("") is False

    def test_invalid_email_spaces(self):
        """Email avec espaces invalide."""
        assert is_valid_email("test @example.com") is False


class TestIsValidPhone:
    """Tests pour is_valid_phone."""

    def test_valid_phone_french(self):
        """Numéro français valide."""
        assert is_valid_phone("0612345678") is True

    def test_valid_phone_with_spaces(self):
        """Numéro avec espaces."""
        assert is_valid_phone("06 12 34 56 78") is True

    def test_valid_phone_international(self):
        """Numéro international."""
        assert is_valid_phone("+33612345678") is True

    def test_invalid_phone_short(self):
        """Numéro trop court."""
        assert is_valid_phone("0612") is False

    def test_invalid_phone_letters(self):
        """Numéro avec lettres."""
        assert is_valid_phone("06123abc78") is False

    def test_invalid_phone_empty(self):
        """Numéro vide."""
        assert is_valid_phone("") is False


class TestClamp:
    """Tests pour clamp."""

    def test_clamp_in_range(self):
        """Valeur dans la plage."""
        assert clamp(5, 0, 10) == 5

    def test_clamp_below_min(self):
        """Valeur sous le minimum."""
        assert clamp(-5, 0, 10) == 0

    def test_clamp_above_max(self):
        """Valeur au-dessus du maximum."""
        assert clamp(15, 0, 10) == 10

    def test_clamp_at_min(self):
        """Valeur égale au minimum."""
        assert clamp(0, 0, 10) == 0

    def test_clamp_at_max(self):
        """Valeur égale au maximum."""
        assert clamp(10, 0, 10) == 10

    def test_clamp_floats(self):
        """Clamp avec floats."""
        assert clamp(5.5, 0.0, 10.0) == 5.5
        assert clamp(-0.1, 0.0, 1.0) == 0.0


class TestValidateRange:
    """Tests pour validate_range (retourne tuple[bool, str])."""

    def test_validate_range_valid(self):
        """Valeur dans la plage."""
        is_valid, msg = validate_range(5, 0, 10)
        assert is_valid is True
        assert msg == ""

    def test_validate_range_invalid_low(self):
        """Valeur trop basse."""
        is_valid, msg = validate_range(-1, 0, 10)
        assert is_valid is False
        assert "0" in msg

    def test_validate_range_invalid_high(self):
        """Valeur trop haute."""
        is_valid, msg = validate_range(11, 0, 10)
        assert is_valid is False
        assert "10" in msg

    def test_validate_range_boundaries(self):
        """Valeurs aux bornes (inclusif)."""
        is_valid_min, _ = validate_range(0, 0, 10)
        is_valid_max, _ = validate_range(10, 0, 10)
        assert is_valid_min is True
        assert is_valid_max is True


class TestValidateStringLength:
    """Tests pour validate_string_length (retourne tuple[bool, str])."""

    def test_validate_length_valid(self):
        """Longueur valide."""
        is_valid, msg = validate_string_length("hello", min_length=1, max_length=10)
        assert is_valid is True
        assert msg == ""

    def test_validate_length_too_short(self):
        """Trop court."""
        is_valid, msg = validate_string_length("ab", min_length=3)
        assert is_valid is False
        assert "3" in msg

    def test_validate_length_too_long(self):
        """Trop long."""
        is_valid, msg = validate_string_length("hello world", max_length=5)
        assert is_valid is False

    def test_validate_length_exact_min(self):
        """Exactement le minimum."""
        is_valid, _ = validate_string_length("abc", min_length=3)
        assert is_valid is True

    def test_validate_length_exact_max(self):
        """Exactement le maximum."""
        is_valid, _ = validate_string_length("abcde", max_length=5)
        assert is_valid is True

    def test_validate_length_empty(self):
        """Chaîne vide."""
        is_valid_fail, _ = validate_string_length("", min_length=1)
        is_valid_ok, _ = validate_string_length("", min_length=0)
        assert is_valid_fail is False
        assert is_valid_ok is True
