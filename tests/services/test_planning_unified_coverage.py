"""
Tests complets pour src/services/planning_unified.py
Objectif: couverture >80%
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS MODELES PYDANTIC
# ═══════════════════════════════════════════════════════════

class TestJourCompletSchema:
    """Tests pour JourCompletSchema model."""
    
    def test_jour_complet_schema_minimal(self):
        """Test minimal JourCompletSchema creation."""
        from src.services.planning_unified import JourCompletSchema
        
        jour = JourCompletSchema(
            date=date(2026, 2, 7),
            charge="normal",
            charge_score=50
        )
        
        assert jour.date == date(2026, 2, 7)
        assert jour.charge == "normal"
        assert jour.charge_score == 50
        assert jour.repas == []
        assert jour.activites == []
        assert jour.projets == []
        assert jour.routines == []
        assert jour.events == []
        assert jour.budget_jour == 0.0
        assert jour.alertes == []
        assert jour.suggestions_ia == []
    
    def test_jour_complet_schema_full(self):
        """Test full JourCompletSchema with all fields."""
        from src.services.planning_unified import JourCompletSchema
        
        jour = JourCompletSchema(
            date=date(2026, 2, 7),
            charge="intense",
            charge_score=85,
            repas=[{"id": 1, "type": "déjeuner", "recette": "Poulet"}],
            activites=[{"id": 1, "titre": "Sortie parc"}],
            projets=[{"id": 1, "nom": "Rangement"}],
            routines=[{"id": 1, "nom": "Bain Jules"}],
            events=[{"id": 1, "titre": "RDV médecin"}],
            budget_jour=45.50,
            alertes=["⚠️ Jour très chargé"],
            suggestions_ia=["Simplifier les repas"]
        )
        
        assert jour.charge_score == 85
        assert len(jour.repas) == 1
        assert len(jour.activites) == 1
        assert jour.budget_jour == 45.50
        assert len(jour.alertes) == 1
    
    def test_jour_complet_schema_charge_faible(self):
        """Test with faible charge."""
        from src.services.planning_unified import JourCompletSchema
        
        jour = JourCompletSchema(
            date=date(2026, 2, 8),
            charge="faible",
            charge_score=20
        )
        
        assert jour.charge == "faible"
        assert jour.charge_score == 20


class TestSemaineCompleSchema:
    """Tests pour SemaineCompleSchema model."""
    
    def test_semaine_complete_schema_minimal(self):
        """Test minimal SemaineCompleSchema creation."""
        from src.services.planning_unified import SemaineCompleSchema, JourCompletSchema
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=40
            )
        
        semaine = SemaineCompleSchema(
            semaine_debut=date(2026, 2, 2),
            semaine_fin=date(2026, 2, 8),
            jours=jours,
            charge_globale="normal"
        )
        
        assert semaine.semaine_debut == date(2026, 2, 2)
        assert semaine.semaine_fin == date(2026, 2, 8)
        assert len(semaine.jours) == 7
        assert semaine.charge_globale == "normal"
        assert semaine.stats_semaine == {}
        assert semaine.alertes_semaine == []
    
    def test_semaine_complete_schema_with_stats(self):
        """Test with stats and alerts."""
        from src.services.planning_unified import SemaineCompleSchema, JourCompletSchema
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="intense" if i % 2 == 0 else "faible",
                charge_score=80 if i % 2 == 0 else 20
            )
        
        semaine = SemaineCompleSchema(
            semaine_debut=date(2026, 2, 2),
            semaine_fin=date(2026, 2, 8),
            jours=jours,
            stats_semaine={"total_repas": 14, "total_activites": 5},
            charge_globale="normal",
            alertes_semaine=["👶 Peu d'activités pour Jules"]
        )
        
        assert semaine.stats_semaine["total_repas"] == 14
        assert len(semaine.alertes_semaine) == 1


class TestSemaineGenereeIASchema:
    """Tests pour SemaineGenereeIASchema model."""
    
    def test_semaine_generee_ia_schema_minimal(self):
        """Test minimal SemaineGenereeIASchema creation."""
        from src.services.planning_unified import SemaineGenereeIASchema
        
        semaine = SemaineGenereeIASchema()
        
        assert semaine.repas_proposes == []
        assert semaine.activites_proposees == []
        assert semaine.projets_suggeres == []
        assert semaine.harmonie_description == ""
        assert semaine.raisons == []
    
    def test_semaine_generee_ia_schema_full(self):
        """Test full SemaineGenereeIASchema."""
        from src.services.planning_unified import SemaineGenereeIASchema
        
        semaine = SemaineGenereeIASchema(
            repas_proposes=[
                {"jour": "Lundi", "dejeuner": "Pâtes", "diner": "Soupe"}
            ],
            activites_proposees=[
                {"jour": "Mardi", "activite": "Parc", "pour_jules": True}
            ],
            projets_suggeres=[
                {"projet": "Rangement cuisine", "priorite": "haute"}
            ],
            harmonie_description="Semaine équilibrée avec activités variées",
            raisons=["Météo favorable", "Budget respecté"]
        )
        
        assert len(semaine.repas_proposes) == 1
        assert len(semaine.activites_proposees) == 1
        assert len(semaine.projets_suggeres) == 1
        assert "équilibrée" in semaine.harmonie_description
        assert len(semaine.raisons) == 2


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING AI SERVICE INIT
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceInit:
    """Tests for PlanningAIService initialization."""
    
    def test_service_init(self):
        """Test service initialization."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        assert service.model_name == "CalendarEvent"
        assert service.cache_ttl == 1800
    
    def test_get_planning_unified_service_factory(self):
        """Test get_planning_unified_service factory function."""
        from src.services.planning_unified import get_planning_unified_service
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = get_planning_unified_service()
        
        assert service is not None
    
    def test_get_unified_planning_service_alias(self):
        """Test get_unified_planning_service alias."""
        from src.services.planning_unified import get_unified_planning_service
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = get_unified_planning_service()
        
        assert service is not None


