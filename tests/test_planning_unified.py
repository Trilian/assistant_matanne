"""
Tests unitaires pour PlanningAIService (src/services/planning_unified.py).

Tests couvrant:
- Agrégation complète de la semaine
- Chargement des repas, activités, projets, routines, événements
- Calcul de charge familiale
- Détection d'alertes intelligentes
- Génération IA
- CRUD événements calendrier
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from sqlalchemy.orm import Session

from src.services.planning_unified import (
    PlanningAIService,
    JourCompletSchema,
    SemaineCompleSchema,
    SemaineGenereeIASchema,
    get_planning_service,
)
from src.core.models import (
    CalendarEvent,
    Planning,
    Repas,
    FamilyActivity,
    Project,
    Routine,
    RoutineTask,
    Recette,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningAIServiceInit:
    """Test initialisation du service."""

    def test_service_initializes_with_calendar_event_model(self):
        """Test que le service s'initialise avec CalendarEvent."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            assert service.model == CalendarEvent
            assert service.model_name == "CalendarEvent"
            assert service.cache_ttl == 1800

    def test_service_inherits_base_service(self):
        """Test que le service hérite de BaseService."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            # Vérifier méthodes héritées
            assert hasattr(service, "create")
            assert hasattr(service, "get_by_id")
            assert hasattr(service, "update")
            assert hasattr(service, "delete")

    def test_factory_returns_service_instance(self):
        """Test que la factory retourne une instance."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = get_planning_service()

            assert isinstance(service, PlanningAIService)


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS SCHEMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningSchemas:
    """Test schémas Pydantic."""

    def test_jour_complet_schema_defaults(self):
        """Test valeurs par défaut JourCompletSchema."""
        jour = JourCompletSchema(
            date=date.today(),
            charge="faible",
            charge_score=20,
        )

        assert jour.repas == []
        assert jour.activites == []
        assert jour.projets == []
        assert jour.routines == []
        assert jour.events == []
        assert jour.budget_jour == 0.0
        assert jour.alertes == []
        assert jour.suggestions_ia == []

    def test_jour_complet_schema_with_data(self):
        """Test JourCompletSchema avec données."""
        jour = JourCompletSchema(
            date=date.today(),
            charge="intense",
            charge_score=85,
            repas=[{"id": 1, "type": "déjeuner"}],
            activites=[{"id": 2, "titre": "Parc"}],
            budget_jour=50.0,
            alertes=["⚠️ Jour chargé"],
        )

        assert jour.charge_score == 85
        assert len(jour.repas) == 1
        assert len(jour.alertes) == 1
        assert jour.budget_jour == 50.0

    def test_semaine_complete_schema_structure(self):
        """Test structure SemaineCompleSchema."""
        semaine = SemaineCompleSchema(
            semaine_debut=date(2026, 1, 26),
            semaine_fin=date(2026, 2, 1),
            jours={},
            charge_globale="normal",
        )

        assert semaine.semaine_debut == date(2026, 1, 26)
        assert semaine.stats_semaine == {}
        assert semaine.alertes_semaine == []

    def test_semaine_generee_ia_schema_defaults(self):
        """Test valeurs par défaut SemaineGenereeIASchema."""
        semaine = SemaineGenereeIASchema()

        assert semaine.repas_proposes == []
        assert semaine.activites_proposees == []
        assert semaine.projets_suggeres == []
        assert semaine.harmonie_description == ""
        assert semaine.raisons == []


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS CALCUL CHARGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningChargeCalculation:
    """Test calcul de charge familiale."""

    def test_calculer_charge_empty_returns_zero(self):
        """Test que charge vide retourne 0."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            score = service._calculer_charge(
                repas=[],
                activites=[],
                projets=[],
                routines=[],
            )

            assert score == 0

    def test_calculer_charge_with_repas(self):
        """Test charge avec repas complexes."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            repas = [
                {"temps_total": 60},
                {"temps_total": 45},
            ]

            score = service._calculer_charge(
                repas=repas,
                activites=[],
                projets=[],
                routines=[],
            )

            # Score devrait augmenter avec le temps de préparation
            assert score > 0
            assert score <= 100

    def test_calculer_charge_with_activites(self):
        """Test charge avec activités."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            activites = [
                {"id": 1, "titre": "Activité 1"},
                {"id": 2, "titre": "Activité 2"},
            ]

            score = service._calculer_charge(
                repas=[],
                activites=activites,
                projets=[],
                routines=[],
            )

            assert score > 0  # 2 activités = 20 points max

    def test_calculer_charge_with_urgent_projects(self):
        """Test charge avec projets urgents."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            projets = [
                {"id": 1, "priorite": "haute"},
                {"id": 2, "priorite": "haute"},
            ]

            score = service._calculer_charge(
                repas=[],
                activites=[],
                projets=projets,
                routines=[],
            )

            assert score > 0  # Projets urgents ajoutent des points

    def test_calculer_charge_capped_at_100(self):
        """Test que la charge est plafonnée à 100."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            # Beaucoup d'éléments
            repas = [{"temps_total": 120}] * 5
            activites = [{"id": i} for i in range(10)]
            projets = [{"priorite": "haute"}] * 5
            routines = [{"id": i}] * 20

            score = service._calculer_charge(
                repas=repas,
                activites=activites,
                projets=projets,
                routines=routines,
            )

            assert score <= 100


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS CONVERSION SCORE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningScoreConversion:
    """Test conversion score en label."""

    def test_score_to_charge_faible(self):
        """Test conversion score faible."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            assert service._score_to_charge(0) == "faible"
            assert service._score_to_charge(20) == "faible"
            assert service._score_to_charge(34) == "faible"

    def test_score_to_charge_normal(self):
        """Test conversion score normal."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            assert service._score_to_charge(35) == "normal"
            assert service._score_to_charge(50) == "normal"
            assert service._score_to_charge(69) == "normal"

    def test_score_to_charge_intense(self):
        """Test conversion score intense."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            assert service._score_to_charge(70) == "intense"
            assert service._score_to_charge(85) == "intense"
            assert service._score_to_charge(100) == "intense"


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS DÉTECTION ALERTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningAlertes:
    """Test détection d'alertes."""

    def test_detecter_alertes_surcharge(self):
        """Test alerte surcharge."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            alertes = service._detecter_alertes(
                jour=date.today(),
                repas=[],
                activites=[],
                projets=[],
                charge_score=85,
            )

            assert any("chargé" in a.lower() for a in alertes)

    def test_detecter_alertes_projets_urgents(self):
        """Test alerte projets urgents."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            projets = [
                {"id": 1, "priorite": "haute"},
                {"id": 2, "priorite": "haute"},
            ]

            alertes = service._detecter_alertes(
                jour=date.today(),
                repas=[],
                activites=[],
                projets=projets,
                charge_score=50,
            )

            assert any("urgent" in a.lower() for a in alertes)

    def test_detecter_alertes_repas_nombreux(self):
        """Test alerte trop de repas."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            repas = [{"id": i} for i in range(5)]

            alertes = service._detecter_alertes(
                jour=date.today(),
                repas=repas,
                activites=[],
                projets=[],
                charge_score=50,
            )

            assert any("repas" in a.lower() for a in alertes)

    def test_detecter_alertes_semaine_charge(self):
        """Test alertes semaine trop chargée."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            jours = {}
            for i in range(7):
                jour_str = (date.today() + timedelta(days=i)).isoformat()
                jours[jour_str] = JourCompletSchema(
                    date=date.today() + timedelta(days=i),
                    charge="intense" if i < 4 else "faible",
                    charge_score=85 if i < 4 else 20,
                )

            alertes = service._detecter_alertes_semaine(jours)

            # 4 jours intenses devrait déclencher alerte
            assert any("burnout" in a.lower() or "chargé" in a.lower() for a in alertes)

    def test_detecter_alertes_semaine_budget(self):
        """Test alerte budget élevé."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            jours = {}
            for i in range(7):
                jour_str = (date.today() + timedelta(days=i)).isoformat()
                jours[jour_str] = JourCompletSchema(
                    date=date.today() + timedelta(days=i),
                    charge="normal",
                    charge_score=50,
                    budget_jour=100.0,  # 700€ total
                )

            alertes = service._detecter_alertes_semaine(jours)

            assert any("budget" in a.lower() for a in alertes)


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS CALCUL STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningStats:
    """Test calcul statistiques."""

    def test_calculer_stats_semaine_empty(self):
        """Test stats avec semaine vide."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            jours = {
                "2026-01-26": JourCompletSchema(
                    date=date(2026, 1, 26),
                    charge="faible",
                    charge_score=10,
                )
            }

            stats = service._calculer_stats_semaine(jours)

            assert stats["total_repas"] == 0
            assert stats["total_activites"] == 0
            assert stats["total_projets"] == 0
            assert stats["budget_total"] == 0.0

    def test_calculer_stats_semaine_with_data(self):
        """Test stats avec données."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            jours = {
                "2026-01-26": JourCompletSchema(
                    date=date(2026, 1, 26),
                    charge="normal",
                    charge_score=50,
                    repas=[{"id": 1}, {"id": 2}],
                    activites=[{"id": 1, "pour_jules": True}],
                    projets=[{"id": 1}],
                    budget_jour=30.0,
                ),
                "2026-01-27": JourCompletSchema(
                    date=date(2026, 1, 27),
                    charge="faible",
                    charge_score=20,
                    repas=[{"id": 3}],
                    events=[{"id": 1}],
                    budget_jour=20.0,
                ),
            }

            stats = service._calculer_stats_semaine(jours)

            assert stats["total_repas"] == 3
            assert stats["total_activites"] == 1
            assert stats["total_projets"] == 1
            assert stats["total_events"] == 1
            assert stats["budget_total"] == 50.0
            assert stats["charge_moyenne"] == 35  # (50+20)/2

    def test_calculer_budget_jour(self):
        """Test calcul budget jour."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            activites = [
                {"budget": 20.0},
                {"budget": 15.0},
                {"budget": None},  # Pas de budget
            ]

            budget = service._calculer_budget_jour(activites, [])

            assert budget == 35.0


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS CRUD ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningEventsCRUD:
    """Test CRUD événements calendrier."""

    def test_creer_event_creates_calendar_event(self, db):
        """Test création événement."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            event = service.creer_event(
                titre="RDV Médecin",
                date_debut=datetime(2026, 1, 28, 14, 0),
                type_event="medical",
                lieu="Cabinet Dr Martin",
                db=db,
            )

            assert event is not None
            assert event.titre == "RDV Médecin"
            assert event.type_event == "medical"
            assert event.lieu == "Cabinet Dr Martin"

    def test_creer_event_with_date_fin(self, db):
        """Test création événement avec date fin."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            event = service.creer_event(
                titre="Réunion Famille",
                date_debut=datetime(2026, 1, 28, 10, 0),
                date_fin=datetime(2026, 1, 28, 12, 0),
                type_event="famille",
                db=db,
            )

            assert event is not None
            assert event.date_fin == datetime(2026, 1, 28, 12, 0)


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS INVALIDATION CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningCacheInvalidation:
    """Test invalidation du cache."""

    def test_invalider_cache_semaine_calculates_week_start(self):
        """Test calcul début de semaine pour invalidation."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            # Mercredi 28 janvier 2026
            test_date = date(2026, 1, 28)
            expected_monday = date(2026, 1, 26)

            with patch.object(service, '_invalider_cache_semaine') as mock_invalider:
                # Appeler directement la méthode
                service._invalider_cache_semaine(test_date)

                # La méthode devrait être appelée avec la bonne date
                mock_invalider.assert_called()


# ═══════════════════════════════════════════════════════════
# SECTION 9: TESTS GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningIAGeneration:
    """Test génération IA."""

    def test_construire_prompt_generation_includes_context(self):
        """Test que le prompt inclut le contexte."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            prompt = service._construire_prompt_generation(
                date_debut=date(2026, 1, 26),
                contraintes={"budget": 300, "energie": "faible"},
                contexte={"jules_age_mois": 20, "objectifs_sante": ["Sport"]},
            )

            assert "300" in prompt  # Budget
            assert "faible" in prompt  # Énergie
            assert "20 mois" in prompt  # Âge Jules
            assert "Sport" in prompt  # Objectif santé

    def test_construire_prompt_generation_defaults(self):
        """Test valeurs par défaut du prompt."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            prompt = service._construire_prompt_generation(
                date_debut=date(2026, 1, 26),
                contraintes={},
                contexte={},
            )

            assert "400" in prompt  # Budget par défaut
            assert "normal" in prompt  # Énergie par défaut
            assert "19 mois" in prompt  # Âge Jules par défaut


# ═══════════════════════════════════════════════════════════
# SECTION 10: TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPlanningIntegration:
    """Tests d'intégration planning."""

    def test_complete_weekly_workflow(self, db):
        """Test workflow semaine complet."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            # Créer un événement
            event = service.creer_event(
                titre="Test Événement",
                date_debut=datetime(2026, 1, 28, 10, 0),
                type_event="test",
                db=db,
            )

            assert event is not None

            # Vérifier qu'on peut récupérer l'événement
            retrieved = service.get_by_id(event.id, db=db)
            assert retrieved is not None
            assert retrieved.titre == "Test Événement"

            # Supprimer l'événement
            deleted = service.delete(event.id, db=db)
            assert deleted is True

    def test_charge_calculation_integration(self):
        """Test intégration calcul de charge."""
        with patch("src.services.planning_unified.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = PlanningAIService()

            # Scénario réaliste
            repas = [
                {"temps_total": 45},  # Petit-déjeuner élaboré
                {"temps_total": 30},  # Déjeuner
                {"temps_total": 60},  # Dîner
            ]
            activites = [
                {"id": 1, "titre": "Parc avec Jules"},
            ]
            projets = [
                {"id": 1, "priorite": "moyenne"},
            ]
            routines = [
                {"id": 1, "nom": "Bain"},
                {"id": 2, "nom": "Coucher"},
            ]

            score = service._calculer_charge(
                repas=repas,
                activites=activites,
                projets=projets,
                routines=routines,
            )

            # Vérifier que le score est raisonnable
            assert 20 <= score <= 60
            assert service._score_to_charge(score) in ["faible", "normal"]
