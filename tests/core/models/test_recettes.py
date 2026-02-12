"""
Tests unitaires pour recettes.py

Module: src.core.models.recettes
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timedelta

from src.core.models.recettes import (
    Ingredient,
    Recette,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    HistoriqueRecette,
    BatchMeal,
    Recipe,
)


@pytest.mark.unit
class TestIngredient:
    """Tests pour la classe Ingredient."""

    def test_ingredient_tablename(self):
        """Test du nom de table."""
        assert Ingredient.__tablename__ == "ingredients"

    def test_ingredient_creation(self):
        """Test de création de Ingredient."""
        ingredient = Ingredient(
            id=1,
            nom="Tomate",
            categorie="légumes",
            unite="kg",
        )
        
        assert ingredient.id == 1
        assert ingredient.nom == "Tomate"
        assert ingredient.categorie == "légumes"
        assert ingredient.unite == "kg"

    def test_ingredient_repr(self):
        """Test de la représentation string."""
        ingredient = Ingredient(id=1, nom="Carotte")
        
        repr_str = repr(ingredient)
        assert "Ingredient" in repr_str
        assert "Carotte" in repr_str
        assert "1" in repr_str

    def test_ingredient_default_unite(self):
        """Test valeur par défaut de l'unité."""
        # Check column default, not instance value
        unite_col = Ingredient.__table__.c.unite
        assert unite_col.default.arg == "pcs"