# ═══════════════════════════════════════════════════════════
# TESTS HELPER METHODS
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceCalculerCharge:
    """Tests for _calculer_charge method."""
    
    def test_calculer_charge_empty(self):
        """Test charge calculation with empty data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        score = service._calculer_charge(
            repas=[],
            activites=[],
            projets=[],
            routines=[]
        )
        
        assert score == 0
    
    def test_calculer_charge_with_repas(self):
        """Test charge calculation with meals."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        repas = [
            {"id": 1, "temps_total": 60},
            {"id": 2, "temps_total": 45}
        ]
        
        score = service._calculer_charge(
            repas=repas,
            activites=[],
            projets=[],
            routines=[]
        )
        
        assert score > 0
    
    def test_calculer_charge_with_activites(self):
        """Test charge calculation with activities."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        activites = [
            {"id": 1, "titre": "Activite 1"},
            {"id": 2, "titre": "Activite 2"}
        ]
        
        score = service._calculer_charge(
            repas=[],
            activites=activites,
            projets=[],
            routines=[]
        )
        
        assert score == 20  # 2 activites * 10 = 20
    
    def test_calculer_charge_with_projets_urgents(self):
        """Test charge calculation with urgent projects."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        projets = [
            {"id": 1, "priorite": "haute"},
            {"id": 2, "priorite": "haute"},
            {"id": 3, "priorite": "normale"}
        ]
        
        score = service._calculer_charge(
            repas=[],
            activites=[],
            projets=projets,
            routines=[]
        )
        
        assert score >= 25  # 2 urgent projects * 15 = 30, capped at 25
    
    def test_calculer_charge_with_routines(self):
        """Test charge calculation with routines."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        routines = [{"id": i} for i in range(6)]
        
        score = service._calculer_charge(
            repas=[],
            activites=[],
            projets=[],
            routines=routines
        )
        
        assert score == 25  # 6 * 5 = 30, capped at 25
    
    def test_calculer_charge_max_100(self):
        """Test charge calculation with high load."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        # Create overloaded day
        # repas: temps_total=120 -> 120//30 = 4 (max 30, but only 4 pts)
        repas = [{"temps_total": 120}]  # 4 pts
        activites = [{"id": i} for i in range(5)]  # 5*10 = 50, capped at 20 pts
        projets = [{"priorite": "haute"} for i in range(5)]  # 5*15 = 75, capped at 25 pts
        routines = [{"id": i} for i in range(10)]  # 10*5 = 50, capped at 25 pts
        
        score = service._calculer_charge(
            repas=repas,
            activites=activites,
            projets=projets,
            routines=routines
        )
        
        # Total: 4 + 20 + 25 + 25 = 74
        assert score == 74


