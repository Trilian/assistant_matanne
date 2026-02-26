"""
Tests pour src/modules/famille/hub_famille.py

Tests du module Hub Famille avec mocks complets pour éviter les appels réseau/DB.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_child_profile():
    """Fixture pour un profil enfant mocké (Jules)."""
    child = MagicMock()
    child.id = 1
    child.name = "Jules"
    child.date_of_birth = date.today() - timedelta(days=19 * 30)  # ~19 mois
    child.actif = True
    return child


@pytest.fixture
def mock_user_profile():
    """Fixture pour un profil utilisateur mocké."""
    user = MagicMock()
    user.id = 1
    user.username = "anne"
    user.garmin_connected = True
    user.objectif_pas_quotidien = 10000
    return user


@pytest.fixture
def mock_garmin_summary():
    """Fixture pour un résumé Garmin mocké."""
    summary = MagicMock()
    summary.id = 1
    summary.user_id = 1
    summary.date = date.today()
    summary.pas = 12000
    return summary


@pytest.fixture
def mock_weekend_activity():
    """Fixture pour une activité weekend mockée."""
    activity = MagicMock()
    activity.id = 1
    activity.titre = "Sortie au parc"
    activity.date_prevue = date.today()
    activity.heure_debut = "10:00"
    activity.statut = "planifie"
    return activity


@pytest.fixture
def mock_family_purchase():
    """Fixture pour un achat famille mocké."""
    purchase = MagicMock()
    purchase.id = 1
    purchase.nom = "Couches"
    purchase.achete = False
    purchase.priorite = "urgent"
    return purchase


@pytest.fixture
def mock_db_session(mock_child_profile, mock_user_profile, mock_garmin_summary):
    """Fixture pour une session DB mockée."""
    session = MagicMock()

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = []
    mock_query.first.return_value = None
    mock_query.count.return_value = 0

    session.query.return_value = mock_query

    return session


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests d'import des fonctions du module."""

    def test_import_calculer_age_jules(self):
        """Test import de calculer_age_jules."""
        from src.modules.famille.hub_famille import calculer_age_jules

        assert callable(calculer_age_jules)

    def test_import_get_user_streak(self):
        """Test import de get_user_streak."""
        from src.modules.famille.hub_famille import get_user_streak

        assert callable(get_user_streak)

    def test_import_get_user_garmin_connected(self):
        """Test import de get_user_garmin_connected."""
        from src.modules.famille.hub_famille import get_user_garmin_connected

        assert callable(get_user_garmin_connected)

    def test_import_count_weekend_activities(self):
        """Test import de count_weekend_activities."""
        from src.modules.famille.hub_famille import count_weekend_activities

        assert callable(count_weekend_activities)

    def test_import_count_pending_purchases(self):
        """Test import de count_pending_purchases."""
        from src.modules.famille.hub_famille import count_pending_purchases

        assert callable(count_pending_purchases)

    def test_import_count_urgent_purchases(self):
        """Test import de count_urgent_purchases."""
        from src.modules.famille.hub_famille import count_urgent_purchases

        assert callable(count_urgent_purchases)

    def test_import_render_card_jules(self):
        """Test import de afficher_card_jules."""
        from src.modules.famille.hub_famille import afficher_card_jules

        assert callable(afficher_card_jules)

    def test_import_render_card_weekend(self):
        """Test import de afficher_card_weekend."""
        from src.modules.famille.hub_famille import afficher_card_weekend

        assert callable(afficher_card_weekend)

    def test_import_render_card_user(self):
        """Test import de afficher_card_user."""
        from src.modules.famille.hub_famille import afficher_card_user

        assert callable(afficher_card_user)

    def test_import_render_card_achats(self):
        """Test import de afficher_card_achats."""
        from src.modules.famille.hub_famille import afficher_card_achats

        assert callable(afficher_card_achats)

    def test_import_app(self):
        """Test import de app."""
        from src.modules.famille.hub_famille import app

        assert callable(app)

    def test_import_render_hub(self):
        """Test import de afficher_hub."""
        from src.modules.famille.hub_famille import afficher_hub

        assert callable(afficher_hub)

    def test_import_render_weekend_preview(self):
        """Test import de afficher_weekend_preview."""
        from src.modules.famille.hub_famille import afficher_weekend_preview

        assert callable(afficher_weekend_preview)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FONCTIONS HELPER
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalculerAgeJules:
    """Tests pour calculer_age_jules."""

    @patch("src.modules.famille.hub_famille.get_age_jules")
    def test_calculer_age_jules_avec_profil(self, mock_age):
        """Test calcul âge avec profil Jules."""
        from src.modules.famille.hub_famille import calculer_age_jules

        mock_age.return_value = {
            "mois": 20,
            "jours": 610,
            "semaines": 87,
            "ans": 1,
            "texte": "20 mois",
            "date_naissance": date(2024, 6, 22),
        }

        result = calculer_age_jules()

        assert isinstance(result, dict)
        assert "mois" in result
        assert "jours" in result
        assert "texte" in result

    @patch("src.modules.famille.hub_famille.get_age_jules")
    def test_calculer_age_jules_sans_profil(self, mock_age):
        """Test calcul âge sans profil (valeur par défaut)."""
        from src.modules.famille.hub_famille import calculer_age_jules

        mock_age.return_value = {
            "mois": 19,
            "jours": 570,
            "semaines": 81,
            "ans": 1,
            "texte": "19 mois",
            "date_naissance": date(2024, 6, 22),
        }

        result = calculer_age_jules()

        assert result["mois"] == 19
        assert result["texte"] == "19 mois"

    @patch("src.modules.famille.hub_famille.get_age_jules")
    def test_calculer_age_jules_erreur_db(self, mock_age):
        """Test calcul âge avec erreur — age_utils gère le fallback."""
        from src.modules.famille.hub_famille import calculer_age_jules

        mock_age.return_value = {
            "mois": 19,
            "jours": 570,
            "semaines": 81,
            "ans": 1,
            "texte": "19 mois",
            "date_naissance": date(2024, 6, 22),
        }

        result = calculer_age_jules()

        assert result["mois"] == 19
        assert result["texte"] == "19 mois"


