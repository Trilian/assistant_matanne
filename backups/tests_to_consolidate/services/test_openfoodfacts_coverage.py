"""
Tests complets pour src/services/openfoodfacts.py
Objectif: Atteindre 80%+ de couverture

Tests couvrant:
- rechercher_produit avec cache hit/miss, errors, timeout
- rechercher_par_nom avec rÃ©sultats/vide/erreur
- obtenir_nutriscore_emoji pour tous les grades
- obtenir_nova_description pour tous les groupes
- _parser_produit avec donnÃ©es complÃ¨tes/partielles
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch


class TestOpenFoodFactsServiceInit:
    """Tests d'initialisation du service."""

    def test_service_init(self):
        """VÃ©rifie l'initialisation correcte du service."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.timeout == 10.0
        assert "AssistantMatanne" in service.user_agent

    def test_get_openfoodfacts_service_singleton(self):
        """VÃ©rifie que la factory retourne un singleton."""
        from src.services.openfoodfacts import get_openfoodfacts_service

        service1 = get_openfoodfacts_service()
        service2 = get_openfoodfacts_service()
        assert service1 is service2


class TestRechercherProduitCacheHit:
    """Tests rechercher_produit avec cache hit."""

    @patch("src.services.openfoodfacts.Cache")
    def test_rechercher_produit_cache_hit(self, mock_cache_class):
        """Produit trouvÃ© en cache, pas d'appel API."""
        from src.services.openfoodfacts import OpenFoodFactsService, ProduitOpenFoodFacts

        # Mock du produit en cache
        cached_product = ProduitOpenFoodFacts(
            code_barres="3017620422003", nom="Nutella", marque="Ferrero"
        )
        mock_cache_class.obtenir.return_value = cached_product

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("3017620422003")

        assert result is not None
        assert result.nom == "Nutella"
        mock_cache_class.obtenir.assert_called_once_with("off_product_3017620422003")


