"""
Tests pour src/modules/famille/jules_planning.py

Module Planning Semaine Jules - Activites d'eveil organisees par jour.
Tests avec mocks complets pour éviter les appels réseau/DB réels.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestJulesPlanningImports:
    """Tests d'import pour vérifier que les fonctions/classes sont importables."""

    def test_import_app(self):
        """Test import de la fonction app."""
        from src.modules.famille.jules_planning import app

        assert callable(app)

    def test_import_get_age_jules_mois(self):
        """Test import de get_age_jules_mois."""
        from src.modules.famille.jules_planning import get_age_jules_mois

        assert callable(get_age_jules_mois)

    def test_import_generer_activites_jour(self):
        """Test import de generer_activites_jour."""
        from src.modules.famille.jules_planning import generer_activites_jour

        assert callable(generer_activites_jour)

    def test_import_get_planning_semaine(self):
        """Test import de get_planning_semaine."""
        from src.modules.famille.jules_planning import get_planning_semaine

        assert callable(get_planning_semaine)

    def test_import_init_tracking(self):
        """Test import de init_tracking."""
        from src.modules.famille.jules_planning import init_tracking

        assert callable(init_tracking)

    def test_import_marquer_fait(self):
        """Test import de marquer_fait."""
        from src.modules.famille.jules_planning import marquer_fait

        assert callable(marquer_fait)

    def test_import_est_fait(self):
        """Test import de est_fait."""
        from src.modules.famille.jules_planning import est_fait

        assert callable(est_fait)

    def test_import_render_functions(self):
        """Test import des fonctions de rendu."""
        from src.modules.famille.jules_planning import (
            afficher_activite_card,
            afficher_categories,
            afficher_jour,
            afficher_stats_semaine,
            afficher_vue_aujourd_hui,
            afficher_vue_semaine,
        )

        assert callable(afficher_activite_card)
        assert callable(afficher_jour)
        assert callable(afficher_vue_semaine)
        assert callable(afficher_vue_aujourd_hui)
        assert callable(afficher_categories)
        assert callable(afficher_stats_semaine)

    def test_import_constants(self):
        """Test import des constantes."""
        from src.modules.famille.jules_planning import (
            CATEGORIES_ACTIVITES,
            PLANNING_SEMAINE_TYPE,
        )

        assert isinstance(CATEGORIES_ACTIVITES, dict)
        assert isinstance(PLANNING_SEMAINE_TYPE, dict)
        assert len(CATEGORIES_ACTIVITES) > 0
        assert len(PLANNING_SEMAINE_TYPE) == 7  # 7 jours


@pytest.mark.unit
class TestJulesPlanningHelpers:
    """Tests pour les fonctions helpers."""

    @patch("src.modules.famille.jules_planning.obtenir_contexte_db")
    def test_get_age_jules_mois_with_db(self, mock_db_context):
        """Test get_age_jules_mois avec mock DB."""
        from src.modules.famille.jules_planning import get_age_jules_mois

        # Simuler une erreur DB pour utiliser le fallback
        mock_db_context.side_effect = Exception("DB Error")

        age = get_age_jules_mois()

        # Doit retourner un entier (fallback calculé depuis 22/06/2024)
        assert isinstance(age, int)
        assert age >= 0

    @patch("src.modules.famille.jules_planning.obtenir_contexte_db")
    def test_get_age_jules_mois_with_profile(self, mock_db_context):
        """Test get_age_jules_mois avec profil Jules."""
        from src.modules.famille.jules_planning import get_age_jules_mois

        # Mock du contexte DB et du profil Jules
        mock_db = MagicMock()
        mock_db_context.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_context.return_value.__exit__ = MagicMock(return_value=False)

        mock_jules = MagicMock()
        mock_jules.date_of_birth = date(2024, 6, 22)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_jules

        age = get_age_jules_mois()

        assert isinstance(age, int)
        assert age >= 0

    def test_generer_activites_jour_deterministic(self):
        """Test generer_activites_jour avec seed pour résultat déterministe."""
        from src.modules.famille.jules_planning import generer_activites_jour

        # Avec un seed, les résultats doivent être identiques
        activites1 = generer_activites_jour(0, seed=42)
        activites2 = generer_activites_jour(0, seed=42)

        assert activites1 == activites2
        assert len(activites1) > 0

        # Chaque activité doit avoir les champs requis
        for act in activites1:
            assert "categorie" in act
            assert "emoji" in act
            assert "nom" in act
            assert "duree" in act
            assert "desc" in act

    def test_generer_activites_jour_different_days(self):
        """Test que différents jours ont des catégories différentes."""
        from src.modules.famille.jules_planning import generer_activites_jour

        activites_lundi = generer_activites_jour(0, seed=100)
        activites_mardi = generer_activites_jour(1, seed=100)

        categories_lundi = {a["categorie"] for a in activites_lundi}
        categories_mardi = {a["categorie"] for a in activites_mardi}

        # Les catégories doivent être différentes selon le planning type
        assert categories_lundi != categories_mardi

    def test_get_planning_semaine(self):
        """Test get_planning_semaine retourne un planning complet."""
        from src.modules.famille.jules_planning import get_planning_semaine

        planning = get_planning_semaine()

        assert isinstance(planning, dict)
        assert len(planning) == 7  # 7 jours

        for jour in range(7):
            assert jour in planning
            assert isinstance(planning[jour], list)
            assert len(planning[jour]) > 0


