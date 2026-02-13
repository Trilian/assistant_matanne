"""
Tests pour src/modules/outils/barcode_utils.py
"""

import pytest

from src.modules.outils.barcode_utils import (
    detecter_pays_origine,
    detecter_type_code_barres,
    extraire_infos_produit,
    formater_code_barres,
    nettoyer_code_barres,
    suggerer_categorie_produit,
    valider_checksum_ean13,
    valider_code_barres,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def code_ean13_france_valide():
    """Fixture: code EAN-13 français valide avec checksum correct"""
    # Code avec checksum valide: 3401500400121
    return "3401500400121"


@pytest.fixture
def code_ean8_valide():
    """Fixture: code EAN-8 valide"""
    return "12345678"


@pytest.fixture
def code_upc_a_valide():
    """Fixture: code UPC-A valide (12 chiffres)"""
    return "012345678912"


@pytest.fixture
def code_itf14_valide():
    """Fixture: code ITF-14 valide (14 chiffres)"""
    return "01234567891234"


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION CODE-BARRES
# ═══════════════════════════════════════════════════════════


class TestValiderCodeBarres:
    """Tests pour la fonction valider_code_barres"""

    def test_code_vide(self):
        """Teste qu'un code vide est invalide"""
        valide, erreur = valider_code_barres("")
        assert valide is False
        assert "vide" in erreur.lower()

    def test_code_none(self):
        """Teste qu'un code None est invalide"""
        valide, erreur = valider_code_barres(None)
        assert valide is False

    def test_code_trop_court(self):
        """Teste qu'un code trop court est invalide"""
        valide, erreur = valider_code_barres("1234567")
        assert valide is False
        assert "court" in erreur.lower()

    def test_code_non_numerique(self):
        """Teste qu'un code non numérique est invalide"""
        valide, erreur = valider_code_barres("12345ABC90")
        assert valide is False
        assert "chiffres" in erreur.lower()

    def test_longueur_invalide_9(self):
        """Teste qu'une longueur de 9 est invalide"""
        valide, erreur = valider_code_barres("123456789")
        assert valide is False
        assert "Longueur invalide" in erreur

    def test_longueur_invalide_10(self):
        """Teste qu'une longueur de 10 est invalide"""
        valide, erreur = valider_code_barres("1234567890")
        assert valide is False

    def test_longueur_invalide_11(self):
        """Teste qu'une longueur de 11 est invalide"""
        valide, erreur = valider_code_barres("12345678901")
        assert valide is False

    def test_ean8_valide(self, code_ean8_valide):
        """Teste qu'un code EAN-8 est valide"""
        valide, erreur = valider_code_barres(code_ean8_valide)
        assert valide is True
        assert erreur is None

    def test_upc_a_valide(self, code_upc_a_valide):
        """Teste qu'un code UPC-A est valide"""
        valide, erreur = valider_code_barres(code_upc_a_valide)
        assert valide is True

    def test_ean13_valide(self, code_ean13_france_valide):
        """Teste qu'un code EAN-13 est valide"""
        valide, erreur = valider_code_barres(code_ean13_france_valide)
        assert valide is True

    def test_itf14_valide(self, code_itf14_valide):
        """Teste qu'un code ITF-14 est valide"""
        valide, erreur = valider_code_barres(code_itf14_valide)
        assert valide is True

    def test_code_avec_espaces(self):
        """Teste qu'un code avec espaces est nettoyé"""
        valide, erreur = valider_code_barres("  12345678  ")
        assert valide is True


# ═══════════════════════════════════════════════════════════
# TESTS CHECKSUM EAN-13
# ═══════════════════════════════════════════════════════════


class TestValiderChecksumEan13:
    """Tests pour la fonction valider_checksum_ean13"""

    def test_longueur_incorrecte(self):
        """Teste qu'un code de mauvaise longueur retourne False"""
        assert valider_checksum_ean13("12345678") is False
        assert valider_checksum_ean13("123456789012") is False
        assert valider_checksum_ean13("12345678901234") is False

    def test_checksum_valide(self):
        """Teste un code EAN-13 avec checksum valide"""
        # 5901234123457 est un exemple standard avec checksum valide
        assert valider_checksum_ean13("5901234123457") is True

    def test_checksum_invalide(self):
        """Teste un code EAN-13 avec checksum invalide"""
        # Changeons le dernier chiffre
        assert valider_checksum_ean13("5901234123456") is False

    def test_code_non_numerique(self):
        """Teste qu'un code non numérique retourne False"""
        assert valider_checksum_ean13("590123412345A") is False

    def test_code_vide(self):
        """Teste qu'un code vide retourne False"""
        assert valider_checksum_ean13("") is False

    def test_plusieurs_codes_valides(self):
        """Teste plusieurs codes EAN-13 valides connus"""
        codes_valides = [
            "4006381333931",  # Exemple allemand
            "8710398509857",  # Exemple néerlandais
        ]
        for code in codes_valides:
            assert valider_checksum_ean13(code) is True, f"Code {code} devrait être valide"


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION TYPE CODE-BARRES
# ═══════════════════════════════════════════════════════════


class TestDetecterTypeCodeBarres:
    """Tests pour la fonction detecter_type_code_barres"""

    def test_ean8(self, code_ean8_valide):
        """Teste la détection EAN-8"""
        assert detecter_type_code_barres(code_ean8_valide) == "EAN-8"

    def test_upc_a(self, code_upc_a_valide):
        """Teste la détection UPC-A"""
        assert detecter_type_code_barres(code_upc_a_valide) == "UPC-A"

    def test_ean13(self, code_ean13_france_valide):
        """Teste la détection EAN-13"""
        assert detecter_type_code_barres(code_ean13_france_valide) == "EAN-13"

    def test_itf14(self, code_itf14_valide):
        """Teste la détection ITF-14"""
        assert detecter_type_code_barres(code_itf14_valide) == "ITF-14"

    def test_longueur_inconnue(self):
        """Teste la détection pour une longueur inconnue"""
        assert detecter_type_code_barres("123456789") == "Inconnu"
        assert detecter_type_code_barres("12345") == "Inconnu"
        assert detecter_type_code_barres("123456789012345") == "Inconnu"


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION PAYS D'ORIGINE
# ═══════════════════════════════════════════════════════════


class TestDetecterPaysOrigine:
    """Tests pour la fonction detecter_pays_origine"""

    def test_code_non_ean13(self):
        """Teste qu'un code non EAN-13 retourne None"""
        assert detecter_pays_origine("12345678") is None
        assert detecter_pays_origine("012345678912") is None

    def test_code_france(self):
        """Teste la détection France (300-379)"""
        assert detecter_pays_origine("3001234567890") == "France"
        assert detecter_pays_origine("3501234567890") == "France"
        assert detecter_pays_origine("3791234567890") == "France"

    def test_code_allemagne(self):
        """Teste la détection Allemagne (400-440)"""
        assert detecter_pays_origine("4001234567890") == "Allemagne"
        assert detecter_pays_origine("4401234567890") == "Allemagne"

    def test_code_royaume_uni(self):
        """Teste la détection Royaume-Uni (500-509)"""
        assert detecter_pays_origine("5001234567890") == "Royaume-Uni"

    def test_code_chine(self):
        """Teste la détection Chine (690-699)"""
        assert detecter_pays_origine("6901234567890") == "Chine"
        assert detecter_pays_origine("6991234567890") == "Chine"

    def test_code_italie(self):
        """Teste la détection Italie (800-839)"""
        assert detecter_pays_origine("8001234567890") == "Italie"

    def test_code_espagne(self):
        """Teste la détection Espagne (840-849)"""
        assert detecter_pays_origine("8401234567890") == "Espagne"

    def test_code_pays_inconnu(self):
        """Teste qu'un préfixe inconnu retourne None"""
        assert detecter_pays_origine("0001234567890") is None
        assert detecter_pays_origine("9991234567890") is None

    def test_code_prefixe_non_numerique(self):
        """Teste qu'un préfixe non numérique retourne None (ValueError)"""
        # Code de 13 caractères avec préfixe non numérique pour déclencher ValueError
        assert detecter_pays_origine("ABC1234567890") is None
        assert detecter_pays_origine("X001234567890") is None


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormaterCodeBarres:
    """Tests pour la fonction formater_code_barres"""

    def test_format_ean13(self):
        """Teste le formatage EAN-13"""
        result = formater_code_barres("1234567890123")
        assert result == "123 4567 89012 3"

    def test_format_upc_a(self):
        """Teste le formatage UPC-A"""
        result = formater_code_barres("012345678912")
        assert result == "0 12345 67891 2"

    def test_format_ean8(self):
        """Teste le formatage EAN-8"""
        result = formater_code_barres("12345678")
        assert result == "1234 5678"

    def test_format_itf14(self):
        """Teste le formatage ITF-14"""
        result = formater_code_barres("01234567891234")
        assert result == "01 234567 89123 4"

    def test_format_autre_longueur(self):
        """Teste qu'une longueur non standard retourne le code tel quel"""
        code = "123456789"
        assert formater_code_barres(code) == code

    def test_code_avec_espaces(self):
        """Teste que les espaces sont nettoyés avant formatage"""
        result = formater_code_barres("  12345678  ")
        assert result == "1234 5678"


# ═══════════════════════════════════════════════════════════
# TESTS NETTOYAGE
# ═══════════════════════════════════════════════════════════


class TestNettoyerCodeBarres:
    """Tests pour la fonction nettoyer_code_barres"""

    def test_code_propre(self):
        """Teste qu'un code propre reste inchangé"""
        assert nettoyer_code_barres("12345678") == "12345678"

    def test_code_avec_espaces(self):
        """Teste la suppression des espaces"""
        assert nettoyer_code_barres("1234 5678") == "12345678"
        assert nettoyer_code_barres(" 1234 5678 ") == "12345678"

    def test_code_avec_tirets(self):
        """Teste la suppression des tirets"""
        assert nettoyer_code_barres("1234-5678") == "12345678"
        assert nettoyer_code_barres("1234-56-78") == "12345678"

    def test_code_avec_lettres(self):
        """Teste la suppression des lettres"""
        assert nettoyer_code_barres("1234ABC5678") == "12345678"

    def test_code_mixte(self):
        """Teste la suppression de caractères mixtes"""
        assert nettoyer_code_barres("12-34 AB 56-78") == "12345678"

    def test_code_vide(self):
        """Teste avec un code vide"""
        assert nettoyer_code_barres("") == ""

    def test_code_sans_chiffres(self):
        """Teste avec un code sans chiffres"""
        assert nettoyer_code_barres("ABC-DEF") == ""


# ═══════════════════════════════════════════════════════════
# TESTS EXTRACTION INFOS PRODUIT
# ═══════════════════════════════════════════════════════════


class TestExtraireInfosProduit:
    """Tests pour la fonction extraire_infos_produit"""

    def test_code_invalide(self):
        """Teste qu'un code invalide retourne l'erreur"""
        result = extraire_infos_produit("123")
        assert result["valide"] is False
        assert "erreur" in result

    def test_code_ean13_valide(self):
        """Teste l'extraction pour un code EAN-13"""
        result = extraire_infos_produit("5901234123457")
        assert result["valide"] is True
        assert result["type"] == "EAN-13"
        assert result["longueur"] == 13
        assert "code_formate" in result
        assert "pays_origine" in result
        assert "checksum_valide" in result

    def test_code_ean8_valide(self, code_ean8_valide):
        """Teste l'extraction pour un code EAN-8"""
        result = extraire_infos_produit(code_ean8_valide)
        assert result["valide"] is True
        assert result["type"] == "EAN-8"
        assert result["longueur"] == 8
        assert result["pays_origine"] is None
        assert result["checksum_valide"] is None

    def test_code_upc_valide(self, code_upc_a_valide):
        """Teste l'extraction pour un code UPC-A"""
        result = extraire_infos_produit(code_upc_a_valide)
        assert result["valide"] is True
        assert result["type"] == "UPC-A"

    def test_contient_code_formate(self, code_ean13_france_valide):
        """Teste que le code formaté est présent"""
        result = extraire_infos_produit(code_ean13_france_valide)
        assert "code_formate" in result
        assert " " in result["code_formate"]

    def test_checksum_valide_pour_ean13(self):
        """Teste le checksum pour un EAN-13 valide"""
        result = extraire_infos_produit("5901234123457")
        assert result["checksum_valide"] is True

    def test_checksum_invalide_pour_ean13(self):
        """Teste le checksum pour un EAN-13 invalide"""
        result = extraire_infos_produit("5901234123456")
        assert result["checksum_valide"] is False


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS CATÉGORIE
# ═══════════════════════════════════════════════════════════


class TestSuggererCategorieProduit:
    """Tests pour la fonction suggerer_categorie_produit"""

    def test_code_non_ean13(self):
        """Teste qu'un code non EAN-13 retourne None"""
        assert suggerer_categorie_produit("12345678") is None
        assert suggerer_categorie_produit("012345678912") is None

    def test_produit_francais(self):
        """Teste la suggestion pour un produit français"""
        result = suggerer_categorie_produit("3001234567890")
        assert result == "Produit français"

    def test_produit_francais_autres_prefixes(self):
        """Teste pour les autres préfixes français"""
        assert suggerer_categorie_produit("3501234567890") == "Produit français"
        assert suggerer_categorie_produit("3791234567890") == "Produit français"

    def test_produit_importe(self):
        """Teste la suggestion pour un produit importé"""
        result = suggerer_categorie_produit("4001234567890")  # Allemagne
        assert result == "Produit importe"

    def test_code_vide_longueur(self):
        """Teste avec un code de mauvaise longueur"""
        assert suggerer_categorie_produit("") is None
        assert suggerer_categorie_produit("123") is None
