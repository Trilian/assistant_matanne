"""Tests pour le module planning/components."""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


class TestPlanningCalendarComponent:
    """Tests pour le composant calendrier."""
    
    @patch('streamlit.columns')
    def test_afficher_calendrier_mois(self, mock_columns):
        """Affiche le calendrier du mois."""
        from src.modules.planning.components import afficher_calendrier_mois
        
        mock_columns.return_value = [MagicMock() for _ in range(7)]
        
        result = afficher_calendrier_mois(annee=2026, mois=1)
        assert result is not None
    
    @patch('streamlit.button')
    def test_navigation_mois_precedent(self, mock_button):
        """Navigation vers le mois précédent."""
        from src.modules.planning.components import bouton_mois_precedent
        
        mock_button.return_value = True
        with patch('streamlit.session_state', {}):
            result = bouton_mois_precedent()
            assert mock_button.called
    
    @patch('streamlit.button')
    def test_navigation_mois_suivant(self, mock_button):
        """Navigation vers le mois suivant."""
        from src.modules.planning.components import bouton_mois_suivant
        
        mock_button.return_value = True
        result = bouton_mois_suivant()
        assert mock_button.called


class TestPlanningWeekView:
    """Tests pour la vue semaine."""
    
    @patch('streamlit.columns')
    def test_afficher_semaine(self, mock_columns):
        """Affiche la vue semaine."""
        from src.modules.planning.components import afficher_vue_semaine
        
        mock_columns.return_value = [MagicMock() for _ in range(7)]
        
        debut_semaine = date(2026, 1, 26)
        result = afficher_vue_semaine(debut_semaine)
        assert result is not None
    
    def test_calculer_debut_semaine(self):
        """Calcule le début de la semaine."""
        from src.modules.planning.components import calculer_debut_semaine
        
        une_date = date(2026, 1, 28)  # Mercredi
        debut = calculer_debut_semaine(une_date)
        
        assert debut.weekday() == 0  # Lundi
        assert debut <= une_date
    
    def test_obtenir_jours_semaine(self):
        """Obtient les 7 jours de la semaine."""
        from src.modules.planning.components import obtenir_jours_semaine
        
        debut = date(2026, 1, 26)
        jours = obtenir_jours_semaine(debut)
        
        assert len(jours) == 7
        assert jours[0] == debut
        assert jours[-1] == debut + timedelta(days=6)


class TestPlanningDayView:
    """Tests pour la vue journalière."""
    
    @patch('streamlit.container')
    def test_afficher_vue_jour(self, mock_container):
        """Affiche la vue d'un jour."""
        from src.modules.planning.components import afficher_vue_jour
        
        mock_container.return_value.__enter__ = Mock()
        mock_container.return_value.__exit__ = Mock()
        
        jour = date(2026, 1, 28)
        result = afficher_vue_jour(jour)
        assert result is not None
    
    @patch('streamlit.time_input')
    def test_selecteur_heure(self, mock_time):
        """Sélectionne une heure."""
        from src.modules.planning.components import selecteur_heure
        
        from datetime import time
        mock_time.return_value = time(14, 30)
        
        result = selecteur_heure("Heure du repas")
        assert result is not None


class TestPlanningEventCard:
    """Tests pour les cartes d'événements."""
    
    @patch('streamlit.container')
    def test_afficher_carte_repas(self, mock_container):
        """Affiche une carte repas."""
        from src.modules.planning.components import afficher_carte_repas
        
        mock_container.return_value.__enter__ = Mock()
        mock_container.return_value.__exit__ = Mock()
        
        repas = {
            "nom": "Poulet rôti",
            "type": "diner",
            "heure": "19:00"
        }
        
        afficher_carte_repas(repas)
        assert mock_container.called
    
    @patch('streamlit.container')
    def test_afficher_carte_activite(self, mock_container):
        """Affiche une carte activité."""
        from src.modules.planning.components import afficher_carte_activite
        
        mock_container.return_value.__enter__ = Mock()
        mock_container.return_value.__exit__ = Mock()
        
        activite = {
            "nom": "Parc",
            "heure_debut": "15:00",
            "heure_fin": "17:00"
        }
        
        afficher_carte_activite(activite)
        assert mock_container.called


