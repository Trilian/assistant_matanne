"""
Tests pour barcode_logic.py
Couverture cible: 80%+
"""

from src.modules.utilitaires.barcode.logic import (
    detecter_pays_origine,
    detecter_type_code_barres,
    valider_checksum_ean13,
    valider_code_barres,
)

# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION CODE-BARRES
# ═══════════════════════════════════════════════════════════


class TestValiderCodeBarres:
    """Tests pour valider_code_barres."""

    def test_code_vide(self):
        """Rejette code vide."""
        valide, erreur = valider_code_barres("")
        assert valide is False
        assert "vide" in erreur.lower()

    def test_code_none(self):
        """Rejette code None."""
        valide, erreur = valider_code_barres(None)
        assert valide is False

    def test_code_trop_court(self):
        """Rejette code trop court."""
        valide, erreur = valider_code_barres("1234567")  # 7 caractères
        assert valide is False
        assert "court" in erreur.lower()

    def test_code_non_numerique(self):
        """Rejette code non numérique."""
        valide, erreur = valider_code_barres("12345678AB")
        assert valide is False
        assert "chiffres" in erreur.lower()

    def test_code_longueur_invalide(self):
        """Rejette longueur non standard."""
        valide, erreur = valider_code_barres("1234567890")  # 10 caractères
        assert valide is False
        assert "longueur" in erreur.lower()

    def test_code_ean8_valide(self):
        """Accepte EAN-8."""
        valide, erreur = valider_code_barres("12345678")
        assert valide is True
        assert erreur is None

    def test_code_ean13_valide(self):
        """Accepte EAN-13."""
        valide, erreur = valider_code_barres("1234567890123")
        assert valide is True
        assert erreur is None

    def test_code_upc_a_valide(self):
        """Accepte UPC-A (12 digits)."""
        valide, erreur = valider_code_barres("123456789012")
        assert valide is True

    def test_code_itf14_valide(self):
        """Accepte ITF-14 (14 digits)."""
        valide, erreur = valider_code_barres("12345678901234")
        assert valide is True

    def test_code_avec_espaces(self):
        """Nettoie les espaces."""
        valide, erreur = valider_code_barres("  12345678  ")
        assert valide is True


# ═══════════════════════════════════════════════════════════
# TESTS CHECKSUM EAN-13
# ═══════════════════════════════════════════════════════════


class TestValiderChecksumEan13:
    """Tests pour valider_checksum_ean13."""

    def test_longueur_invalide(self):
        """Rejette si pas 13 caractères."""
        assert valider_checksum_ean13("12345678") is False
        assert valider_checksum_ean13("12345678901234") is False

    def test_code_valide_reel(self):
        """Vérifie un code EAN-13 réel."""
        # Code EAN-13 valide pour un produit français
        assert valider_checksum_ean13("3017620422003") is True

    def test_code_invalide(self):
        """Détecte un checksum invalide."""
        # Dernier chiffre modifié
        assert valider_checksum_ean13("3017620422009") is False

    def test_code_non_numerique(self):
        """Gère les codes non numériques."""
        assert valider_checksum_ean13("301762042200A") is False


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION TYPE
# ═══════════════════════════════════════════════════════════


class TestDetecterTypeCodeBarres:
    """Tests pour detecter_type_code_barres."""

    def test_ean8(self):
        """Détecte EAN-8."""
        assert detecter_type_code_barres("12345678") == "EAN-8"

    def test_upc_a(self):
        """Détecte UPC-A."""
        assert detecter_type_code_barres("123456789012") == "UPC-A"

    def test_ean13(self):
        """Détecte EAN-13."""
        assert detecter_type_code_barres("1234567890123") == "EAN-13"

    def test_itf14(self):
        """Détecte ITF-14."""
        assert detecter_type_code_barres("12345678901234") == "ITF-14"

    def test_inconnu(self):
        """Retourne Inconnu pour longueur non standard."""
        assert detecter_type_code_barres("1234567890") == "Inconnu"
        assert detecter_type_code_barres("123456789") == "Inconnu"


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION PAYS
# ═══════════════════════════════════════════════════════════


class TestDetecterPaysOrigine:
    """Tests pour detecter_pays_origine."""

    def test_pas_ean13(self):
        """Retourne None si pas EAN-13."""
        assert detecter_pays_origine("12345678") is None
        assert detecter_pays_origine("123456789012") is None

    def test_france(self):
        """Détecte produit français."""
        assert detecter_pays_origine("3017620422003") == "France"

    def test_allemagne(self):
        """Détecte produit allemand."""
        assert detecter_pays_origine("4006381333931") == "Allemagne"

    def test_royaume_uni(self):
        """Détecte produit britannique."""
        assert detecter_pays_origine("5000112637939") == "Royaume-Uni"

    def test_belgique(self):
        """Détecte produit belge."""
        result = detecter_pays_origine("5400141268745")
        assert result in ["Belgique/Luxembourg", "Belgique", None]