class TestPlanningAIServiceScoreToCharge:
    """Tests for _score_to_charge method."""
    
    def test_score_to_charge_faible(self):
        """Test faible charge label."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        assert service._score_to_charge(0) == "faible"
        assert service._score_to_charge(20) == "faible"
        assert service._score_to_charge(34) == "faible"
    
    def test_score_to_charge_normal(self):
        """Test normal charge label."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        assert service._score_to_charge(35) == "normal"
        assert service._score_to_charge(50) == "normal"
        assert service._score_to_charge(69) == "normal"
    
    def test_score_to_charge_intense(self):
        """Test intense charge label."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        assert service._score_to_charge(70) == "intense"
        assert service._score_to_charge(85) == "intense"
        assert service._score_to_charge(100) == "intense"


class TestPlanningAIServiceDetecterAlertes:
    """Tests for _detecter_alertes method."""
    
    def test_detecter_alertes_surcharge(self):
        """Test surcharge alert detection."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        alertes = service._detecter_alertes(
            jour=date(2026, 2, 7),
            repas=[],
            activites=[],
            projets=[],
            charge_score=85
        )
        
        assert any("chargé" in a for a in alertes)
    
    def test_detecter_alertes_pas_activite_jules(self):
        """Test no Jules activity alert."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        activites = [
            {"id": 1, "titre": "Sortie adultes", "pour_jules": False}
        ]
        
        alertes = service._detecter_alertes(
            jour=date(2026, 2, 7),
            repas=[],
            activites=activites,
            projets=[],
            charge_score=50
        )
        
        assert any("Jules" in a for a in alertes)
    
    def test_detecter_alertes_projets_urgents(self):
        """Test urgent projects alert."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        projets = [
            {"id": 1, "priorite": "haute"},
            {"id": 2, "priorite": "haute"}
        ]
        
        alertes = service._detecter_alertes(
            jour=date(2026, 2, 7),
            repas=[],
            activites=[],
            projets=projets,
            charge_score=50
        )
        
        assert any("urgent" in a for a in alertes)
    
    def test_detecter_alertes_trop_repas(self):
        """Test too many meals alert."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        repas = [{"id": i} for i in range(5)]
        
        alertes = service._detecter_alertes(
            jour=date(2026, 2, 7),
            repas=repas,
            activites=[],
            projets=[],
            charge_score=50
        )
        
        assert any("repas" in a for a in alertes)


class TestPlanningAIServiceDetecterAlertesSemaine:
    """Tests for _detecter_alertes_semaine method."""
    
    def test_detecter_alertes_semaine_no_jules(self):
        """Test no Jules activities for week alert."""
        from src.services.planning_unified import PlanningAIService, JourCompletSchema
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=40,
                activites=[]  # No Jules activities
            )
        
        alertes = service._detecter_alertes_semaine(jours)
        
        assert any("Jules" in a for a in alertes)
    
    def test_detecter_alertes_semaine_burnout(self):
        """Test burnout risk alert."""
        from src.services.planning_unified import PlanningAIService, JourCompletSchema
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="intense",
                charge_score=90,  # Very high
                activites=[]
            )
        
        alertes = service._detecter_alertes_semaine(jours)
        
        assert any("burnout" in a.lower() for a in alertes)
    
    def test_detecter_alertes_semaine_budget(self):
        """Test budget alert."""
        from src.services.planning_unified import PlanningAIService, JourCompletSchema
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=40,
                activites=[],
                budget_jour=100.0  # 700€ total > 500€
            )
        
        alertes = service._detecter_alertes_semaine(jours)
        
        assert any("budget" in a.lower() for a in alertes)


class TestPlanningAIServiceCalculerBudgetJour:
    """Tests for _calculer_budget_jour method."""
    
    def test_calculer_budget_jour_empty(self):
        """Test budget calculation with no activities."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        budget = service._calculer_budget_jour(activites=[], projets=[])
        
        assert budget == 0.0
    
    def test_calculer_budget_jour_with_budget(self):
        """Test budget calculation with activities."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        activites = [
            {"id": 1, "budget": 25.0},
            {"id": 2, "budget": 15.0}
        ]
        
        budget = service._calculer_budget_jour(activites=activites, projets=[])
        
        assert budget == 40.0
    
    def test_calculer_budget_jour_missing_budget(self):
        """Test budget calculation with missing budget field."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        activites = [
            {"id": 1},  # No budget field
            {"id": 2, "budget": 20.0}
        ]
        
        budget = service._calculer_budget_jour(activites=activites, projets=[])
        
        assert budget == 20.0


