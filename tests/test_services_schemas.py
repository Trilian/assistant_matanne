"""
Tests pour src/services/types.py - BaseService et schémas Pydantic des services
Ces tests couvrent ~150 statements de logique métier
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError


# =============================================================================
# Tests schemas Pydantic - courses.py
# =============================================================================

class TestSuggestionCourses:
    """Tests pour SuggestionCourses schema"""
    
    def test_valid_suggestion(self):
        from src.services.courses import SuggestionCourses
        suggestion = SuggestionCourses(
            nom="Tomates",
            quantite=2.5,
            unite="kg",
            priorite="haute",
            rayon="Fruits et légumes"
        )
        assert suggestion.nom == "Tomates"
        assert suggestion.quantite == 2.5
    
    def test_invalid_priorite(self):
        from src.services.courses import SuggestionCourses
        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="Tomates",
                quantite=2.5,
                unite="kg",
                priorite="invalid",
                rayon="Fruits et légumes"
            )
    
    def test_nom_too_short(self):
        from src.services.courses import SuggestionCourses
        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="X",
                quantite=2.5,
                unite="kg",
                priorite="haute",
                rayon="Fruits et légumes"
            )
    
    def test_quantite_must_be_positive(self):
        from src.services.courses import SuggestionCourses
        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="Tomates",
                quantite=-1,
                unite="kg",
                priorite="haute",
                rayon="Fruits"
            )


# =============================================================================
# Tests schemas Pydantic - planning.py
# =============================================================================

class TestJourPlanning:
    """Tests pour JourPlanning schema"""
    
    def test_valid_jour(self):
        from src.services.planning import JourPlanning
        jour = JourPlanning(
            jour="2025-01-28",
            dejeuner="Pâtes carbonara",
            diner="Salade composée"
        )
        assert jour.jour == "2025-01-28"
        assert jour.dejeuner == "Pâtes carbonara"
    
    def test_jour_too_short(self):
        from src.services.planning import JourPlanning
        with pytest.raises(ValidationError):
            JourPlanning(
                jour="2025",
                dejeuner="Pâtes",
                diner="Salade"
            )
    
    def test_dejeuner_too_short(self):
        from src.services.planning import JourPlanning
        with pytest.raises(ValidationError):
            JourPlanning(
                jour="2025-01-28",
                dejeuner="X",  # trop court
                diner="Salade composée"
            )


# =============================================================================
# Tests schemas Pydantic - recettes.py
# =============================================================================

class TestRecetteInput:
    """Tests pour RecetteInput schema du service recettes"""
    
    def test_valid_recette(self):
        from src.core.validators_pydantic import RecetteInput
        recette = RecetteInput(
            nom="Tarte aux pommes",
            description="Délicieuse tarte maison"
        )
        assert recette.nom == "Tarte aux pommes"
    
    def test_nom_required(self):
        from src.core.validators_pydantic import RecetteInput
        with pytest.raises(ValidationError):
            RecetteInput(description="Description sans nom")


class TestIngredientInput:
    """Tests pour IngredientInput schema"""
    
    def test_valid_ingredient(self):
        from src.core.validators_pydantic import IngredientInput
        ingredient = IngredientInput(
            nom="Pomme",
            quantite=3.0,
            unite="pièces"
        )
        assert ingredient.nom == "Pomme"
        assert ingredient.quantite == 3.0
    
    def test_quantite_must_be_positive(self):
        from src.core.validators_pydantic import IngredientInput
        with pytest.raises(ValidationError):
            IngredientInput(
                nom="Pomme",
                quantite=-1,
                unite="pièces"
            )


class TestEtapeInput:
    """Tests pour EtapeInput schema"""
    
    def test_valid_etape(self):
        from src.core.validators_pydantic import EtapeInput
        etape = EtapeInput(
            numero=1,
            description="Préchauffer le four"
        )
        assert etape.numero == 1
    
    def test_numero_must_be_positive(self):
        from src.core.validators_pydantic import EtapeInput
        with pytest.raises(ValidationError):
            EtapeInput(
                numero=0,
                description="Etape invalide"
            )


class TestIngredientStockInput:
    """Tests pour IngredientStockInput schema"""
    
    def test_valid_stock(self):
        from src.core.validators_pydantic import IngredientStockInput
        stock = IngredientStockInput(
            ingredient_id=1,
            quantite=500.0,
            date_peremption=date(2025, 12, 31)
        )
        assert stock.ingredient_id == 1
    
    def test_quantite_must_be_positive(self):
        from src.core.validators_pydantic import IngredientStockInput
        with pytest.raises(ValidationError):
            IngredientStockInput(
                ingredient_id=1,
                quantite=-10,
                date_peremption=date(2025, 12, 31)
            )


class TestRepasInput:
    """Tests pour RepasInput schema"""
    
    def test_valid_repas(self):
        from src.core.validators_pydantic import RepasInput
        repas = RepasInput(
            planning_id=1,
            date=date(2025, 1, 28),
            type_repas="dejeuner",
            recette_id=5
        )
        assert repas.type_repas == "dejeuner"
    
    def test_invalid_type_repas(self):
        from src.core.validators_pydantic import RepasInput
        with pytest.raises(ValidationError):
            RepasInput(
                planning_id=1,
                date=date(2025, 1, 28),
                type_repas="gouter",  # pas valide
                recette_id=5
            )


class TestRoutineInput:
    """Tests pour RoutineInput schema"""
    
    def test_valid_routine(self):
        from src.core.validators_pydantic import RoutineInput
        routine = RoutineInput(
            nom="Routine du matin",
            type_routine="matin"
        )
        assert routine.nom == "Routine du matin"
    
    def test_invalid_type(self):
        from src.core.validators_pydantic import RoutineInput
        with pytest.raises(ValidationError):
            RoutineInput(
                nom="Routine",
                type_routine="invalid"
            )


class TestTacheRoutineInput:
    """Tests pour TacheRoutineInput schema"""
    
    def test_valid_tache(self):
        from src.core.validators_pydantic import TacheRoutineInput
        tache = TacheRoutineInput(
            routine_id=1,
            description="Se brosser les dents",
            ordre=1
        )
        assert tache.description == "Se brosser les dents"
    
    def test_ordre_must_be_positive(self):
        from src.core.validators_pydantic import TacheRoutineInput
        with pytest.raises(ValidationError):
            TacheRoutineInput(
                routine_id=1,
                description="Tâche",
                ordre=0
            )


class TestEntreeJournalInput:
    """Tests pour EntreeJournalInput schema"""
    
    def test_valid_entree(self):
        from src.core.validators_pydantic import EntreeJournalInput
        entree = EntreeJournalInput(
            date=date(2025, 1, 28),
            contenu="Aujourd'hui Jules a marché!"
        )
        assert "Jules" in entree.contenu
    
    def test_contenu_min_length(self):
        from src.core.validators_pydantic import EntreeJournalInput
        with pytest.raises(ValidationError):
            EntreeJournalInput(
                date=date(2025, 1, 28),
                contenu="X"  # trop court
            )


class TestProjetInput:
    """Tests pour ProjetInput schema"""
    
    def test_valid_projet(self):
        from src.core.validators_pydantic import ProjetInput
        projet = ProjetInput(
            nom="Rénovation cuisine",
            statut="en_cours"
        )
        assert projet.nom == "Rénovation cuisine"
    
    def test_invalid_statut(self):
        from src.core.validators_pydantic import ProjetInput
        with pytest.raises(ValidationError):
            ProjetInput(
                nom="Projet",
                statut="invalid"
            )


# =============================================================================
# Tests BaseService Logic (sans BD)
# =============================================================================

class TestBaseServiceInit:
    """Tests pour l'initialisation de BaseService"""
    
    def test_base_service_init(self):
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette, cache_ttl=300)
        assert service.model == Recette
        assert service.model_name == "Recette"
        assert service.cache_ttl == 300
    
    def test_base_service_default_ttl(self):
        from src.services.types import BaseService
        from src.core.models import Planning
        
        service = BaseService(Planning)
        assert service.cache_ttl == 60  # default


# =============================================================================
# Tests CoursesService Init
# =============================================================================

class TestCoursesServiceInit:
    """Tests pour l'initialisation de CoursesService"""
    
    def test_courses_service_init(self):
        from src.services.courses import CoursesService
        
        service = CoursesService()
        assert service.model_name == "ArticleCourses"
        assert service.service_name == "courses"


# =============================================================================
# Tests PlanningService Init
# =============================================================================

class TestPlanningServiceInit:
    """Tests pour l'initialisation de PlanningService"""
    
    def test_planning_service_init(self):
        from src.services.planning import PlanningService
        
        service = PlanningService()
        assert service.model_name == "Planning"
        assert service.service_name == "planning"
