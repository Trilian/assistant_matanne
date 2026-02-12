"""
Tests complets pour src/services/barcode.py
Objectif: couverture >80%
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODELES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBarcodeData:
    """Tests pour BarcodeData model."""
    
    def test_barcode_data_valid(self):
        """Test valid barcode data creation."""
        from src.services.barcode import BarcodeData
        
        data = BarcodeData(code="3017760000000")
        
        assert data.code == "3017760000000"
        assert data.type_code == "EAN-13"
        assert data.source == "scanner"
        assert isinstance(data.timestamp, datetime)
    
    def test_barcode_data_custom_values(self):
        """Test custom values for barcode data."""
        from src.services.barcode import BarcodeData
        
        ts = datetime(2024, 1, 1)
        data = BarcodeData(
            code="12345678",
            type_code="EAN-8",
            source="manuel",
            timestamp=ts
        )
        
        assert data.code == "12345678"
        assert data.type_code == "EAN-8"
        assert data.source == "manuel"
    
    def test_barcode_data_code_too_short(self):
        """Test minimum length validation."""
        from src.services.barcode import BarcodeData
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            BarcodeData(code="1234567")  # Too short


class TestBarcodeArticle:
    """Tests pour BarcodeArticle model."""
    
    def test_barcode_article_defaults(self):
        """Test default values for barcode article."""
        from src.services.barcode import BarcodeArticle
        
        article = BarcodeArticle(
            barcode="3017760000000",
            article_id=1,
            nom_article="Test Article",
            categorie="Alimentation"
        )
        
        assert article.quantite_defaut == 1.0
        assert article.unite_defaut == "unitÃ©"
        assert article.lieu_stockage == "Placard"
        assert article.prix_unitaire is None
    
    def test_barcode_article_custom(self):
        """Test custom values for barcode article."""
        from src.services.barcode import BarcodeArticle
        
        article = BarcodeArticle(
            barcode="3017760000000",
            article_id=1,
            nom_article="Lait",
            quantite_defaut=2.0,
            unite_defaut="L",
            categorie="Produits laitiers",
            prix_unitaire=1.50,
            date_peremption_jours=7,
            lieu_stockage="Frigo"
        )
        
        assert article.quantite_defaut == 2.0
        assert article.prix_unitaire == 1.50
        assert article.lieu_stockage == "Frigo"


class TestBarcodeRecette:
    """Tests pour BarcodeRecette model."""
    
    def test_barcode_recette_basic(self):
        """Test basic barcode recette."""
        from src.services.barcode import BarcodeRecette
        
        recette = BarcodeRecette(
            barcode="3017760000000",
            recette_id=1,
            nom_recette="GÃ¢teau"
        )
        
        assert recette.barcode == "3017760000000"
        assert recette.recette_id == 1
        assert recette.nom_recette == "GÃ¢teau"
        assert recette.ingredient_detecete is None


class TestScanResultat:
    """Tests pour ScanResultat model."""
    
    def test_scan_resultat_article(self):
        """Test scan result for article."""
        from src.services.barcode import ScanResultat
        
        result = ScanResultat(
            barcode="3017760000000",
            type_scan="article",
            details={"nom": "Lait", "quantite": 1}
        )
        
        assert result.barcode == "3017760000000"
        assert result.type_scan == "article"
        assert result.details["nom"] == "Lait"
    
    def test_scan_resultat_inconnu(self):
        """Test scan result for unknown barcode."""
        from src.services.barcode import ScanResultat
        
        result = ScanResultat(
            barcode="9999999999999",
            type_scan="inconnu",
            details={"message": "Non trouvÃ©"}
        )
        
        assert result.type_scan == "inconnu"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDATION BARCODE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBarcodeValidation:
    """Tests for barcode validation methods."""
    
    def test_valider_barcode_ean13_valid(self):
        """Test valid EAN-13 validation."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # Valid EAN-13
        valid, code_type = service.valider_barcode("3017760000000")
        
        assert valid is True
        assert code_type == "EAN-13"
    
    def test_valider_barcode_ean13_invalid_checksum(self):
        """Test EAN-13 with invalid checksum."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        valid, reason = service.valider_barcode("3017760000001")
        
        assert valid is False
        assert "Checksum" in reason
    
    def test_valider_barcode_ean8_valid(self):
        """Test valid EAN-8 validation."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # Create valid EAN-8 (need to calculate checksum)
        # Using known valid EAN-8: 96385074
        valid, code_type = service.valider_barcode("96385074")
        
        assert valid is True
        assert code_type == "EAN-8"
    
    def test_valider_barcode_ean8_invalid(self):
        """Test EAN-8 with invalid checksum."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        valid, reason = service.valider_barcode("12345679")
        
        assert valid is False
        assert "Checksum" in reason
    
    def test_valider_barcode_upc_valid(self):
        """Test valid UPC validation."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # UPC is 12 digits - using valid UPC-A
        valid, code_type = service.valider_barcode("012345678905")
        
        assert valid is True
        assert code_type == "UPC"
    
    def test_valider_barcode_upc_invalid(self):
        """Test UPC with invalid checksum."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        valid, reason = service.valider_barcode("012345678901")
        
        assert valid is False
        assert "Checksum" in reason
    
    def test_valider_barcode_qr(self):
        """Test QR code validation."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        valid, code_type = service.valider_barcode("ABCD123456-XYZ")
        
        assert valid is True
        assert code_type == "QR"
    
    def test_valider_barcode_code128(self):
        """Test CODE128 validation - utilise 8-9 caractÃ¨res pour Ã©viter QR (10+)."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # CODE128: 8+ caractÃ¨res alphanum ; QR: 10+ caractÃ¨res
        # Donc on utilise 9 caractÃ¨res pour Ã©viter le pattern QR
        valid, code_type = service.valider_barcode("ABCD12345")
        
        assert valid is True
        assert code_type == "CODE128"
    
    def test_valider_barcode_code39(self):
        """Test CODE39 validation."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # CODE39 accepts alphanumeric and some symbols
        valid, code_type = service.valider_barcode("ABC-123.456$")
        
        assert valid is True
        assert code_type == "CODE39"
    
    def test_valider_barcode_unknown_format(self):
        """Test unknown barcode format."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        valid, reason = service.valider_barcode("invalid!")
        
        assert valid is False
        assert "non reconnu" in reason


class TestChecksumValidation:
    """Tests for checksum validation methods."""
    
    def test_checksum_ean13_true(self):
        """Test EAN-13 checksum for valid code."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_ean13("3017760000000")
        
        assert result is True
    
    def test_checksum_ean13_false_wrong_length(self):
        """Test EAN-13 checksum with wrong length."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_ean13("12345")
        
        assert result is False
    
    def test_checksum_ean13_false_not_digits(self):
        """Test EAN-13 checksum with non-digits."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_ean13("123456789012A")
        
        assert result is False
    
    def test_checksum_ean8_false_wrong_length(self):
        """Test EAN-8 checksum with wrong length."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_ean8("12345")
        
        assert result is False
    
    def test_checksum_ean8_false_not_digits(self):
        """Test EAN-8 checksum with non-digits."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_ean8("1234567A")
        
        assert result is False
    
    def test_checksum_upc_false_wrong_length(self):
        """Test UPC checksum with wrong length."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_upc("12345")
        
        assert result is False
    
    def test_checksum_upc_false_not_digits(self):
        """Test UPC checksum with non-digits."""
        from src.services.barcode import BarcodeService
        
        result = BarcodeService._valider_checksum_upc("12345678901A")
        
        assert result is False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BARCODE SERVICE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBarcodeServiceInit:
    """Tests for BarcodeService initialization."""
    
    def test_service_init(self):
        """Test service initialization."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        assert service.cache_ttl == 3600
        assert service.barcode_mappings == {}


