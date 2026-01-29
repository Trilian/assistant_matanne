"""Tests pour les composants du module planning avec les vraies fonctions."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import streamlit as st


class TestPlanningBadges:
    """Tests pour les badges de planning."""
    
    @patch('streamlit.markdown')
    def test_afficher_badge_charge_faible(self, mock_markdown):
        """Badge charge faible."""
        from src.domains.planning.logic.components import afficher_badge_charge
        
        afficher_badge_charge(charge_score=25, taille="normal")
        mock_markdown.assert_called_once()
        args = str(mock_markdown.call_args[0][0])
        assert "badge" in args.lower() or "25" in args
    
    @patch('streamlit.markdown')
    def test_afficher_badge_charge_elevee(self, mock_markdown):
        """Badge charge élevée."""
        from src.domains.planning.logic.components import afficher_badge_charge
        
        afficher_badge_charge(charge_score=85, taille="normal")
        mock_markdown.assert_called_once()
    
    @patch('streamlit.markdown')
    def test_afficher_badge_priorite_haute(self, mock_markdown):
        """Badge priorité haute."""
        from src.domains.planning.logic.components import afficher_badge_priorite
        
        afficher_badge_priorite(priorite="haute")
        mock_markdown.assert_called_once()
        args = str(mock_markdown.call_args[0][0])
        assert "haute" in args.lower() or "priorité" in args.lower()
    
    @patch('streamlit.markdown')
    def test_afficher_badge_priorite_basse(self, mock_markdown):
        """Badge priorité basse."""
        from src.domains.planning.logic.components import afficher_badge_priorite
        
        afficher_badge_priorite(priorite="basse")
        mock_markdown.assert_called_once()
    
    @patch('streamlit.markdown')
    def test_afficher_badge_activite_jules_adapte(self, mock_markdown):
        """Badge activité adaptée à Jules."""
        from src.domains.planning.logic.components import afficher_badge_activite_jules
        
        afficher_badge_activite_jules(adapte=True)
        mock_markdown.assert_called_once()
        args = str(mock_markdown.call_args[0][0])
        assert "adapté" in args.lower() or "âœ“" in args or "âœ…" in args
    
    @patch('streamlit.markdown')
    def test_afficher_badge_activite_jules_non_adapte(self, mock_markdown):
        """Badge activité non adaptée à Jules."""
        from src.domains.planning.logic.components import afficher_badge_activite_jules
        
        afficher_badge_activite_jules(adapte=False)
        mock_markdown.assert_called_once()


class TestPlanningSelecteurs:
    """Tests pour les sélecteurs de planning."""
    
    @patch('streamlit.columns')
    @patch('streamlit.date_input')
    def test_selecteur_semaine(self, mock_date, mock_columns):
        """Teste sélecteur de semaine."""
        from src.domains.planning.logic.components import selecteur_semaine
        
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_date.return_value = date.today()
        
        debut, fin = selecteur_semaine(key_prefix="test")
        assert isinstance(debut, date)
        assert isinstance(fin, date)
        assert fin >= debut
    
    @patch('streamlit.columns')
    @patch('streamlit.date_input')
    @patch('streamlit.button')
    def test_selecteur_semaine_buttons(self, mock_button, mock_date, mock_columns):
        """Teste les boutons du sélecteur."""
        from src.domains.planning.logic.components import selecteur_semaine
        
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_date.return_value = date.today()
        mock_button.return_value = False
        
        debut, fin = selecteur_semaine(key_prefix="test2")
        assert isinstance(debut, date)
        assert isinstance(fin, date)


class TestPlanningCartes:
    """Tests pour les cartes d'affichage."""
    
    @patch('streamlit.container')
    @patch('streamlit.markdown')
    def test_carte_repas(self, mock_markdown, mock_container):
        """Teste affichage carte repas."""
        from src.domains.planning.logic.components import carte_repas
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        repas = {
            "nom": "PÃ¢tes Carbonara",
            "type": "diner",
            "date": date.today(),
            "calories": 650
        }
        
        carte_repas(repas)
        assert mock_markdown.called or mock_container.called
    
    @patch('streamlit.container')
    @patch('streamlit.markdown')
    def test_carte_activite(self, mock_markdown, mock_container):
        """Teste affichage carte activité."""
        from src.domains.planning.logic.components import carte_activite
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        activite = {
            "nom": "Parc",
            "date": date.today(),
            "duree": 120,
            "participants": "Famille"
        }
        
        carte_activite(activite)
        assert mock_markdown.called or mock_container.called
    
    @patch('streamlit.container')
    @patch('streamlit.markdown')
    def test_carte_projet(self, mock_markdown, mock_container):
        """Teste affichage carte projet."""
        from src.domains.planning.logic.components import carte_projet
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        projet = {
            "titre": "Rénovation cuisine",
            "statut": "en_cours",
            "priorite": "haute",
            "progression": 45
        }
        
        carte_projet(projet)
        assert mock_markdown.called or mock_container.called
    
    @patch('streamlit.container')
    @patch('streamlit.markdown')
    def test_carte_event(self, mock_markdown, mock_container):
        """Teste affichage carte événement."""
        from src.domains.planning.logic.components import carte_event
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        event = {
            "titre": "Réunion parents",
            "date": date.today(),
            "heure": "14:00",
            "lieu": "Ã‰cole"
        }
        
        carte_event(event)
        assert mock_markdown.called or mock_container.called


class TestPlanningAlertes:
    """Tests pour les alertes de planning."""
    
    @patch('streamlit.warning')
    def test_afficher_alerte_warning(self, mock_warning):
        """Teste affichage alerte warning."""
        from src.domains.planning.logic.components import afficher_alerte
        
        afficher_alerte("Test alert", type_alerte="warning")
        mock_warning.assert_called_once()
    
    @patch('streamlit.error')
    def test_afficher_alerte_error(self, mock_error):
        """Teste affichage alerte error."""
        from src.domains.planning.logic.components import afficher_alerte
        
        afficher_alerte("Error test", type_alerte="error")
        mock_error.assert_called_once()
    
    @patch('streamlit.info')
    def test_afficher_alerte_info(self, mock_info):
        """Teste affichage alerte info."""
        from src.domains.planning.logic.components import afficher_alerte
        
        afficher_alerte("Info test", type_alerte="info")
        mock_info.assert_called_once()
    
    @patch('streamlit.warning')
    def test_afficher_liste_alertes(self, mock_warning):
        """Teste affichage liste d'alertes."""
        from src.domains.planning.logic.components import afficher_liste_alertes
        
        alertes = ["Alerte 1", "Alerte 2", "Alerte 3"]
        afficher_liste_alertes(alertes)
        # Au moins une alerte affichée
        assert mock_warning.call_count >= 1


class TestPlanningStats:
    """Tests pour les statistiques de planning."""
    
    @patch('streamlit.metric')
    @patch('streamlit.columns')
    def test_afficher_stats_semaine(self, mock_columns, mock_metric):
        """Teste affichage stats hebdomadaires."""
        from src.domains.planning.logic.components import afficher_stats_semaine
        
        mock_columns.return_value = [MagicMock() for _ in range(4)]
        
        stats = {
            "repas_planifies": 14,
            "activites": 5,
            "projets_actifs": 3,
            "taux_completion": 75
        }
        
        afficher_stats_semaine(stats)
        # Vérifie que des métriques ont été affichées
        assert mock_metric.call_count >= 1 or mock_columns.called