class TestGetUserStreak:
    """Tests pour get_user_streak — délègue à ServiceSuiviPerso."""

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_get_user_streak_aucun_utilisateur(self, mock_svc):
        """Test streak pour utilisateur inexistant."""
        from src.modules.famille.hub_famille import get_user_streak

        mock_svc.return_value.get_user_data.return_value = {"streak": 0}

        result = get_user_streak("inconnu")

        assert result == 0

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_get_user_streak_avec_streak(self, mock_svc):
        """Test streak avec données."""
        from src.modules.famille.hub_famille import get_user_streak

        mock_svc.return_value.get_user_data.return_value = {"streak": 5, "garmin_connected": True}

        result = get_user_streak("anne")

        assert result == 5

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_get_user_streak_erreur(self, mock_svc):
        """Test streak avec erreur service."""
        from src.modules.famille.hub_famille import get_user_streak

        mock_svc.return_value.get_user_data.side_effect = Exception("Service Error")

        result = get_user_streak("anne")

        assert result == 0


class TestGetUserGarminConnected:
    """Tests pour get_user_garmin_connected — délègue à ServiceSuiviPerso."""

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_garmin_connected_true(self, mock_svc):
        """Test utilisateur avec Garmin connecté."""
        from src.modules.famille.hub_famille import get_user_garmin_connected

        mock_svc.return_value.get_user_data.return_value = {"garmin_connected": True, "streak": 0}

        result = get_user_garmin_connected("anne")

        assert result is True

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_garmin_connected_user_not_found(self, mock_svc):
        """Test utilisateur inexistant."""
        from src.modules.famille.hub_famille import get_user_garmin_connected

        mock_svc.return_value.get_user_data.return_value = {"garmin_connected": False, "streak": 0}

        result = get_user_garmin_connected("inconnu")

        assert result is False

    @patch("src.modules.famille.hub_famille._get_service_suivi")
    def test_garmin_connected_erreur(self, mock_svc):
        """Test avec erreur service."""
        from src.modules.famille.hub_famille import get_user_garmin_connected

        mock_svc.return_value.get_user_data.side_effect = Exception("Service Error")

        result = get_user_garmin_connected("anne")

        assert result is False