class TestRechercherProduitAPICalls:
    """Tests rechercher_produit avec appels API."""

    @patch("src.services.openfoodfacts.Cache")
    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_produit_api_success(self, mock_client_class, mock_cache_class):
        """Produit trouvÃ© via API, mis en cache."""
        from src.services.openfoodfacts import OpenFoodFactsService

        # Cache miss
        mock_cache_class.obtenir.return_value = None

        # Mock HTTP response
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name_fr": "Nutella",
                "brands": "Ferrero",
                "quantity": "400g",
                "nutriments": {
                    "energy-kcal_100g": 539,
                    "proteins_100g": 6.3,
                    "carbohydrates_100g": 57.5,
                    "sugars_100g": 56.3,
                    "fat_100g": 30.9,
                },
                "nutriscore_grade": "e",
                "nova_group": 4,
                "categories_tags": ["en:spreads", "en:chocolate-spreads"],
                "completeness": 80,
            },
        }
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("3017620422003")

        assert result is not None
        assert result.nom == "Nutella"
        assert result.marque == "Ferrero"
        assert result.nutrition.energie_kcal == 539
        assert result.nutrition.nutriscore == "E"
        mock_cache_class.definir.assert_called_once()

    @patch("src.services.openfoodfacts.Cache")
    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_produit_http_404(self, mock_client_class, mock_cache_class):
        """HTTP 404 retourne None."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_cache_class.obtenir.return_value = None

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("0000000000000")

        assert result is None

    @patch("src.services.openfoodfacts.Cache")
    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_produit_status_not_found(self, mock_client_class, mock_cache_class):
        """API retourne status != 1 (produit non trouvÃ©)."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_cache_class.obtenir.return_value = None

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 0, "status_verbose": "product not found"}
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("9999999999999")

        assert result is None

    @patch("src.services.openfoodfacts.Cache")
    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_produit_timeout(self, mock_client_class, mock_cache_class):
        """Timeout retourne None."""
        import httpx

        from src.services.openfoodfacts import OpenFoodFactsService

        mock_cache_class.obtenir.return_value = None

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("3017620422003")

        assert result is None

    @patch("src.services.openfoodfacts.Cache")
    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_produit_generic_exception(self, mock_client_class, mock_cache_class):
        """Exception gÃ©nÃ©rique retourne None."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_cache_class.obtenir.return_value = None

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        mock_client.get.side_effect = Exception("Network error")

        service = OpenFoodFactsService()
        service.cache = mock_cache_class

        result = service.rechercher_produit("3017620422003")

        assert result is None


class TestRechercherParNom:
    """Tests rechercher_par_nom."""

    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_par_nom_with_results(self, mock_client_class):
        """Recherche par nom retourne des produits."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [
                {
                    "code": "3017620422003",
                    "product_name_fr": "Nutella",
                    "brands": "Ferrero",
                    "nutriments": {},
                    "completeness": 50,
                },
                {
                    "code": "3017620425035",
                    "product_name_fr": "Nutella B-Ready",
                    "brands": "Ferrero",
                    "nutriments": {},
                    "completeness": 40,
                },
            ]
        }
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        results = service.rechercher_par_nom("nutella", limite=5)

        assert len(results) == 2
        assert results[0].nom == "Nutella"
        assert results[1].nom == "Nutella B-Ready"

    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_par_nom_empty_results(self, mock_client_class):
        """Recherche sans rÃ©sultats retourne liste vide."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"products": []}
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        results = service.rechercher_par_nom("xyznonexistentproduct")

        assert results == []

    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_par_nom_http_error(self, mock_client_class):
        """HTTP error retourne liste vide."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        results = service.rechercher_par_nom("nutella")

        assert results == []

    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_par_nom_exception(self, mock_client_class):
        """Exception retourne liste vide."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        mock_client.get.side_effect = Exception("Connection error")

        service = OpenFoodFactsService()
        results = service.rechercher_par_nom("nutella")

        assert results == []

    @patch("src.services.openfoodfacts.httpx.Client")
    def test_rechercher_par_nom_product_without_code(self, mock_client_class):
        """Produits sans code sont ignorÃ©s."""
        from src.services.openfoodfacts import OpenFoodFactsService

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [
                {"product_name": "Sans code", "nutriments": {}},  # No code
                {"code": "", "product_name": "Code vide", "nutriments": {}},  # Empty code
                {
                    "code": "123",
                    "product_name_fr": "Avec code",
                    "nutriments": {},
                    "completeness": 30,
                },
            ]
        }
        mock_client.get.return_value = mock_response

        service = OpenFoodFactsService()
        results = service.rechercher_par_nom("test")

        assert len(results) == 1
        assert results[0].nom == "Avec code"


class TestNutriscoreEmoji:
    """Tests obtenir_nutriscore_emoji."""

    def test_nutriscore_a(self):
        """Nutriscore A retourne emoji vert."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("A") == "ðŸŸ¢"
        assert service.obtenir_nutriscore_emoji("a") == "ðŸŸ¢"

    def test_nutriscore_b(self):
        """Nutriscore B retourne emoji jaune."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("B") == "ðŸŸ¡"
        assert service.obtenir_nutriscore_emoji("b") == "ðŸŸ¡"

    def test_nutriscore_c(self):
        """Nutriscore C retourne emoji orange."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("C") == "ðŸŸ "

    def test_nutriscore_d(self):
        """Nutriscore D retourne emoji orange foncÃ©."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("D") == "ðŸŸ§"

    def test_nutriscore_e(self):
        """Nutriscore E retourne emoji rouge."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("E") == "ðŸ”´"
        assert service.obtenir_nutriscore_emoji("e") == "ðŸ”´"

    def test_nutriscore_none(self):
        """Nutriscore None retourne emoji blanc."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji(None) == "âšª"

    def test_nutriscore_unknown(self):
        """Nutriscore inconnu retourne emoji blanc."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        assert service.obtenir_nutriscore_emoji("X") == "âšª"
        assert service.obtenir_nutriscore_emoji("") == "âšª"


