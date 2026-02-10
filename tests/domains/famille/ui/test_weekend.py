"""
Tests pour src/domains/famille/ui/weekend/

Couverture ciblée: 80%
- helpers.py: get_next_weekend, get_weekend_activities, get_budget_weekend, etc.
- ai_service.py: WeekendAIService
- components.py: render_dashboard, render_calendar, render_activities
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, timedelta
from contextlib import contextmanager

from tests.fixtures.ui_mocks import (
    create_streamlit_mock,
    create_ui_test_context,
    assert_streamlit_called,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_st():
    """Mock Streamlit configuré pour famille."""
    return create_ui_test_context("famille")


@contextmanager
def mock_db_context():
    """Mock pour obtenir_contexte_db."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_db.get.return_value = None
    
    @contextmanager
    def context():
        yield mock_db
    
    with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
        yield mock_db


def create_mock_activity(date_prevue, statut="prévu", cout_estime=50, cout_reel=None):
    """Factory pour WeekendActivity mock."""
    act = MagicMock()
    act.id = 1
    act.date_prevue = date_prevue
    act.statut = statut
    act.cout_estime = cout_estime
    act.cout_reel = cout_reel
    act.heure_debut = "10:00"
    act.note_lieu = 4
    return act


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS - Pure functions
# ═══════════════════════════════════════════════════════════

class TestWeekendHelpersImport:
    """Tests d'import des helpers."""
    
    def test_import_helpers(self):
        """Vérifie que les helpers s'importent."""
        from src.domains.famille.ui.weekend.helpers import (
            get_next_weekend,
            get_weekend_activities,
            get_budget_weekend,
            get_lieux_testes,
            get_age_jules_mois,
            mark_activity_done,
        )
        assert callable(get_next_weekend)
        assert callable(get_weekend_activities)
        assert callable(get_budget_weekend)
        assert callable(get_lieux_testes)
        assert callable(get_age_jules_mois)
        assert callable(mark_activity_done)


class TestGetNextWeekend:
    """Tests pour get_next_weekend()."""
    
    def test_get_next_weekend_from_monday(self):
        """Test depuis lundi retourne samedi/dimanche."""
        from src.domains.famille.ui.weekend.helpers import get_next_weekend
        
        # Simule un lundi
        monday = date(2025, 7, 14)  # C'est un lundi
        
        with patch("src.domains.famille.ui.weekend.helpers.date") as mock_date:
            mock_date.today.return_value = monday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            saturday, sunday = get_next_weekend()
        
        assert saturday.weekday() == 5  # Samedi
        assert sunday.weekday() == 6  # Dimanche
        assert sunday - saturday == timedelta(days=1)
    
    def test_get_next_weekend_from_saturday(self):
        """Test depuis samedi retourne ce weekend."""
        from src.domains.famille.ui.weekend.helpers import get_next_weekend
        
        saturday_date = date(2025, 7, 19)  # C'est un samedi
        
        with patch("src.domains.famille.ui.weekend.helpers.date") as mock_date:
            mock_date.today.return_value = saturday_date
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            saturday, sunday = get_next_weekend()
        
        assert saturday == saturday_date
        assert sunday == saturday_date + timedelta(days=1)
    
    def test_get_next_weekend_from_sunday(self):
        """Test depuis dimanche retourne le prochain weekend."""
        from src.domains.famille.ui.weekend.helpers import get_next_weekend
        
        sunday_date = date(2025, 7, 20)  # C'est un dimanche
        
        with patch("src.domains.famille.ui.weekend.helpers.date") as mock_date:
            mock_date.today.return_value = sunday_date
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            saturday, sunday = get_next_weekend()
        
        # Le prochain samedi
        assert saturday.weekday() == 5
    
    def test_get_next_weekend_returns_valid_dates(self):
        """Test que la fonction retourne des dates valides."""
        from src.domains.famille.ui.weekend.helpers import get_next_weekend
        
        saturday, sunday = get_next_weekend()
        
        assert isinstance(saturday, date)
        assert isinstance(sunday, date)
        assert sunday > saturday