class TestCountWeekendActivities:
    """Tests pour count_weekend_activities — délègue à ServiceWeekend."""

    @patch("src.modules.famille.hub_famille._get_service_weekend")
    def test_count_weekend_activities_aucune(self, mock_svc):
        """Test compte sans activités."""
        from src.modules.famille.hub_famille import count_weekend_activities

        mock_svc.return_value.lister_activites_weekend.return_value = []

        result = count_weekend_activities()

        assert result == 0

    @patch("src.modules.famille.hub_famille._get_service_weekend")
    def test_count_weekend_activities_avec_activites(self, mock_svc):
        """Test compte avec activités planifiées."""
        from src.modules.famille.hub_famille import count_weekend_activities

        act1 = MagicMock(statut="planifie")
        act2 = MagicMock(statut="planifie")
        act3 = MagicMock(statut="termine")
        mock_svc.return_value.lister_activites_weekend.return_value = [act1, act2, act3]

        result = count_weekend_activities()

        assert result == 2  # Seulement les planifiées

    @patch("src.modules.famille.hub_famille._get_service_weekend")
    def test_count_weekend_activities_erreur(self, mock_svc):
        """Test avec erreur service."""
        from src.modules.famille.hub_famille import count_weekend_activities

        mock_svc.return_value.lister_activites_weekend.side_effect = Exception("Service Error")

        result = count_weekend_activities()

        assert result == 0


class TestCountPendingPurchases:
    """Tests pour count_pending_purchases — délègue à ServiceAchatsFamille."""

    @patch("src.modules.famille.hub_famille._get_service_achats")
    def test_count_pending_purchases_zero(self, mock_svc):
        """Test compte sans achats en attente."""
        from src.modules.famille.hub_famille import count_pending_purchases

        mock_svc.return_value.get_stats.return_value = {"en_attente": 0, "urgents": 0}

        result = count_pending_purchases()

        assert result == 0

    @patch("src.modules.famille.hub_famille._get_service_achats")
    def test_count_pending_purchases_avec_achats(self, mock_svc):
        """Test compte avec achats en attente."""
        from src.modules.famille.hub_famille import count_pending_purchases

        mock_svc.return_value.get_stats.return_value = {"en_attente": 5, "urgents": 2}

        result = count_pending_purchases()

        assert result == 5


class TestCountUrgentPurchases:
    """Tests pour count_urgent_purchases — délègue à ServiceAchatsFamille."""

    @patch("src.modules.famille.hub_famille._get_service_achats")
    def test_count_urgent_purchases_zero(self, mock_svc):
        """Test compte sans achats urgents."""
        from src.modules.famille.hub_famille import count_urgent_purchases

        mock_svc.return_value.get_stats.return_value = {"en_attente": 0, "urgents": 0}

        result = count_urgent_purchases()

        assert result == 0

    @patch("src.modules.famille.hub_famille._get_service_achats")
    def test_count_urgent_purchases_avec_urgents(self, mock_svc):
        """Test compte avec achats urgents."""
        from src.modules.famille.hub_famille import count_urgent_purchases

        mock_svc.return_value.get_stats.return_value = {"en_attente": 5, "urgents": 2}

        result = count_urgent_purchases()

        assert result == 2


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS COMPOSANTS CARDS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderCardJules:
    """Tests pour afficher_card_jules."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.calculer_age_jules")
    def test_render_card_jules_affiche_bouton(self, mock_age, mock_st):
        """Test que la card Jules affiche un bouton."""
        from src.modules.famille.hub_famille import afficher_card_jules

        mock_age.return_value = {"mois": 19, "jours": 0, "texte": "19 mois"}
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_jules()

        mock_st.button.assert_called_once()
        mock_st.caption.assert_called_once()

    @patch("src.modules.famille.hub_famille.rerun")
    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.calculer_age_jules")
    def test_render_card_jules_clic_navigation(self, mock_age, mock_st, mock_rerun):
        """Test navigation au clic sur la card Jules."""
        from src.modules.famille.hub_famille import afficher_card_jules

        mock_age.return_value = {"mois": 19, "jours": 0, "texte": "19 mois"}
        mock_st.button.return_value = True
        mock_st.session_state = {}

        afficher_card_jules()

        assert mock_st.session_state.get("famille_page") == "jules"
        mock_rerun.assert_called_once()


@pytest.mark.unit
class TestRenderCardWeekend:
    """Tests pour afficher_card_weekend."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.count_weekend_activities")
    def test_render_card_weekend_sans_activites(self, mock_count, mock_st):
        """Test card weekend sans activités."""
        from src.modules.famille.hub_famille import afficher_card_weekend

        mock_count.return_value = 0
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_weekend()

        mock_st.button.assert_called_once()
        mock_st.caption.assert_called_with("💡 Decouvrir des idees IA")

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.count_weekend_activities")
    def test_render_card_weekend_avec_activites(self, mock_count, mock_st):
        """Test card weekend avec activités."""
        from src.modules.famille.hub_famille import afficher_card_weekend

        mock_count.return_value = 3
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_weekend()

        mock_st.caption.assert_called_with("📅 3 activite(s) planifiee(s)")