class TestPlanningAIServiceCalculerStatsSemaine:
    """Tests for _calculer_stats_semaine method."""
    
    def test_calculer_stats_semaine_empty(self):
        """Test stats calculation with empty week."""
        from src.services.planning_unified import PlanningAIService, JourCompletSchema
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="faible",
                charge_score=10
            )
        
        stats = service._calculer_stats_semaine(jours)
        
        assert stats["total_repas"] == 0
        assert stats["total_activites"] == 0
        assert stats["total_projets"] == 0
        assert stats["total_events"] == 0
        assert stats["budget_total"] == 0.0
    
    def test_calculer_stats_semaine_with_data(self):
        """Test stats calculation with data."""
        from src.services.planning_unified import PlanningAIService, JourCompletSchema
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        jours = {}
        for i in range(7):
            jour_date = date(2026, 2, 2) + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=50,
                repas=[{"id": 1}, {"id": 2}],
                activites=[{"id": 1, "pour_jules": True}],
                projets=[{"id": 1}],
                events=[{"id": 1}],
                budget_jour=50.0
            )
        
        stats = service._calculer_stats_semaine(jours)
        
        assert stats["total_repas"] == 14  # 2 per day * 7
        assert stats["total_activites"] == 7  # 1 per day * 7
        assert stats["activites_jules"] == 7  # All for Jules
        assert stats["total_projets"] == 7
        assert stats["total_events"] == 7
        assert stats["budget_total"] == 350.0  # 50 * 7
        assert stats["charge_moyenne"] == 50


# ═══════════════════════════════════════════════════════════
# TESTS LOADERS (Chargers)
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceChargerRepas:
    """Tests for _charger_repas method."""
    
    def test_charger_repas_empty(self):
        """Test loading meals when none exist."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_repas(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert result == {}
    
    def test_charger_repas_with_data(self):
        """Test loading meals with data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_meal = Mock()
        mock_meal.id = 1
        mock_meal.date_repas = date(2026, 2, 3)
        mock_meal.type_repas = "déjeuner"
        mock_meal.portion_ajustee = 4
        mock_meal.notes = "Note"
        
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.nom = "Poulet rôti"
        mock_recipe.portions = 4
        mock_recipe.temps_preparation = 15
        mock_recipe.temps_cuisson = 45
        
        mock_session = Mock()
        mock_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [
            (mock_meal, mock_recipe)
        ]
        
        result = service._charger_repas(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert "2026-02-03" in result
        assert len(result["2026-02-03"]) == 1


class TestPlanningAIServiceChargerActivites:
    """Tests for _charger_activites method."""
    
    def test_charger_activites_empty(self):
        """Test loading activities when none exist."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_activites(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert result == {}
    
    def test_charger_activites_with_data(self):
        """Test loading activities with data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_activity = Mock()
        mock_activity.id = 1
        mock_activity.date_prevue = date(2026, 2, 3)
        mock_activity.titre = "Sortie parc"
        mock_activity.type_activite = "sortie"
        mock_activity.lieu = "Parc"
        mock_activity.cout_estime = 10.0
        mock_activity.duree_heures = 2.0
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_activity]
        
        result = service._charger_activites(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert "2026-02-03" in result


class TestPlanningAIServiceChargerProjets:
    """Tests for _charger_projets method."""
    
    def test_charger_projets_empty(self):
        """Test loading projects when none exist."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_projets(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert result == {}
    
    def test_charger_projets_with_data(self):
        """Test loading projects with data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_project = Mock()
        mock_project.id = 1
        mock_project.nom = "Rangement"
        mock_project.priorite = "haute"
        mock_project.statut = "à_faire"
        mock_project.date_fin_prevue = date(2026, 2, 5)
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_project]
        
        result = service._charger_projets(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert "2026-02-05" in result
        assert result["2026-02-05"][0]["nom"] == "Rangement"
    
    def test_charger_projets_no_date_fin(self):
        """Test loading projects without date_fin."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_project = Mock()
        mock_project.id = 1
        mock_project.nom = "Sans date fin"
        mock_project.priorite = "normale"
        mock_project.statut = "en_cours"
        mock_project.date_fin_prevue = None  # No date_fin
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_project]
        
        result = service._charger_projets(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        # Should use date_fin as fallback (2026-02-08)
        assert "2026-02-08" in result


class TestPlanningAIServiceChargerRoutines:
    """Tests for _charger_routines method."""
    
    def test_charger_routines_empty(self):
        """Test loading routines when none exist."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_routines(mock_session)
        
        assert result == {}
    
    def test_charger_routines_with_data(self):
        """Test loading routines with data."""
        from src.services.planning_unified import PlanningAIService
        from datetime import time
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_task = Mock()
        mock_task.id = 1
        mock_task.nom = "Bain Jules"
        mock_task.heure_prevue = time(19, 0)
        mock_task.fait_le = None
        
        mock_routine = Mock()
        mock_routine.id = 1
        mock_routine.nom = "Routine soir"
        
        mock_session = Mock()
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_task, mock_routine)
        ]
        
        result = service._charger_routines(mock_session)
        
        assert "routine_quotidienne" in result
        assert len(result["routine_quotidienne"]) == 1
        assert result["routine_quotidienne"][0]["nom"] == "Bain Jules"


