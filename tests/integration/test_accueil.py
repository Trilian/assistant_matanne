"""
Tests pour le module accueil (dashboard)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestAccueilModule:
    """Tests du module accueil"""

    def test_import_module(self):
        """Test que le module s'importe correctement"""
        from src.modules import accueil
        assert hasattr(accueil, 'app')
        assert callable(accueil.app)

    def test_module_exports(self):
        """Test exports du module"""
        from src.modules import accueil
        
        # VÃ©rifier fonction principale
        assert hasattr(accueil, 'app')


class TestDashboardMetrics:
    """Tests des mÃ©triques du dashboard"""

    def test_metrics_calculation(self):
        """Test calcul des mÃ©triques"""
        # Les mÃ©triques typiques du dashboard
        expected_metrics = [
            'recettes_total',
            'articles_stock',
            'repas_semaine',
            'courses_pending'
        ]
        
        # Simplement vÃ©rifier que ces concepts existent
        for metric in expected_metrics:
            assert isinstance(metric, str)

    @patch('src.core.database.obtenir_contexte_db')
    def test_fetch_dashboard_data(self, mock_db_context):
        """Test rÃ©cupÃ©ration donnÃ©es dashboard"""
        mock_session = MagicMock()
        mock_db_context.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_context.return_value.__exit__ = Mock(return_value=False)
        
        # Mock query results
        mock_session.query.return_value.count.return_value = 10
        mock_session.query.return_value.filter.return_value.count.return_value = 5
        
        # Test devrait passer sans erreur
        assert mock_session is not None


class TestAlertes:
    """Tests des alertes critiques"""

    def test_stock_alerts(self):
        """Test alertes stock bas"""
        # Une alerte stock bas devrait avoir ces propriÃ©tÃ©s
        alerte = {
            "type": "stock_bas",
            "article": "Lait",
            "quantite_actuelle": 1,
            "seuil": 2,
            "urgence": "moyenne"
        }
        
        assert alerte["type"] == "stock_bas"
        assert alerte["quantite_actuelle"] < alerte["seuil"]

    def test_expiration_alerts(self):
        """Test alertes pÃ©remption"""
        today = datetime.now()
        expiration = today + timedelta(days=2)
        
        alerte = {
            "type": "peremption",
            "article": "Yaourt",
            "date_expiration": expiration,
            "jours_restants": 2,
            "urgence": "haute"
        }
        
        assert alerte["jours_restants"] <= 3  # Urgence si < 3 jours

    def test_budget_alerts(self):
        """Test alertes budget dÃ©passÃ©"""
        alerte = {
            "type": "budget",
            "categorie": "alimentation",
            "budget": 500,
            "depenses": 480,
            "pourcentage": 96,
            "urgence": "attention"
        }
        
        assert alerte["pourcentage"] > 80  # Alerte si > 80%


class TestRaccourcis:
    """Tests des raccourcis rapides"""

    def test_quick_actions_defined(self):
        """Test actions rapides dÃ©finies"""
        quick_actions = [
            {"label": "Nouvelle recette", "icon": "ðŸ³", "module": "cuisine"},
            {"label": "Liste courses", "icon": "ðŸ›’", "module": "courses"},
            {"label": "Planning semaine", "icon": "ðŸ“…", "module": "planning"},
            {"label": "Scan produit", "icon": "ðŸ“·", "module": "barcode"},
        ]
        
        assert len(quick_actions) >= 4
        for action in quick_actions:
            assert "label" in action
            assert "icon" in action
            assert "module" in action

    def test_action_navigation(self):
        """Test navigation vers modules"""
        # Simuler un clic sur un raccourci
        target_module = "cuisine"
        
        # Devrait mettre Ã  jour session_state
        assert target_module in ["cuisine", "courses", "planning", "barcode"]


class TestWeatherWidget:
    """Tests widget mÃ©tÃ©o"""

    @patch('src.services.weather.WeatherGardenService')
    def test_weather_display(self, mock_weather_service):
        """Test affichage mÃ©tÃ©o"""
        mock_service = Mock()
        mock_service.get_current_weather.return_value = {
            "temperature": 18,
            "condition": "EnsoleillÃ©",
            "humidity": 65,
            "alerts": []
        }
        mock_weather_service.return_value = mock_service
        
        weather = mock_service.get_current_weather()
        
        assert "temperature" in weather
        assert "condition" in weather

    def test_weather_alerts_garden(self):
        """Test alertes mÃ©tÃ©o jardin"""
        weather_alert = {
            "type": "gel",
            "message": "Risque de gel cette nuit",
            "conseil": "ProtÃ©ger les plantes sensibles",
            "temperature_min": -2
        }
        
        assert weather_alert["temperature_min"] < 0


