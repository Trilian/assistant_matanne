"""
Tests pour le service OpenFoodFacts.

Couverture cible: >80%
- Modèles de données (NutritionInfo, ProduitOpenFoodFacts)
- Recherche par code-barres (avec mocks httpx)
- Recherche par nom
- Parser de réponses API
- Fonctions utilitaires (nutriscore, nova)
"""

from datetime import datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from src.services.integrations.produit import (
    CACHE_TTL,
    OPENFOODFACTS_API,
    OPENFOODFACTS_SEARCH,
    NutritionInfo,
    OpenFoodFactsService,
    ProduitOpenFoodFacts,
    get_openfoodfacts_service,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance du service pour les tests."""
    return OpenFoodFactsService()


@pytest.fixture
def mock_cache():
    """Cache mocké."""
    cache = Mock()
    cache.obtenir.return_value = None
    cache.definir = Mock()
    return cache


@pytest.fixture
def api_response_nutella():
    """Réponse API simulée pour Nutella."""
    return {
        "status": 1,
        "product": {
            "code": "3017620422003",
            "product_name_fr": "Nutella",
            "product_name": "Nutella Hazelnut Spread",
            "brands": "Ferrero",
            "quantity": "400g",
            "categories_tags_fr": ["en:spreads", "en:breakfast", "en:chocolate"],
            "image_front_url": "https://images.openfoodfacts.org/nutella.jpg",
            "image_front_small_url": "https://images.openfoodfacts.org/nutella_thumb.jpg",
            "nutriments": {
                "energy-kcal_100g": 539,
                "proteins_100g": 6.3,
                "carbohydrates_100g": 57.5,
                "sugars_100g": 56.3,
                "fat_100g": 30.9,
                "saturated-fat_100g": 10.6,
                "fiber_100g": 0,
                "salt_100g": 0.107,
            },
            "nutriscore_grade": "e",
            "nova_group": 4,
            "ecoscore_grade": "c",
            "ingredients_text_fr": "Sucre, huile de palme, noisettes 13%, cacao maigre 7.4%...",
            "allergens_tags": ["en:milk", "en:nuts"],
            "traces_tags": ["en:gluten", "en:soy"],
            "labels_tags_fr": ["en:no-artificial-colors"],
            "origins": "Italie",
            "conservation_conditions": "À conserver au frais",
            "completeness": 90,
        },
    }


@pytest.fixture
def api_response_not_found():
    """Réponse API pour produit non trouvé."""
    return {"status": 0, "status_verbose": "product not found"}


@pytest.fixture
def api_search_response():
    """Réponse API pour recherche."""
    return {
        "count": 2,
        "products": [
            {
                "code": "3017620422003",
                "product_name_fr": "Nutella 400g",
                "brands": "Ferrero",
                "nutriments": {},
                "completeness": 80,
            },
            {
                "code": "3017620429002",
                "product_name_fr": "Nutella 750g",
                "brands": "Ferrero",
                "nutriments": {},
                "completeness": 75,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES DE DONNÉES
# ═══════════════════════════════════════════════════════════


class TestNutritionInfo:
    """Tests du modèle NutritionInfo."""

    def test_creation_vide(self):
        """Test création sans données."""
        nutrition = NutritionInfo()

        assert nutrition.energie_kcal is None
        assert nutrition.proteines_g is None
        assert nutrition.nutriscore is None

    def test_creation_complete(self):
        """Test création avec toutes les données."""
        nutrition = NutritionInfo(
            energie_kcal=539,
            proteines_g=6.3,
            glucides_g=57.5,
            sucres_g=56.3,
            lipides_g=30.9,
            satures_g=10.6,
            fibres_g=0,
            sel_g=0.107,
            nutriscore="E",
            nova_group=4,
            ecoscore="C",
        )

        assert nutrition.energie_kcal == 539
        assert nutrition.proteines_g == 6.3
        assert nutrition.nutriscore == "E"
        assert nutrition.nova_group == 4


class TestProduitOpenFoodFacts:
    """Tests du modèle ProduitOpenFoodFacts."""

    def test_creation_minimale(self):
        """Test création avec champs requis."""
        produit = ProduitOpenFoodFacts(code_barres="3017620422003", nom="Nutella")

        assert produit.code_barres == "3017620422003"
        assert produit.nom == "Nutella"
        assert produit.source == "openfoodfacts"
        assert produit.confiance == 0.0

    def test_creation_complete(self):
        """Test création avec tous les champs."""
        nutrition = NutritionInfo(energie_kcal=539)
        produit = ProduitOpenFoodFacts(
            code_barres="3017620422003",
            nom="Nutella",
            marque="Ferrero",
            quantite="400g",
            categories=["Pâtes à tartiner", "Petit-déjeuner"],
            image_url="https://example.com/image.jpg",
            nutrition=nutrition,
            ingredients_texte="Sucre, huile de palme...",
            allergenes=["Lait", "Fruits à coque"],
            traces=["Gluten"],
            labels=["Sans colorants artificiels"],
            origine="Italie",
            conservation="Conserver au frais",
            confiance=0.9,
        )

        assert produit.marque == "Ferrero"
        assert produit.quantite == "400g"
        assert len(produit.categories) == 2
        assert produit.nutrition.energie_kcal == 539
        assert "Lait" in produit.allergenes
        assert produit.confiance == 0.9

    def test_valeurs_par_defaut(self):
        """Test des valeurs par défaut."""
        produit = ProduitOpenFoodFacts(code_barres="12345678", nom="Test")

        assert produit.marque is None
        assert produit.categories == []
        assert produit.allergenes == []
        assert produit.labels == []
        assert isinstance(produit.date_recuperation, datetime)


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE INIT
# ═══════════════════════════════════════════════════════════


class TestServiceInit:
    """Tests d'initialisation du service."""

    def test_init(self, service):
        """Test initialisation correcte."""
        assert service.timeout == 10.0
        assert "AssistantMatanne" in service.user_agent

    def test_cache_reference(self, service):
        """Test référence au cache."""
        assert service.cache is not None


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE PAR CODE-BARRES
# ═══════════════════════════════════════════════════════════


class TestRechercherProduit:
    """Tests de la recherche par code-barres."""

    def test_recherche_cache_hit(self, service, mock_cache):
        """Test recherche avec cache hit."""
        cached_produit = ProduitOpenFoodFacts(code_barres="3017620422003", nom="Nutella (cached)")
        mock_cache.obtenir.return_value = cached_produit

        with patch.object(service, "cache", mock_cache):
            result = service.rechercher_produit("3017620422003")

            assert result is not None
            assert result.nom == "Nutella (cached)"
            mock_cache.obtenir.assert_called_once()

    def test_recherche_succes(self, service, api_response_nutella):
        """Test recherche réussie."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_nutella

        with patch.object(service.cache, "obtenir", return_value=None):
            with patch.object(service.cache, "definir") as mock_definir:
                with patch("httpx.Client") as mock_client:
                    mock_client.return_value.__enter__ = Mock(
                        return_value=Mock(get=Mock(return_value=mock_response))
                    )
                    mock_client.return_value.__exit__ = Mock(return_value=False)

                    result = service.rechercher_produit("3017620422003")

                    assert result is not None
                    assert result.code_barres == "3017620422003"
                    assert result.nom == "Nutella"
                    assert result.marque == "Ferrero"

    def test_recherche_produit_non_trouve(self, service, api_response_not_found):
        """Test recherche produit non trouvé."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_not_found

        with patch.object(service.cache, "obtenir", return_value=None):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__ = Mock(
                    return_value=Mock(get=Mock(return_value=mock_response))
                )
                mock_client.return_value.__exit__ = Mock(return_value=False)

                result = service.rechercher_produit("0000000000000")

                assert result is None

    def test_recherche_erreur_http(self, service):
        """Test recherche avec erreur HTTP."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(service.cache, "obtenir", return_value=None):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__ = Mock(
                    return_value=Mock(get=Mock(return_value=mock_response))
                )
                mock_client.return_value.__exit__ = Mock(return_value=False)

                result = service.rechercher_produit("3017620422003")

                assert result is None

    def test_recherche_timeout(self, service):
        """Test recherche avec timeout."""
        with patch.object(service.cache, "obtenir", return_value=None):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__ = Mock(
                    return_value=Mock(get=Mock(side_effect=httpx.TimeoutException("Timeout")))
                )
                mock_client.return_value.__exit__ = Mock(return_value=False)

                result = service.rechercher_produit("3017620422003")

                assert result is None

    def test_recherche_exception(self, service):
        """Test recherche avec exception générale."""
        with patch.object(service.cache, "obtenir", return_value=None):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__ = Mock(
                    return_value=Mock(get=Mock(side_effect=Exception("Network error")))
                )
                mock_client.return_value.__exit__ = Mock(return_value=False)

                result = service.rechercher_produit("3017620422003")

                assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS PARSER PRODUIT
# ═══════════════════════════════════════════════════════════


class TestParserProduit:
    """Tests du parser de produit."""

    def test_parser_nom_fr(self, service):
        """Test parsing avec nom français."""
        data = {"product_name_fr": "Pâtes", "product_name": "Pasta"}
        result = service._parser_produit("123", data)

        assert result.nom == "Pâtes"

    def test_parser_nom_fallback(self, service):
        """Test parsing avec fallback nom."""
        data = {"product_name": "Pasta"}
        result = service._parser_produit("123", data)

        assert result.nom == "Pasta"

    def test_parser_nom_generic(self, service):
        """Test parsing avec nom générique."""
        data = {"generic_name_fr": "Pâtes alimentaires"}
        result = service._parser_produit("123", data)

        assert result.nom == "Pâtes alimentaires"

    def test_parser_nom_inconnu(self, service):
        """Test parsing sans nom."""
        data = {}
        result = service._parser_produit("123", data)

        assert result.nom == "Produit inconnu"

    def test_parser_nutrition(self, service, api_response_nutella):
        """Test parsing nutrition."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert result.nutrition is not None
        assert result.nutrition.energie_kcal == 539
        assert result.nutrition.proteines_g == 6.3
        assert result.nutrition.nutriscore == "E"
        assert result.nutrition.nova_group == 4

    def test_parser_categories(self, service, api_response_nutella):
        """Test parsing catégories."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert len(result.categories) > 0
        # Les catégories sont nettoyées et formatées
        assert all(isinstance(c, str) for c in result.categories)

    def test_parser_allergenes(self, service, api_response_nutella):
        """Test parsing allergènes."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert len(result.allergenes) == 2
        assert "Milk" in result.allergenes or "Nuts" in result.allergenes

    def test_parser_traces(self, service, api_response_nutella):
        """Test parsing traces."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert len(result.traces) == 2

    def test_parser_labels(self, service, api_response_nutella):
        """Test parsing labels."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert len(result.labels) > 0

    def test_parser_confiance(self, service, api_response_nutella):
        """Test calcul confiance."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        # Avec completeness=90, confiance devrait être 0.9
        assert result.confiance == 0.9

    def test_parser_confiance_sans_completeness(self, service):
        """Test confiance sans completeness."""
        data = {"product_name": "Test"}
        result = service._parser_produit("123", data)

        # Sans completeness, confiance par défaut = 0.5
        assert result.confiance == 0.5

    def test_parser_images(self, service, api_response_nutella):
        """Test parsing images."""
        data = api_response_nutella["product"]
        result = service._parser_produit("3017620422003", data)

        assert result.image_url is not None
        assert result.image_thumb_url is not None


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE PAR NOM
# ═══════════════════════════════════════════════════════════


class TestRechercherParNom:
    """Tests de la recherche par nom."""

    def test_recherche_succes(self, service, api_search_response):
        """Test recherche par nom réussie."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_search_response

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = Mock(
                return_value=Mock(get=Mock(return_value=mock_response))
            )
            mock_client.return_value.__exit__ = Mock(return_value=False)

            results = service.rechercher_par_nom("nutella")

            assert len(results) == 2
            assert results[0].nom == "Nutella 400g"
            assert results[1].nom == "Nutella 750g"

    def test_recherche_vide(self, service):
        """Test recherche sans résultats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "products": []}

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = Mock(
                return_value=Mock(get=Mock(return_value=mock_response))
            )
            mock_client.return_value.__exit__ = Mock(return_value=False)

            results = service.rechercher_par_nom("xyznonexistent")

            assert results == []

    def test_recherche_erreur_http(self, service):
        """Test recherche avec erreur HTTP."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = Mock(
                return_value=Mock(get=Mock(return_value=mock_response))
            )
            mock_client.return_value.__exit__ = Mock(return_value=False)

            results = service.rechercher_par_nom("nutella")

            assert results == []

    def test_recherche_exception(self, service):
        """Test recherche avec exception."""
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = Mock(
                return_value=Mock(get=Mock(side_effect=Exception("Network error")))
            )
            mock_client.return_value.__exit__ = Mock(return_value=False)

            results = service.rechercher_par_nom("nutella")

            assert results == []

    def test_recherche_limite(self, service, api_search_response):
        """Test limite de résultats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_search_response

        with patch("httpx.Client") as mock_client:
            mock_instance = Mock()
            mock_instance.get = Mock(return_value=mock_response)
            mock_client.return_value.__enter__ = Mock(return_value=mock_instance)
            mock_client.return_value.__exit__ = Mock(return_value=False)

            service.rechercher_par_nom("nutella", limite=5)

            # Vérifier que page_size=5 est passé
            call_args = mock_instance.get.call_args
            assert call_args[1]["params"]["page_size"] == 5


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestUtilitaires:
    """Tests des fonctions utilitaires."""

    def test_nutriscore_emoji_a(self, service):
        """Test emoji nutriscore A."""
        assert service.obtenir_nutriscore_emoji("A") == "🟢"
        assert service.obtenir_nutriscore_emoji("a") == "🟢"

    def test_nutriscore_emoji_b(self, service):
        """Test emoji nutriscore B."""
        assert service.obtenir_nutriscore_emoji("B") == "🟡"

    def test_nutriscore_emoji_c(self, service):
        """Test emoji nutriscore C."""
        assert service.obtenir_nutriscore_emoji("C") == "🟠"

    def test_nutriscore_emoji_d(self, service):
        """Test emoji nutriscore D."""
        assert service.obtenir_nutriscore_emoji("D") == "🟧"

    def test_nutriscore_emoji_e(self, service):
        """Test emoji nutriscore E."""
        assert service.obtenir_nutriscore_emoji("E") == "🔴"

    def test_nutriscore_emoji_inconnu(self, service):
        """Test emoji nutriscore inconnu."""
        assert service.obtenir_nutriscore_emoji(None) == "⚪"
        assert service.obtenir_nutriscore_emoji("") == "⚪"

    def test_nova_description_1(self, service):
        """Test description NOVA 1."""
        result = service.obtenir_nova_description(1)
        assert "non transformé" in result

    def test_nova_description_2(self, service):
        """Test description NOVA 2."""
        result = service.obtenir_nova_description(2)
        assert "culinaire" in result

    def test_nova_description_3(self, service):
        """Test description NOVA 3."""
        result = service.obtenir_nova_description(3)
        assert "transformé" in result

    def test_nova_description_4(self, service):
        """Test description NOVA 4."""
        result = service.obtenir_nova_description(4)
        assert "Ultra-transformé" in result

    def test_nova_description_inconnu(self, service):
        """Test description NOVA inconnu."""
        result = service.obtenir_nova_description(None)
        assert "Inconnu" in result

        result = service.obtenir_nova_description(5)
        assert "Inconnu" in result


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes."""

    def test_api_urls(self):
        """Test URLs API."""
        assert "openfoodfacts.org" in OPENFOODFACTS_API
        assert "openfoodfacts.org" in OPENFOODFACTS_SEARCH

    def test_cache_ttl(self):
        """Test TTL du cache (24h)."""
        assert CACHE_TTL == 86400


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests de la factory."""

    def test_get_openfoodfacts_service(self):
        """Test obtention du service."""
        service = get_openfoodfacts_service()
        assert isinstance(service, OpenFoodFactsService)

    def test_singleton(self):
        """Test que la factory retourne le même instance."""
        s1 = get_openfoodfacts_service()
        s2 = get_openfoodfacts_service()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION CACHE
# ═══════════════════════════════════════════════════════════


class TestCacheIntegration:
    """Tests d'intégration avec le cache."""

    def test_cache_set_on_success(self, service, api_response_nutella):
        """Test que le cache est mis à jour après succès."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_nutella

        with patch.object(service.cache, "obtenir", return_value=None):
            with patch.object(service.cache, "definir") as mock_definir:
                with patch("httpx.Client") as mock_client:
                    mock_client.return_value.__enter__ = Mock(
                        return_value=Mock(get=Mock(return_value=mock_response))
                    )
                    mock_client.return_value.__exit__ = Mock(return_value=False)

                    result = service.rechercher_produit("3017620422003")

                    # Vérifier que le cache a été mis à jour
                    mock_definir.assert_called_once()
                    cache_key = mock_definir.call_args[0][0]
                    assert "3017620422003" in cache_key

    def test_cache_not_set_on_not_found(self, service, api_response_not_found):
        """Test que le cache n'est pas mis à jour si non trouvé."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_not_found

        with patch.object(service.cache, "obtenir", return_value=None):
            with patch.object(service.cache, "definir") as mock_definir:
                with patch("httpx.Client") as mock_client:
                    mock_client.return_value.__enter__ = Mock(
                        return_value=Mock(get=Mock(return_value=mock_response))
                    )
                    mock_client.return_value.__exit__ = Mock(return_value=False)

                    result = service.rechercher_produit("0000000000000")

                    # Le cache ne doit pas être mis à jour pour un produit non trouvé
                    mock_definir.assert_not_called()