class TestGetWeekendActivities:
    """Tests pour get_weekend_activities()."""
    
    def test_get_weekend_activities_empty(self):
        """Test sans activités."""
        from src.domains.famille.ui.weekend.helpers import get_weekend_activities
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        with mock_db_context():
            result = get_weekend_activities(saturday, sunday)
        
        assert result == {"saturday": [], "sunday": []}
    
    def test_get_weekend_activities_with_data(self):
        """Test avec activités."""
        from src.domains.famille.ui.weekend.helpers import get_weekend_activities
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        mock_activities = [
            create_mock_activity(saturday),
            create_mock_activity(sunday),
        ]
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_activities
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            result = get_weekend_activities(saturday, sunday)
        
        assert len(result["saturday"]) == 1
        assert len(result["sunday"]) == 1
    
    def test_get_weekend_activities_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.weekend.helpers import get_weekend_activities
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_weekend_activities(date.today(), date.today())
        
        assert result == {"saturday": [], "sunday": []}


class TestGetBudgetWeekend:
    """Tests pour get_budget_weekend()."""
    
    def test_get_budget_weekend_empty(self):
        """Test sans activités."""
        from src.domains.famille.ui.weekend.helpers import get_budget_weekend
        
        with mock_db_context():
            result = get_budget_weekend(date.today(), date.today())
        
        assert result == {"estime": 0, "reel": 0}
    
    def test_get_budget_weekend_with_data(self):
        """Test avec activités."""
        from src.domains.famille.ui.weekend.helpers import get_budget_weekend
        
        mock_activities = [
            create_mock_activity(date.today(), statut="prévu", cout_estime=50),
            create_mock_activity(date.today(), statut="terminé", cout_estime=30, cout_reel=25),
        ]
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = mock_activities
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            result = get_budget_weekend(date.today(), date.today())
        
        assert result["estime"] == 80  # 50 + 30
        assert result["reel"] == 25  # Seulement l'activité terminée
    
    def test_get_budget_weekend_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.weekend.helpers import get_budget_weekend
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_budget_weekend(date.today(), date.today())
        
        assert result == {"estime": 0, "reel": 0}


class TestGetLieuxTestes:
    """Tests pour get_lieux_testes()."""
    
    def test_get_lieux_testes_empty(self):
        """Test sans lieux."""
        from src.domains.famille.ui.weekend.helpers import get_lieux_testes
        
        with mock_db_context():
            result = get_lieux_testes()
        
        assert result == []
    
    def test_get_lieux_testes_with_data(self):
        """Test avec lieux."""
        from src.domains.famille.ui.weekend.helpers import get_lieux_testes
        
        mock_lieux = [create_mock_activity(date.today(), statut="terminé")]
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_lieux
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            result = get_lieux_testes()
        
        assert len(result) == 1
    
    def test_get_lieux_testes_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.weekend.helpers import get_lieux_testes
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_lieux_testes()
        
        assert result == []


class TestGetAgeJulesMois:
    """Tests pour get_age_jules_mois()."""
    
    def test_get_age_jules_mois_with_profile(self):
        """Test avec profil Jules."""
        from src.domains.famille.ui.weekend.helpers import get_age_jules_mois
        
        mock_jules = MagicMock()
        mock_jules.date_of_birth = date(2024, 6, 22)
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_jules
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            result = get_age_jules_mois()
        
        assert isinstance(result, int)
        assert result >= 0
    
    def test_get_age_jules_mois_without_profile(self):
        """Test sans profil (valeur par défaut)."""
        from src.domains.famille.ui.weekend.helpers import get_age_jules_mois
        
        with mock_db_context():
            result = get_age_jules_mois()
        
        assert result == 19  # Valeur par défaut
    
    def test_get_age_jules_mois_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.weekend.helpers import get_age_jules_mois
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            result = get_age_jules_mois()
        
        assert result == 19  # Valeur par défaut


class TestMarkActivityDone:
    """Tests pour mark_activity_done()."""
    
    def test_mark_activity_done_success(self):
        """Test marquer terminé avec succès."""
        from src.domains.famille.ui.weekend.helpers import mark_activity_done
        
        mock_activity = MagicMock()
        mock_db = MagicMock()
        mock_db.get.return_value = mock_activity
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            mark_activity_done(1)
        
        assert mock_activity.statut == "terminé"
        mock_db.commit.assert_called_once()
    
    def test_mark_activity_done_not_found(self):
        """Test avec activité non trouvée."""
        from src.domains.famille.ui.weekend.helpers import mark_activity_done
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db", context):
            # Ne doit pas lever d'exception
            mark_activity_done(999)
        
        mock_db.commit.assert_not_called()
    
    def test_mark_activity_done_db_error(self):
        """Test avec erreur DB."""
        from src.domains.famille.ui.weekend.helpers import mark_activity_done
        
        with patch("src.domains.famille.ui.weekend.helpers.obtenir_contexte_db",
                   side_effect=Exception("DB Error")):
            # Ne doit pas lever d'exception
            mark_activity_done(1)


