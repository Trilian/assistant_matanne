"""
Tests pour PlanningService - Service critique
Tests complets pour la planification des repas
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.services.planning import PlanningService, get_planning_service


# ═══════════════════════════════════════════════════════════
# TESTS INSTANCIATION ET FACTORY
# ═══════════════════════════════════════════════════════════

class TestPlanningServiceFactory:
    """Tests pour la factory et l'instanciation du service."""
    
    def test_get_planning_service_returns_instance(self):
        """La factory retourne une instance de PlanningService."""
        service = get_planning_service()
        assert service is not None
        assert isinstance(service, PlanningService)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - PLANNING
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceCRUD:
    """Tests pour le CRUD des plannings."""
    
    def test_creer_planning(self, db, planning_service):
        """Créer un nouveau planning."""
        debut = date.today()
        fin = debut + timedelta(days=6)
        
        planning = planning_service.creer_planning(
            nom="Semaine test",
            date_debut=debut,
            date_fin=fin,
            db=db
        )
        
        assert planning is not None
        assert planning.nom == "Semaine test"
        assert planning.semaine_debut == debut
    
    def test_obtenir_planning_actif(self, db, planning_factory, planning_service):
        """Obtenir le planning actif de la semaine."""
        planning = planning_factory.create(
            nom="Planning actif",
            semaine_debut=date.today()
        )
        
        actif = planning_service.obtenir_planning_actif(db=db)
        
        assert actif is not None
        assert actif.id == planning.id
    
    def test_lister_plannings(self, db, planning_factory, planning_service):
        """Lister tous les plannings."""
        planning_factory.create(nom="Planning 1")
        planning_factory.create(nom="Planning 2")
        
        plannings = planning_service.lister_plannings(db=db)
        
        assert len(plannings) >= 2
    
    def test_supprimer_planning(self, db, planning_factory, planning_service):
        """Supprimer un planning."""
        planning = planning_factory.create(nom="À supprimer")
        planning_id = planning.id
        
        resultat = planning_service.supprimer_planning(planning_id, db=db)
        
        assert resultat is True


# ═══════════════════════════════════════════════════════════
# TESTS REPAS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceRepas:
    """Tests pour la gestion des repas dans le planning."""
    
    def test_ajouter_repas(self, db, planning_factory, recette_factory, planning_service):
        """Ajouter un repas au planning."""
        planning = planning_factory.create()
        recette = recette_factory.create(nom="Poulet rôti")
        
        repas = planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=date.today(),
            type_repas="dîner",
            db=db
        )
        
        assert repas is not None
        assert repas.type_repas == "dîner"
        assert repas.recette_id == recette.id
    
    def test_obtenir_repas_jour(self, db, planning_factory, recette_factory, planning_service):
        """Obtenir les repas d'un jour spécifique."""
        planning = planning_factory.create()
        recette = recette_factory.create()
        
        planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=date.today(),
            type_repas="déjeuner",
            db=db
        )
        
        repas = planning_service.obtenir_repas_jour(date.today(), db=db)
        
        assert len(repas) >= 1
    
    def test_obtenir_repas_semaine(self, db, planning_factory, recette_factory, planning_service):
        """Obtenir tous les repas de la semaine."""
        planning = planning_factory.create()
        recette = recette_factory.create()
        
        # Ajouter plusieurs repas
        for i in range(3):
            planning_service.ajouter_repas(
                planning_id=planning.id,
                recette_id=recette.id,
                date=date.today() + timedelta(days=i),
                type_repas="dîner",
                db=db
            )
        
        repas = planning_service.obtenir_repas_semaine(
            date_debut=date.today(),
            db=db
        )
        
        assert len(repas) >= 3
    
    def test_modifier_repas(self, db, planning_factory, recette_factory, planning_service):
        """Modifier un repas existant."""
        planning = planning_factory.create()
        recette1 = recette_factory.create(nom="Recette 1")
        recette2 = recette_factory.create(nom="Recette 2")
        
        repas = planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette1.id,
            date=date.today(),
            type_repas="dîner",
            db=db
        )
        
        repas_maj = planning_service.modifier_repas(
            repas.id,
            {"recette_id": recette2.id},
            db=db
        )
        
        assert repas_maj.recette_id == recette2.id
    
    def test_supprimer_repas(self, db, planning_factory, recette_factory, planning_service):
        """Supprimer un repas du planning."""
        planning = planning_factory.create()
        recette = recette_factory.create()
        
        repas = planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=date.today(),
            type_repas="dîner",
            db=db
        )
        
        resultat = planning_service.supprimer_repas(repas.id, db=db)
        
        assert resultat is True


