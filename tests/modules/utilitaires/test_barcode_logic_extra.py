"""
Tests complémentaires pour barcode_logic.py — fonctions non couvertes.

Couvre: formater_code_barres, nettoyer_code_barres, extraire_infos_produit, suggerer_categorie_produit
"""

import pytest

from src.modules.utilitaires.barcode.logic import (
    extraire_infos_produit,
    formater_code_barres,
    nettoyer_code_barres,
    suggerer_categorie_produit,
)

# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormaterCodeBarres:
    """Tests pour formater_code_barres."""

    def test_ean13_formate(self):
        """EAN-13 formaté: XXX XXXX XXXXX X."""
        result = formater_code_barres("3017620422003")
        assert result == "301 7620 42200 3"

    def test_upc_a_formate(self):
        """UPC-A formaté: X XXXXX XXXXX X."""
        result = formater_code_barres("123456789012")
        assert result == "1 23456 78901 2"

    def test_ean8_formate(self):
        """EAN-8 formaté: XXXX XXXX."""
        result = formater_code_barres("12345678")
        assert result == "1234 5678"

    def test_itf14_formate(self):
        """ITF-14 formaté: XX XXXXXX XXXXX X."""
        result = formater_code_barres("12345678901234")
        assert result == "12 345678 90123 4"

    def test_longueur_non_standard_unchanged(self):
        """Longueur non standard retournée telle quelle."""
        assert formater_code_barres("1234567890") == "1234567890"
        assert formater_code_barres("123") == "123"

    def test_strip_espaces(self):
        """Supprime les espaces avant formatage."""
        result = formater_code_barres("  3017620422003  ")
        assert result == "301 7620 42200 3"


class TestNettoyerCodeBarres:
    """Tests pour nettoyer_code_barres."""

    def test_supprime_espaces(self):
        """Supprime tous les espaces."""
        assert nettoyer_code_barres("123 456 789") == "123456789"

    def test_supprime_tirets(self):
        """Supprime les tirets."""
        assert nettoyer_code_barres("123-456-789") == "123456789"

    def test_supprime_tout_non_digit(self):
        """Garde uniquement les chiffres."""
        assert nettoyer_code_barres("ABC123def456") == "123456"

    def test_code_propre_unchanged(self):
        """Code déjà propre reste inchangé."""
        assert nettoyer_code_barres("1234567890123") == "1234567890123"

    def test_code_vide(self):
        """Code vide retourne vide."""
        assert nettoyer_code_barres("") == ""

    def test_que_lettres_retourne_vide(self):
        """Uniquement des lettres retourne vide."""
        assert nettoyer_code_barres("abcdef") == ""


# ═══════════════════════════════════════════════════════════
# TESTS EXTRACTION INFOS
# ═══════════════════════════════════════════════════════════


class TestExtraireInfosProduit:
    """Tests pour extraire_infos_produit."""

    def test_code_invalide(self):
        """Code invalide retourne {valide: False, erreur: ...}."""
        result = extraire_infos_produit("")
        assert result["valide"] is False
        assert "erreur" in result

    def test_ean13_complet(self):
        """EAN-13 extrait toutes les infos."""
        result = extraire_infos_produit("3017620422003")

        assert result["valide"] is True
        assert result["code"] == "3017620422003"
        assert result["type"] == "EAN-13"
        assert result["pays_origine"] == "France"
        assert result["checksum_valide"] is True
        assert result["longueur"] == 13
        assert "code_formate" in result

    def test_ean8_partiel(self):
        """EAN-8 n'a pas de pays ni checksum."""
        result = extraire_infos_produit("12345678")

        assert result["valide"] is True
        assert result["type"] == "EAN-8"
        assert result["pays_origine"] is None
        assert result["checksum_valide"] is None
        assert result["longueur"] == 8

    def test_upc_a_partiel(self):
        """UPC-A n'a pas de pays."""
        result = extraire_infos_produit("123456789012")

        assert result["valide"] is True
        assert result["type"] == "UPC-A"
        assert result["pays_origine"] is None


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTION CATÉGORIE
# ═══════════════════════════════════════════════════════════


class TestSuggererCategorieProduit:
    """Tests pour suggerer_categorie_produit."""

    def test_non_ean13(self):
        """Retourne None si pas EAN-13."""
        assert suggerer_categorie_produit("12345678") is None
        assert suggerer_categorie_produit("123456789012") is None
        assert suggerer_categorie_produit("12345678901234") is None

    def test_produit_francais(self):
        """Préfixe 300-379 = produit français."""
        assert suggerer_categorie_produit("3017620422003") == "Produit français"
        assert suggerer_categorie_produit("3400140000008") == "Produit français"
        assert suggerer_categorie_produit("3790000000000") == "Produit français"

    def test_produit_importe(self):
        """Préfixe hors 300-379 = produit importé."""
        assert suggerer_categorie_produit("4006381333931") == "Produit importe"  # Allemagne
        assert suggerer_categorie_produit("5000112637939") == "Produit importe"  # UK
        assert suggerer_categorie_produit("0012345678905") == "Produit importe"  # USA

    def test_code_vide(self):
        """Code vide retourne None."""
        assert suggerer_categorie_produit("") is None
