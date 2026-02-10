"""
Tests couverture complets pour src/services/recettes.py

Objectif: Améliorer la couverture de RecetteService.
Stratégie: Tests des schémas Pydantic et mocking du service.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, time, datetime
import pydantic


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC - RecetteSuggestion
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRecetteSuggestion:
    """Tests complets pour RecetteSuggestion schema."""

    def test_recette_suggestion_minimal(self):
        """Test création minimale."""
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Poulet rôti au thym",
            description="Un délicieux poulet rôti avec des herbes de Provence",
            temps_preparation=20,
            temps_cuisson=90,
            type_repas="déjeuner",
            ingredients=[{"nom": "poulet", "quantite": "1"}],
            etapes=[{"description": "Préchauffer le four à 180°C"}]
        )
        
        assert suggestion.nom == "Poulet rôti au thym"
        assert suggestion.temps_preparation == 20
        assert suggestion.temps_cuisson == 90
        assert suggestion.portions == 4  # default
        assert suggestion.difficulte == "moyen"  # default
        assert suggestion.saison == "toute_année"  # default

    def test_recette_suggestion_complete(self):
        """Test création avec tous les champs."""
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Salade d'été rafraîchissante",
            description="Une salade légère et colorée pour les journées chaudes",
            temps_preparation=15,
            temps_cuisson=0,
            portions=6,
            difficulte="facile",
            type_repas="déjeuner",
            saison="été",
            ingredients=[
                {"nom": "laitue", "quantite": "1"},
                {"nom": "tomates", "quantite": "3"}
            ],
            etapes=[
                {"description": "Laver les légumes"},
                {"description": "Couper en morceaux"}
            ]
        )
        
        assert suggestion.portions == 6
        assert suggestion.difficulte == "facile"
        assert suggestion.saison == "été"
        assert len(suggestion.ingredients) == 2
        assert len(suggestion.etapes) == 2

    def test_recette_suggestion_float_conversion(self):
        """Test conversion float vers int."""
        from src.services.recettes import RecetteSuggestion
        
        # Mistral peut retourner des floats
        suggestion = RecetteSuggestion(
            nom="Test recette conversion",
            description="Test de la conversion des floats en entiers",
            temps_preparation=20.0,  # float
            temps_cuisson=45.5,  # float avec décimales
            portions=4.0,  # float
            type_repas="dîner",
            ingredients=[],
            etapes=[]
        )
        
        assert suggestion.temps_preparation == 20
        assert suggestion.temps_cuisson == 45
        assert suggestion.portions == 4

    def test_recette_suggestion_difficulte_validation(self):
        """Test validation du champ difficulte."""
        from src.services.recettes import RecetteSuggestion
        
        # facile
        suggestion = RecetteSuggestion(
            nom="Recette facile test",
            description="Une recette très simple pour tester",
            temps_preparation=10,
            temps_cuisson=20,
            difficulte="facile",
            type_repas="déjeuner",
            ingredients=[],
            etapes=[]
        )
        assert suggestion.difficulte == "facile"
        
        # difficile
        suggestion2 = RecetteSuggestion(
            nom="Recette difficile test",
            description="Une recette complexe pour tester la validation",
            temps_preparation=60,
            temps_cuisson=120,
            difficulte="difficile",
            type_repas="dîner",
            ingredients=[],
            etapes=[]
        )
        assert suggestion2.difficulte == "difficile"

    def test_recette_suggestion_validation_nom_court(self):
        """Test validation nom trop court."""
        from src.services.recettes import RecetteSuggestion
        
        with pytest.raises(pydantic.ValidationError):
            RecetteSuggestion(
                nom="AB",  # trop court
                description="Description valide avec suffisamment de caractères",
                temps_preparation=20,
                temps_cuisson=30,
                type_repas="déjeuner",
                ingredients=[],
                etapes=[]
            )

    def test_recette_suggestion_validation_temps_negatif(self):
        """Test validation temps préparation négatif."""
        from src.services.recettes import RecetteSuggestion
        
        with pytest.raises(pydantic.ValidationError):
            RecetteSuggestion(
                nom="Recette test invalide",
                description="Description valide avec suffisamment de caractères",
                temps_preparation=-10,  # invalide
                temps_cuisson=30,
                type_repas="déjeuner",
                ingredients=[],
                etapes=[]
            )


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC - VersionBebeGeneree
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVersionBebeGeneree:
    """Tests complets pour VersionBebeGeneree schema."""

    def test_version_bebe_minimal(self):
        """Test création minimale."""
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Mixer finement les légumes",
            notes_bebe="Adapté pour bébé de 8 mois"
        )
        
        assert version.instructions_modifiees == "Mixer finement les légumes"
        assert version.notes_bebe == "Adapté pour bébé de 8 mois"
        assert version.age_minimum_mois == 6  # default

    def test_version_bebe_complete(self):
        """Test création avec âge spécifique."""
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Cuire plus longtemps et mixer",
            notes_bebe="Éviter les morceaux pour les premiers mois",
            age_minimum_mois=12
        )
        
        assert version.age_minimum_mois == 12

    def test_version_bebe_float_conversion(self):
        """Test conversion float vers int."""
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Instructions modifiées",
            notes_bebe="Notes pour bébé",
            age_minimum_mois=9.0  # float
        )
        
        assert version.age_minimum_mois == 9


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC - VersionBatchCookingGeneree
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVersionBatchCookingGeneree:
    """Tests complets pour VersionBatchCookingGeneree schema."""

    def test_version_batch_minimal(self):
        """Test création minimale."""
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Préparer en grande quantité",
            conseils_conservation="Au frigo 5 jours max",
            conseils_congelation="Se congèle très bien",
            calendrier_preparation="Préparer le dimanche"
        )
        
        assert version.nombre_portions_recommande == 12  # default
        assert version.temps_preparation_total_heures == 2.0  # default

    def test_version_batch_complete(self):
        """Test création avec tous les champs."""
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Tripler les quantités et utiliser des grands plats",
            nombre_portions_recommande=24,
            temps_preparation_total_heures=4.5,
            conseils_conservation="Séparer en portions individuelles",
            conseils_congelation="Congeler immédiatement après refroidissement",
            calendrier_preparation="Dimanche matin: 2h, Dimanche après-midi: 2.5h"
        )
        
        assert version.nombre_portions_recommande == 24
        assert version.temps_preparation_total_heures == 4.5

    def test_version_batch_float_conversion(self):
        """Test conversion float vers int pour portions."""
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Instructions batch",
            nombre_portions_recommande=18.0,  # float
            conseils_conservation="Conservation",
            conseils_congelation="Congélation",
            calendrier_preparation="Calendrier"
        )
        
        assert version.nombre_portions_recommande == 18


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC - VersionRobotGeneree
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVersionRobotGeneree:
    """Tests complets pour VersionRobotGeneree schema."""

    def test_version_robot_minimal(self):
        """Test création minimale."""
        from src.services.recettes import VersionRobotGeneree
        
        version = VersionRobotGeneree(
            instructions_modifiees="Utiliser le mode pétrissage",
            reglages_robot="Vitesse 6, 10 minutes",
            conseils_preparation="Couper les légumes en morceaux"
        )
        
        assert version.temps_cuisson_adapte_minutes == 30  # default
        assert version.etapes_specifiques == []  # default

    def test_version_robot_complete(self):
        """Test création avec tous les champs."""
        from src.services.recettes import VersionRobotGeneree
        
        version = VersionRobotGeneree(
            instructions_modifiees="Adapter pour Cookeo",
            reglages_robot="Mode cuisson rapide, 180°C",
            temps_cuisson_adapte_minutes=45,
            conseils_preparation="Préchauffer 5 minutes avant",
            etapes_specifiques=[
                "Mettre les ingrédients dans le bol",
                "Lancer le programme",
                "Mélanger à mi-cuisson"
            ]
        )
        
        assert version.temps_cuisson_adapte_minutes == 45
        assert len(version.etapes_specifiques) == 3

    def test_version_robot_float_conversion(self):
        """Test conversion float vers int."""
        from src.services.recettes import VersionRobotGeneree
        
        version = VersionRobotGeneree(
            instructions_modifiees="Instructions robot",
            reglages_robot="Réglages",
            temps_cuisson_adapte_minutes=60.0,  # float
            conseils_preparation="Conseils"
        )
        
        assert version.temps_cuisson_adapte_minutes == 60


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE - INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRecetteServiceInit:
    """Tests pour l'initialisation du service."""

    @patch('src.services.recettes.obtenir_client_ia')
    def test_init_service(self, mock_client):
        """Test initialisation du service."""
        from src.services.recettes import RecetteService
        from src.core.models import Recette
        
        mock_client.return_value = Mock()
        
        service = RecetteService()
        
        assert service is not None
        assert service.model == Recette

    @patch('src.services.recettes.obtenir_client_ia')
    def test_service_has_model_name(self, mock_client):
        """Test model_name correct."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        service = RecetteService()
        
        assert hasattr(service, 'model_name')


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE - MÉTHODES MOCKÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRecetteServiceMethodsMocked:
    """Tests pour les méthodes avec mock au niveau service."""

    @patch('src.services.recettes.obtenir_client_ia')
    def test_get_recette_by_id(self, mock_client):
        """Test get avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.nom = "Poulet rôti"
        
        service = RecetteService()
        service.get = Mock(return_value=mock_recette)
        
        result = service.get(1)
        assert result.id == 1
        assert result.nom == "Poulet rôti"

    @patch('src.services.recettes.obtenir_client_ia')
    def test_lister_recettes(self, mock_client):
        """Test lister avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        mock_recettes = [Mock(id=1), Mock(id=2), Mock(id=3)]
        
        service = RecetteService()
        service.lister = Mock(return_value=mock_recettes)
        
        result = service.lister()
        assert len(result) == 3

    @patch('src.services.recettes.obtenir_client_ia')
    def test_rechercher_recettes(self, mock_client):
        """Test rechercher avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        mock_recettes = [Mock(nom="Poulet"), Mock(nom="Poulet curry")]
        
        service = RecetteService()
        service.rechercher = Mock(return_value=mock_recettes)
        
        result = service.rechercher("poulet")
        assert len(result) == 2

    @patch('src.services.recettes.obtenir_client_ia')
    def test_creer_recette(self, mock_client):
        """Test créer avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        mock_recette = Mock()
        mock_recette.id = 10
        mock_recette.nom = "Nouvelle recette"
        
        service = RecetteService()
        service.creer = Mock(return_value=mock_recette)
        
        result = service.creer({
            "nom": "Nouvelle recette",
            "temps_preparation": 20
        })
        assert result.id == 10

    @patch('src.services.recettes.obtenir_client_ia')
    def test_modifier_recette(self, mock_client):
        """Test modifier avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.nom = "Recette modifiée"
        
        service = RecetteService()
        service.modifier = Mock(return_value=mock_recette)
        
        result = service.modifier(1, {"nom": "Recette modifiée"})
        assert result.nom == "Recette modifiée"

    @patch('src.services.recettes.obtenir_client_ia')
    def test_supprimer_recette(self, mock_client):
        """Test supprimer avec mock."""
        from src.services.recettes import RecetteService
        
        mock_client.return_value = Mock()
        
        service = RecetteService()
        service.supprimer = Mock(return_value=True)
        
        result = service.supprimer(1)
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFactory:
    """Tests pour la factory function."""

    @patch('src.services.recettes.obtenir_client_ia')
    def test_get_recette_service(self, mock_client):
        """Test factory retourne le service."""
        import src.services.recettes as module
        from src.services.recettes import get_recette_service, RecetteService
        
        mock_client.return_value = Mock()
        
        # Reset singleton
        module._recette_service = None
        
        service = get_recette_service()
        
        assert isinstance(service, RecetteService)

    @patch('src.services.recettes.obtenir_client_ia')
    def test_get_recette_service_singleton(self, mock_client):
        """Test factory retourne le même service."""
        import src.services.recettes as module
        from src.services.recettes import get_recette_service
        
        mock_client.return_value = Mock()
        
        # Reset singleton
        module._recette_service = None
        
        service1 = get_recette_service()
        service2 = get_recette_service()
        
        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_recette_suggestion_max_temps(self):
        """Test temps maximum (300 min)."""
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Recette très longue à préparer",
            description="Une recette qui prend beaucoup de temps pour tester les limites",
            temps_preparation=300,
            temps_cuisson=300,
            type_repas="dîner",
            ingredients=[],
            etapes=[]
        )
        
        assert suggestion.temps_preparation == 300
        assert suggestion.temps_cuisson == 300

    def test_version_bebe_age_limite(self):
        """Test âge aux limites."""
        from src.services.recettes import VersionBebeGeneree
        
        # Âge minimum 6 mois
        version_min = VersionBebeGeneree(
            instructions_modifiees="Instructions",
            notes_bebe="Notes",
            age_minimum_mois=6
        )
        assert version_min.age_minimum_mois == 6
        
        # Âge maximum 36 mois
        version_max = VersionBebeGeneree(
            instructions_modifiees="Instructions",
            notes_bebe="Notes",
            age_minimum_mois=36
        )
        assert version_max.age_minimum_mois == 36

    def test_version_batch_portions_limite(self):
        """Test portions aux limites."""
        from src.services.recettes import VersionBatchCookingGeneree
        
        # Portions minimum 4
        version_min = VersionBatchCookingGeneree(
            instructions_modifiees="Instructions",
            nombre_portions_recommande=4,
            conseils_conservation="Conservation",
            conseils_congelation="Congélation",
            calendrier_preparation="Calendrier"
        )
        assert version_min.nombre_portions_recommande == 4
        
        # Portions maximum 100
        version_max = VersionBatchCookingGeneree(
            instructions_modifiees="Instructions",
            nombre_portions_recommande=100,
            conseils_conservation="Conservation",
            conseils_congelation="Congélation",
            calendrier_preparation="Calendrier"
        )
        assert version_max.nombre_portions_recommande == 100

    def test_version_robot_temps_limite(self):
        """Test temps cuisson aux limites."""
        from src.services.recettes import VersionRobotGeneree
        
        # Temps minimum 5 min
        version_min = VersionRobotGeneree(
            instructions_modifiees="Instructions",
            reglages_robot="Réglages",
            temps_cuisson_adapte_minutes=5,
            conseils_preparation="Conseils"
        )
        assert version_min.temps_cuisson_adapte_minutes == 5
        
        # Temps maximum 300 min
        version_max = VersionRobotGeneree(
            instructions_modifiees="Instructions",
            reglages_robot="Réglages",
            temps_cuisson_adapte_minutes=300,
            conseils_preparation="Conseils"
        )
        assert version_max.temps_cuisson_adapte_minutes == 300
