"""
Tests complets pour src/services/recettes.py

Couverture cible: >80%
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestRecetteSuggestion:
    """Tests schéma RecetteSuggestion."""

    def test_import_schema(self):
        from src.services.recettes import RecetteSuggestion
        assert RecetteSuggestion is not None

    def test_creation_valide(self):
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Poulet rôti aux herbes",
            description="Un délicieux poulet rôti avec des herbes de Provence",
            temps_preparation=20,
            temps_cuisson=60,
            portions=4,
            difficulte="moyen",
            type_repas="plat",
            ingredients=[{"nom": "Poulet", "quantite": 1, "unite": "kg"}],
            etapes=[{"ordre": 1, "description": "Préchauffer le four"}]
        )
        
        assert suggestion.nom == "Poulet rôti aux herbes"
        assert suggestion.temps_preparation == 20
        assert suggestion.difficulte == "moyen"

    def test_conversion_float_to_int(self):
        from src.services.recettes import RecetteSuggestion
        
        # Mistral peut retourner des floats
        suggestion = RecetteSuggestion(
            nom="Test recette",
            description="Description de test pour la recette",
            temps_preparation=20.0,  # Float au lieu de int
            temps_cuisson=30.0,
            portions=4.0,
            difficulte="facile",
            type_repas="entrée",
            ingredients=[],
            etapes=[]
        )
        
        assert isinstance(suggestion.temps_preparation, int)
        assert suggestion.temps_preparation == 20

    def test_validation_difficulte(self):
        from src.services.recettes import RecetteSuggestion
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Test",
                description="Description de test minimum",
                temps_preparation=10,
                temps_cuisson=20,
                difficulte="impossible",  # Invalide
                type_repas="plat",
                ingredients=[],
                etapes=[]
            )

    def test_validation_temps_preparation_min(self):
        from src.services.recettes import RecetteSuggestion
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Test",
                description="Description minimum de test",
                temps_preparation=0,  # Doit être > 0
                temps_cuisson=20,
                difficulte="facile",
                type_repas="plat",
                ingredients=[],
                etapes=[]
            )


class TestVersionBebeGeneree:
    """Tests schéma VersionBebeGeneree."""

    def test_creation_valide(self):
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Mixer finement tous les légumes",
            notes_bebe="Adapter la texture selon l'âge",
            age_minimum_mois=8
        )
        
        assert version.age_minimum_mois == 8
        assert "Mixer" in version.instructions_modifiees

    def test_conversion_float_age(self):
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Instructions",
            notes_bebe="Notes",
            age_minimum_mois=12.0  # Float
        )
        
        assert isinstance(version.age_minimum_mois, int)
        assert version.age_minimum_mois == 12

    def test_validation_age_min(self):
        from src.services.recettes import VersionBebeGeneree
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            VersionBebeGeneree(
                instructions_modifiees="Test",
                notes_bebe="Test",
                age_minimum_mois=3  # Minimum 6
            )


class TestVersionBatchCookingGeneree:
    """Tests schéma VersionBatchCookingGeneree."""

    def test_creation_valide(self):
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Préparer en grande quantité",
            nombre_portions_recommande=12,
            temps_preparation_total_heures=2.5,
            conseils_conservation="Conserver au frigo 5 jours",
            conseils_congelation="Se congèle bien pendant 3 mois",
            calendrier_preparation="Jour 1: préparation, Jour 2: cuisson"
        )
        
        assert version.nombre_portions_recommande == 12
        assert version.temps_preparation_total_heures == 2.5

    def test_conversion_float_portions(self):
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Test",
            nombre_portions_recommande=20.0,  # Float
            temps_preparation_total_heures=3.0,
            conseils_conservation="Test",
            conseils_congelation="Test",
            calendrier_preparation="Test"
        )
        
        assert isinstance(version.nombre_portions_recommande, int)


class TestVersionRobotGeneree:
    """Tests schéma VersionRobotGeneree."""

    def test_creation_valide(self):
        from src.services.recettes import VersionRobotGeneree
        
        version = VersionRobotGeneree(
            instructions_modifiees="Utiliser le mode sauce",
            reglages_robot="Température 100°C, vitesse 3",
            temps_cuisson_adapte_minutes=25,
            conseils_preparation="Couper les légumes en petits morceaux",
            etapes_specifiques=["Mettre tous les ingrédients", "Lancer programme sauce"]
        )
        
        assert version.temps_cuisson_adapte_minutes == 25
        assert len(version.etapes_specifiques) == 2


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE RECETTES
# ═══════════════════════════════════════════════════════════


class TestRecetteServiceInit:
    """Tests initialisation du service."""

    def test_import_service(self):
        from src.services.recettes import RecetteService
        assert RecetteService is not None

    def test_init_service(self):
        from src.services.recettes import RecetteService
        
        service = RecetteService()
        
        # Vérifier que le service est bien créé
        assert service is not None

    def test_heritage_multiple(self):
        from src.services.recettes import RecetteService
        from src.services.types import BaseService
        from src.services.base_ai_service import BaseAIService
        
        service = RecetteService()
        
        assert isinstance(service, BaseService)
        assert isinstance(service, BaseAIService)


class TestRecetteServiceMethods:
    """Tests des méthodes du service."""

    def test_service_has_crud_methods(self):
        from src.services.recettes import RecetteService
        
        service = RecetteService()
        
        # Méthodes héritées de BaseService
        assert hasattr(service, 'get_all')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'create')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')

    def test_service_has_ai_methods(self):
        from src.services.recettes import RecetteService
        
        service = RecetteService()
        
        # Méthodes héritées de BaseAIService
        assert hasattr(service, 'call_with_list_parsing_sync')
        
        # Méthodes héritées de RecipeAIMixin
        assert hasattr(service, 'build_recipe_context')


# ═══════════════════════════════════════════════════════════
# TESTS MODELS IMPORTS
# ═══════════════════════════════════════════════════════════


class TestRecettesModels:
    """Tests imports modèles DB."""

    def test_import_models(self):
        from src.core.models import (
            Recette,
            Ingredient,
            RecetteIngredient,
            EtapeRecette,
            VersionRecette,
        )
        
        assert Recette is not None
        assert Ingredient is not None
        assert RecetteIngredient is not None
        assert EtapeRecette is not None
        assert VersionRecette is not None


class TestRecettesValidators:
    """Tests validators Pydantic."""

    def test_import_validators(self):
        from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
        
        assert RecetteInput is not None
        assert IngredientInput is not None
        assert EtapeInput is not None


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestRecettesEdgeCases:
    """Tests cas limites."""

    def test_recette_temps_max(self):
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Recette longue",
            description="Une recette avec temps maximum de préparation",
            temps_preparation=300,  # Max
            temps_cuisson=300,  # Max
            difficulte="difficile",
            type_repas="plat",
            ingredients=[],
            etapes=[]
        )
        
        assert suggestion.temps_preparation == 300
        assert suggestion.temps_cuisson == 300

    def test_recette_temps_zero_cuisson(self):
        from src.services.recettes import RecetteSuggestion
        
        # Certaines recettes n'ont pas de cuisson (salades, etc.)
        suggestion = RecetteSuggestion(
            nom="Salade fraîcheur",
            description="Une salade qui ne nécessite pas de cuisson",
            temps_preparation=15,
            temps_cuisson=0,  # Pas de cuisson
            difficulte="facile",
            type_repas="entrée",
            ingredients=[],
            etapes=[]
        )
        
        assert suggestion.temps_cuisson == 0

    def test_version_bebe_age_max(self):
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Test",
            notes_bebe="Test",
            age_minimum_mois=36  # Max
        )
        
        assert version.age_minimum_mois == 36

    def test_version_batch_portions_limites(self):
        from src.services.recettes import VersionBatchCookingGeneree
        from pydantic import ValidationError
        
        # Minimum
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Test",
            nombre_portions_recommande=4,  # Min
            temps_preparation_total_heures=1.0,
            conseils_conservation="Test",
            conseils_congelation="Test",
            calendrier_preparation="Test"
        )
        assert version.nombre_portions_recommande == 4
        
        # Maximum
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Test",
            nombre_portions_recommande=100,  # Max
            temps_preparation_total_heures=1.0,
            conseils_conservation="Test",
            conseils_congelation="Test",
            calendrier_preparation="Test"
        )
        assert version.nombre_portions_recommande == 100

    def test_version_robot_temps_limites(self):
        from src.services.recettes import VersionRobotGeneree
        
        # Minimum
        version = VersionRobotGeneree(
            instructions_modifiees="Test",
            reglages_robot="Test",
            temps_cuisson_adapte_minutes=5,  # Min
            conseils_preparation="Test"
        )
        assert version.temps_cuisson_adapte_minutes == 5
        
        # Maximum
        version = VersionRobotGeneree(
            instructions_modifiees="Test",
            reglages_robot="Test",
            temps_cuisson_adapte_minutes=300,  # Max
            conseils_preparation="Test"
        )
        assert version.temps_cuisson_adapte_minutes == 300


class TestRecettesIntegration:
    """Tests d'intégration."""

    def test_workflow_suggestion_complete(self):
        from src.services.recettes import RecetteSuggestion
        
        # Créer une suggestion complète comme le ferait l'IA
        suggestion = RecetteSuggestion(
            nom="Gratin dauphinois",
            description="Le classique gratin de pommes de terre à la crème",
            temps_preparation=30,
            temps_cuisson=60,
            portions=6,
            difficulte="moyen",
            type_repas="accompagnement",
            saison="hiver",
            ingredients=[
                {"nom": "Pommes de terre", "quantite": 1, "unite": "kg"},
                {"nom": "Crème fraîche", "quantite": 30, "unite": "cl"},
                {"nom": "Ail", "quantite": 2, "unite": "gousses"},
                {"nom": "Muscade", "quantite": 1, "unite": "pincée"},
            ],
            etapes=[
                {"ordre": 1, "description": "Préchauffer le four à 180°C"},
                {"ordre": 2, "description": "Éplucher et couper les pommes de terre en rondelles"},
                {"ordre": 3, "description": "Frotter le plat avec l'ail"},
                {"ordre": 4, "description": "Disposer les pommes de terre en couches"},
                {"ordre": 5, "description": "Verser la crème et enfourner"},
            ]
        )
        
        assert len(suggestion.ingredients) == 4
        assert len(suggestion.etapes) == 5
        assert suggestion.saison == "hiver"

    def test_workflow_versions_recette(self):
        from src.services.recettes import (
            RecetteSuggestion,
            VersionBebeGeneree,
            VersionBatchCookingGeneree,
            VersionRobotGeneree
        )
        
        # Recette originale
        recette = RecetteSuggestion(
            nom="Purée de carottes",
            description="Purée de carottes maison simple et savoureuse",
            temps_preparation=15,
            temps_cuisson=20,
            difficulte="facile",
            type_repas="accompagnement",
            ingredients=[{"nom": "Carottes", "quantite": 500, "unite": "g"}],
            etapes=[{"ordre": 1, "description": "Cuire les carottes"},]
        )
        
        # Version bébé
        version_bebe = VersionBebeGeneree(
            instructions_modifiees="Mixer très finement sans sel",
            notes_bebe="Parfait pour diversification alimentaire",
            age_minimum_mois=6
        )
        
        # Version batch cooking
        version_batch = VersionBatchCookingGeneree(
            instructions_modifiees="Préparer 2kg de carottes en une fois",
            nombre_portions_recommande=16,
            temps_preparation_total_heures=1.0,
            conseils_conservation="Se conserve 5 jours au frigo",
            conseils_congelation="Congeler en portions individuelles",
            calendrier_preparation="Dimanche matin"
        )
        
        # Version robot
        version_robot = VersionRobotGeneree(
            instructions_modifiees="Utiliser le programme vapeur puis mixer",
            reglages_robot="Vapeur 20min, puis vitesse 10 pendant 30s",
            temps_cuisson_adapte_minutes=20,
            conseils_preparation="Couper en morceaux réguliers",
            etapes_specifiques=["Mettre eau dans le bol", "Ajouter carottes dans varoma"]
        )
        
        # Toutes les versions sont valides
        assert recette.nom == "Purée de carottes"
        assert version_bebe.age_minimum_mois == 6
        assert version_batch.nombre_portions_recommande == 16
        assert version_robot.temps_cuisson_adapte_minutes == 20