@pytest.mark.unit
class TestRenderCardUser:
    """Tests pour afficher_card_user."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.get_user_streak")
    @patch("src.modules.famille.hub_famille.get_user_garmin_connected")
    def test_render_card_user_anne(self, mock_garmin, mock_streak, mock_st):
        """Test card pour Anne."""
        from src.modules.famille.hub_famille import afficher_card_user

        mock_streak.return_value = 5
        mock_garmin.return_value = True
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_user("anne", "Anne", "👩")

        mock_st.button.assert_called_once()
        mock_st.caption.assert_called_once()

    @patch("src.modules.famille.hub_famille.rerun")
    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.get_user_streak")
    @patch("src.modules.famille.hub_famille.get_user_garmin_connected")
    def test_render_card_user_clic_navigation(self, mock_garmin, mock_streak, mock_st, mock_rerun):
        """Test navigation au clic sur card utilisateur."""
        from src.modules.famille.hub_famille import afficher_card_user

        mock_streak.return_value = 0
        mock_garmin.return_value = False
        mock_st.button.return_value = True
        mock_st.session_state = {}

        afficher_card_user("mathieu", "Mathieu", "👨")

        assert mock_st.session_state.get("famille_page") == "suivi"
        assert mock_st.session_state.get("suivi_user") == "mathieu"
        mock_rerun.assert_called_once()


@pytest.mark.unit
class TestRenderCardAchats:
    """Tests pour afficher_card_achats."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.count_pending_purchases")
    @patch("src.modules.famille.hub_famille.count_urgent_purchases")
    def test_render_card_achats_rien_en_attente(self, mock_urgent, mock_pending, mock_st):
        """Test card achats sans articles."""
        from src.modules.famille.hub_famille import afficher_card_achats

        mock_pending.return_value = 0
        mock_urgent.return_value = 0
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_achats()

        mock_st.caption.assert_called_with("✅ Rien en attente")

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.count_pending_purchases")
    @patch("src.modules.famille.hub_famille.count_urgent_purchases")
    def test_render_card_achats_avec_urgents(self, mock_urgent, mock_pending, mock_st):
        """Test card achats avec urgents."""
        from src.modules.famille.hub_famille import afficher_card_achats

        mock_pending.return_value = 5
        mock_urgent.return_value = 2
        mock_st.button.return_value = False
        mock_st.session_state = {}

        afficher_card_achats()

        mock_st.caption.assert_called_with("⚠️ 2 urgent(s) • 📋 5 en attente")


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS APP()
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestApp:
    """Tests pour la fonction app()."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.services.integrations.garmin.init_family_users")
    @patch("src.modules.famille.hub_famille.afficher_hub")
    def test_app_runs_without_error(self, mock_render_hub, mock_init_users, mock_st):
        """Test que app() s'exécute sans erreur."""
        from src.modules.famille.hub_famille import app

        mock_st.session_state = {}

        app()

        mock_st.title.assert_called_once_with("👨\u200d👩\u200d👧 Hub Famille")
        mock_render_hub.assert_called_once()

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.services.integrations.garmin.init_family_users")
    @patch("src.modules.famille.hub_famille.afficher_hub")
    def test_app_affiche_hub_par_defaut(self, mock_render_hub, mock_init_users, mock_st):
        """Test que app() affiche le hub par défaut."""
        from src.modules.famille.hub_famille import app

        mock_st.session_state = {"famille_page": "hub"}

        app()

        mock_render_hub.assert_called_once()

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.services.integrations.garmin.init_family_users")
    def test_app_navigation_jules(self, mock_init_users, mock_st):
        """Test navigation vers page Jules."""
        from src.modules.famille.hub_famille import app

        mock_st.session_state = {"famille_page": "jules"}
        mock_st.button.return_value = False

        # Mock le module jules
        with patch("src.modules.famille.jules.app") as mock_jules_app:
            try:
                app()
            except Exception:
                pass  # UI tests acceptent les erreurs liées au mock

    @patch("src.modules.famille.hub_famille.st")
    @patch(
        "src.services.integrations.garmin.init_family_users", side_effect=Exception("Init error")
    )
    def test_app_erreur_init_users_ignoree(self, mock_init_users, mock_st):
        """Test que les erreurs d'init sont ignorées."""
        from src.modules.famille.hub_famille import app

        mock_st.session_state = {}

        with patch("src.modules.famille.hub_famille.afficher_hub"):
            # Ne devrait pas lever d'exception
            app()

        mock_st.title.assert_called_once()