class TestPlanningAIServiceChargerEvents:
    """Tests for _charger_events method."""
    
    def test_charger_events_empty(self):
        """Test loading events when none exist."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_events(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert result == {}
    
    def test_charger_events_with_data(self):
        """Test loading events with data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_event = Mock()
        mock_event.id = 1
        mock_event.date_debut = datetime(2026, 2, 3, 10, 0)
        mock_event.date_fin = datetime(2026, 2, 3, 11, 0)
        mock_event.titre = "RDV médecin"
        mock_event.type_event = "rdv"
        mock_event.lieu = "Cabinet"
        mock_event.couleur = "#FF0000"
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_event]
        
        result = service._charger_events(date(2026, 2, 2), date(2026, 2, 8), mock_session)
        
        assert "2026-02-03" in result


# ═══════════════════════════════════════════════════════════
# TESTS CREER EVENT
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceCreerEvent:
    """Tests for creer_event method."""
    
    def test_creer_event_success(self):
        """Test creating event successfully."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        
        with patch.object(service, '_invalider_cache_semaine'):
            result = service.creer_event(
                titre="RDV médecin",
                date_debut=datetime(2026, 2, 7, 10, 0),
                type_event="rdv",
                db=mock_session
            )
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
    
    def test_creer_event_with_all_params(self):
        """Test creating event with all parameters."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        
        with patch.object(service, '_invalider_cache_semaine'):
            result = service.creer_event(
                titre="RDV important",
                date_debut=datetime(2026, 2, 7, 10, 0),
                date_fin=datetime(2026, 2, 7, 11, 0),
                type_event="rdv",
                lieu="Cabinet médical",
                description="Description",
                couleur="#FF0000",
                recurrence=None,
                db=mock_session
            )
        
        mock_session.add.assert_called()
    
    def test_creer_event_failure(self):
        """Test creating event with failure."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        mock_session.add.side_effect = Exception("DB Error")
        
        with patch.object(service, '_invalider_cache_semaine'):
            result = service.creer_event(
                titre="RDV médecin",
                date_debut=datetime(2026, 2, 7, 10, 0),
                type_event="rdv",
                db=mock_session
            )
        
        assert result is None
        mock_session.rollback.assert_called()


class TestPlanningAIServiceInvaliderCacheSemaine:
    """Tests for _invalider_cache_semaine method."""
    
    def test_invalider_cache_semaine(self):
        """Test cache invalidation for week."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        with patch('src.services.planning_unified.Cache') as mock_cache:
            service._invalider_cache_semaine(date(2026, 2, 5))
            
            # Should call invalider twice (complete and ia)
            assert mock_cache.invalider.call_count == 2