class TestBarcodeServiceScan:
    """Tests for scanner_code method."""
    
    def test_scanner_code_invalid_barcode(self):
        """Test scanning invalid barcode raises error."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurValidation
        
        service = BarcodeService()
        mock_session = Mock()
        
        with pytest.raises(ErreurValidation):
            service.scanner_code("invalid!", session=mock_session)
    
    def test_scanner_code_article_found(self):
        """Test scanning barcode finds article."""
        from src.services.barcode import BarcodeService, ScanResultat
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 2
        mock_article.unite = "L"
        mock_article.prix_unitaire = 1.50
        mock_article.date_peremption = datetime.now() + timedelta(days=7)
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with patch('src.services.barcode.obtenir_contexte_db') as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            result = service.scanner_code("3017760000000", session=mock_session)
        
        assert result.type_scan == "article"
        assert result.details["nom"] == "Lait"
    
    def test_scanner_code_not_found(self):
        """Test scanning unknown barcode."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with patch('src.services.barcode.obtenir_contexte_db') as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            result = service.scanner_code("3017760000000", session=mock_session)
        
        assert result.type_scan == "inconnu"


class TestBarcodeServiceArticleOperations:
    """Tests for article operations with barcodes."""
    
    def test_ajouter_article_par_barcode_invalid_code(self):
        """Test adding article with invalid barcode raises error."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurValidation
        
        service = BarcodeService()
        mock_session = Mock()
        
        with pytest.raises(ErreurValidation):
            service.ajouter_article_par_barcode(
                code="invalid!",
                nom="Test",
                session=mock_session
            )
    
    def test_ajouter_article_par_barcode_exists(self):
        """Test adding article with existing barcode raises error."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurValidation
        
        service = BarcodeService()
        
        mock_existing = Mock()
        mock_existing.nom = "Existing"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_existing
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ErreurValidation):
            service.ajouter_article_par_barcode(
                code="3017760000000",
                nom="New",
                session=mock_session
            )
    
    def test_incrementer_stock_barcode_not_found(self):
        """Test incrementing stock for unknown barcode raises error."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurNonTrouve
        
        service = BarcodeService()
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ErreurNonTrouve):
            service.incrementer_stock_barcode("3017760000000", session=mock_session)
    
    def test_incrementer_stock_barcode_success(self):
        """Test incrementing stock for known barcode."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        service.cache = Mock()  # Mock cache pour Ã©viter AttributeError
        
        mock_article = Mock()
        mock_article.nom = "Lait"
        mock_article.quantite = 2
        mock_article.unite = "L"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.incrementer_stock_barcode(
            "3017760000000",
            quantite=1.0,
            session=mock_session
        )
        
        assert result.quantite == 3
        service.cache.invalidate.assert_called_once()


