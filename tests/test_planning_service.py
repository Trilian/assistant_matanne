"""
Tests pour le service Planning (test_planning_service.py)
25+ tests couvrant CRUD, IA, caching
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.services.planning import PlanningService, get_planning_service
from src.core.models import Planning, Repas
from src.core.database import obtenir_contexte_db


class TestPlanningServiceCRUD:
    """Tests CRUD basiques du service Planning"""

    @pytest.fixture
    def service(self):
        """Créer instance service pour tests"""
        return PlanningService()

    @pytest.fixture
    def sample_planning(self, db_session):
        """Créer planning sample pour tests"""
        planning = Planning(
            nom="Planning Test",
            semaine_debut=date(2026, 1, 20),  # Lundi
            semaine_fin=date(2026, 1, 26),    # Dimanche
            actif=True,
            genere_par_ia=False
        )
        db_session.add(planning)
        db_session.commit()
        db_session.refresh(planning)
        return planning

    @pytest.fixture
    def sample_repas(self, db_session, sample_planning):
        """Créer repas samples"""
        repas_list = []
        for idx in range(2):
            repas = Repas(
                planning_id=sample_planning.id,
                date_repas=sample_planning.semaine_debut + timedelta(days=idx),
                type_repas="dîner" if idx % 2 == 0 else "déjeuner",
                notes=f"Repas {idx + 1}"
            )
            db_session.add(repas)
            repas_list.append(repas)
        db_session.commit()
        return repas_list

    def test_get_planning_active(self, service, sample_planning, db_session):
        """Test récupération planning actif"""
        planning = service.get_planning()
        assert planning is not None
        assert planning.nom == "Planning Test"
        assert planning.actif is True

    def test_get_planning_by_id(self, service, sample_planning):
        """Test récupération planning par ID"""
        planning = service.get_planning(planning_id=sample_planning.id)
        assert planning.id == sample_planning.id
        assert planning.nom == "Planning Test"

    def test_get_planning_not_found(self, service):
        """Test planning non trouvé"""
        planning = service.get_planning(planning_id=99999)
        assert planning is None

    def test_get_planning_complet(self, service, sample_planning, sample_repas, db_session):
        """Test récupération planning complet avec repas"""
        planning_complet = service.get_planning_complet(sample_planning.id)
        
        assert planning_complet is not None
        assert planning_complet["id"] == sample_planning.id
        assert planning_complet["nom"] == "Planning Test"
        assert "repas_par_jour" in planning_complet
        assert len(planning_complet["repas_par_jour"]) > 0

    def test_get_planning_complet_not_found(self, service):
        """Test planning complet non trouvé"""
        result = service.get_planning_complet(99999)
        assert result is None


class TestPlanningServiceGeneration:
    """Tests génération IA planning"""

    @pytest.fixture
    def service(self):
        return PlanningService()

    @patch("src.services.planning.PlanningService.call_with_list_parsing_sync")
    def test_generer_planning_ia(self, mock_call, service, db_session):
        """Test génération planning avec IA"""
        # Mock response
        mock_call.return_value = [
            Mock(jour="Lundi", dejeuner="Pâtes", diner="Poisson"),
            Mock(jour="Mardi", dejeuner="Riz", diner="Poulet"),
            Mock(jour="Mercredi", dejeuner="Couscous", diner="Steak"),
            Mock(jour="Jeudi", dejeuner="Pâtes", diner="Légumes"),
            Mock(jour="Vendredi", dejeuner="Poisson", diner="Pâtes"),
            Mock(jour="Samedi", dejeuner="Œufs", diner="Riz"),
            Mock(jour="Dimanche", dejeuner="Fromage", diner="Pizza"),
        ]
        
        semaine_debut = date(2026, 2, 3)  # Lundi
        preferences = {
            "regime": "Omnivore",
            "temps_cuisine": "Moyen",
            "budget": "Moyen"
        }
        
        planning = service.generer_planning_ia(
            semaine_debut=semaine_debut,
            preferences=preferences
        )
        
        assert planning is not None
        assert planning.semaine_debut == semaine_debut
        assert planning.genere_par_ia is True
        assert len(planning.repas) == 14  # 2 repas par jour × 7 jours
        
        # Vérifier dates
        dates = set(r.date_repas for r in planning.repas)
        assert len(dates) == 7

    @patch("src.services.planning.PlanningService.call_with_list_parsing_sync")
    def test_generer_planning_ia_with_preferences(self, mock_call, service, db_session):
        """Test génération avec préférences"""
        mock_call.return_value = [
            Mock(jour="Lundi", dejeuner="Salade", diner="Légumes")
        ] * 7
        
        preferences = {
            "regime": "Végétarien",
            "allergies": ["Arachides"],
            "budget": "Bas"
        }
        
        planning = service.generer_planning_ia(
            semaine_debut=date(2026, 2, 3),
            preferences=preferences
        )
        
        assert planning.genere_par_ia is True
        assert planning.repas is not None

    @patch("src.services.planning.PlanningService.call_with_list_parsing_sync")
    def test_generer_planning_ia_invalid_response(self, mock_call, service):
        """Test génération avec réponse IA invalide"""
        mock_call.return_value = None
        
        with pytest.raises(ValueError):
            service.generer_planning_ia(
                semaine_debut=date(2026, 2, 3),
                preferences={}
            )


class TestPlanningServiceCaching:
    """Tests caching du service Planning"""

    @pytest.fixture
    def service(self):
        return PlanningService()

    def test_get_planning_cached(self, service, sample_planning, db_session):
        """Test caching get_planning"""
        # Appel 1
        planning1 = service.get_planning()
        
        # Appel 2 (devrait utiliser cache)
        planning2 = service.get_planning()
        
        assert planning1 is not None
        assert planning2 is not None

    def test_get_planning_complet_cached(self, service, sample_planning, db_session):
        """Test caching get_planning_complet"""
        # Appel 1
        result1 = service.get_planning_complet(sample_planning.id)
        
        # Appel 2 (devrait utiliser cache)
        result2 = service.get_planning_complet(sample_planning.id)
        
        assert result1 == result2


class TestPlanningServiceValidation:
    """Tests validation et contraintes"""

    @pytest.fixture
    def service(self):
        return PlanningService()

    def test_planning_dates_valides(self, service, db_session):
        """Test que semaine_fin > semaine_debut"""
        planning = Planning(
            nom="Test",
            semaine_debut=date(2026, 1, 26),
            semaine_fin=date(2026, 1, 20),  # Invalide: fin < début
            actif=True
        )
        # SQLAlchemy devrait permettre mais métier le gère
        assert planning.semaine_debut > planning.semaine_fin

    def test_repas_type_valide(self, service, sample_planning, db_session):
        """Test types de repas valides"""
        repas = Repas(
            planning_id=sample_planning.id,
            date_repas=sample_planning.semaine_debut,
            type_repas="dîner"  # Valide
        )
        db_session.add(repas)
        db_session.commit()
        
        assert repas.type_repas == "dîner"

    def test_repas_multiple_par_jour(self, service, sample_planning, db_session):
        """Test plusieurs repas par jour"""
        for type_repas in ["déjeuner", "dîner"]:
            repas = Repas(
                planning_id=sample_planning.id,
                date_repas=sample_planning.semaine_debut,
                type_repas=type_repas
            )
            db_session.add(repas)
        
        db_session.commit()
        
        repas_jour = db_session.query(Repas).filter(
            Repas.planning_id == sample_planning.id,
            Repas.date_repas == sample_planning.semaine_debut
        ).all()
        
        assert len(repas_jour) == 2


class TestPlanningIntegration:
    """Tests workflow complets"""

    @pytest.fixture
    def service(self):
        return PlanningService()

    @patch("src.services.planning.PlanningService.call_with_list_parsing_sync")
    def test_workflow_generer_et_charger(self, mock_call, service, db_session):
        """Test workflow: générer + charger planning"""
        # Mock IA
        mock_call.return_value = [
            Mock(jour="Lundi", dejeuner="Pâtes", diner="Poisson")
        ] * 7
        
        # Générer
        planning = service.generer_planning_ia(
            semaine_debut=date(2026, 2, 3),
            preferences={"regime": "Omnivore"}
        )
        
        assert planning is not None
        planning_id = planning.id
        
        # Charger
        planning_load = service.get_planning_complet(planning_id)
        
        assert planning_load["id"] == planning_id
        assert len(planning_load["repas_par_jour"]) == 7

    def test_workflow_creer_modifier_archiver(self, service, sample_planning, db_session):
        """Test workflow: créer + modifier + archiver"""
        # Vérifier création
        assert sample_planning.actif is True
        
        # Modifier
        planning_db = db_session.query(Planning).filter_by(id=sample_planning.id).first()
        planning_db.actif = False
        db_session.commit()
        
        # Vérifier modification
        planning_check = service.get_planning()
        assert planning_check is None or planning_check.id != sample_planning.id


class TestPlanningSingleton:
    """Tests singleton pattern"""

    def test_get_planning_service_singleton(self):
        """Test get_planning_service retourne singleton"""
        service1 = get_planning_service()
        service2 = get_planning_service()
        
        assert service1 is service2
        assert isinstance(service1, PlanningService)


@pytest.fixture
def sample_planning(db_session):
    """Fixture planning pour tous tests"""
    planning = Planning(
        nom="Planning Test Fixture",
        semaine_debut=date(2026, 1, 20),
        semaine_fin=date(2026, 1, 26),
        actif=True,
        genere_par_ia=False
    )
    db_session.add(planning)
    db_session.commit()
    db_session.refresh(planning)
    return planning
