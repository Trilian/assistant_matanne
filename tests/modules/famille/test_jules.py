"""
Tests pour src/modules/famille/jules (module complet)

Tests du module Jules - Activités adaptées, achats suggérés, conseils développement.
Teste le point d'entrée app() et les exports du module.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestJulesImports:
    """Tests d'import du module Jules"""

    def test_import_module(self):
        """Test que le module s'importe correctement"""
        import src.modules.famille.jules as jules

        assert jules is not None

    def test_app_function_exists(self):
        """Test que la fonction app() existe"""
        from src.modules.famille.jules import app

        assert callable(app)

    def test_exports_ai_service(self):
        """Test que JulesAIService est exporté"""
        from src.modules.famille.jules import JulesAIService

        assert JulesAIService is not None

    def test_exports_helpers(self):
        """Test que les helpers sont exportés"""
        from src.modules.famille.jules import (
            get_achats_jules_en_attente,
            get_activites_pour_age,
            get_age_jules,
            get_taille_vetements,
        )

        assert callable(get_age_jules)
        assert callable(get_activites_pour_age)
        assert callable(get_taille_vetements)
        assert callable(get_achats_jules_en_attente)

    def test_exports_ui_functions(self):
        """Test que les fonctions UI sont exportées"""
        from src.modules.famille.jules import (
            afficher_achats_categorie,
            afficher_activites,
            afficher_conseils,
            afficher_dashboard,
            afficher_form_ajout_achat,
            afficher_shopping,
        )

        assert callable(afficher_dashboard)
        assert callable(afficher_activites)
        assert callable(afficher_shopping)
        assert callable(afficher_achats_categorie)
        assert callable(afficher_form_ajout_achat)
        assert callable(afficher_conseils)

    def test_all_exports(self):
        """Test que __all__ contient les bons exports"""
        from src.modules.famille.jules import __all__

        expected_exports = [
            "app",
            "JulesAIService",
            "get_age_jules",
            "get_activites_pour_age",
            "get_taille_vetements",
            "get_achats_jules_en_attente",
            "afficher_dashboard",
            "afficher_activites",
            "afficher_shopping",
            "afficher_achats_categorie",
            "afficher_form_ajout_achat",
            "afficher_conseils",
        ]

        for export in expected_exports:
            assert export in __all__, f"{export} devrait être dans __all__"


class TestJulesApp:
    """Tests de la fonction app() du module Jules"""

    @patch("src.modules.famille.jules.st")
    @patch("src.modules.famille.jules.afficher_dashboard")
    @patch("src.modules.famille.jules.afficher_activites")
    @patch("src.modules.famille.jules.afficher_shopping")
    @patch("src.modules.famille.jules.afficher_conseils")
    @patch("src.modules.famille.jules.get_age_jules")
    def test_app_calls_st_title(
        self,
        mock_get_age_jules,
        mock_render_conseils,
        mock_render_shopping,
        mock_render_activites,
        mock_render_dashboard,
        mock_st,
    ):
        """Test que app() appelle st.title avec le bon titre"""
        # Setup
        mock_get_age_jules.return_value = {
            "mois": 20,
            "semaines": 87,
            "jours": 610,
            "date_naissance": date(2024, 6, 22),
        }

        mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = mock_tabs

        # Configurer les context managers
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=False)

        from src.modules.famille.jules import app

        # Execute
        app()

        # Assert
        mock_st.title.assert_called_once_with("👶 Jules")

    @patch("src.modules.famille.jules.st")
    @patch("src.modules.famille.jules.afficher_dashboard")
    @patch("src.modules.famille.jules.afficher_activites")
    @patch("src.modules.famille.jules.afficher_shopping")
    @patch("src.modules.famille.jules.afficher_conseils")
    @patch("src.modules.famille.jules.get_age_jules")
    def test_app_displays_age_caption(
        self,
        mock_get_age_jules,
        mock_render_conseils,
        mock_render_shopping,
        mock_render_activites,
        mock_render_dashboard,
        mock_st,
    ):
        """Test que app() affiche l'âge en caption"""
        # Setup
        mock_get_age_jules.return_value = {
            "mois": 20,
            "semaines": 87,
            "jours": 610,
            "date_naissance": date(2024, 6, 22),
        }

        mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = mock_tabs

        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=False)

        from src.modules.famille.jules import app

        # Execute
        app()

        # Assert
        mock_st.caption.assert_called_once()
        call_args = mock_st.caption.call_args[0][0]
        assert "20 mois" in call_args
        assert "22/06/2024" in call_args

    @patch("src.modules.famille.jules.st")
    @patch("src.modules.famille.jules.afficher_dashboard")
    @patch("src.modules.famille.jules.afficher_activites")
    @patch("src.modules.famille.jules.afficher_shopping")
    @patch("src.modules.famille.jules.afficher_conseils")
    @patch("src.modules.famille.jules.get_age_jules")
    def test_app_creates_tabs(
        self,
        mock_get_age_jules,
        mock_render_conseils,
        mock_render_shopping,
        mock_render_activites,
        mock_render_dashboard,
        mock_st,
    ):
        """Test que app() crée les 4 onglets"""
        # Setup
        mock_get_age_jules.return_value = {
            "mois": 20,
            "semaines": 87,
            "jours": 610,
            "date_naissance": date(2024, 6, 22),
        }

        mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = mock_tabs

        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=False)

        from src.modules.famille.jules import app

        # Execute
        app()

        # Assert
        mock_st.tabs.assert_called_once()
        tabs_arg = mock_st.tabs.call_args[0][0]
        assert len(tabs_arg) == 4
        assert "📊 Dashboard" in tabs_arg
        assert "🎨 Activités" in tabs_arg
        assert "🛒 Shopping" in tabs_arg
        assert "💡 Conseils" in tabs_arg

    @patch("src.modules.famille.jules.st")
    @patch("src.modules.famille.jules.afficher_dashboard")
    @patch("src.modules.famille.jules.afficher_activites")
    @patch("src.modules.famille.jules.afficher_shopping")
    @patch("src.modules.famille.jules.afficher_conseils")
    @patch("src.modules.famille.jules.get_age_jules")
    def test_app_calls_render_functions(
        self,
        mock_get_age_jules,
        mock_render_conseils,
        mock_render_shopping,
        mock_render_activites,
        mock_render_dashboard,
        mock_st,
    ):
        """Test que app() appelle les fonctions de rendu"""
        # Setup
        mock_get_age_jules.return_value = {
            "mois": 20,
            "semaines": 87,
            "jours": 610,
            "date_naissance": date(2024, 6, 22),
        }

        mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = mock_tabs

        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=False)

        from src.modules.famille.jules import app

        # Execute
        app()

        # Assert - chaque fonction de rendu est appelée une fois
        mock_render_dashboard.assert_called_once()
        mock_render_activites.assert_called_once()
        mock_render_shopping.assert_called_once()
        mock_render_conseils.assert_called_once()


