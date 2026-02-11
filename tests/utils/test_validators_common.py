"""
Tests pour src/utils/validators/common.py
"""
import pytest
from src.utils.validators.common import (
    valider_email,
    valider_telephone,
    borner,
    valider_plage,
    valider_longueur_texte,
)


class TestValiderEmail:
    """Tests pour valider_email."""

    def test_valid_email_simple(self):
        """Email simple valide."""
        assert valider_email("test@example.com") is True

    def test_valid_email_subdomain(self):
        """Email avec sous-domaine."""
        assert valider_email("user@mail.example.com") is True

    def test_valid_email_plus_sign(self):
        """Email avec +."""
        assert valider_email("user+tag@example.com") is True

    def test_invalid_email_no_at(self):
        """Sans @ invalide."""
        assert valider_email("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Sans domaine invalide."""
        assert valider_email("test@") is False

    def test_invalid_email_empty(self):
        """Email vide invalide."""
        assert valider_email("") is False

    def test_invalid_email_spaces(self):
        """Email avec espaces invalide."""
        assert valider_email("test @example.com") is False


class TestValiderTelephone:
    """Tests pour valider_telephone."""

    def test_valid_phone_french(self):
        """Numéro français valide."""
        assert valider_telephone("0612345678") is True

    def test_valid_phone_with_spaces(self):
        """Numéro avec espaces."""
        assert valider_telephone("06 12 34 56 78") is True

    def test_valid_phone_international(self):
        """Numéro international."""
        assert valider_telephone("+33612345678") is True

    def test_invalid_phone_short(self):
        """Numéro trop court."""
        assert valider_telephone("0612") is False

    def test_invalid_phone_letters(self):
        """Numéro avec lettres."""
        assert valider_telephone("06123abc78") is False

    def test_invalid_phone_empty(self):
        """Numéro vide."""
        assert valider_telephone("") is False


class TestBorner:
    """Tests pour borner."""

    def test_borner_in_range(self):
        """Valeur dans la plage."""
        assert borner(5, 0, 10) == 5

    def test_borner_below_min(self):
        """Valeur sous le minimum."""
        assert borner(-5, 0, 10) == 0

    def test_borner_above_max(self):
        """Valeur au-dessus du maximum."""
        assert borner(15, 0, 10) == 10

    def test_borner_at_min(self):
        """Valeur égale au minimum."""
        assert borner(0, 0, 10) == 0

    def test_borner_at_max(self):
        """Valeur égale au maximum."""
        assert borner(10, 0, 10) == 10

    def test_borner_floats(self):
        """Borner avec floats."""
        assert borner(5.5, 0.0, 10.0) == 5.5
        assert borner(-0.1, 0.0, 1.0) == 0.0


class TestValiderPlage:
    """Tests pour valider_plage (retourne tuple[bool, str])."""

    def test_valider_plage_valid(self):
        """Valeur dans la plage."""
        is_valid, msg = valider_plage(5, 0, 10)
        assert is_valid is True
        assert msg == ""

    def test_valider_plage_invalid_low(self):
        """Valeur trop basse."""
        is_valid, msg = valider_plage(-1, 0, 10)
        assert is_valid is False
        assert "0" in msg

    def test_valider_plage_invalid_high(self):
        """Valeur trop haute."""
        is_valid, msg = valider_plage(11, 0, 10)
        assert is_valid is False
        assert "10" in msg

    def test_valider_plage_boundaries(self):
        """Valeurs aux bornes (inclusif)."""
        is_valid_min, _ = valider_plage(0, 0, 10)
        is_valid_max, _ = valider_plage(10, 0, 10)
        assert is_valid_min is True
        assert is_valid_max is True


class TestValiderLongueurTexte:
    """Tests pour valider_longueur_texte (retourne tuple[bool, str])."""

    def test_valider_longueur_valid(self):
        """Longueur valide."""
        is_valid, msg = valider_longueur_texte("hello", min_length=1, max_length=10)
        assert is_valid is True
        assert msg == ""

    def test_valider_longueur_too_short(self):
        """Trop court."""
        is_valid, msg = valider_longueur_texte("ab", min_length=3)
        assert is_valid is False
        assert "3" in msg

    def test_valider_longueur_too_long(self):
        """Trop long."""
        is_valid, msg = valider_longueur_texte("hello world", max_length=5)
        assert is_valid is False

    def test_valider_longueur_exact_min(self):
        """Exactement le minimum."""
        is_valid, _ = valider_longueur_texte("abc", min_length=3)
        assert is_valid is True

    def test_valider_longueur_exact_max(self):
        """Exactement le maximum."""
        is_valid, _ = valider_longueur_texte("abcde", max_length=5)
        assert is_valid is True

    def test_valider_longueur_empty(self):
        """Chaîne vide."""
        is_valid_fail, _ = valider_longueur_texte("", min_length=1)
        is_valid_ok, _ = valider_longueur_texte("", min_length=0)
        assert is_valid_fail is False
        assert is_valid_ok is True