# ═══════════════════════════════════════════════════════════
# TESTS GENERER SEMAINE IA
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceGenererSemaineIA:
    """Tests for generer_semaine_ia method."""
    
    def test_generer_semaine_ia_success(self):
        """Test generating week with AI successfully."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_response = [{
            "repas_proposes": [{"jour": "Lundi", "dejeuner": "Pâtes"}],
            "activites_proposees": [{"jour": "Mardi", "activite": "Parc"}],
            "projets_suggeres": [],
            "harmonie_description": "Semaine équilibrée",
            "raisons": []
        }]
        
        with patch.object(service, 'call_with_list_parsing_sync', return_value=mock_response):
            result = service.generer_semaine_ia(
                date_debut=date(2026, 2, 2),
                contraintes={"budget": 300},
                contexte={"jules_age_mois": 19}
            )
        
        assert result is not None
        assert result.harmonie_description == "Semaine équilibrée"
    
    def test_generer_semaine_ia_failure(self):
        """Test generating week with AI failure."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        with patch.object(service, 'call_with_list_parsing_sync', return_value=None):
            result = service.generer_semaine_ia(
                date_debut=date(2026, 2, 2),
                contraintes={},
                contexte={}
            )
        
        assert result is None
    
    def test_generer_semaine_ia_empty_response(self):
        """Test generating week with empty AI response."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        with patch.object(service, 'call_with_list_parsing_sync', return_value=[]):
            result = service.generer_semaine_ia(
                date_debut=date(2026, 2, 2),
                contraintes={},
                contexte={}
            )
        
        # Empty list returns None
        assert result is None
    
    def test_construire_prompt_generation(self):
        """Test prompt construction."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        prompt = service._construire_prompt_generation(
            date_debut=date(2026, 2, 2),
            contraintes={"budget": 300, "energie": "faible"},
            contexte={"jules_age_mois": 19, "objectifs_sante": ["perdre poids"]}
        )
        
        assert "2026-02-02" in prompt
        assert "300" in prompt
        assert "faible" in prompt
        assert "19" in prompt
        assert "perdre poids" in prompt
    
    def test_construire_prompt_generation_defaults(self):
        """Test prompt construction with defaults."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        prompt = service._construire_prompt_generation(
            date_debut=date(2026, 2, 2),
            contraintes={},
            contexte={}
        )
        
        assert "400" in prompt  # Default budget
        assert "normal" in prompt  # Default energy


# ═══════════════════════════════════════════════════════════
# TESTS GET SEMAINE COMPLETE
# ═══════════════════════════════════════════════════════════

class TestPlanningAIServiceGetSemaineComplete:
    """Tests for get_semaine_complete method."""
    
    def test_get_semaine_complete_mock(self):
        """Test get_semaine_complete with mocked data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        
        # Mock all loaders to return empty data
        with patch.object(service, '_charger_repas', return_value={}), \
             patch.object(service, '_charger_activites', return_value={}), \
             patch.object(service, '_charger_projets', return_value={}), \
             patch.object(service, '_charger_routines', return_value={}), \
             patch.object(service, '_charger_events', return_value={}):
            
            result = service.get_semaine_complete(date(2026, 2, 2), mock_session)
        
        assert result is not None
        assert result.semaine_debut == date(2026, 2, 2)
        assert result.semaine_fin == date(2026, 2, 8)
        assert len(result.jours) == 7
    
    def test_get_semaine_complete_with_data(self):
        """Test get_semaine_complete with data."""
        from src.services.planning_unified import PlanningAIService
        
        with patch('src.services.planning_unified.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = PlanningAIService()
        
        mock_session = Mock()
        
        # Mock loaders with some data
        repas_data = {"2026-02-03": [{"id": 1, "temps_total": 60}]}
        activites_data = {"2026-02-03": [{"id": 1, "pour_jules": True, "budget": 10}]}
        
        with patch.object(service, '_charger_repas', return_value=repas_data), \
             patch.object(service, '_charger_activites', return_value=activites_data), \
             patch.object(service, '_charger_projets', return_value={}), \
             patch.object(service, '_charger_routines', return_value={}), \
             patch.object(service, '_charger_events', return_value={}):
            
            result = service.get_semaine_complete(date(2026, 2, 2), mock_session)
        
        assert result is not None
        assert result.semaine_debut == date(2026, 2, 2)
        # Check day with data
        jour_key = "2026-02-03"
        assert len(result.jours[jour_key].repas) == 1


# ═══════════════════════════════════════════════════════════
# TESTS MODULE EXPORTS
# ═══════════════════════════════════════════════════════════

class TestModuleExports:
    """Tests for module exports."""
    
    def test_jour_complet_schema_exported(self):
        """Test JourCompletSchema is accessible."""
        from src.services.planning_unified import JourCompletSchema
        
        assert JourCompletSchema is not None
    
    def test_semaine_complete_schema_exported(self):
        """Test SemaineCompleSchema is accessible."""
        from src.services.planning_unified import SemaineCompleSchema
        
        assert SemaineCompleSchema is not None
    
    def test_semaine_generee_ia_schema_exported(self):
        """Test SemaineGenereeIASchema is accessible."""
        from src.services.planning_unified import SemaineGenereeIASchema
        
        assert SemaineGenereeIASchema is not None
    
    def test_planning_ai_service_exported(self):
        """Test PlanningAIService is accessible."""
        from src.services.planning_unified import PlanningAIService
        
        assert PlanningAIService is not None
    
    def test_factory_functions_exported(self):
        """Test factory functions are accessible."""
        from src.services.planning_unified import get_planning_unified_service, get_unified_planning_service
        
        assert get_planning_unified_service is not None
        assert get_unified_planning_service is not None