class TestPlanningFilters:
    """Tests pour les filtres de planning."""
    
    @patch('streamlit.multiselect')
    def test_filtre_types_evenements(self, mock_select):
        """Filtre par types d'événements."""
        from src.modules.planning.components import filtre_types_evenements
        
        mock_select.return_value = ["repas", "activite"]
        
        result = filtre_types_evenements()
        assert isinstance(result, list)
    
    @patch('streamlit.selectbox')
    def test_filtre_periode(self, mock_select):
        """Filtre par période."""
        from src.modules.planning.components import filtre_periode
        
        mock_select.return_value = "Cette semaine"
        
        result = filtre_periode()
        assert result in ["Aujourd'hui", "Cette semaine", "Ce mois"]


class TestPlanningTimeSlots:
    """Tests pour les créneaux horaires."""
    
    def test_generer_creneaux_journee(self):
        """Génère les créneaux d'une journée."""
        from src.modules.planning.components import generer_creneaux_journee
        
        creneaux = generer_creneaux_journee(debut=8, fin=22, intervalle=1)
        
        assert len(creneaux) == 14  # 8h à 22h = 14 heures
        assert creneaux[0] == "08:00"
        assert creneaux[-1] == "22:00"
    
    def test_trouver_creneau_disponible(self):
        """Trouve un créneau disponible."""
        from src.modules.planning.components import trouver_creneau_disponible
        
        creneaux_occupes = ["09:00", "10:00", "14:00"]
        tous_creneaux = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00"]
        
        disponible = trouver_creneau_disponible(tous_creneaux, creneaux_occupes)
        
        assert disponible not in creneaux_occupes
        assert disponible in ["08:00", "11:00", "15:00"]


class TestPlanningModal:
    """Tests pour les modales de planning."""
    
    @patch('streamlit.form')
    def test_modale_ajouter_repas(self, mock_form):
        """Ouvre la modale d'ajout de repas."""
        from src.modules.planning.components import modale_ajouter_repas
        
        mock_form.return_value.__enter__ = Mock()
        mock_form.return_value.__exit__ = Mock()
        
        with patch('streamlit.form_submit_button', return_value=False):
            result = modale_ajouter_repas()
            assert mock_form.called
    
    @patch('streamlit.form')
    def test_modale_modifier_evenement(self, mock_form):
        """Ouvre la modale de modification."""
        from src.modules.planning.components import modale_modifier_evenement
        
        mock_form.return_value.__enter__ = Mock()
        mock_form.return_value.__exit__ = Mock()
        
        evenement = {"id": 1, "nom": "Test"}
        
        with patch('streamlit.form_submit_button', return_value=False):
            result = modale_modifier_evenement(evenement)
            assert mock_form.called


class TestPlanningNavigation:
    """Tests pour la navigation."""
    
    @patch('streamlit.date_input')
    def test_selecteur_date(self, mock_date):
        """Sélectionne une date."""
        from src.modules.planning.components import selecteur_date
        
        mock_date.return_value = date(2026, 1, 28)
        
        result = selecteur_date("Sélectionner une date")
        assert result == date(2026, 1, 28)
    
    @patch('streamlit.button')
    def test_bouton_aujourdhui(self, mock_button):
        """Bouton retour à aujourd'hui."""
        from src.modules.planning.components import bouton_aujourdhui
        
        mock_button.return_value = True
        
        result = bouton_aujourdhui()
        assert mock_button.called


class TestPlanningDragDrop:
    """Tests pour le drag and drop."""
    
    def test_detecter_debut_drag(self):
        """Détecte le début du drag."""
        from src.modules.planning.components import detecter_debut_drag
        
        with patch('streamlit.session_state', {}):
            detecter_debut_drag(element_id=123)
            assert st.session_state.get("dragging") == 123
    
    def test_detecter_drop(self):
        """Détecte le drop."""
        from src.modules.planning.components import detecter_drop
        
        with patch('streamlit.session_state', {"dragging": 123}):
            result = detecter_drop(cible_id=456)
            assert result == {"source": 123, "cible": 456}


