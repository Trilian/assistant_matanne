"""Tests pour src/services/recettes/types.py"""

import pytest
from pydantic import ValidationError

from src.services.recettes.types import (
    BabyVersionGenerated,
    BatchCookingVersionGenerated,
    RecetteSuggestion,
    # Aliases anglais
    RecipeSuggestion,
    RobotVersionGenerated,
    VersionBatchCookingGeneree,
    VersionBebeGeneree,
    VersionRobotGeneree,
)


class TestRecetteSuggestion:
    """Tests pour RecetteSuggestion."""

    def test_valid_recette_suggestion(self):
        """Test création valide."""
        data = {
            "nom": "Poulet rôti aux herbes",
            "description": "Un délicieux poulet rôti parfait pour le dimanche",
            "temps_preparation": 15,
            "temps_cuisson": 60,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "diner",
            "saison": "toute_année",
            "ingredients": [{"nom": "poulet", "quantite": 1.5, "unite": "kg"}],
            "etapes": [{"description": "Préchauffer le four"}],
        }
        recette = RecetteSuggestion(**data)
        assert recette.nom == "Poulet rôti aux herbes"
        assert recette.temps_preparation == 15
        assert recette.temps_cuisson == 60
        assert recette.portions == 4
        assert recette.difficulte == "facile"

    def test_float_to_int_conversion(self):
        """Test conversion float->int (Mistral peut retourner 20.0)."""
        data = {
            "nom": "Test recette",
            "description": "Description test minimum",
            "temps_preparation": 20.0,  # Float
            "temps_cuisson": 30.0,  # Float
            "portions": 4.0,  # Float
            "difficulte": "moyen",
            "type_repas": "diner",
            "ingredients": [{"nom": "test", "quantite": 1, "unite": "kg"}],
            "etapes": [{"description": "Première étape"}],
        }
        recette = RecetteSuggestion(**data)
        assert recette.temps_preparation == 20
        assert isinstance(recette.temps_preparation, int)
        assert recette.temps_cuisson == 30
        assert recette.portions == 4

    def test_nom_too_short(self):
        """Test nom trop court (min 3 chars)."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="AB",  # Trop court
                description="Description suffisante",
                temps_preparation=10,
                temps_cuisson=20,
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_description_too_short(self):
        """Test description trop courte (min 10 chars)."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Recette test",
                description="Court",  # Trop court
                temps_preparation=10,
                temps_cuisson=20,
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_temps_preparation_zero_or_negative(self):
        """Test temps_preparation > 0."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Recette test",
                description="Description suffisante",
                temps_preparation=0,  # Doit être > 0
                temps_cuisson=20,
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_temps_preparation_too_high(self):
        """Test temps_preparation <= 300."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Recette test",
                description="Description suffisante",
                temps_preparation=301,  # Trop élevé
                temps_cuisson=20,
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_invalid_difficulte(self):
        """Test difficulté invalide."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Recette test",
                description="Description suffisante",
                temps_preparation=10,
                temps_cuisson=20,
                difficulte="très_difficile",  # Invalide
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_portions_zero(self):
        """Test portions > 0."""
        with pytest.raises(ValidationError):
            RecetteSuggestion(
                nom="Recette test",
                description="Description suffisante",
                temps_preparation=10,
                temps_cuisson=20,
                portions=0,
                type_repas="diner",
                ingredients=[],
                etapes=[],
            )

    def test_default_values(self):
        """Test valeurs par défaut."""
        data = {
            "nom": "Recette simple",
            "description": "Description suffisante pour le test",
            "temps_preparation": 10,
            "temps_cuisson": 0,
            "type_repas": "diner",
            "ingredients": [],
            "etapes": [],
        }
        recette = RecetteSuggestion(**data)
        assert recette.portions == 4
        assert recette.difficulte == "moyen"
        assert recette.saison == "toute_année"


class TestVersionBebeGeneree:
    """Tests pour VersionBebeGeneree."""

    def test_valid_version_bebe(self):
        """Test création valide."""
        version = VersionBebeGeneree(
            instructions_modifiees="Cuire jusqu'à très tendre",
            notes_bebe="Éviter le sel, mixer si nécessaire",
            age_minimum_mois=12,
        )
        assert version.instructions_modifiees == "Cuire jusqu'à très tendre"
        assert version.age_minimum_mois == 12

    def test_default_age(self):
        """Test âge par défaut (6 mois)."""
        version = VersionBebeGeneree(
            instructions_modifiees="Instructions",
            notes_bebe="Notes bébé",
        )
        assert version.age_minimum_mois == 6

    def test_float_age_conversion(self):
        """Test conversion float->int pour l'âge."""
        version = VersionBebeGeneree(
            instructions_modifiees="Instructions",
            notes_bebe="Notes",
            age_minimum_mois=12.0,  # Float
        )
        assert version.age_minimum_mois == 12
        assert isinstance(version.age_minimum_mois, int)

    def test_age_too_low(self):
        """Test âge minimum >= 6."""
        with pytest.raises(ValidationError):
            VersionBebeGeneree(
                instructions_modifiees="Instructions",
                notes_bebe="Notes",
                age_minimum_mois=4,  # Trop bas
            )

    def test_age_too_high(self):
        """Test âge maximum <= 36."""
        with pytest.raises(ValidationError):
            VersionBebeGeneree(
                instructions_modifiees="Instructions",
                notes_bebe="Notes",
                age_minimum_mois=40,  # Trop élevé
            )