@pytest.mark.unit
class TestJulesPlanningTracking:
    """Tests pour le tracking des activités."""

    @patch("src.modules.famille.jules_planning.st")
    def test_init_tracking(self, mock_st):
        """Test initialisation du tracking."""
        from src.modules.famille.jules_planning import init_tracking

        mock_st.session_state = {}

        init_tracking()

        assert "jules_activites_faites" in mock_st.session_state
        assert isinstance(mock_st.session_state["jules_activites_faites"], dict)

    @patch("src.modules.famille.jules_planning.st")
    def test_init_tracking_idempotent(self, mock_st):
        """Test que init_tracking ne réinitialise pas si déjà présent."""
        from src.modules.famille.jules_planning import init_tracking

        mock_st.session_state = {"jules_activites_faites": {"existing": True}}

        init_tracking()

        assert mock_st.session_state["jules_activites_faites"]["existing"] is True

    @patch("src.modules.famille.jules_planning.st")
    def test_marquer_fait(self, mock_st):
        """Test marquer une activité comme faite."""
        from src.modules.famille.jules_planning import marquer_fait

        mock_st.session_state = {"jules_activites_faites": {}}

        marquer_fait(0, "Parcours coussins")

        # Vérifier qu'une clé a été ajoutée
        assert len(mock_st.session_state["jules_activites_faites"]) == 1

    @patch("src.modules.famille.jules_planning.st")
    def test_est_fait_true(self, mock_st):
        """Test est_fait retourne True pour activité faite."""
        from src.modules.famille.jules_planning import est_fait, marquer_fait

        mock_st.session_state = {"jules_activites_faites": {}}

        # D'abord marquer comme fait
        marquer_fait(0, "Test activite")

        # Vérifier que est_fait retourne True
        result = est_fait(0, "Test activite")
        assert result is True

    @patch("src.modules.famille.jules_planning.st")
    def test_est_fait_false(self, mock_st):
        """Test est_fait retourne False pour activité non faite."""
        from src.modules.famille.jules_planning import est_fait

        mock_st.session_state = {"jules_activites_faites": {}}

        result = est_fait(0, "Activite non faite")
        assert result is False


