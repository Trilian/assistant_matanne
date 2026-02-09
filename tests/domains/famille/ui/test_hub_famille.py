"""
Tests complets pour src/domains/famille/ui/hub_famille.py
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import date, timedelta

import src.domains.famille.ui.hub_famille as hub_famille


# ═══════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════


def test_import_hub_famille_ui():
    import src.domains.famille.ui.hub_famille
    assert hub_famille is not None


def test_card_styles_defined():
    assert hasattr(hub_famille, "CARD_STYLES")
    assert isinstance(hub_famille.CARD_STYLES, str)
    assert "family-card" in hub_famille.CARD_STYLES


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_AGE_JULES
# ═══════════════════════════════════════════════════════════


class TestCalculerAgeJules:
    """Tests pour calculer_age_jules."""

    def test_calculer_age_jules_defaut(self):
        """Test avec retour par défaut si pas de profil trouvé."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.calculer_age_jules()
            assert "mois" in result
            assert "texte" in result

    def test_calculer_age_jules_avec_profil(self):
        """Test avec profil Jules existant."""
        mock_jules = MagicMock()
        # Jules né il y a 600 jours (environ 20 mois)
        mock_jules.date_of_birth = date.today() - timedelta(days=600)
        mock_jules.actif = True
        mock_jules.name = "Jules"
        
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_jules
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.calculer_age_jules()
            assert "mois" in result
            assert result["mois"] >= 1

    def test_calculer_age_jules_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.calculer_age_jules()
            # Should return default values
            assert result["mois"] == 19


# ═══════════════════════════════════════════════════════════
# TESTS GET_USER_STREAK
# ═══════════════════════════════════════════════════════════


class TestGetUserStreak:
    """Tests pour get_user_streak."""

    def test_get_user_streak_no_user(self):
        """Test sans utilisateur trouvé."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.get_user_streak("unknown")
            assert result == 0

    def test_get_user_streak_no_summaries(self):
        """Test sans résumés Garmin."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.get_user_streak("anne")
            assert result == 0

    def test_get_user_streak_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.get_user_streak("anne")
            assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS GET_USER_GARMIN_CONNECTED
# ═══════════════════════════════════════════════════════════


class TestGetUserGarminConnected:
    """Tests pour get_user_garmin_connected."""

    def test_garmin_connected_true(self):
        """Test avec utilisateur connecté à Garmin."""
        mock_user = MagicMock()
        mock_user.garmin_connected = True
        
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.get_user_garmin_connected("anne")
            assert result is True

    def test_garmin_connected_false(self):
        """Test avec utilisateur non connecté."""
        mock_user = MagicMock()
        mock_user.garmin_connected = False
        
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.get_user_garmin_connected("mathieu")
            assert result is False

    def test_garmin_no_user(self):
        """Test sans utilisateur trouvé."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.get_user_garmin_connected("unknown")
            assert result is False

    def test_garmin_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.get_user_garmin_connected("anne")
            assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS COUNT_WEEKEND_ACTIVITIES
# ═══════════════════════════════════════════════════════════


class TestCountWeekendActivities:
    """Tests pour count_weekend_activities."""

    def test_count_weekend_zero(self):
        """Test sans activités."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_weekend_activities()
            assert result == 0

    def test_count_weekend_multiple(self):
        """Test avec plusieurs activités."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.count.return_value = 3
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_weekend_activities()
            assert result == 3

    def test_count_weekend_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.count_weekend_activities()
            assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS COUNT_PENDING_PURCHASES
# ═══════════════════════════════════════════════════════════


class TestCountPendingPurchases:
    """Tests pour count_pending_purchases."""

    def test_count_pending_zero(self):
        """Test sans achats en attente."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.count.return_value = 0
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_pending_purchases()
            assert result == 0

    def test_count_pending_multiple(self):
        """Test avec plusieurs achats."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter_by.return_value.count.return_value = 5
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_pending_purchases()
            assert result == 5

    def test_count_pending_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.count_pending_purchases()
            assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS COUNT_URGENT_PURCHASES
# ═══════════════════════════════════════════════════════════


class TestCountUrgentPurchases:
    """Tests pour count_urgent_purchases."""

    def test_count_urgent_zero(self):
        """Test sans achats urgents."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_urgent_purchases()
            assert result == 0

    def test_count_urgent_multiple(self):
        """Test avec plusieurs achats urgents."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.count.return_value = 2
        
        with patch("src.domains.famille.ui.hub_famille.get_db_context", return_value=mock_session):
            result = hub_famille.count_urgent_purchases()
            assert result == 2

    def test_count_urgent_exception(self):
        """Test avec exception."""
        with patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error")):
            result = hub_famille.count_urgent_purchases()
            assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS APP FUNCTION
# ═══════════════════════════════════════════════════════════


class TestAppFunction:
    """Tests pour la fonction app."""

    def test_app_exists(self):
        assert hasattr(hub_famille, "app")
        assert callable(hub_famille.app)

    @patch("streamlit.title")
    @patch("streamlit.session_state", {"famille_page": "hub"})
    @patch("src.domains.famille.ui.hub_famille.init_family_users")
    @patch("src.domains.famille.ui.hub_famille.render_hub")
    def test_app_renders_hub_by_default(self, mock_render, mock_init, mock_title):
        """Test que app() affiche le hub par défaut."""
        hub_famille.app()
        mock_title.assert_called_once()
        mock_render.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_CARD FUNCTIONS
# ═══════════════════════════════════════════════════════════


class TestRenderCardFunctions:
    """Tests pour les fonctions render_card."""

    @patch("streamlit.button", return_value=False)
    @patch("streamlit.caption")
    @patch("src.domains.famille.ui.hub_famille.calculer_age_jules")
    def test_render_card_jules(self, mock_age, mock_caption, mock_button):
        """Test render_card_jules."""
        mock_age.return_value = {"mois": 19, "jours": 5, "texte": "19 mois et 5j"}
        hub_famille.render_card_jules()
        mock_button.assert_called_once()
        mock_caption.assert_called_once()

    @patch("streamlit.button", return_value=False)
    @patch("streamlit.caption")
    @patch("src.domains.famille.ui.hub_famille.count_weekend_activities")
    def test_render_card_weekend(self, mock_count, mock_caption, mock_button):
        """Test render_card_weekend."""
        mock_count.return_value = 2
        hub_famille.render_card_weekend()
        mock_button.assert_called_once()
        mock_caption.assert_called_once()

    @patch("streamlit.button", return_value=False)
    @patch("streamlit.caption")
    @patch("src.domains.famille.ui.hub_famille.get_user_streak")
    @patch("src.domains.famille.ui.hub_famille.get_user_garmin_connected")
    def test_render_card_user(self, mock_garmin, mock_streak, mock_caption, mock_button):
        """Test render_card_user."""
        mock_streak.return_value = 5
        mock_garmin.return_value = True
        hub_famille.render_card_user("anne", "Anne", "👩")
        mock_button.assert_called_once()
        mock_caption.assert_called_once()

    @patch("streamlit.button", return_value=False)
    @patch("streamlit.caption")
    @patch("src.domains.famille.ui.hub_famille.count_pending_purchases")
    @patch("src.domains.famille.ui.hub_famille.count_urgent_purchases")
    def test_render_card_achats(self, mock_urgent, mock_pending, mock_caption, mock_button):
        """Test render_card_achats."""
        mock_pending.return_value = 5
        mock_urgent.return_value = 1
        hub_famille.render_card_achats()
        mock_button.assert_called_once()
        mock_caption.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_HUB
# ═══════════════════════════════════════════════════════════


class TestRenderHub:
    """Tests pour render_hub."""

    def test_render_hub_exists(self):
        assert hasattr(hub_famille, "render_hub")
        assert callable(hub_famille.render_hub)

    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    @patch("streamlit.subheader")
    @patch("src.domains.famille.ui.hub_famille.render_card_jules")
    @patch("src.domains.famille.ui.hub_famille.render_card_weekend")
    @patch("src.domains.famille.ui.hub_famille.render_card_user")
    @patch("src.domains.famille.ui.hub_famille.render_card_achats")
    @patch("src.domains.famille.ui.hub_famille.render_weekend_preview")
    def test_render_hub(self, mock_preview, mock_achats, mock_user, mock_weekend, 
                        mock_jules, mock_subheader, mock_container, mock_columns, mock_markdown):
        """Test render_hub s'exécute."""
        mock_columns.return_value = [MagicMock(), MagicMock()]
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        hub_famille.render_hub()
        
        mock_markdown.assert_called()
        mock_columns.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_WEEKEND_PREVIEW