class TestJulesHelpers:
    """Tests des fonctions helpers du module Jules"""

    @patch("src.modules.famille.jules.utils.obtenir_contexte_db")
    def test_get_age_jules_with_db_profile(self, mock_db_context):
        """Test get_age_jules avec un profil en base"""
        # Setup
        mock_db = MagicMock()
        mock_db_context.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_context.return_value.__exit__ = MagicMock(return_value=False)

        mock_profile = MagicMock()
        mock_profile.date_of_birth = date(2024, 6, 22)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_profile

        from src.modules.famille.jules import get_age_jules

        # Execute
        result = get_age_jules()

        # Assert
        assert "mois" in result
        assert "semaines" in result
        assert "jours" in result
        assert "date_naissance" in result
        assert result["date_naissance"] == date(2024, 6, 22)

    @patch("src.modules.famille.jules.utils.obtenir_contexte_db")
    def test_get_age_jules_fallback_default(self, mock_db_context):
        """Test get_age_jules retourne valeur par défaut si erreur DB"""
        # Setup - simule une erreur DB
        mock_db_context.side_effect = Exception("DB Error")

        from src.modules.famille.jules import get_age_jules

        # Execute
        result = get_age_jules()

        # Assert - devrait retourner la valeur par défaut
        assert "mois" in result
        assert "date_naissance" in result
        assert result["date_naissance"] == date(2024, 6, 22)

    def test_get_activites_pour_age_18_24_mois(self):
        """Test get_activites_pour_age pour 18-24 mois"""
        from src.modules.famille.jules import get_activites_pour_age

        # Execute
        result = get_activites_pour_age(20)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        # Vérifie la structure des activités
        for activite in result:
            assert "nom" in activite
            assert "emoji" in activite
            assert "duree" in activite
            assert "description" in activite

    def test_get_activites_pour_age_24_36_mois(self):
        """Test get_activites_pour_age pour 24-36 mois"""
        from src.modules.famille.jules import get_activites_pour_age

        # Execute
        result = get_activites_pour_age(30)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_activites_pour_age_default(self):
        """Test get_activites_pour_age retourne défaut pour âge non couvert"""
        from src.modules.famille.jules import get_activites_pour_age

        # Execute - âge hors plage
        result = get_activites_pour_age(12)

        # Assert - retourne les activités par défaut (18-24)
        assert isinstance(result, list)

    def test_get_taille_vetements_18_24_mois(self):
        """Test get_taille_vetements pour 18-24 mois"""
        from src.modules.famille.jules import get_taille_vetements

        # Execute
        result = get_taille_vetements(20)

        # Assert
        assert "vetements" in result
        assert "chaussures" in result
        assert result["vetements"] == "86-92"
        assert result["chaussures"] == "22-23"

    def test_get_taille_vetements_24_36_mois(self):
        """Test get_taille_vetements pour 24-36 mois"""
        from src.modules.famille.jules import get_taille_vetements

        # Execute
        result = get_taille_vetements(30)

        # Assert
        assert result["vetements"] == "92-98"
        assert result["chaussures"] == "24-25"

    def test_get_taille_vetements_default(self):
        """Test get_taille_vetements retourne défaut pour âge non couvert"""
        from src.modules.famille.jules import get_taille_vetements

        # Execute - âge hors plage
        result = get_taille_vetements(48)

        # Assert - retourne les tailles par défaut
        assert "vetements" in result
        assert "chaussures" in result

    @patch("src.modules.famille.jules.utils.obtenir_contexte_db")
    def test_get_achats_jules_en_attente(self, mock_db_context):
        """Test get_achats_jules_en_attente"""
        # Setup
        mock_db = MagicMock()
        mock_db_context.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_context.return_value.__exit__ = MagicMock(return_value=False)

        mock_achat = MagicMock()
        mock_achat.nom = "Pantalon"
        mock_achat.categorie = "jules_vetements"
        mock_achat.priorite = "haute"

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_achat
        ]

        from src.modules.famille.jules import get_achats_jules_en_attente

        # Execute
        result = get_achats_jules_en_attente()

        # Assert
        assert isinstance(result, list)

    @patch("src.modules.famille.jules.utils.obtenir_contexte_db")
    def test_get_achats_jules_en_attente_error_returns_empty(self, mock_db_context):
        """Test get_achats_jules_en_attente retourne liste vide si erreur"""
        # Setup - simule une erreur
        mock_db_context.side_effect = Exception("DB Error")

        from src.modules.famille.jules import get_achats_jules_en_attente

        # Execute
        result = get_achats_jules_en_attente()

        # Assert
        assert result == []