# ═══════════════════════════════════════════════════════════
# TESTS COMPONENTS
# ═══════════════════════════════════════════════════════════

class TestWeekendComponents:
    """Tests pour weekend/components.py"""
    
    def test_import_components(self):
        """Vérifie l'import des composants."""
        from src.domains.famille.ui.weekend.components import (
            render_planning,
            render_day_activities,
            render_suggestions,
            render_lieux_testes,
            render_add_activity,
            render_noter_sortie,
        )
        assert callable(render_planning)
        assert callable(render_day_activities)
        assert callable(render_suggestions)
        assert callable(render_lieux_testes)
        assert callable(render_add_activity)
        assert callable(render_noter_sortie)
    
    def test_render_planning(self, mock_st):
        """Test render_planning affiche les metrics."""
        from src.domains.famille.ui.weekend import components
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_next_weekend", return_value=(saturday, sunday)):
                with patch.object(components, "get_weekend_activities", return_value={
                    "saturday": [], "sunday": []
                }):
                    with patch.object(components, "get_budget_weekend", return_value={
                        "estime": 100, "reel": 80
                    }):
                        with patch.object(components, "render_day_activities", MagicMock()):
                            components.render_planning()
        
        mock_st.subheader.assert_called()
        assert mock_st.columns.called
    
    def test_render_day_activities_empty(self, mock_st):
        """Test render_day_activities sans activités."""
        from src.domains.famille.ui.weekend import components
        
        with patch.object(components, "st", mock_st):
            components.render_day_activities(date(2025, 7, 19), [])
        
        mock_st.caption.assert_called()
        assert mock_st.button.called
    
    def test_render_day_activities_with_data(self, mock_st):
        """Test render_day_activities avec activités."""
        from src.domains.famille.ui.weekend import components
        
        mock_activity = create_mock_activity(date(2025, 7, 19))
        mock_activity.type_activite = "parc"
        mock_activity.nom = "Parc test"
        mock_activity.heure_debut = "10:00"
        mock_activity.duree_minutes = 60
        mock_activity.statut = "prévu"
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "mark_activity_done", MagicMock()):
                components.render_day_activities(date(2025, 7, 19), [mock_activity])
        
        assert mock_st.container.called


