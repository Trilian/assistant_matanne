"""
Tests de couverture pour barcode_logic.py
Objectif: Atteindre â‰¥80% de couverture
"""

from src.modules.outils.logic.barcode_logic import (
    detecter_pays_origine,
    detecter_type_code_barres,
    extraire_infos_produit,
    formater_code_barres,
    nettoyer_code_barres,
    suggerer_categorie_produit,
    valider_checksum_ean13,
    valider_code_barres,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDER CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderCodeBarres:
    """Tests pour valider_code_barres."""

    def test_code_vide(self):
        """Code vide retourne erreur."""
        valide, erreur = valider_code_barres("")
        assert valide is False
        assert "vide" in erreur.lower()

    def test_code_none(self):
        """Code None retourne erreur."""
        valide, erreur = valider_code_barres(None)
        assert valide is False

    def test_code_trop_court(self):
        """Code trop court retourne erreur."""
        valide, erreur = valider_code_barres("1234567")
        assert valide is False
        assert "trop court" in erreur.lower()

    def test_code_non_numerique(self):
        """Code avec lettres retourne erreur."""
        valide, erreur = valider_code_barres("12345678AB")
        assert valide is False
        assert "chiffres" in erreur.lower()

    def test_code_longueur_invalide(self):
        """Code de longueur invalide."""
        valide, erreur = valider_code_barres("1234567890")  # 10 chiffres
        assert valide is False
        assert "invalide" in erreur.lower()

    def test_code_ean8_valide(self):
        """Code EAN-8 valide."""
        valide, erreur = valider_code_barres("12345678")
        assert valide is True
        assert erreur is None

    def test_code_upc_a_valide(self):
        """Code UPC-A valide (12 chiffres)."""
        valide, erreur = valider_code_barres("012345678901")
        assert valide is True
        assert erreur is None

    def test_code_ean13_valide(self):
        """Code EAN-13 valide."""
        valide, erreur = valider_code_barres("3401234567890")
        assert valide is True

    def test_code_itf14_valide(self):
        """Code ITF-14 valide (14 chiffres)."""
        valide, erreur = valider_code_barres("01234567890123")
        assert valide is True

    def test_code_avec_espaces(self):
        """Code avec espaces est nettoyÃ©."""
        valide, erreur = valider_code_barres("  12345678  ")
        assert valide is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDER CHECKSUM EAN-13
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderChecksumEan13:
    """Tests pour valider_checksum_ean13."""

    def test_longueur_incorrecte(self):
        """Code non EAN-13 retourne False."""
        assert valider_checksum_ean13("12345678") is False

    def test_checksum_valide(self):
        """Code avec checksum valide."""
        # Exemple valide: 3017620429484 (Nutella)
        assert valider_checksum_ean13("3017620429484") is True

    def test_checksum_invalide(self):
        """Code avec checksum invalide."""
        # Modifier le dernier chiffre pour rendre invalide
        assert valider_checksum_ean13("3017620429483") is False

    def test_code_non_numerique(self):
        """Code non numÃ©rique retourne False."""
        assert valider_checksum_ean13("301762042948A") is False

    def test_code_vide(self):
        """Code vide retourne False."""
        assert valider_checksum_ean13("") is False

    def test_calcul_checksum_zero(self):
        """VÃ©rifie le cas oÃ¹ checksum devient 0."""
        # Trouver un code oÃ¹ (10 - total%10) = 10 â†’ 0
        assert valider_checksum_ean13("0000000000000") is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DETECTER TYPE CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDetecterTypeCodeBarres:
    """Tests pour detecter_type_code_barres."""

    def test_ean8(self):
        """DÃ©tecte EAN-8."""
        assert detecter_type_code_barres("12345678") == "EAN-8"

    def test_upc_a(self):
        """DÃ©tecte UPC-A."""
        assert detecter_type_code_barres("012345678901") == "UPC-A"

    def test_ean13(self):
        """DÃ©tecte EAN-13."""
        assert detecter_type_code_barres("3401234567890") == "EAN-13"

    def test_itf14(self):
        """DÃ©tecte ITF-14."""
        assert detecter_type_code_barres("01234567890123") == "ITF-14"

    def test_inconnu(self):
        """Type inconnu pour longueur non standard."""
        assert detecter_type_code_barres("123456") == "Inconnu"
        assert detecter_type_code_barres("1234567890") == "Inconnu"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DETECTER PAYS ORIGINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDetecterPaysOrigine:
    """Tests pour detecter_pays_origine."""

    def test_longueur_incorrecte(self):
        """Code non EAN-13 retourne None."""
        assert detecter_pays_origine("12345678") is None

    def test_france(self):
        """DÃ©tecte produit franÃ§ais."""
        assert detecter_pays_origine("3401234567890") == "France"
        assert detecter_pays_origine("3501234567890") == "France"

    def test_allemagne(self):
        """DÃ©tecte produit allemand."""
        assert detecter_pays_origine("4001234567890") == "Allemagne"
        assert detecter_pays_origine("4401234567890") == "Allemagne"

    def test_royaume_uni(self):
        """DÃ©tecte produit UK."""
        assert detecter_pays_origine("5001234567890") == "Royaume-Uni"

    def test_italie(self):
        """DÃ©tecte produit italien."""
        assert detecter_pays_origine("8001234567890") == "Italie"

    def test_espagne(self):
        """DÃ©tecte produit espagnol."""
        assert detecter_pays_origine("8401234567890") == "Espagne"

    def test_chine(self):
        """DÃ©tecte produit chinois."""
        assert detecter_pays_origine("6901234567890") == "Chine"

    def test_japon(self):
        """DÃ©tecte produit japonais."""
        assert detecter_pays_origine("4501234567890") == "Japon"
        assert detecter_pays_origine("4901234567890") == "Japon"

    def test_belgique(self):
        """DÃ©tecte produit belge."""
        assert detecter_pays_origine("5401234567890") == "Belgique/Luxembourg"

    def test_suisse(self):
        """DÃ©tecte produit suisse."""
        assert detecter_pays_origine("7601234567890") == "Suisse"

    def test_pays_inconnu(self):
        """Pays non reconnu retourne None."""
        # PrÃ©fixe non mappÃ©
        assert detecter_pays_origine("0001234567890") is None

    def test_prefixe_simple(self):
        """Teste prÃ©fixes Ã  valeur unique."""
        assert detecter_pays_origine("4711234567890") == "TaÃ¯wan"
        assert detecter_pays_origine("5281234567890") == "Liban"
        assert detecter_pays_origine("5391234567890") == "Irlande"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMATER CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormaterCodeBarres:
    """Tests pour formater_code_barres."""

    def test_formater_ean13(self):
        """Formate EAN-13 avec espaces."""
        result = formater_code_barres("3017620429484")
        assert result == "301 7620 42948 4"

    def test_formater_upc_a(self):
        """Formate UPC-A avec espaces."""
        result = formater_code_barres("012345678905")
        assert result == "0 12345 67890 5"

    def test_formater_ean8(self):
        """Formate EAN-8 avec espaces."""
        result = formater_code_barres("12345678")
        assert result == "1234 5678"

    def test_formater_itf14(self):
        """Formate ITF-14 avec espaces."""
        result = formater_code_barres("01234567890123")
        assert result == "01 234567 89012 3"

    def test_formater_autre_longueur(self):
        """Code d'autre longueur retournÃ© tel quel."""
        result = formater_code_barres("123456")
        assert result == "123456"

    def test_formater_avec_espaces(self):
        """Code avec espaces est nettoyÃ© avant formatage."""
        result = formater_code_barres("  12345678  ")
        assert result == "1234 5678"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS NETTOYER CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNettoyerCodeBarres:
    """Tests pour nettoyer_code_barres."""

    def test_code_propre(self):
        """Code dÃ©jÃ  propre reste inchangÃ©."""
        assert nettoyer_code_barres("3017620429484") == "3017620429484"

    def test_code_avec_espaces(self):
        """Supprime les espaces."""
        assert nettoyer_code_barres("301 7620 42948 4") == "3017620429484"

    def test_code_avec_tirets(self):
        """Supprime les tirets."""
        assert nettoyer_code_barres("301-7620-42948-4") == "3017620429484"

    def test_code_avec_lettres(self):
        """Supprime les lettres."""
        assert nettoyer_code_barres("ABC123DEF456") == "123456"

    def test_code_complexe(self):
        """Nettoie un code avec mÃ©lange."""
        assert nettoyer_code_barres("EAN: 301 7620-42948-4") == "3017620429484"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXTRAIRE INFOS PRODUIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtraireInfosProduit:
    """Tests pour extraire_infos_produit."""

    def test_code_invalide(self):
        """Code invalide retourne erreur."""
        result = extraire_infos_produit("")
        assert result["valide"] is False
        assert "erreur" in result

    def test_code_ean13_complet(self):
        """Extrait toutes les infos d'un EAN-13."""
        result = extraire_infos_produit("3017620429484")

        assert result["valide"] is True
        assert result["code"] == "3017620429484"
        assert result["type"] == "EAN-13"
        assert result["pays_origine"] == "France"
        assert result["checksum_valide"] is True
        assert result["longueur"] == 13
        assert " " in result["code_formate"]  # FormatÃ© avec espaces

    def test_code_ean8(self):
        """Extrait infos d'un EAN-8."""
        result = extraire_infos_produit("12345678")

        assert result["valide"] is True
        assert result["type"] == "EAN-8"
        assert result["pays_origine"] is None  # Pas de pays pour EAN-8
        assert result["checksum_valide"] is None  # Pas vÃ©rifiÃ© pour EAN-8

    def test_code_upc_a(self):
        """Extrait infos d'un UPC-A."""
        result = extraire_infos_produit("012345678901")

        assert result["valide"] is True
        assert result["type"] == "UPC-A"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGERER CATEGORIE PRODUIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggererCategorieProduit:
    """Tests pour suggerer_categorie_produit."""

    def test_longueur_incorrecte(self):
        """Code non EAN-13 retourne None."""
        assert suggerer_categorie_produit("12345678") is None

    def test_produit_francais(self):
        """Produit franÃ§ais dÃ©tectÃ©."""
        assert suggerer_categorie_produit("3401234567890") == "Produit franÃ§ais"
        assert suggerer_categorie_produit("3501234567890") == "Produit franÃ§ais"

    def test_produit_importe(self):
        """Produit non franÃ§ais = importÃ©."""
        assert suggerer_categorie_produit("4001234567890") == "Produit importÃ©"
        assert suggerer_categorie_produit("5001234567890") == "Produit importÃ©"