class TestPlanningColors:
    """Tests pour les couleurs par type."""
    
    def test_obtenir_couleur_type_repas(self):
        """Obtient la couleur pour un type de repas."""
        from src.modules.planning.components import obtenir_couleur_type
        
        couleur_petit_dej = obtenir_couleur_type("petit_dejeuner")
        couleur_diner = obtenir_couleur_type("diner")
        
        assert couleur_petit_dej != couleur_diner
        assert "#" in couleur_petit_dej or "rgb" in couleur_petit_dej
    
    def test_obtenir_couleur_activite(self):
        """Obtient la couleur pour une activité."""
        from src.modules.planning.components import obtenir_couleur_type
        
        couleur = obtenir_couleur_type("activite")
        assert couleur is not None


class TestPlanningStats:
    """Tests pour les statistiques."""
    
    def test_compter_evenements_semaine(self):
        """Compte les événements de la semaine."""
        from src.modules.planning.components import compter_evenements_semaine
        
        evenements = [
            {"date": date(2026, 1, 27)},
            {"date": date(2026, 1, 28)},
            {"date": date(2026, 1, 29)},
        ]
        
        debut_semaine = date(2026, 1, 26)
        count = compter_evenements_semaine(evenements, debut_semaine)
        
        assert count == 3
    
    @patch('streamlit.metric')
    def test_afficher_stats_planning(self, mock_metric):
        """Affiche les stats du planning."""
        from src.modules.planning.components import afficher_stats_planning
        
        stats = {
            "total_repas": 21,
            "total_activites": 7,
            "jours_planifies": 7
        }
        
        afficher_stats_planning(stats)
        assert mock_metric.call_count >= 3


class TestPlanningExport:
    """Tests pour l'export."""
    
    def test_exporter_planning_csv(self):
        """Exporte le planning en CSV."""
        from src.modules.planning.components import exporter_planning_csv
        
        evenements = [
            {"date": "2026-01-28", "type": "repas", "nom": "Poulet"},
            {"date": "2026-01-29", "type": "activite", "nom": "Parc"}
        ]
        
        csv_content = exporter_planning_csv(evenements)
        assert "date" in csv_content.lower()
        assert "Poulet" in csv_content
    
    @patch('streamlit.download_button')
    def test_bouton_export(self, mock_button):
        """Affiche le bouton d'export."""
        from src.modules.planning.components import bouton_export_planning
        
        mock_button.return_value = False
        
        evenements = [{"date": "2026-01-28", "nom": "Test"}]
        bouton_export_planning(evenements)
        
        assert mock_button.called


class TestPlanningValidation:
    """Tests pour la validation."""
    
    def test_valider_heure_format(self):
        """Valide le format d'heure."""
        from src.modules.planning.components import valider_format_heure
        
        assert valider_format_heure("14:30") is True
        assert valider_format_heure("25:00") is False
        assert valider_format_heure("14h30") is False
    
    def test_valider_conflit_horaire(self):
        """Vérifie les conflits d'horaires."""
        from src.modules.planning.components import verifier_conflit_horaire
        
        nouvel_event = {
            "date": date(2026, 1, 28),
            "heure_debut": "14:00",
            "heure_fin": "16:00"
        }
        
        events_existants = [
            {"date": date(2026, 1, 28), "heure_debut": "15:00", "heure_fin": "17:00"}
        ]
        
        conflit = verifier_conflit_horaire(nouvel_event, events_existants)
        assert conflit is True


@pytest.fixture
def mock_planning_data():
    """Données de planning simulées."""
    return {
        "repas": [
            {"id": 1, "date": date(2026, 1, 28), "type": "diner", "nom": "Poulet"},
            {"id": 2, "date": date(2026, 1, 29), "type": "dejeuner", "nom": "Pâtes"}
        ],
        "activites": [
            {"id": 3, "date": date(2026, 1, 28), "nom": "Parc", "heure": "15:00"}
        ]
    }


@pytest.fixture
def mock_streamlit_widgets():
    """Mock des widgets Streamlit."""
    with patch('streamlit.columns'), \
         patch('streamlit.container'), \
         patch('streamlit.button'), \
         patch('streamlit.selectbox'):
        yield