# ═══════════════════════════════════════════════════════════


class TestRenderWeekendPreview:
    """Tests pour render_weekend_preview."""

    def test_render_weekend_preview_exists(self):
        assert hasattr(hub_famille, "render_weekend_preview")
        assert callable(hub_famille.render_weekend_preview)

    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("src.domains.famille.ui.hub_famille._render_day_activities")
    def test_render_weekend_preview(self, mock_render_day, mock_markdown, mock_columns):
        """Test render_weekend_preview."""
        col1 = MagicMock()
        col2 = MagicMock()
        col1.__enter__ = MagicMock(return_value=col1)
        col1.__exit__ = MagicMock()
        col2.__enter__ = MagicMock(return_value=col2)
        col2.__exit__ = MagicMock()
        mock_columns.return_value = [col1, col2]
        
        hub_famille.render_weekend_preview()
        
        mock_columns.assert_called_once_with(2)


# ═══════════════════════════════════════════════════════════
# TESTS _RENDER_DAY_ACTIVITIES
# ═══════════════════════════════════════════════════════════


class TestRenderDayActivities:
    """Tests pour _render_day_activities."""

    def test_render_day_activities_exists(self):
        assert hasattr(hub_famille, "_render_day_activities")
        assert callable(hub_famille._render_day_activities)

    @patch("streamlit.write")
    @patch("streamlit.caption")
    @patch("streamlit.button")
    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_render_day_activities_with_activities(self, mock_db, mock_button, mock_caption, mock_write):
        """Test avec des activités."""
        mock_activity = MagicMock()
        mock_activity.titre = "Parc"
        mock_activity.heure_debut = "10:00"
        
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_activity]
        mock_db.return_value = mock_session
        
        hub_famille._render_day_activities(date.today())
        mock_write.assert_called()

    @patch("streamlit.caption")
    @patch("streamlit.button", return_value=False)
    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_render_day_activities_no_activities(self, mock_db, mock_button, mock_caption):
        """Test sans activités."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db.return_value = mock_session
        
        hub_famille._render_day_activities(date.today())
        mock_caption.assert_called_with("Rien de prévu")

    @patch("streamlit.caption")
    @patch("src.domains.famille.ui.hub_famille.get_db_context", side_effect=Exception("DB Error"))
    def test_render_day_activities_exception(self, mock_db, mock_caption):
        """Test avec exception."""
        hub_famille._render_day_activities(date.today())
        mock_caption.assert_called_with("Rien de prévu")