class TestBarcodeServiceStockVerification:
    """Tests for stock verification methods."""
    
    def test_verifier_stock_barcode_not_found(self):
        """Test verifying stock for unknown barcode."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurNonTrouve
        
        service = BarcodeService()
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ErreurNonTrouve):
            service.verifier_stock_barcode("3017760000000", session=mock_session)
    
    def test_verifier_stock_barcode_critique(self):
        """Test stock status CRITIQUE when quantity is 0."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 0
        mock_article.unite = "L"
        mock_article.quantite_min = 1
        mock_article.date_peremption = None
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["etat_stock"] == "CRITIQUE"
    
    def test_verifier_stock_barcode_faible(self):
        """Test stock status FAIBLE when below minimum."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 1
        mock_article.unite = "L"
        mock_article.quantite_min = 2
        mock_article.date_peremption = None
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["etat_stock"] == "FAIBLE"
    
    def test_verifier_stock_barcode_ok(self):
        """Test stock status OK when sufficient."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 5
        mock_article.unite = "L"
        mock_article.quantite_min = 2
        mock_article.date_peremption = None
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["etat_stock"] == "OK"
    
    def test_verifier_stock_barcode_peremption_urgent(self):
        """Test expiration status URGENT."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 5
        mock_article.unite = "L"
        mock_article.quantite_min = 2
        mock_article.date_peremption = datetime.now() + timedelta(days=3)
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["peremption_etat"] == "URGENT"
    
    def test_verifier_stock_barcode_perime(self):
        """Test expiration status PÃ‰RIMÃ‰."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 5
        mock_article.unite = "L"
        mock_article.quantite_min = 2
        mock_article.date_peremption = datetime.now() - timedelta(days=1)
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["peremption_etat"] == "PÃ‰RIMÃ‰"
    
    def test_verifier_stock_barcode_peremption_bientot(self):
        """Test expiration status BIENTÃ”T."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Lait"
        mock_article.quantite = 5
        mock_article.unite = "L"
        mock_article.quantite_min = 2
        mock_article.date_peremption = datetime.now() + timedelta(days=15)
        mock_article.prix_unitaire = 1.50
        mock_article.emplacement = "Frigo"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.verifier_stock_barcode("3017760000000", session=mock_session)
        
        assert result["peremption_etat"] == "BIENTÃ”T"


class TestBarcodeServiceMappings:
    """Tests for barcode mapping operations."""
    
    def test_mettre_a_jour_barcode_invalid_code(self):
        """Test updating to invalid barcode."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurValidation
        
        service = BarcodeService()
        mock_session = Mock()
        
        with pytest.raises(ErreurValidation):
            service.mettre_a_jour_barcode(1, "invalid!", session=mock_session)
    
    def test_mettre_a_jour_barcode_not_found(self):
        """Test updating barcode for non-existent article."""
        from src.services.barcode import BarcodeService
        from src.core.errors_base import ErreurNonTrouve
        
        service = BarcodeService()
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ErreurNonTrouve):
            service.mettre_a_jour_barcode(1, "3017760000000", session=mock_session)
    
    def test_mettre_a_jour_barcode_success(self):
        """Test successfully updating barcode."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        service.cache = Mock()  # Mock cache pour Ã©viter AttributeError
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.code_barres = "OLD0000000000"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        result = service.mettre_a_jour_barcode(1, "3017760000000", session=mock_session)
        
        assert result.code_barres == "3017760000000"
        mock_session.commit.assert_called_once()
        service.cache.invalidate.assert_called_once()
    
    def test_lister_articles_avec_barcode(self):
        """Test listing articles with barcodes."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mock_article1 = Mock()
        mock_article1.id = 1
        mock_article1.nom = "Lait"
        mock_article1.code_barres = "3017760000000"
        mock_article1.quantite = 2
        mock_article1.unite = "L"
        mock_article1.categorie = "Laitier"
        
        mock_article2 = Mock()
        mock_article2.id = 2
        mock_article2.nom = "Pain"
        mock_article2.code_barres = "3017760000001"
        mock_article2.quantite = 1
        mock_article2.unite = "piÃ¨ce"
        mock_article2.categorie = "Boulangerie"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_article1, mock_article2]
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        
        with patch('src.services.barcode.obtenir_contexte_db') as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            result = service.lister_articles_avec_barcode(session=mock_session)
        
        assert len(result) == 2
        assert result[0]["nom"] == "Lait"