class TestWeekendComponentsAdvanced:
    """Tests avancés pour weekend/components.py"""
    
    def test_render_suggestions(self, mock_st):
        """Test render_suggestions rendu."""
        from src.domains.famille.ui.weekend import components
        
        mock_st.button.return_value = False  # Bouton non cliqué
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules_mois", return_value=19):
                components.render_suggestions()
        
        mock_st.subheader.assert_called()
        assert mock_st.columns.called
        mock_st.selectbox.assert_called()
        mock_st.slider.assert_called()
    
    def test_render_suggestions_with_click(self, mock_st):
        """Test render_suggestions avec clic sur bouton IA."""
        from src.domains.famille.ui.weekend import components
        
        mock_st.button.return_value = True  # Bouton cliqué
        mock_st.selectbox.return_value = "ensoleillé"
        mock_st.slider.return_value = 50
        mock_st.text_input.return_value = "Paris"
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules_mois", return_value=19):
                with patch.object(components, "WeekendAIService") as mock_ai:
                    import asyncio
                    mock_service = MagicMock()
                    mock_service.suggerer_activites = MagicMock(return_value="Suggestion test")
                    mock_ai.return_value = mock_service
                    
                    with patch("asyncio.run", return_value="Suggestion test"):
                        components.render_suggestions()
        
        mock_st.spinner.assert_called()
    
    def test_render_lieux_testes_empty(self, mock_st):
        """Test render_lieux_testes sans lieux."""
        from src.domains.famille.ui.weekend import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_lieux_testes", return_value=[]):
                components.render_lieux_testes()
        
        mock_st.subheader.assert_called()
        mock_st.info.assert_called()
    
    def test_render_lieux_testes_with_data(self, mock_st):
        """Test render_lieux_testes avec données."""
        from src.domains.famille.ui.weekend import components
        
        mock_lieu = create_mock_activity(date(2025, 7, 19), statut="terminé")
        mock_lieu.type_activite = "parc"
        mock_lieu.titre = "Parc de la Villette"
        mock_lieu.lieu = "Paris"
        mock_lieu.commentaire = "Super!"
        mock_lieu.note_lieu = 4
        mock_lieu.a_refaire = True
        mock_lieu.cout_reel = 30
        
        mock_st.selectbox.return_value = "Tous"
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_lieux_testes", return_value=[mock_lieu]):
                components.render_lieux_testes()
        
        mock_st.subheader.assert_called()
        assert mock_st.container.called
    
    def test_render_add_activity(self, mock_st):
        """Test render_add_activity formulaire."""
        from src.domains.famille.ui.weekend import components
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        mock_st.form_submit_button.return_value = False
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_next_weekend", return_value=(saturday, sunday)):
                components.render_add_activity()
        
        mock_st.subheader.assert_called()
        mock_st.form.assert_called()
        mock_st.text_input.assert_called()
    
    def test_render_add_activity_submit(self, mock_st):
        """Test render_add_activity soumission formulaire."""
        from src.domains.famille.ui.weekend import components
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.side_effect = ["Parc test", "Paris"]
        mock_st.selectbox.side_effect = ["parc", saturday]
        mock_st.time_input.return_value = MagicMock()
        mock_st.number_input.side_effect = [60, 30]
        mock_st.text_area.return_value = "Notes"
        
        mock_db = MagicMock()
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_next_weekend", return_value=(saturday, sunday)):
                with patch.object(components, "obtenir_contexte_db", context):
                    components.render_add_activity()
        
        mock_db.add.assert_called()
    
    def test_render_noter_sortie(self, mock_st):
        """Test render_noter_sortie formulaire."""
        from src.domains.famille.ui.weekend import components
        
        mock_st.form_submit_button.return_value = False
        
        mock_activity = create_mock_activity(date(2025, 7, 19), statut="terminé")
        mock_activity.id = 1
        mock_activity.titre = "Sortie test"
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "obtenir_contexte_db", context):
                components.render_noter_sortie()
        
        mock_st.subheader.assert_called()
    
    def test_render_noter_sortie_no_activities(self, mock_st):
        """Test render_noter_sortie sans activités à noter."""
        from src.domains.famille.ui.weekend import components
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "obtenir_contexte_db", context):
                components.render_noter_sortie()
        
        mock_st.info.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS MODULE APP
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# TESTS AI SERVICE
# ═══════════════════════════════════════════════════════════

class TestWeekendAIServiceImport:
    """Tests d'import du service IA."""
    
    def test_import_ai_service(self):
        """Vérifie l'import du service IA."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        assert WeekendAIService is not None
    
    def test_ai_service_inherits_base(self):
        """Vérifie l'héritage de BaseAIService."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        from src.services.base_ai_service import BaseAIService
        
        assert issubclass(WeekendAIService, BaseAIService)


class TestWeekendAIServiceInit:
    """Tests pour l'initialisation du service IA."""
    
    def test_init_with_defaults(self):
        """Test initialisation avec valeurs par défaut."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
        
        assert service.cache_prefix == "weekend"
        assert service.default_ttl == 3600
        assert service.service_name == "weekend_ai"
    
    def test_init_creates_client(self):
        """Test que l'initialisation crée un ClientIA."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_client.assert_called_once()


class TestSuggererActivites:
    """Tests pour suggerer_activites()."""
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_default_params(self):
        """Test avec paramètres par défaut."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Suggestions test")
            result = await service.suggerer_activites()
        
        assert "Suggestions test" in result
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_custom_params(self):
        """Test avec paramètres personnalisés."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Custom suggestions")
            service.call_with_cache = mock_call
            
            result = await service.suggerer_activites(
                meteo="ensoleillé",
                age_enfant_mois=24,
                budget=100,
                region="Lyon",
                nb_suggestions=5
            )
            
            # Vérifier que le prompt contient les paramètres
            call_args = mock_call.call_args
            prompt = call_args[1]["prompt"]
            
            assert "24 mois" in prompt
            assert "ensoleillé" in prompt
            assert "100" in prompt
            assert "Lyon" in prompt
            assert "5 activités" in prompt
        
        assert result == "Custom suggestions"
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_uses_cache(self):
        """Test que la méthode utilise le cache."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Cached")
            service.call_with_cache = mock_call
            
            await service.suggerer_activites()
            
            mock_call.assert_called_once()
            assert mock_call.call_args[1]["max_tokens"] == 800
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_prompt_structure(self):
        """Test la structure du prompt généré."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Result")
            service.call_with_cache = mock_call
            
            await service.suggerer_activites(
                meteo="pluvieux",
                age_enfant_mois=18,
                budget=40,
                region="Paris",
                nb_suggestions=2
            )
            
            prompt = mock_call.call_args[1]["prompt"]
            
            # Vérifier des éléments clés du prompt
            assert "18 mois" in prompt
            assert "pluvieux" in prompt
            assert "40€" in prompt
            assert "Paris" in prompt
            assert "2 activités" in prompt
            assert "🎯" in prompt  # Emoji pour activité
            assert "📍" in prompt  # Emoji pour lieu
            assert "💰" in prompt  # Emoji pour budget


