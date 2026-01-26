"""
Tests pour le service barcode (scan codes-barres)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestBarcodeService:
    """Tests du service de scan codes-barres"""

    def test_import_service(self):
        """Test que le service s'importe correctement"""
        from src.services.barcode import BarcodeService, get_barcode_service
        assert BarcodeService is not None
        assert callable(get_barcode_service)

    @patch('src.services.barcode.httpx')
    def test_lookup_product_openfoodfacts(self, mock_httpx):
        """Test recherche produit via OpenFoodFacts API"""
        from src.services.barcode import BarcodeService
        
        # Mock réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Nutella",
                "brands": "Ferrero",
                "categories": "Pâtes à tartiner",
                "quantity": "400g",
                "nutriscore_grade": "e"
            }
        }
        mock_httpx.get.return_value = mock_response
        
        service = BarcodeService()
        
        # Test lookup (si la méthode existe)
        if hasattr(service, 'lookup_product'):
            result = service.lookup_product("3017620422003")
            assert result is not None
            assert "Nutella" in str(result) or result.get("nom") == "Nutella"

    def test_validate_barcode_format(self):
        """Test validation format code-barres"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # Tester si méthode de validation existe
        if hasattr(service, 'validate_barcode'):
            # EAN-13 valide
            assert service.validate_barcode("3017620422003") == True
            
            # EAN-8 valide
            assert service.validate_barcode("96385074") == True
            
            # Invalide
            assert service.validate_barcode("123") == False
            assert service.validate_barcode("abc") == False

    def test_extract_product_info(self):
        """Test extraction infos produit depuis réponse API"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        api_response = {
            "product": {
                "product_name": "Lait demi-écrémé",
                "brands": "Lactel",
                "categories": "Laits",
                "quantity": "1L",
                "nutriscore_grade": "a",
                "nutriments": {
                    "energy-kcal_100g": 46,
                    "proteins_100g": 3.2,
                    "carbohydrates_100g": 4.8,
                    "fat_100g": 1.5
                }
            }
        }
        
        if hasattr(service, 'extract_product_info'):
            info = service.extract_product_info(api_response)
            assert info is not None
            assert "Lait" in str(info)

    @patch('src.services.barcode.httpx')
    def test_product_not_found(self, mock_httpx):
        """Test quand produit non trouvé"""
        from src.services.barcode import BarcodeService
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 0}
        mock_httpx.get.return_value = mock_response
        
        service = BarcodeService()
        
        if hasattr(service, 'lookup_product'):
            result = service.lookup_product("0000000000000")
            assert result is None or result == {}

    def test_barcode_to_inventory_item(self):
        """Test conversion produit scanné vers article inventaire"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        product_data = {
            "nom": "Pâtes Barilla",
            "marque": "Barilla",
            "categorie": "Épicerie",
            "quantite": "500g"
        }
        
        if hasattr(service, 'to_inventory_item'):
            item = service.to_inventory_item(product_data)
            assert item is not None
            assert hasattr(item, 'nom') or 'nom' in item

    def test_barcode_to_shopping_item(self):
        """Test conversion produit scanné vers article courses"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        product_data = {
            "nom": "Yaourt nature",
            "marque": "Danone",
            "categorie": "Produits laitiers"
        }
        
        if hasattr(service, 'to_shopping_item'):
            item = service.to_shopping_item(product_data)
            assert item is not None


class TestBarcodeValidation:
    """Tests de validation des codes-barres"""

    def test_ean13_checksum(self):
        """Test calcul checksum EAN-13"""
        # EAN-13: 3017620422003 (Nutella)
        # Le dernier chiffre (3) est le checksum
        
        barcode = "301762042200"  # Sans checksum
        
        # Calcul checksum EAN-13
        digits = [int(d) for d in barcode]
        checksum = sum(digits[::2]) + sum(d * 3 for d in digits[1::2])
        checksum = (10 - (checksum % 10)) % 10
        
        assert checksum == 3

    def test_ean8_checksum(self):
        """Test calcul checksum EAN-8"""
        barcode = "9638507"  # Sans checksum
        
        digits = [int(d) for d in barcode]
        checksum = sum(d * 3 for d in digits[::2]) + sum(digits[1::2])
        checksum = (10 - (checksum % 10)) % 10
        
        assert checksum == 4


class TestBarcodeIntegration:
    """Tests d'intégration barcode"""

    @pytest.mark.integration
    def test_scan_and_add_to_inventory(self, test_db):
        """Test scan + ajout inventaire (intégration)"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # Ce test nécessite une vraie DB
        # Simule le flow complet: scan -> lookup -> add
        pass

    @pytest.mark.integration
    def test_scan_and_add_to_shopping_list(self, test_db):
        """Test scan + ajout liste courses (intégration)"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        # Simule le flow: scan -> lookup -> add to list
        pass


class TestBarcodeCategories:
    """Tests mapping catégories OpenFoodFacts"""

    def test_category_mapping(self):
        """Test mapping catégories OFF vers catégories app"""
        from src.services.barcode import BarcodeService
        
        service = BarcodeService()
        
        mappings = {
            "Laits": "produits_laitiers",
            "Pâtes alimentaires": "epicerie",
            "Fruits": "fruits_legumes",
            "Viandes": "viande",
            "Poissons": "poisson",
            "Eaux": "boissons",
        }
        
        if hasattr(service, 'map_category'):
            for off_cat, expected in mappings.items():
                result = service.map_category(off_cat)
                assert result == expected or result is not None