class TestBarcodeServiceExportImport:
    """Tests for export/import functionality."""
    
    def test_exporter_barcodes(self):
        """Test exporting barcodes to CSV."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        mock_session = Mock()
        
        # Mock lister_articles_avec_barcode
        mock_articles = [
            {"barcode": "3017760000000", "nom": "Lait", "quantite": 2, "unite": "L", "categorie": "Laitier"}
        ]
        
        with patch.object(service, 'lister_articles_avec_barcode', return_value=mock_articles):
            result = service.exporter_barcodes(session=mock_session)
        
        assert "barcode" in result
        assert "3017760000000" in result
        assert "Lait" in result
    
    def test_importer_barcodes_success(self):
        """Test importing barcodes from CSV."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        csv_content = "barcode,nom,quantite,unite,categorie\n3017760000000,Lait,2,L,Laitier"
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Not existing
        mock_session.query.return_value = mock_query
        
        with patch.object(service, 'ajouter_article_par_barcode') as mock_add:
            result = service.importer_barcodes(csv_content, session=mock_session)
        
        assert result["success"] == 1
        assert result["errors"] == []
    
    def test_importer_barcodes_with_error(self):
        """Test importing barcodes with error."""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        csv_content = "barcode,nom,quantite,unite,categorie\n3017760000000,Lait,2,L,Laitier"
        
        mock_session = Mock()
        
        with patch.object(service, 'ajouter_article_par_barcode', side_effect=Exception("Error")):
            result = service.importer_barcodes(csv_content, session=mock_session)
        
        assert result["success"] == 0
        assert len(result["errors"]) == 1
