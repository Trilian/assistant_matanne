"""
Tests unitaires pour text.py

Module: src.utils.formatters.text
"""

import pytest
from src.utils.formatters.text import (
    tronquer,
    nettoyer_texte,
    generer_slug,
    extraire_nombre,
    capitaliser_premiere,
    capitaliser_mots,
)


class TestText:
    """Tests pour le module text."""

    def test_tronquer(self):
        """Test de la fonction tronquer."""
        assert tronquer("Un texte très long", length=10) == "Un text..."
        assert tronquer("Court", length=10) == "Court"

    def test_nettoyer_texte(self):
        """Test de la fonction nettoyer_texte."""
        assert "<script>" not in nettoyer_texte("<script>alert('xss')</script>")
        assert nettoyer_texte("") == ""

    def test_generer_slug(self):
        """Test de la fonction generer_slug."""
        assert generer_slug("Tarte aux Pommes") == "tarte-aux-pommes"
        assert generer_slug("Café Crème") == "cafe-creme"

    def test_extraire_nombre(self):
        """Test de la fonction extraire_nombre."""
        assert extraire_nombre("2.5 kg") == 2.5
        assert extraire_nombre("Prix: 10,50â‚¬") == 10.5
        assert extraire_nombre("") is None

    def test_capitaliser_premiere(self):
        """Test de la fonction capitaliser_premiere."""
        assert capitaliser_premiere("tomate") == "Tomate"
        assert capitaliser_premiere("") == ""

    def test_capitaliser_mots(self):
        """Test de la fonction capitaliser_mots."""
        assert capitaliser_mots("bonjour le monde") == "Bonjour Le Monde"
        assert capitaliser_mots("") == ""