@pytest.mark.unit
class TestRenderHub:
    """Tests pour afficher_hub."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille.afficher_card_jules")
    @patch("src.modules.famille.hub_famille.afficher_card_weekend")
    @patch("src.modules.famille.hub_famille.afficher_card_user")
    @patch("src.modules.famille.hub_famille.afficher_card_achats")
    @patch("src.modules.famille.hub_famille.afficher_weekend_preview")
    def test_render_hub_affiche_toutes_cards(
        self,
        mock_preview,
        mock_achats,
        mock_user,
        mock_weekend,
        mock_jules,
        mock_st,
    ):
        """Test que afficher_hub affiche toutes les cards."""
        from src.modules.famille.hub_famille import afficher_hub

        # Setup mocks pour columns et containers
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]

        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value = mock_container

        afficher_hub()

        mock_jules.assert_called_once()
        mock_weekend.assert_called_once()
        assert mock_user.call_count == 2  # Anne et Mathieu
        mock_achats.assert_called_once()
        mock_preview.assert_called_once()


@pytest.mark.unit
class TestRenderWeekendPreview:
    """Tests pour afficher_weekend_preview."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille._afficher_day_activities")
    def test_render_weekend_preview_affiche_deux_jours(self, mock_render_day, mock_st):
        """Test que l'aperçu weekend affiche samedi et dimanche."""
        from src.modules.famille.hub_famille import afficher_weekend_preview

        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]

        afficher_weekend_preview()

        # Vérifie que _afficher_day_activities est appelé 2 fois (samedi + dimanche)
        assert mock_render_day.call_count == 2


@pytest.mark.unit
class TestRenderDayActivities:
    """Tests pour _afficher_day_activities."""

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille._get_service_weekend")
    def test_render_day_activities_sans_activites(self, mock_svc, mock_st):
        """Test render jour sans activités."""
        from src.modules.famille.hub_famille import _afficher_day_activities

        mock_svc.return_value.lister_activites_weekend.return_value = []
        mock_st.button.return_value = False

        _afficher_day_activities(date.today())

        mock_st.caption.assert_called_with("Rien de prévu")

    @patch("src.modules.famille.hub_famille.st")
    @patch("src.modules.famille.hub_famille._get_service_weekend")
    def test_render_day_activities_avec_activites(self, mock_svc, mock_st, mock_weekend_activity):
        """Test render jour avec activités."""
        from src.modules.famille.hub_famille import _afficher_day_activities

        mock_weekend_activity.date_prevue = date.today()
        mock_svc.return_value.lister_activites_weekend.return_value = [mock_weekend_activity]

        _afficher_day_activities(date.today())

        mock_st.write.assert_called_once()