class TestDetailsLieu:
    """Tests pour details_lieu()."""
    
    @pytest.mark.asyncio
    async def test_details_lieu_basic(self):
        """Test récupération détails lieu."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Détails du lieu")
            result = await service.details_lieu("Jardin des Plantes", "parc")
        
        assert "Détails du lieu" in result
    
    @pytest.mark.asyncio
    async def test_details_lieu_prompt_content(self):
        """Test contenu du prompt pour détails lieu."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Info")
            service.call_with_cache = mock_call
            
            await service.details_lieu("Musée d'Orsay", "musee")
            
            prompt = mock_call.call_args[1]["prompt"]
            
            assert "Musée d'Orsay" in prompt
            assert "musee" in prompt
            assert "Horaires" in prompt
            assert "Tarifs" in prompt
            assert "poussette" in prompt or "change" in prompt
    
    @pytest.mark.asyncio
    async def test_details_lieu_max_tokens(self):
        """Test limite de tokens pour détails lieu."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Result")
            service.call_with_cache = mock_call
            
            await service.details_lieu("Zoo de Vincennes", "zoo")
            
            assert mock_call.call_args[1]["max_tokens"] == 500
    
    @pytest.mark.asyncio
    async def test_details_lieu_system_prompt(self):
        """Test system prompt pour détails lieu."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            mock_call = AsyncMock(return_value="Result")
            service.call_with_cache = mock_call
            
            await service.details_lieu("Aquarium de Paris", "piscine")
            
            system_prompt = mock_call.call_args[1]["system_prompt"]
            assert "guide" in system_prompt.lower() or "touristique" in system_prompt.lower()


class TestWeekendAIServiceEdgeCases:
    """Tests pour cas limites du service IA."""
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_age_zero(self):
        """Test avec âge 0 mois."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Baby activities")
            result = await service.suggerer_activites(age_enfant_mois=0)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_high_budget(self):
        """Test avec budget élevé."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Luxury activities")
            result = await service.suggerer_activites(budget=500)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_suggerer_activites_zero_budget(self):
        """Test avec budget 0."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Free activities")
            result = await service.suggerer_activites(budget=0)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_details_lieu_special_characters(self):
        """Test avec caractères spéciaux dans le nom du lieu."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Result")
            result = await service.details_lieu("Café-Restaurant L'Étoile", "restaurant")
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_details_lieu_empty_name(self):
        """Test avec nom vide."""
        from src.domains.famille.ui.weekend.ai_service import WeekendAIService
        
        with patch("src.domains.famille.ui.weekend.ai_service.ClientIA") as mock_client:
            mock_client.return_value = MagicMock()
            service = WeekendAIService()
            
            service.call_with_cache = AsyncMock(return_value="Result")
            result = await service.details_lieu("", "autre")
        
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS MODULE APP
# ═══════════════════════════════════════════════════════════

class TestWeekendApp:
    """Tests pour weekend/__init__.py (app entry point)"""
    
    def test_import_app(self):
        """Vérifie l'import de app."""
        from src.domains.famille.ui.weekend import app
        assert callable(app)
    
    def test_app_renders_without_error(self, mock_st):
        """Test que app() s'exécute."""
        from src.domains.famille.ui import weekend
        
        saturday = date(2025, 7, 19)
        sunday = date(2025, 7, 20)
        
        with patch.object(weekend, "st", mock_st):
            with patch.object(weekend, "get_next_weekend", return_value=(saturday, sunday)):
                with patch.object(weekend, "render_planning", MagicMock()):
                    with patch.object(weekend, "render_suggestions", MagicMock()):
                        with patch.object(weekend, "render_add_activity", MagicMock()):
                            with patch.object(weekend, "render_lieux_testes", MagicMock()):
                                with patch.object(weekend, "render_noter_sortie", MagicMock()):
                                    weekend.app()
        
        mock_st.title.assert_called()