class TestNovaDescription:
    """Tests obtenir_nova_description."""

    def test_nova_1(self):
        """NOVA 1 - Aliments non transformÃ©s."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(1)
        assert (
            "non transformÃ©" in result.lower()
            or "unprocessed" in result.lower()
            or "ðŸ¥¬" in result
        )

    def test_nova_2(self):
        """NOVA 2 - IngrÃ©dients culinaires."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(2)
        assert "culinaire" in result.lower() or "ðŸ§‚" in result

    def test_nova_3(self):
        """NOVA 3 - Aliments transformÃ©s."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(3)
        assert "transformÃ©" in result.lower() or "ðŸ¥«" in result

    def test_nova_4(self):
        """NOVA 4 - Ultra-transformÃ©s."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(4)
        assert "ultra" in result.lower() or "ðŸŸ" in result

    def test_nova_none(self):
        """NOVA None - Inconnu."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(None)
        assert "inconnu" in result.lower() or "â“" in result

    def test_nova_invalid(self):
        """NOVA invalide - Inconnu."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()
        result = service.obtenir_nova_description(5)
        assert "inconnu" in result.lower() or "â“" in result
        result = service.obtenir_nova_description(0)
        assert "inconnu" in result.lower() or "â“" in result


class TestParserProduit:
    """Tests _parser_produit avec diffÃ©rentes donnÃ©es."""

    def test_parser_produit_complet(self):
        """Parser avec donnÃ©es complÃ¨tes."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {
            "product_name_fr": "Biscuits Petit DÃ©jeuner",
            "brands": "Lu",
            "quantity": "400g",
            "nutriments": {
                "energy-kcal_100g": 450,
                "proteins_100g": 7.5,
                "carbohydrates_100g": 65,
                "sugars_100g": 25,
                "fat_100g": 18,
                "saturated-fat_100g": 5,
                "fiber_100g": 3,
                "salt_100g": 0.8,
            },
            "nutriscore_grade": "c",
            "nova_group": 4,
            "ecoscore_grade": "c",
            "categories_tags": ["en:biscuits", "fr:petit-dejeuner"],
            "labels_tags": ["en:organic", "fr:sans-gluten"],
            "allergens_tags": ["en:gluten", "en:eggs"],
            "traces_tags": ["en:nuts"],
            "ingredients_text_fr": "Farine de blÃ©, sucre, huile vÃ©gÃ©tale...",
            "origins": "France",
            "conservation_conditions": "Ã€ conserver au sec",
            "image_front_url": "https://example.com/image.jpg",
            "image_front_small_url": "https://example.com/thumb.jpg",
            "completeness": 85,
        }

        result = service._parser_produit("3017620422003", data)

        assert result.code_barres == "3017620422003"
        assert result.nom == "Biscuits Petit DÃ©jeuner"
        assert result.marque == "Lu"
        assert result.quantite == "400g"
        assert result.nutrition.energie_kcal == 450
        assert result.nutrition.nutriscore == "C"
        assert result.nutrition.nova_group == 4
        assert len(result.categories) == 2
        assert len(result.labels) == 2
        assert len(result.allergenes) == 2
        assert len(result.traces) == 1
        assert result.confiance == 0.85

    def test_parser_produit_minimal(self):
        """Parser avec donnÃ©es minimales."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {}  # DonnÃ©es vides

        result = service._parser_produit("1234567890123", data)

        assert result.code_barres == "1234567890123"
        assert result.nom == "Produit inconnu"
        assert result.marque is None
        assert result.nutrition is not None
        assert result.categories == []

    def test_parser_produit_fallback_names(self):
        """Parser utilise les fallbacks pour le nom."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        # product_name_fr absent, utilise product_name
        data1 = {"product_name": "English Name"}
        result1 = service._parser_produit("111", data1)
        assert result1.nom == "English Name"

        # product_name absent, utilise generic_name_fr
        data2 = {"generic_name_fr": "Nom GÃ©nÃ©rique FR"}
        result2 = service._parser_produit("222", data2)
        assert result2.nom == "Nom GÃ©nÃ©rique FR"

        # Tous absents sauf generic_name
        data3 = {"generic_name": "Generic Name"}
        result3 = service._parser_produit("333", data3)
        assert result3.nom == "Generic Name"

    def test_parser_produit_ingredients_fallback(self):
        """Parser utilise le fallback pour ingredients."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        # ingredients_text_fr absent, utilise ingredients_text
        data = {"product_name": "Test", "ingredients_text": "Wheat flour, sugar, salt"}
        result = service._parser_produit("123", data)
        assert result.ingredients_texte == "Wheat flour, sugar, salt"

    def test_parser_produit_categories_limit(self):
        """Parser limite les catÃ©gories Ã  5."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {"product_name": "Test", "categories_tags": [f"en:category-{i}" for i in range(10)]}
        result = service._parser_produit("123", data)
        assert len(result.categories) == 5

    def test_parser_produit_empty_nutriscore(self):
        """Parser gÃ¨re nutriscore vide."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {
            "product_name": "Test",
            "nutriscore_grade": "",
            "ecoscore_grade": "",
        }
        result = service._parser_produit("123", data)
        assert result.nutrition.nutriscore is None
        assert result.nutrition.ecoscore is None

    def test_parser_produit_confiance_sans_completeness(self):
        """Parser retourne 0.5 de confiance si completeness absent."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {"product_name": "Test"}
        result = service._parser_produit("123", data)
        assert result.confiance == 0.5

    def test_parser_produit_confiance_max(self):
        """Parser limite la confiance Ã  1.0."""
        from src.services.openfoodfacts import OpenFoodFactsService

        service = OpenFoodFactsService()

        data = {"product_name": "Test", "completeness": 150}  # > 100
        result = service._parser_produit("123", data)
        assert result.confiance == 1.0


class TestDataclasses:
    """Tests des dataclasses."""

    def test_nutrition_info_defaults(self):
        """NutritionInfo avec valeurs par dÃ©faut."""
        from src.services.openfoodfacts import NutritionInfo

        info = NutritionInfo()
        assert info.energie_kcal is None
        assert info.proteines_g is None
        assert info.nutriscore is None

    def test_nutrition_info_with_values(self):
        """NutritionInfo avec valeurs."""
        from src.services.openfoodfacts import NutritionInfo

        info = NutritionInfo(
            energie_kcal=250,
            proteines_g=10.5,
            glucides_g=30,
            sucres_g=15,
            lipides_g=12,
            satures_g=4,
            fibres_g=2,
            sel_g=0.5,
            nutriscore="B",
            nova_group=3,
            ecoscore="C",
        )
        assert info.energie_kcal == 250
        assert info.nutriscore == "B"

    def test_produit_openfoodfacts_defaults(self):
        """ProduitOpenFoodFacts avec valeurs par dÃ©faut."""
        from src.services.openfoodfacts import ProduitOpenFoodFacts

        produit = ProduitOpenFoodFacts(code_barres="123", nom="Test")
        assert produit.marque is None
        assert produit.categories == []
        assert produit.source == "openfoodfacts"
        assert isinstance(produit.date_recuperation, datetime)

    def test_produit_openfoodfacts_with_nutrition(self):
        """ProduitOpenFoodFacts avec nutrition."""
        from src.services.openfoodfacts import NutritionInfo, ProduitOpenFoodFacts

        nutrition = NutritionInfo(energie_kcal=100)
        produit = ProduitOpenFoodFacts(code_barres="123", nom="Test", nutrition=nutrition)
        assert produit.nutrition.energie_kcal == 100