# ═══════════════════════════════════════════════════════════
# TESTS TYPES DE REPAS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceTypesRepas:
    """Tests pour les différents types de repas."""
    
    def test_types_repas_disponibles(self, planning_service):
        """Vérifier les types de repas disponibles."""
        types = planning_service.obtenir_types_repas()
        
        assert "petit_déjeuner" in types or "déjeuner" in types
        assert "dîner" in types or "diner" in types
    
    def test_ajouter_repas_petit_dejeuner(self, db, planning_factory, recette_factory, planning_service):
        """Ajouter un petit-déjeuner."""
        planning = planning_factory.create()
        recette = recette_factory.create(type_repas="petit_déjeuner")
        
        repas = planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=date.today(),
            type_repas="petit_déjeuner",
            db=db
        )
        
        assert repas.type_repas == "petit_déjeuner"
    
    def test_ajouter_repas_gouter(self, db, planning_factory, recette_factory, planning_service):
        """Ajouter un goûter."""
        planning = planning_factory.create()
        recette = recette_factory.create(type_repas="goûter")
        
        repas = planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=date.today(),
            type_repas="goûter",
            db=db
        )
        
        assert repas.type_repas == "goûter"


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceIA:
    """Tests pour la génération de planning via IA."""
    
    @patch('src.services.planning.PlanningService.call_with_list_parsing_sync')
    def test_generer_planning_semaine_ia(self, mock_ia, db, planning_service):
        """Générer un planning de semaine via IA."""
        mock_ia.return_value = [
            Mock(jour="lundi", type_repas="dîner", recette_suggestion="Poulet rôti"),
            Mock(jour="mardi", type_repas="dîner", recette_suggestion="Pasta"),
        ]
        
        suggestions = planning_service.generer_planning_ia(
            date_debut=date.today(),
            preferences={"regime": "omnivore"},
            db=db
        )
        
        assert len(suggestions) >= 2
        mock_ia.assert_called_once()
    
    @patch('src.services.planning.PlanningService.call_with_parsing_sync')
    def test_suggerer_repas_pour_jour(self, mock_ia, db, planning_service):
        """Suggérer un repas pour un jour spécifique."""
        mock_ia.return_value = Mock(
            recette_suggestion="Salade César",
            raison="Repas léger adapté à la météo"
        )
        
        suggestion = planning_service.suggerer_repas(
            date=date.today(),
            type_repas="déjeuner",
            db=db
        )
        
        assert suggestion is not None


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceStats:
    """Tests pour les statistiques de planning."""
    
    def test_compter_repas_semaine(self, db, planning_factory, recette_factory, planning_service):
        """Compter les repas planifiés pour la semaine."""
        planning = planning_factory.create()
        recette = recette_factory.create()
        
        for i in range(5):
            planning_service.ajouter_repas(
                planning_id=planning.id,
                recette_id=recette.id,
                date=date.today() + timedelta(days=i),
                type_repas="dîner",
                db=db
            )
        
        count = planning_service.compter_repas_semaine(
            date_debut=date.today(),
            db=db
        )
        
        assert count >= 5
    
    def test_statistiques_equilibre(self, db, planning_factory, recette_factory, planning_service):
        """Obtenir les statistiques d'équilibre nutritionnel."""
        planning = planning_factory.create()
        
        # Créer des recettes de différents types
        recettes = [
            recette_factory.create(type_repas="dîner"),
            recette_factory.create(type_repas="déjeuner"),
        ]
        
        for r in recettes:
            planning_service.ajouter_repas(
                planning_id=planning.id,
                recette_id=r.id,
                date=date.today(),
                type_repas=r.type_repas,
                db=db
            )
        
        stats = planning_service.statistiques_equilibre(
            planning_id=planning.id,
            db=db
        )
        
        assert stats is not None


# ═══════════════════════════════════════════════════════════
# TESTS DUPLICATION ET COPIE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceDuplication:
    """Tests pour la duplication de plannings."""
    
    def test_dupliquer_planning(self, db, planning_factory, recette_factory, planning_service):
        """Dupliquer un planning existant."""
        # Créer un planning avec des repas
        planning = planning_factory.create(nom="Planning source")
        recette = recette_factory.create()
        
        planning_service.ajouter_repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date=planning.semaine_debut,
            type_repas="dîner",
            db=db
        )
        
        # Dupliquer
        nouveau = planning_service.dupliquer_planning(
            planning_id=planning.id,
            nouvelle_date=date.today() + timedelta(weeks=1),
            db=db
        )
        
        assert nouveau is not None
        assert nouveau.id != planning.id
        assert nouveau.nom != planning.nom or "copie" in nouveau.nom.lower()