@pytest.mark.unit
class TestRecette:
    """Tests pour la classe Recette."""

    def test_recette_tablename(self):
        """Test du nom de table."""
        assert Recette.__tablename__ == "recettes"

    def test_recette_creation(self):
        """Test de création de Recette."""
        recette = Recette(
            id=1,
            nom="Tarte aux pommes",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            difficulte="facile",
        )
        
        assert recette.id == 1
        assert recette.nom == "Tarte aux pommes"
        assert recette.temps_preparation == 30
        assert recette.temps_cuisson == 45
        assert recette.portions == 8
        assert recette.difficulte == "facile"

    def test_recette_repr(self):
        """Test de la représentation string."""
        recette = Recette(id=1, nom="Quiche lorraine", temps_preparation=20)
        
        repr_str = repr(recette)
        assert "Recette" in repr_str
        assert "Quiche lorraine" in repr_str

    def test_recette_temps_total_property(self):
        """Test propriété temps_total."""
        recette = Recette(
            nom="Test",
            temps_preparation=15,
            temps_cuisson=30,
        )
        
        assert recette.temps_total == 45

    def test_recette_temps_total_no_cuisson(self):
        """Test temps_total sans cuisson."""
        recette = Recette(
            nom="Salade",
            temps_preparation=10,
            temps_cuisson=0,
        )
        
        assert recette.temps_total == 10

    def test_recette_robots_compatibles_empty(self):
        """Test robots_compatibles quand aucun robot."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            compatible_cookeo=False,
            compatible_monsieur_cuisine=False,
            compatible_airfryer=False,
            compatible_multicooker=False,
        )
        
        assert recette.robots_compatibles == []

    def test_recette_robots_compatibles_all(self):
        """Test robots_compatibles avec tous les robots."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            compatible_cookeo=True,
            compatible_monsieur_cuisine=True,
            compatible_airfryer=True,
            compatible_multicooker=True,
        )
        
        robots = recette.robots_compatibles
        assert "Cookeo" in robots
        assert "Monsieur Cuisine" in robots
        assert "Airfryer" in robots
        assert "Multicooker" in robots
        assert len(robots) == 4

    def test_recette_robots_compatibles_partial(self):
        """Test robots_compatibles avec quelques robots."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            compatible_cookeo=True,
            compatible_airfryer=True,
            compatible_monsieur_cuisine=False,
            compatible_multicooker=False,
        )
        
        robots = recette.robots_compatibles
        assert "Cookeo" in robots
        assert "Airfryer" in robots
        assert "Monsieur Cuisine" not in robots
        assert len(robots) == 2

    def test_recette_tags_empty(self):
        """Test tags quand aucun tag actif."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            est_rapide=False,
            est_equilibre=False,
            compatible_bebe=False,
            compatible_batch=False,
            congelable=False,
            est_bio=False,
            est_local=False,
        )
        
        assert recette.tags == []

    def test_recette_tags_all(self):
        """Test tags avec tous les flags actifs."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            est_rapide=True,
            est_equilibre=True,
            compatible_bebe=True,
            compatible_batch=True,
            congelable=True,
            est_bio=True,
            est_local=True,
        )
        
        tags = recette.tags
        assert "rapide" in tags
        assert "équilibré" in tags
        assert "bébé" in tags
        assert "batch" in tags
        assert "congélation" in tags
        assert "bio" in tags
        assert "local" in tags
        assert len(tags) == 7

    def test_recette_tags_partial(self):
        """Test tags avec quelques flags."""
        recette = Recette(
            nom="Test",
            temps_preparation=10,
            est_rapide=True,
            est_bio=True,
            est_equilibre=False,
            compatible_bebe=False,
            compatible_batch=False,
            congelable=False,
            est_local=False,
        )
        
        tags = recette.tags
        assert "rapide" in tags
        assert "bio" in tags
        assert "équilibré" not in tags
        assert len(tags) == 2

    def test_recipe_alias(self):
        """Test que Recipe est un alias de Recette."""
        assert Recipe is Recette


@pytest.mark.unit
class TestRecetteIngredient:
    """Tests pour la classe RecetteIngredient."""

    def test_recetteingredient_tablename(self):
        """Test du nom de table."""
        assert RecetteIngredient.__tablename__ == "recette_ingredients"

    def test_recetteingredient_creation(self):
        """Test de création."""
        ri = RecetteIngredient(
            id=1,
            recette_id=1,
            ingredient_id=2,
            quantite=200.0,
            unite="g",
            optionnel=False,
        )
        
        assert ri.recette_id == 1
        assert ri.ingredient_id == 2
        assert ri.quantite == 200.0
        assert ri.unite == "g"
        assert ri.optionnel is False

    def test_recetteingredient_repr(self):
        """Test de la représentation string."""
        ri = RecetteIngredient(id=1, recette_id=1, ingredient_id=2, quantite=100.0, unite="g")
        
        repr_str = repr(ri)
        assert "RecetteIngredient" in repr_str


@pytest.mark.unit
class TestEtapeRecette:
    """Tests pour la classe EtapeRecette."""

    def test_etaperecette_tablename(self):
        """Test du nom de table."""
        assert EtapeRecette.__tablename__ == "etapes_recette"

    def test_etaperecette_creation(self):
        """Test de création."""
        etape = EtapeRecette(
            id=1,
            recette_id=1,
            ordre=1,
            description="Préchauffer le four Ã  180Â°C",
            duree=5,
        )
        
        assert etape.ordre == 1
        assert etape.description == "Préchauffer le four Ã  180Â°C"
        assert etape.duree == 5

    def test_etaperecette_repr(self):
        """Test de la représentation string."""
        etape = EtapeRecette(id=1, recette_id=1, ordre=2, description="Mélanger")
        
        repr_str = repr(etape)
        assert "EtapeRecette" in repr_str
        assert "2" in repr_str  # ordre


@pytest.mark.unit
class TestVersionRecette:
    """Tests pour la classe VersionRecette."""

    def test_versionrecette_tablename(self):
        """Test du nom de table."""
        assert VersionRecette.__tablename__ == "versions_recette"

    def test_versionrecette_creation(self):
        """Test de création."""
        version = VersionRecette(
            id=1,
            recette_base_id=1,
            type_version="bébé",
            instructions_modifiees="Mixer finement",
            notes_bebe="Adapté pour 12 mois+",
        )
        
        assert version.type_version == "bébé"
        assert version.notes_bebe == "Adapté pour 12 mois+"

    def test_versionrecette_repr(self):
        """Test de la représentation string."""
        version = VersionRecette(id=1, recette_base_id=1, type_version="batch_cooking")
        
        repr_str = repr(version)
        assert "VersionRecette" in repr_str
        assert "batch_cooking" in repr_str


@pytest.mark.unit
class TestHistoriqueRecette:
    """Tests pour la classe HistoriqueRecette."""

    def test_historiquerecette_tablename(self):
        """Test du nom de table."""
        assert HistoriqueRecette.__tablename__ == "historique_recettes"

    def test_historiquerecette_creation(self):
        """Test de création."""
        hist = HistoriqueRecette(
            id=1,
            recette_id=1,
            date_cuisson=date(2024, 1, 15),
            portions_cuisinees=4,
            note=5,
            avis="Excellent!",
        )
        
        assert hist.date_cuisson == date(2024, 1, 15)
        assert hist.note == 5
        assert hist.avis == "Excellent!"

    def test_historiquerecette_repr(self):
        """Test de la représentation string."""
        hist = HistoriqueRecette(
            id=1,
            recette_id=1,
            date_cuisson=date(2024, 1, 15),
            note=4,
        )
        
        repr_str = repr(hist)
        assert "HistoriqueRecette" in repr_str
        assert "2024-01-15" in repr_str

    def test_historiquerecette_nb_jours_depuis(self):
        """Test propriété nb_jours_depuis."""
        yesterday = date.today() - timedelta(days=1)
        hist = HistoriqueRecette(
            id=1,
            recette_id=1,
            date_cuisson=yesterday,
        )
        
        assert hist.nb_jours_depuis == 1

    def test_historiquerecette_nb_jours_depuis_today(self):
        """Test nb_jours_depuis pour aujourd'hui."""
        today = date.today()
        hist = HistoriqueRecette(
            id=1,
            recette_id=1,
            date_cuisson=today,
        )
        
        assert hist.nb_jours_depuis == 0

    def test_historiquerecette_nb_jours_depuis_week_ago(self):
        """Test nb_jours_depuis pour il y a une semaine."""
        week_ago = date.today() - timedelta(days=7)
        hist = HistoriqueRecette(
            id=1,
            recette_id=1,
            date_cuisson=week_ago,
        )
        
        assert hist.nb_jours_depuis == 7


@pytest.mark.unit
class TestBatchMeal:
    """Tests pour la classe BatchMeal."""

    def test_batchmeal_tablename(self):
        """Test du nom de table."""
        assert BatchMeal.__tablename__ == "batch_meals"

    def test_batchmeal_creation(self):
        """Test de création."""
        batch = BatchMeal(
            id=1,
            nom="Bolognaise",
            portions_creees=8,
            portions_restantes=6,
            date_preparation=date(2024, 1, 15),
            date_peremption=date(2024, 1, 20),
            localisation="Congélateur",
        )
        
        assert batch.nom == "Bolognaise"
        assert batch.portions_creees == 8
        assert batch.portions_restantes == 6
        assert batch.localisation == "Congélateur"

    def test_batchmeal_repr(self):
        """Test de la représentation string."""
        batch = BatchMeal(
            id=1,
            nom="Ratatouille",
            portions_creees=4,
            portions_restantes=2,
            date_preparation=date.today(),
            date_peremption=date.today() + timedelta(days=5),
        )
        
        repr_str = repr(batch)
        assert "BatchMeal" in repr_str
        assert "Ratatouille" in repr_str
        assert "2" in repr_str  # portions_restantes

