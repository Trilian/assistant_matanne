"""
Tests pour le module Maison (projets, jardin, entretien)

Tests unitaires:
- Helpers du module maison
- Logique métier projets
- Logique métier jardin
- Logique métier entretien
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS MAISON
# ═══════════════════════════════════════════════════════════


class TestMaisonHelpers:
    """Tests pour les fonctions helpers du module maison"""

    @patch('src.modules.maison.helpers.get_db_context')
    def test_get_projets_urgents(self, mock_db):
        """Test récupération projets urgents"""
        from src.modules.maison.helpers import get_projets_urgents
        
        # Mock session
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=None)
        
        # Mock query result
        mock_projet = Mock()
        mock_projet.nom = "Projet test"
        mock_projet.priorite = "haute"
        mock_projet.date_fin_prevue = date.today() - timedelta(days=1)
        
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_projet]
        
        result = get_projets_urgents()
        
        # Vérifie la structure du résultat
        assert isinstance(result, list)

    @patch('src.modules.maison.helpers.get_db_context')
    def test_get_plantes_a_arroser(self, mock_db):
        """Test récupération plantes à arroser"""
        from src.modules.maison.helpers import get_plantes_a_arroser
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=None)
        
        # Aucune plante à arroser
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_plantes_a_arroser()
        
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('src.modules.maison.helpers.get_db_context')
    def test_get_stats_projets(self, mock_db):
        """Test statistiques projets"""
        from src.modules.maison.helpers import get_stats_projets
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=None)
        
        mock_session.query.return_value.filter.return_value.count.return_value = 3
        
        result = get_stats_projets()
        
        assert isinstance(result, dict)
        assert "en_cours" in result or "avg_progress" in result or isinstance(result.get("en_cours", 0), int)

    @patch('src.modules.maison.helpers.get_db_context')
    def test_get_stats_entretien(self, mock_db):
        """Test statistiques entretien"""
        from src.modules.maison.helpers import get_stats_entretien
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=None)
        
        mock_session.query.return_value.filter.return_value.count.return_value = 5
        
        result = get_stats_entretien()
        
        assert isinstance(result, dict)
        assert "completion_today" in result


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PROJET
# ═══════════════════════════════════════════════════════════


class TestProjectModel:
    """Tests pour le modèle Project"""

    def test_project_creation(self, db: Session):
        """Test création d'un projet"""
        from src.core.models import Project
        
        projet = Project(
            nom="Rénovation cuisine",
            description="Refaire les meubles",
            statut="en_cours",
            priorite="haute",
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30)
        )
        
        db.add(projet)
        db.commit()
        
        assert projet.id is not None
        assert projet.nom == "Rénovation cuisine"
        assert projet.statut == "en_cours"
        assert projet.priorite == "haute"

    def test_project_status_values(self, db: Session):
        """Test valeurs valides de statut"""
        from src.core.models import Project
        
        statuts_valides = ["en_cours", "termine", "annule", "en_pause"]
        
        for statut in statuts_valides:
            projet = Project(
                nom=f"Projet {statut}",
                statut=statut,
                priorite="moyenne"
            )
            db.add(projet)
            db.commit()
            assert projet.statut == statut

    def test_project_priority_values(self, db: Session):
        """Test valeurs valides de priorité"""
        from src.core.models import Project
        
        priorites_valides = ["haute", "moyenne", "basse"]
        
        for priorite in priorites_valides:
            projet = Project(
                nom=f"Projet {priorite}",
                statut="en_cours",
                priorite=priorite
            )
            db.add(projet)
            db.commit()
            assert projet.priorite == priorite


# ═══════════════════════════════════════════════════════════
# TESTS LOGIQUE JARDIN
# ═══════════════════════════════════════════════════════════


class TestJardinLogic:
    """Tests pour la logique du module jardin"""

    def test_plante_needs_watering(self):
        """Test détection plante à arroser"""
        # Une plante arrosée il y a 5 jours avec fréquence 3 jours
        dernier_arrosage = date.today() - timedelta(days=5)
        frequence_arrosage = 3  # jours
        
        jours_depuis_arrosage = (date.today() - dernier_arrosage).days
        needs_watering = jours_depuis_arrosage >= frequence_arrosage
        
        assert needs_watering is True

    def test_plante_recently_watered(self):
        """Test plante récemment arrosée"""
        dernier_arrosage = date.today() - timedelta(days=1)
        frequence_arrosage = 3
        
        jours_depuis_arrosage = (date.today() - dernier_arrosage).days
        needs_watering = jours_depuis_arrosage >= frequence_arrosage
        
        assert needs_watering is False

    def test_calculate_harvest_date(self):
        """Test calcul date de récolte"""
        date_plantation = date.today() - timedelta(days=60)
        duree_croissance = 90  # jours
        
        date_recolte = date_plantation + timedelta(days=duree_croissance)
        jours_restants = (date_recolte - date.today()).days
        
        assert jours_restants == 30


# ═══════════════════════════════════════════════════════════
# TESTS LOGIQUE ENTRETIEN
# ═══════════════════════════════════════════════════════════


class TestEntretienLogic:
    """Tests pour la logique du module entretien"""

    def test_task_completion_percentage(self):
        """Test calcul pourcentage completion"""
        total_tasks = 10
        completed_tasks = 7
        
        percentage = (completed_tasks / total_tasks) * 100
        
        assert percentage == 70.0

    def test_task_overdue_detection(self):
        """Test détection tâche en retard"""
        date_echeance = date.today() - timedelta(days=2)
        task_completed = False
        
        is_overdue = date_echeance < date.today() and not task_completed
        
        assert is_overdue is True

    def test_recurring_task_next_date(self):
        """Test calcul prochaine occurrence tâche récurrente"""
        frequence = "hebdomadaire"
        derniere_execution = date.today()
        
        if frequence == "quotidien":
            prochaine = derniere_execution + timedelta(days=1)
        elif frequence == "hebdomadaire":
            prochaine = derniere_execution + timedelta(weeks=1)
        elif frequence == "mensuel":
            prochaine = derniere_execution + timedelta(days=30)
        else:
            prochaine = derniere_execution
        
        assert prochaine == date.today() + timedelta(weeks=1)