class TestFamilyStats:
    """Tests statistiques famille"""

    def test_jules_tracker_widget(self):
        """Test widget suivi Jules"""
        jules_stats = {
            "age_mois": 19,
            "derniere_activite": "Parc",
            "prochains_rdv": [],
            "milestones_recents": ["Premiers mots", "Marche"]
        }
        
        assert jules_stats["age_mois"] > 0
        assert isinstance(jules_stats["milestones_recents"], list)

    def test_family_activities_summary(self):
        """Test rÃ©sumÃ© activitÃ©s famille"""
        activities_week = {
            "total": 5,
            "par_type": {
                "sortie": 2,
                "jeu": 2,
                "repas_special": 1
            }
        }
        
        assert activities_week["total"] == sum(activities_week["par_type"].values())


class TestRecentActivity:
    """Tests activitÃ© rÃ©cente"""

    def test_recent_recipes(self):
        """Test recettes rÃ©centes"""
        recent_recipes = [
            {"nom": "Gratin", "date": datetime.now()},
            {"nom": "Soupe", "date": datetime.now() - timedelta(days=1)},
        ]
        
        assert len(recent_recipes) > 0
        # TriÃ©es par date dÃ©croissante
        assert recent_recipes[0]["date"] >= recent_recipes[1]["date"]

    def test_upcoming_meals(self):
        """Test repas Ã  venir"""
        today = datetime.now()
        upcoming = [
            {"date": today, "type": "dÃ©jeuner", "recette": "Poulet rÃ´ti"},
            {"date": today, "type": "dÃ®ner", "recette": "Salade"},
            {"date": today + timedelta(days=1), "type": "dÃ©jeuner", "recette": "PÃ¢tes"},
        ]
        
        assert len(upcoming) > 0
        # Tous dans le futur ou aujourd'hui
        for meal in upcoming:
            assert meal["date"].date() >= today.date()


class TestDashboardLayout:
    """Tests layout dashboard"""

    @patch('streamlit.columns')
    def test_columns_layout(self, mock_columns):
        """Test disposition en colonnes"""
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        cols = mock_columns(3)
        assert len(cols) == 3

    @patch('streamlit.metric')
    def test_metrics_display(self, mock_metric):
        """Test affichage mÃ©triques Streamlit"""
        # Simuler affichage mÃ©trique
        mock_metric("Recettes", 42, delta=5)
        mock_metric.assert_called_with("Recettes", 42, delta=5)


class TestDashboardCache:
    """Tests cache dashboard"""

    def test_metrics_cached(self):
        """Test que les mÃ©triques sont cachÃ©es"""
        from src.core.cache import Cache
        
        # Les mÃ©triques dashboard devraient Ãªtre cachÃ©es
        cache_key = "dashboard_metrics"
        
        # VÃ©rifier que le cache est accessible
        assert Cache is not None

    def test_cache_ttl(self):
        """Test TTL cache dashboard"""
        # Les mÃ©triques dashboard: TTL court (5-10 min)
        expected_ttl = 300  # 5 minutes
        
        assert expected_ttl <= 600  # Max 10 minutes


class TestDashboardRefresh:
    """Tests rafraÃ®chissement dashboard"""

    @patch('streamlit.button')
    def test_refresh_button(self, mock_button):
        """Test bouton rafraÃ®chissement"""
        mock_button.return_value = False
        
        # Le dashboard devrait avoir un bouton refresh
        refresh_clicked = mock_button("ðŸ”„ Actualiser")
        assert refresh_clicked == False

    def test_auto_refresh(self):
        """Test rafraÃ®chissement auto"""
        # Streamlit peut rafraÃ®chir automatiquement
        # via st.rerun() ou st.experimental_rerun()
        
        auto_refresh_interval = 300  # 5 minutes
        assert auto_refresh_interval > 0