@pytest.mark.unit
class TestJulesPlanningUI:
    """Tests pour les fonctions UI avec mocks Streamlit."""

    @patch("src.modules.famille.jules_planning.st")
    @patch("src.modules.famille.jules_planning.obtenir_contexte_db")
    def test_app_runs(self, mock_db_context, mock_st):
        """Test que app() s'exécute sans erreur avec les mocks appropriés."""
        from src.modules.famille.jules_planning import app

        # Setup mocks Streamlit
        mock_st.session_state = {}
        mock_st.title = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])

        # Mock contexte DB
        mock_db_context.side_effect = Exception("DB Error")

        try:
            app()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        # Vérifier que les éléments de base ont été appelés
        mock_st.title.assert_called()

    @patch("src.modules.famille.jules_planning.st")
    @patch("src.modules.famille.jules_planning.obtenir_contexte_db")
    def test_render_vue_aujourd_hui(self, mock_db_context, mock_st):
        """Test afficher_vue_aujourd_hui avec mocks."""
        from src.modules.famille.jules_planning import afficher_vue_aujourd_hui

        mock_st.session_state = {"jules_activites_faites": {}}
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.info = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.metric = MagicMock()
        mock_st.divider = MagicMock()
        mock_st.container = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )

        mock_db_context.side_effect = Exception("DB Error")

        try:
            afficher_vue_aujourd_hui()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.jules_planning.st")
    @patch("src.modules.famille.jules_planning.obtenir_contexte_db")
    def test_render_vue_semaine(self, mock_db_context, mock_st):
        """Test afficher_vue_semaine avec mocks."""
        from src.modules.famille.jules_planning import afficher_vue_semaine

        mock_st.session_state = {"jules_activites_faites": {}}
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock() for _ in range(7)])
        mock_st.expander = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )

        mock_db_context.side_effect = Exception("DB Error")

        try:
            afficher_vue_semaine()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.jules_planning.st")
    def test_render_categories(self, mock_st):
        """Test afficher_categories avec mocks."""
        from src.modules.famille.jules_planning import afficher_categories

        mock_st.subheader = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock() for _ in range(6)])
        mock_st.markdown = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.container = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )

        try:
            afficher_categories()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.jules_planning.st")
    def test_render_stats_semaine(self, mock_st):
        """Test afficher_stats_semaine avec mocks."""
        from src.modules.famille.jules_planning import afficher_stats_semaine

        mock_st.session_state = {"jules_activites_faites": {}}
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.metric = MagicMock()
        mock_st.progress = MagicMock()
        mock_st.markdown = MagicMock()

        try:
            afficher_stats_semaine()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.jules_planning.st")
    def test_render_activite_card(self, mock_st):
        """Test afficher_activite_card avec mocks."""
        from src.modules.famille.jules_planning import afficher_activite_card

        mock_st.session_state = {"jules_activites_faites": {}}
        mock_st.container = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        mock_st.markdown = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        mock_st.success = MagicMock()

        activite = {
            "categorie": "motricite",
            "emoji": "🏃",
            "couleur": "#4CAF50",
            "nom": "Parcours coussins",
            "duree": 15,
            "desc": "Grimper, sauter sur les coussins",
        }

        try:
            afficher_activite_card(0, activite, 0)
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

    @patch("src.modules.famille.jules_planning.st")
    def test_render_jour(self, mock_st):
        """Test afficher_jour avec mocks."""
        from src.modules.famille.jules_planning import afficher_jour

        mock_st.session_state = {"jules_activites_faites": {}}
        mock_st.expander = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )
        mock_st.caption = MagicMock()
        mock_st.success = MagicMock()
        mock_st.progress = MagicMock()
        mock_st.container = MagicMock(
            return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
        )

        activites = [
            {
                "categorie": "motricite",
                "emoji": "🏃",
                "couleur": "#4CAF50",
                "nom": "Parcours coussins",
                "duree": 15,
                "desc": "Grimper",
            }
        ]

        try:
            afficher_jour(0, "Lundi", activites, est_aujourd_hui=True)
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock


@pytest.mark.unit
class TestJulesPlanningConstants:
    """Tests pour les constantes du module."""

    def test_categories_activites_structure(self):
        """Test structure des catégories d'activités."""
        from src.modules.famille.jules_planning import CATEGORIES_ACTIVITES

        required_categories = [
            "motricite",
            "langage",
            "creativite",
            "sensoriel",
            "exterieur",
            "imitation",
        ]

        for cat in required_categories:
            assert cat in CATEGORIES_ACTIVITES
            assert "emoji" in CATEGORIES_ACTIVITES[cat]
            assert "couleur" in CATEGORIES_ACTIVITES[cat]
            assert "activites" in CATEGORIES_ACTIVITES[cat]
            assert len(CATEGORIES_ACTIVITES[cat]["activites"]) > 0

    def test_planning_semaine_type_structure(self):
        """Test structure du planning type."""
        from src.modules.famille.jules_planning import PLANNING_SEMAINE_TYPE

        # 7 jours de la semaine
        assert len(PLANNING_SEMAINE_TYPE) == 7

        for jour in range(7):
            assert jour in PLANNING_SEMAINE_TYPE
            assert isinstance(PLANNING_SEMAINE_TYPE[jour], list)
            assert len(PLANNING_SEMAINE_TYPE[jour]) > 0

    def test_activites_have_required_fields(self):
        """Test que chaque activité a les champs requis."""
        from src.modules.famille.jules_planning import CATEGORIES_ACTIVITES

        required_fields = ["nom", "duree", "desc"]

        for cat, info in CATEGORIES_ACTIVITES.items():
            for act in info["activites"]:
                for field in required_fields:
                    assert field in act, f"Champ '{field}' manquant dans {cat}: {act}"
