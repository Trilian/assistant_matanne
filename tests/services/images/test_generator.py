"""
Tests pour src/core/image_generator.py

Tests des fonctions de génération d'images recettes avec mocks pour les APIs.
"""

from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# HELPER: Import avec mocking des prints au chargement du module
# ═══════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _mock_env():
    """Mock les variables d'environnement pour éviter les appels API réels."""
    with patch.dict(
        "os.environ",
        {
            "UNSPLASH_API_KEY": "",
            "PEXELS_API_KEY": "",
            "PIXABAY_API_KEY": "",
            "LEONARDO_API_KEY": "",
            "HUGGINGFACE_API_KEY": "",
            "REPLICATE_API_TOKEN": "",
        },
        clear=False,
    ):
        yield


# ═══════════════════════════════════════════════════════════
# TESTS _construire_query_optimisee
# ═══════════════════════════════════════════════════════════


class TestConstruireQueryOptimisee:
    """Tests pour _construire_query_optimisee."""

    def test_query_basique_nom_seul(self):
        """Query avec juste un nom de recette."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Tarte aux pommes")
        assert "Tarte aux pommes" in result
        assert "cooked" in result or "finished" in result

    def test_query_avec_ingredients(self):
        """Query avec liste d'ingrédients."""
        from src.services.images.generator import _construire_query_optimisee

        ingredients = [{"nom": "pommes"}, {"nom": "farine"}, {"nom": "sucre"}]
        result = _construire_query_optimisee("Tarte", ingredients)
        assert "Tarte" in result
        assert "pommes" in result

    def test_query_ingredient_dedoublonne(self):
        """Ingrédient principal non dupliqué si dans le nom."""
        from src.services.images.generator import _construire_query_optimisee

        ingredients = [{"nom": "pommes"}]
        result = _construire_query_optimisee("Compote de pommes", ingredients)
        # pommes est dans le nom, ne devrait pas être ajouté en double
        assert result.count("pommes") == 1

    def test_query_type_dessert(self):
        """Query dessert inclut mots-clés spécifiques."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Crème brûlée", type_plat="dessert")
        assert "dessert" in result
        assert "beautiful" in result or "decorated" in result

    def test_query_type_soupe(self):
        """Query soupe inclut mots-clés spécifiques."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Soupe", type_plat="soupe")
        assert "soup" in result
        assert "bowl" in result or "hot" in result

    def test_query_type_plat_general(self):
        """Query plat général avec mots-clés cuisine."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Poulet rôti")
        assert "homemade" in result
        assert "delicious" in result

    def test_query_type_petit_dejeuner(self):
        """Query petit déjeuner."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Pancakes", type_plat="petit_déjeuner")
        assert "breakfast" in result

    def test_query_sans_ingredients(self):
        """Query sans ingrédients ne crash pas."""
        from src.services.images.generator import _construire_query_optimisee

        result = _construire_query_optimisee("Pizza", None, "plat")
        assert "Pizza" in result


# ═══════════════════════════════════════════════════════════
# TESTS _construire_prompt_detaille
# ═══════════════════════════════════════════════════════════


class TestConstruirePromptDetaille:
    """Tests pour _construire_prompt_detaille."""

    def test_prompt_basique(self):
        """Prompt contient le nom de la recette."""
        from src.services.images.generator import _construire_prompt_detaille

        result = _construire_prompt_detaille("Tarte Tatin", "")
        assert "Tarte Tatin" in result
        assert "Professional food photography" in result

    def test_prompt_avec_ingredients(self):
        """Prompt mentionne les ingrédients clés."""
        from src.services.images.generator import _construire_prompt_detaille

        ingredients = [{"nom": "pommes"}, {"nom": "beurre"}, {"nom": "sucre"}]
        result = _construire_prompt_detaille("Tarte", "", ingredients)
        assert "pommes" in result
        assert "beurre" in result

    def test_prompt_avec_description(self):
        """Prompt inclut la description."""
        from src.services.images.generator import _construire_prompt_detaille

        result = _construire_prompt_detaille("Gâteau", "Moelleux au chocolat")
        assert "Moelleux au chocolat" in result

    def test_prompt_type_dessert(self):
        """Prompt dessert avec style adapté."""
        from src.services.images.generator import _construire_prompt_detaille

        result = _construire_prompt_detaille("Fondant", "", type_plat="dessert")
        assert "dessert" in result.lower()

    def test_prompt_type_soupe(self):
        """Prompt soupe avec style adapté."""
        from src.services.images.generator import _construire_prompt_detaille

        result = _construire_prompt_detaille("Soupe de légumes", "", type_plat="soupe")
        assert "soup" in result or "Soupe" in result

    def test_prompt_ingredients_string(self):
        """Prompt avec ingrédients en string."""
        from src.services.images.generator import _construire_prompt_detaille

        ingredients = ["pommes", "poires"]
        result = _construire_prompt_detaille("Compote", "", ingredients)
        assert "pommes" in result

    def test_prompt_qualite(self):
        """Prompt contient mentions de qualité."""
        from src.services.images.generator import _construire_prompt_detaille

        result = _construire_prompt_detaille("Salade", "")
        assert "4K" in result
        assert "professional" in result.lower()