class TestJulesAIService:
    """Tests basiques du service IA Jules"""

    def test_jules_ai_service_instantiation(self):
        """Test que JulesAIService peut être instancié"""
        with patch("src.modules.famille.jules.ai_service.ClientIA"):
            from src.modules.famille.jules import JulesAIService

            # Execute
            service = JulesAIService()

            # Assert
            assert service is not None
            assert service.service_name == "jules_ai"

    def test_jules_ai_service_has_required_methods(self):
        """Test que JulesAIService a les méthodes requises"""
        from src.modules.famille.jules import JulesAIService

        # Assert
        assert hasattr(JulesAIService, "suggerer_activites")
        assert hasattr(JulesAIService, "conseil_developpement")
        assert hasattr(JulesAIService, "suggerer_jouets")

    @pytest.mark.asyncio
    @patch("src.modules.famille.jules.ai_service.ClientIA")
    async def test_suggerer_activites_calls_ai(self, mock_client_ia):
        """Test que suggerer_activites appelle l'IA"""
        # Setup
        mock_client = MagicMock()
        mock_client_ia.return_value = mock_client

        from src.modules.famille.jules import JulesAIService

        service = JulesAIService()

        # Mock la méthode call_with_cache
        from unittest.mock import AsyncMock

        service.call_with_cache = AsyncMock(return_value="Activité suggérée")

        # Execute
        result = await service.suggerer_activites(20, "intérieur", 3)

        # Assert
        service.call_with_cache.assert_called_once()
        assert result == "Activité suggérée"


class TestJulesConstants:
    """Tests des constantes du module Jules"""

    def test_activites_par_age_structure(self):
        """Test la structure de ACTIVITES_PAR_AGE"""
        from src.modules.famille.jules.utils import ACTIVITES_PAR_AGE

        # Assert
        assert isinstance(ACTIVITES_PAR_AGE, dict)
        assert (18, 24) in ACTIVITES_PAR_AGE
        assert (24, 36) in ACTIVITES_PAR_AGE

    def test_tailles_par_age_structure(self):
        """Test la structure de TAILLES_PAR_AGE"""
        from src.modules.famille.jules.utils import TAILLES_PAR_AGE

        # Assert
        assert isinstance(TAILLES_PAR_AGE, dict)
        for key, value in TAILLES_PAR_AGE.items():
            assert isinstance(key, tuple)
            assert len(key) == 2
            assert "vetements" in value
            assert "chaussures" in value

    def test_categories_conseils_structure(self):
        """Test la structure de CATEGORIES_CONSEILS"""
        from src.modules.famille.jules.utils import CATEGORIES_CONSEILS

        # Assert
        assert isinstance(CATEGORIES_CONSEILS, dict)
        expected_categories = [
            "proprete",
            "sommeil",
            "alimentation",
            "langage",
            "motricite",
            "social",
        ]
        for cat in expected_categories:
            assert cat in CATEGORIES_CONSEILS
            assert "emoji" in CATEGORIES_CONSEILS[cat]
            assert "titre" in CATEGORIES_CONSEILS[cat]
            assert "description" in CATEGORIES_CONSEILS[cat]