class TestVersionBatchCookingGeneree:
    """Tests pour VersionBatchCookingGeneree."""

    def test_valid_version_batch(self):
        """Test création valide."""
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Préparer en grande quantité",
            nombre_portions_recommande=12,
            temps_preparation_total_heures=2.5,
            conseils_conservation="Réfrigérateur 5 jours",
            conseils_congelation="Jusqu'à 3 mois",
            calendrier_preparation="Dimanche: préparation",
        )
        assert version.nombre_portions_recommande == 12
        assert version.temps_preparation_total_heures == 2.5

    def test_default_values(self):
        """Test valeurs par défaut."""
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Instructions",
            conseils_conservation="Conservation",
            conseils_congelation="Congélation",
            calendrier_preparation="Calendrier",
        )
        assert version.nombre_portions_recommande == 12
        assert version.temps_preparation_total_heures == 2.0

    def test_float_portions_conversion(self):
        """Test conversion float->int pour portions."""
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Instructions",
            nombre_portions_recommande=20.0,  # Float
            conseils_conservation="Conservation",
            conseils_congelation="Congélation",
            calendrier_preparation="Calendrier",
        )
        assert version.nombre_portions_recommande == 20
        assert isinstance(version.nombre_portions_recommande, int)

    def test_portions_too_low(self):
        """Test portions >= 4."""
        with pytest.raises(ValidationError):
            VersionBatchCookingGeneree(
                instructions_modifiees="Instructions",
                nombre_portions_recommande=2,  # Trop bas
                conseils_conservation="Conservation",
                conseils_congelation="Congélation",
                calendrier_preparation="Calendrier",
            )

    def test_temps_too_low(self):
        """Test temps >= 0.5h."""
        with pytest.raises(ValidationError):
            VersionBatchCookingGeneree(
                instructions_modifiees="Instructions",
                temps_preparation_total_heures=0.1,  # Trop bas
                conseils_conservation="Conservation",
                conseils_congelation="Congélation",
                calendrier_preparation="Calendrier",
            )


class TestVersionRobotGeneree:
    """Tests pour VersionRobotGeneree."""

    def test_valid_version_robot(self):
        """Test création valide."""
        version = VersionRobotGeneree(
            instructions_modifiees="Utiliser le mode pressure",
            reglages_robot="Mode haute pression 15 min",
            temps_cuisson_adapte_minutes=45,
            conseils_preparation="Couper en petits morceaux",
            etapes_specifiques=["Préchauffer", "Ajouter ingrédients"],
        )
        assert version.temps_cuisson_adapte_minutes == 45
        assert len(version.etapes_specifiques) == 2

    def test_default_values(self):
        """Test valeurs par défaut."""
        version = VersionRobotGeneree(
            instructions_modifiees="Instructions",
            reglages_robot="Réglages",
            conseils_preparation="Conseils",
        )
        assert version.temps_cuisson_adapte_minutes == 30
        assert version.etapes_specifiques == []

    def test_float_temps_conversion(self):
        """Test conversion float->int pour temps."""
        version = VersionRobotGeneree(
            instructions_modifiees="Instructions",
            reglages_robot="Réglages",
            conseils_preparation="Conseils",
            temps_cuisson_adapte_minutes=60.0,  # Float
        )
        assert version.temps_cuisson_adapte_minutes == 60
        assert isinstance(version.temps_cuisson_adapte_minutes, int)

    def test_temps_too_low(self):
        """Test temps >= 5."""
        with pytest.raises(ValidationError):
            VersionRobotGeneree(
                instructions_modifiees="Instructions",
                reglages_robot="Réglages",
                conseils_preparation="Conseils",
                temps_cuisson_adapte_minutes=3,  # Trop bas
            )

    def test_temps_too_high(self):
        """Test temps <= 300."""
        with pytest.raises(ValidationError):
            VersionRobotGeneree(
                instructions_modifiees="Instructions",
                reglages_robot="Réglages",
                conseils_preparation="Conseils",
                temps_cuisson_adapte_minutes=350,  # Trop élevé
            )


class TestAliasesAnglais:
    """Tests pour les aliases anglais."""

    def test_recipe_suggestion_is_alias(self):
        """Test que RecipeSuggestion est un alias."""
        assert RecipeSuggestion is RecetteSuggestion

    def test_baby_version_is_alias(self):
        """Test que BabyVersionGenerated est un alias."""
        assert BabyVersionGenerated is VersionBebeGeneree

    def test_batch_cooking_is_alias(self):
        """Test que BatchCookingVersionGenerated est un alias."""
        assert BatchCookingVersionGenerated is VersionBatchCookingGeneree

    def test_robot_version_is_alias(self):
        """Test que RobotVersionGenerated est un alias."""
        assert RobotVersionGenerated is VersionRobotGeneree
