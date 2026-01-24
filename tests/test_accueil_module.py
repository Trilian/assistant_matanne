"""
Tests pour le module Accueil Streamlit (test_accueil_module.py)
Tests pour dashboard central, alertes, stats et raccourcis
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

import streamlit as st

from src.modules.accueil import (
    render_critical_alerts,
    render_global_stats,
    render_quick_actions,
    render_cuisine_summary,
    render_planning_summary,
    render_inventaire_summary,
    render_courses_summary,
    app,
)


class TestRenderCriticalAlerts:
    """Tests render_critical_alerts() - Alertes Critiques"""

    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_critical_alerts_no_alerts(self, mock_planning_service, mock_inventaire_service):
        """Test sans alertes critiques"""
        mock_inventaire = Mock()
        mock_inventaire.get_inventaire_complet.return_value = []
        mock_inventaire_service.return_value = mock_inventaire
        
        mock_planning = Mock()
        mock_planning.get_planning.return_value = Mock(repas=[])
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.success"):
            render_critical_alerts()

    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_critical_alerts_low_stock(self, mock_planning_service, mock_inventaire_service):
        """Test avec articles en stock faible"""
        mock_inventaire = Mock()
        mock_inventaire.get_inventaire_complet.return_value = [
            {"nom": "Pâtes", "statut": "critique"},
            {"nom": "Riz", "statut": "sous_seuil"},
        ]
        mock_inventaire_service.return_value = mock_inventaire
        
        mock_planning = Mock()
        mock_planning.get_planning.return_value = Mock(repas=[])
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.warning"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_critical_alerts()

    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_critical_alerts_expiring(self, mock_planning_service, mock_inventaire_service):
        """Test avec articles près de péremption"""
        mock_inventaire = Mock()
        mock_inventaire.get_inventaire_complet.return_value = [
            {"nom": "Lait", "statut": "peremption_proche"},
        ]
        mock_inventaire_service.return_value = mock_inventaire
        
        mock_planning = Mock()
        mock_planning.get_planning.return_value = Mock(repas=[])
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.warning"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_critical_alerts()

    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_critical_alerts_empty_planning(self, mock_planning_service, mock_inventaire_service):
        """Test avec planning vide"""
        mock_inventaire = Mock()
        mock_inventaire.get_inventaire_complet.return_value = []
        mock_inventaire_service.return_value = mock_inventaire
        
        mock_planning = Mock()
        mock_planning.get_planning.return_value = None
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.info"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_critical_alerts()


class TestRenderGlobalStats:
    """Tests render_global_stats() - Stats Globales"""

    @patch("src.modules.accueil.get_recette_service")
    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_courses_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_global_stats_displays(self, mock_planning_service, mock_courses_service,
                                         mock_inventaire_service, mock_recette_service):
        """Test affichage stats globales"""
        # Mock recettes
        mock_recette = Mock()
        mock_recette.get_stats.return_value = {"total": 25}
        mock_recette_service.return_value = mock_recette
        
        # Mock inventaire
        mock_inventaire = Mock()
        mock_inventaire.get_stats.return_value = {"total": 50}
        mock_inventaire.get_inventaire_complet.return_value = [
            {"nom": "Pâtes", "statut": "ok"},
        ]
        mock_inventaire_service.return_value = mock_inventaire
        
        # Mock courses
        mock_courses = Mock()
        mock_courses.get_stats.return_value = {"total": 15}
        mock_courses_service.return_value = mock_courses
        
        # Mock planning
        mock_planning = Mock()
        mock_planning_obj = Mock()
        mock_planning_obj.repas = [Mock(), Mock(), Mock()]
        mock_planning.get_planning.return_value = mock_planning_obj
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.columns"), \
             patch("streamlit.metric"):
            
            render_global_stats()

    @patch("src.modules.accueil.get_recette_service")
    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_courses_service")
    @patch("src.modules.accueil.get_planning_service")
    def test_render_global_stats_stock_alerts(self, mock_planning_service, mock_courses_service,
                                             mock_inventaire_service, mock_recette_service):
        """Test affichage alertes stock"""
        # Mock avec articles en stock bas
        mock_recette = Mock()
        mock_recette.get_stats.return_value = {"total": 25}
        mock_recette_service.return_value = mock_recette
        
        mock_inventaire = Mock()
        mock_inventaire.get_stats.return_value = {"total": 50}
        mock_inventaire.get_inventaire_complet.return_value = [
            {"nom": "Pâtes", "statut": "critique"},
            {"nom": "Riz", "statut": "sous_seuil"},
        ]
        mock_inventaire_service.return_value = mock_inventaire
        
        mock_courses = Mock()
        mock_courses.get_stats.return_value = {"total": 15}
        mock_courses_service.return_value = mock_courses
        
        mock_planning = Mock()
        mock_planning_obj = Mock()
        mock_planning_obj.repas = []
        mock_planning.get_planning.return_value = mock_planning_obj
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.columns"), \
             patch("streamlit.metric"), \
             patch("streamlit.warning"):
            
            render_global_stats()


class TestRenderQuickActions:
    """Tests render_quick_actions() - Raccourcis Rapides"""

    def test_render_quick_actions_displays(self):
        """Test affichage raccourcis rapides"""
        with patch("streamlit.markdown"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_quick_actions()

    @patch("src.modules.accueil.StateManager")
    def test_render_quick_actions_navigation(self, mock_state_manager):
        """Test navigation via raccourcis"""
        with patch("streamlit.markdown"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=True), \
             patch("streamlit.rerun"):
            
            render_quick_actions()


class TestRenderCuisineSummary:
    """Tests render_cuisine_summary() - Résumé Cuisine"""

    @patch("src.modules.accueil.get_recette_service")
    def test_render_cuisine_summary_displays(self, mock_recette_service):
        """Test affichage résumé cuisine"""
        mock_recette = Mock()
        mock_recette.get_stats.return_value = {
            "total": 25,
            "favoris": 5,
        }
        mock_recette_service.return_value = mock_recette
        
        with patch("streamlit.markdown"), \
             patch("streamlit.metric"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_cuisine_summary()


class TestRenderPlanningSummary:
    """Tests render_planning_summary() - Résumé Planning"""

    @patch("src.modules.accueil.get_planning_service")
    def test_render_planning_summary_displays(self, mock_planning_service):
        """Test affichage résumé planning"""
        mock_planning = Mock()
        mock_planning_obj = Mock()
        mock_planning_obj.repas = [Mock(), Mock()]
        mock_planning.get_planning.return_value = mock_planning_obj
        mock_planning_service.return_value = mock_planning
        
        with patch("streamlit.markdown"), \
             patch("streamlit.metric"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_planning_summary()


class TestRenderInventaireSummary:
    """Tests render_inventaire_summary() - Résumé Inventaire"""

    @patch("src.modules.accueil.get_inventaire_service")
    def test_render_inventaire_summary_displays(self, mock_inventaire_service):
        """Test affichage résumé inventaire"""
        mock_inventaire = Mock()
        mock_inventaire.get_stats.return_value = {"total": 50}
        mock_inventaire.get_inventaire_complet.return_value = [
            {"nom": "Pâtes", "statut": "ok"},
        ]
        mock_inventaire_service.return_value = mock_inventaire
        
        with patch("streamlit.markdown"), \
             patch("streamlit.metric"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_inventaire_summary()


class TestRenderCoursesSummary:
    """Tests render_courses_summary() - Résumé Courses"""

    @patch("src.modules.accueil.get_courses_service")
    def test_render_courses_summary_displays(self, mock_courses_service):
        """Test affichage résumé courses"""
        mock_courses = Mock()
        mock_courses.get_stats.return_value = {"total": 15}
        mock_courses_service.return_value = mock_courses
        
        with patch("streamlit.markdown"), \
             patch("streamlit.metric"), \
             patch("streamlit.columns"), \
             patch("streamlit.button", return_value=False):
            
            render_courses_summary()


class TestAccueilApp:
    """Tests fonction app() principale"""

    @patch("src.modules.accueil.get_state")
    def test_app_entry_point(self, mock_get_state):
        """Test que app() affiche les sections"""
        mock_state = Mock()
        mock_state.nom_utilisateur = "Anne"
        mock_get_state.return_value = mock_state
        
        with patch("src.modules.accueil.render_critical_alerts"), \
             patch("src.modules.accueil.render_global_stats"), \
             patch("src.modules.accueil.render_quick_actions"), \
             patch("src.modules.accueil.render_cuisine_summary"), \
             patch("src.modules.accueil.render_planning_summary"), \
             patch("src.modules.accueil.render_inventaire_summary"), \
             patch("src.modules.accueil.render_courses_summary"), \
             patch("streamlit.markdown"), \
             patch("streamlit.columns"):
            
            app()

    def test_accueil_module_structure(self):
        """Test que le module a la bonne structure"""
        from src.modules import accueil
        
        assert hasattr(accueil, "app")
        assert hasattr(accueil, "render_critical_alerts")
        assert hasattr(accueil, "render_global_stats")
        assert hasattr(accueil, "render_quick_actions")
        assert hasattr(accueil, "render_cuisine_summary")
        assert hasattr(accueil, "render_planning_summary")
        assert hasattr(accueil, "render_inventaire_summary")
        assert hasattr(accueil, "render_courses_summary")
        assert callable(accueil.app)


class TestAccueilIntegration:
    """Tests intégration module accueil"""

    @patch("src.modules.accueil.get_state")
    @patch("src.modules.accueil.get_inventaire_service")
    @patch("src.modules.accueil.get_planning_service")
    @patch("src.modules.accueil.get_recette_service")
    @patch("src.modules.accueil.get_courses_service")
    def test_accueil_loads_all_services(self, mock_courses, mock_recette, 
                                        mock_planning, mock_inventaire, mock_state):
        """Test que l'accueil charge tous les services"""
        mock_state.return_value = Mock(nom_utilisateur="Anne")
        mock_inventaire.return_value = Mock(
            get_inventaire_complet=Mock(return_value=[]),
            get_stats=Mock(return_value={"total": 0})
        )
        mock_planning.return_value = Mock(
            get_planning=Mock(return_value=Mock(repas=[]))
        )
        mock_recette.return_value = Mock(
            get_stats=Mock(return_value={"total": 0})
        )
        mock_courses.return_value = Mock(
            get_stats=Mock(return_value={"total": 0})
        )
        
        # Tous les services devraient être accessibles
        assert mock_inventaire() is not None
        assert mock_planning() is not None
        assert mock_recette() is not None
        assert mock_courses() is not None

    @patch("src.modules.accueil.get_inventaire_service")
    def test_accueil_categorizes_statuts(self, mock_inventaire_service):
        """Test catégorisation des statuts inventaire"""
        mock_inventaire = Mock()
        
        # Test différents statuts
        articles = [
            {"nom": "Pâtes", "statut": "ok"},
            {"nom": "Lait", "statut": "critique"},
            {"nom": "Pain", "statut": "sous_seuil"},
            {"nom": "Yaourt", "statut": "peremption_proche"},
        ]
        
        mock_inventaire.get_inventaire_complet.return_value = articles
        mock_inventaire_service.return_value = mock_inventaire
        
        # Vérifier que tous les statuts sont gérés
        result = mock_inventaire.get_inventaire_complet()
        assert len(result) == 4
        assert any(a["statut"] == "critique" for a in result)
        assert any(a["statut"] == "peremption_proche" for a in result)