# ═══════════════════════════════════════════════════════════
# TESTS _rechercher_image_pexels
# ═══════════════════════════════════════════════════════════


class TestRechercherImagePexels:
    """Tests pour _rechercher_image_pexels."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _rechercher_image_pexels

        with patch("src.services.images.generator.PEXELS_API_KEY", None):
            assert _rechercher_image_pexels("Tarte") is None

    @patch("src.services.images.generator.PEXELS_API_KEY", "fake_key")
    @patch("requests.get")
    def test_avec_resultats(self, mock_get):
        """Retourne URL si résultats trouvés."""
        from src.services.images.generator import _rechercher_image_pexels

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "photos": [
                {"src": {"large": "https://images.pexels.com/tarte.jpg"}},
                {"src": {"large": "https://images.pexels.com/tarte2.jpg"}},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _rechercher_image_pexels("Tarte aux pommes")
        assert result is not None
        assert "pexels.com" in result

    @patch("src.services.images.generator.PEXELS_API_KEY", "fake_key")
    @patch("requests.get")
    def test_sans_resultats(self, mock_get):
        """Retourne None si pas de résultats."""
        from src.services.images.generator import _rechercher_image_pexels

        mock_response = MagicMock()
        mock_response.json.return_value = {"photos": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        assert _rechercher_image_pexels("Plat inexistant XYZ") is None

    @patch("src.services.images.generator.PEXELS_API_KEY", "fake_key")
    @patch("requests.get", side_effect=Exception("Network error"))
    def test_erreur_reseau(self, mock_get):
        """Retourne None si erreur réseau."""
        from src.services.images.generator import _rechercher_image_pexels

        assert _rechercher_image_pexels("Tarte") is None


# ═══════════════════════════════════════════════════════════
# TESTS _rechercher_image_pixabay
# ═══════════════════════════════════════════════════════════


class TestRechercherImagePixabay:
    """Tests pour _rechercher_image_pixabay."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _rechercher_image_pixabay

        with patch("src.services.images.generator.PIXABAY_API_KEY", None):
            assert _rechercher_image_pixabay("Salade") is None

    @patch("src.services.images.generator.PIXABAY_API_KEY", "fake_key")
    @patch("requests.get")
    def test_avec_resultats(self, mock_get):
        """Retourne URL si résultats trouvés."""
        from src.services.images.generator import _rechercher_image_pixabay

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "hits": [{"webformatURL": "https://pixabay.com/salade.jpg"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _rechercher_image_pixabay("Salade")
        assert result is not None
        assert "pixabay.com" in result

    @patch("src.services.images.generator.PIXABAY_API_KEY", "fake_key")
    @patch("requests.get")
    def test_sans_resultats(self, mock_get):
        """Retourne None si pas de résultats."""
        from src.services.images.generator import _rechercher_image_pixabay

        mock_response = MagicMock()
        mock_response.json.return_value = {"hits": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        assert _rechercher_image_pixabay("XYZ") is None

    @patch("src.services.images.generator.PIXABAY_API_KEY", "fake_key")
    @patch("requests.get", side_effect=Exception("Timeout"))
    def test_erreur_reseau(self, mock_get):
        """Retourne None si erreur réseau."""
        from src.services.images.generator import _rechercher_image_pixabay

        assert _rechercher_image_pixabay("Pizza") is None


# ═══════════════════════════════════════════════════════════
# TESTS _rechercher_image_unsplash
# ═══════════════════════════════════════════════════════════


class TestRechercherImageUnsplash:
    """Tests pour _rechercher_image_unsplash."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _rechercher_image_unsplash

        with patch("src.services.images.generator.UNSPLASH_API_KEY", None):
            assert _rechercher_image_unsplash("Crêpes") is None

    @patch("src.services.images.generator.UNSPLASH_API_KEY", "fake_key")
    @patch("requests.get")
    def test_avec_resultats(self, mock_get):
        """Retourne URL si résultats trouvés."""
        from src.services.images.generator import _rechercher_image_unsplash

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "urls": {"regular": "https://images.unsplash.com/photo.jpg"},
                    "width": 1000,
                    "height": 800,
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _rechercher_image_unsplash("Crêpes")
        assert result is not None
        assert "unsplash.com" in result

    @patch("src.services.images.generator.UNSPLASH_API_KEY", "fake_key")
    @patch("requests.get")
    def test_sans_resultats(self, mock_get):
        """Retourne None si pas de résultats."""
        from src.services.images.generator import _rechercher_image_unsplash

        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        assert _rechercher_image_unsplash("XYZ introuvable") is None

    @patch("src.services.images.generator.UNSPLASH_API_KEY", "fake_key")
    @patch("requests.get", side_effect=Exception("Error"))
    def test_erreur_reseau(self, mock_get):
        """Retourne None si erreur réseau."""
        from src.services.images.generator import _rechercher_image_unsplash

        assert _rechercher_image_unsplash("Pizza") is None


# ═══════════════════════════════════════════════════════════
# TESTS _generer_via_pollinations
# ═══════════════════════════════════════════════════════════


class TestGenererViaPollinations:
    """Tests pour _generer_via_pollinations."""

    @patch("requests.head")
    def test_genere_url_valide(self, mock_head):
        """Retourne URL Pollinations si accessible."""
        from src.services.images.generator import _generer_via_pollinations

        mock_head.return_value = MagicMock(status_code=200)

        result = _generer_via_pollinations("Tarte", "Délicieuse tarte")
        assert result is not None
        assert "pollinations.ai" in result

    @patch("requests.head", side_effect=Exception("Timeout"))
    def test_erreur_retourne_none(self, mock_head):
        """Retourne None si Pollinations down."""
        from src.services.images.generator import _generer_via_pollinations

        assert _generer_via_pollinations("Tarte", "") is None

    @patch("requests.head")
    def test_url_encode_accents(self, mock_head):
        """URL encode correctement les accents."""
        from src.services.images.generator import _generer_via_pollinations

        mock_head.return_value = MagicMock(status_code=200)

        result = _generer_via_pollinations("Crème brûlée", "Dessert français")
        assert result is not None
        assert "pollinations.ai" in result


# ═══════════════════════════════════════════════════════════
# TESTS _generer_via_huggingface
# ═══════════════════════════════════════════════════════════


class TestGenererViaHuggingface:
    """Tests pour _generer_via_huggingface."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _generer_via_huggingface

        with patch.dict("os.environ", {"HUGGINGFACE_API_KEY": ""}, clear=False):
            assert _generer_via_huggingface("Salade", "") is None

    @patch("requests.post")
    @patch.dict("os.environ", {"HUGGINGFACE_API_KEY": "hf_fake_key"})
    def test_avec_reponse_valide(self, mock_post):
        """Retourne base64 data URI si réponse valide."""
        from src.services.images.generator import _generer_via_huggingface

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n\x00\x00"
        mock_post.return_value = mock_response

        result = _generer_via_huggingface("Gâteau", "Au chocolat")
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    @patch("requests.post")
    @patch.dict("os.environ", {"HUGGINGFACE_API_KEY": "hf_fake_key"})
    def test_erreur_api(self, mock_post):
        """Retourne None si erreur API."""
        from src.services.images.generator import _generer_via_huggingface

        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response

        assert _generer_via_huggingface("Salade", "") is None


# ═══════════════════════════════════════════════════════════
# TESTS _generer_via_leonardo
# ═══════════════════════════════════════════════════════════


class TestGenererViaLeonardo:
    """Tests pour _generer_via_leonardo."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _generer_via_leonardo

        with patch.dict("os.environ", {"LEONARDO_API_KEY": "", "LEONARDO_TOKEN": ""}, clear=False):
            assert _generer_via_leonardo("Poulet", "") is None

    @patch("requests.post")
    @patch.dict("os.environ", {"LEONARDO_API_KEY": "leo_fake_key"})
    def test_avec_reponse_valide(self, mock_post):
        """Retourne URL si génération réussie."""
        from src.services.images.generator import _generer_via_leonardo

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generations": [{"id": "abc123"}]}
        mock_post.return_value = mock_response

        result = _generer_via_leonardo("Poulet", "rôti")
        assert result is not None
        assert "leonardo.ai" in result

    @patch("requests.post")
    @patch.dict("os.environ", {"LEONARDO_API_KEY": "leo_fake_key"})
    def test_erreur_api(self, mock_post):
        """Retourne None si erreur API."""
        from src.services.images.generator import _generer_via_leonardo

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"
        mock_post.return_value = mock_response

        assert _generer_via_leonardo("Salade", "") is None


# ═══════════════════════════════════════════════════════════
# TESTS _generer_via_replicate
# ═══════════════════════════════════════════════════════════


class TestGenererViaReplicate:
    """Tests pour _generer_via_replicate."""

    def test_sans_cle_api(self):
        """Retourne None sans clé API."""
        from src.services.images.generator import _generer_via_replicate

        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": ""}, clear=False):
            assert _generer_via_replicate("Pizza", "") is None


# ═══════════════════════════════════════════════════════════
# TESTS generer_image_recette (intégration)
# ═══════════════════════════════════════════════════════════


class TestGenererImageRecette:
    """Tests pour generer_image_recette (fonction principale)."""

    @patch("src.services.images.generator._generer_via_pollinations")
    def test_fallback_pollinations(self, mock_pollinations):
        """Utilise Pollinations en dernier recours quand aucune API configurée."""
        from src.services.images.generator import generer_image_recette

        mock_pollinations.return_value = "https://pollinations.ai/test.jpg"

        with (
            patch("src.services.images.generator.UNSPLASH_API_KEY", None),
            patch("src.services.images.generator.PEXELS_API_KEY", None),
            patch("src.services.images.generator.PIXABAY_API_KEY", None),
            patch("src.services.images.generator.LEONARDO_API_KEY", None),
            patch.dict("os.environ", {"HUGGINGFACE_API_KEY": ""}, clear=False),
        ):
            result = generer_image_recette("Tarte aux pommes")

        assert result is not None

    @patch("src.services.images.generator._generer_via_pollinations", return_value=None)
    @patch("src.services.images.generator._generer_via_replicate", return_value=None)
    def test_toutes_apis_echouent(self, mock_replicate, mock_pollinations):
        """Retourne None si toutes les APIs échouent."""
        from src.services.images.generator import generer_image_recette

        with (
            patch("src.services.images.generator.UNSPLASH_API_KEY", None),
            patch("src.services.images.generator.PEXELS_API_KEY", None),
            patch("src.services.images.generator.PIXABAY_API_KEY", None),
            patch("src.services.images.generator.LEONARDO_API_KEY", None),
            patch.dict("os.environ", {"HUGGINGFACE_API_KEY": ""}, clear=False),
        ):
            result = generer_image_recette("Plat inconnu")

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS telecharger_image_depuis_url
# ═══════════════════════════════════════════════════════════


class TestTelechargerImageDepuisUrl:
    """Tests pour telecharger_image_depuis_url."""

    @patch("requests.get")
    def test_telechargement_reussi(self, mock_get):
        """Télécharge et sauvegarde une image."""
        from src.services.images.generator import telecharger_image_depuis_url

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n"
        mock_get.return_value = mock_response

        result = telecharger_image_depuis_url("https://example.com/image.png", "test_image")
        assert result is not None
        assert result.endswith(".png")

    @patch("requests.get", side_effect=Exception("Network error"))
    def test_erreur_telechargement(self, mock_get):
        """Retourne None si erreur de téléchargement."""
        from src.services.images.generator import telecharger_image_depuis_url

        result = telecharger_image_depuis_url("https://example.com/image.png", "test_image")
        assert result is None

    @patch("requests.get")
    def test_erreur_status_code(self, mock_get):
        """Retourne None si status code non-200."""
        from src.services.images.generator import telecharger_image_depuis_url

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = telecharger_image_depuis_url("https://example.com/missing.png", "test_image")
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS _get_api_key
# ═══════════════════════════════════════════════════════════


class TestGetApiKey:
    """Tests pour _get_api_key."""

    def test_get_api_key_from_env(self):
        """Récupère clé depuis os.environ."""
        from src.services.images.generator import _get_api_key

        with patch.dict("os.environ", {"TEST_KEY": "my_secret_key"}):
            result = _get_api_key("TEST_KEY")
            assert result == "my_secret_key"

    def test_get_api_key_missing(self):
        """Retourne None si clé absente."""
        from src.services.images.generator import _get_api_key

        with patch.dict("os.environ", {}, clear=True):
            result = _get_api_key("NONEXISTENT_KEY_12345")
            assert result is None
