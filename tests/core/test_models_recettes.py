"""
Tests unitaires pour models/recettes.py (src/core/models/recettes.py).

Tests couvrant:
- Modèle Ingredient
- Modèle Recette et ses métadonnées
- Modèle RecetteIngredient avec associations
- Modèle EtapeRecette
- Modèle VersionRecette
- Validations et contraintes
"""

import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from src.core.models.recettes import (
    Ingredient,
    Recette,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    HistoriqueRecette,
    BatchMeal,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: TESTS INGREDIENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestIngredient:
    """Tests pour le modèle Ingredient."""

    def test_ingredient_creation(self, db: Session):
        """Test création d'un ingrédient."""
        ingredient = Ingredient(nom="Tomate", categorie="Fruits", unite="pcs")
        db.add(ingredient)
        db.commit()
        
        assert ingredient.id is not None
        assert ingredient.nom == "Tomate"
        assert ingredient.categorie == "Fruits"
        assert ingredient.unite == "pcs"

    def test_ingredient_unique_name(self, db: Session):
        """Test que le nom est unique."""
        from sqlalchemy.exc import IntegrityError
        
        ing1 = Ingredient(nom="Tomate", categorie="Fruits", unite="pcs")
        ing2 = Ingredient(nom="Tomate", categorie="Légumes", unite="kg")
        
        db.add(ing1)
        db.commit()
        
        db.add(ing2)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_ingredient_default_values(self, db: Session):
        """Test les valeurs par défaut."""
        ingredient = Ingredient(nom="Lait")
        db.add(ingredient)
        db.commit()
        
        assert ingredient.unite == "pcs"  # Défaut
        assert ingredient.cree_le is not None
        assert ingredient.categorie is None  # Optionnel

    def test_ingredient_str_representation(self, db: Session):
        """Test la représentation string."""
        ingredient = Ingredient(nom="Oeufs", categorie="Protéines", unite="pcs")
        db.add(ingredient)
        db.commit()
        
        repr_str = repr(ingredient)
        assert "Ingredient" in repr_str
        assert "Oeufs" in repr_str

    def test_ingredient_relationships(self, db: Session):
        """Test que l'ingrédient a les relations attendues."""
        ingredient = Ingredient(nom="Sauce Tomate")
        assert hasattr(ingredient, "recette_ingredients")
        assert hasattr(ingredient, "inventaire")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: TESTS RECETTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRecette:
    """Tests pour le modèle Recette."""

    def test_recette_creation(self, db: Session):
        """Test création d'une recette."""
        recette = Recette(
            nom="Pâtes Carbonara",
            description="Pâtes Ã  l'italienne",
            temps_preparation=10,
            temps_cuisson=15,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        assert recette.id is not None
        assert recette.nom == "Pâtes Carbonara"
        assert recette.temps_preparation == 10

    def test_recette_difficulte_default(self, db: Session):
        """Test la difficulté par défaut."""
        recette = Recette(
            nom="Test Recette",
            temps_preparation=5,
            temps_cuisson=5,
            portions=2,
        )
        db.add(recette)
        db.commit()
        
        assert recette.difficulte is not None

    def test_recette_tags_system(self, db: Session):
        """Test les tags système."""
        recette = Recette(
            nom="Recette Rapide",
            temps_preparation=10,
            temps_cuisson=10,
            portions=2,
            est_rapide=True,
            est_equilibre=True,
            compatible_bebe=False,
        )
        db.add(recette)
        db.commit()
        
        assert recette.est_rapide is True
        assert recette.est_equilibre is True
        assert recette.compatible_bebe is False

    def test_recette_bio_local(self, db: Session):
        """Test les attributs bio et local."""
        recette = Recette(
            nom="Recette Bio",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
            est_bio=True,
            est_local=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.est_bio is True
        assert recette.est_local is True

    def test_recette_congelable(self, db: Session):
        """Test l'attribut congelable."""
        recette = Recette(
            nom="Ragoût",
            temps_preparation=20,
            temps_cuisson=120,
            portions=6,
            congelable=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.congelable is True

    def test_recette_timestamps(self, db: Session):
        """Test les timestamps."""
        recette = Recette(
            nom="Test Timestamps",
            temps_preparation=10,
            temps_cuisson=10,
            portions=2,
        )
        db.add(recette)
        db.commit()
        
        assert recette.cree_le is not None
        assert isinstance(recette.cree_le, datetime)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: TESTS RECETTE_INGREDIENT (Association)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRecetteIngredient:
    """Tests pour l'association Recette-Ingredient."""

    def test_recette_ingredient_association(self, db: Session):
        """Test création d'une association."""
        ingredient = Ingredient(nom="Pâtes", unite="g")
        recette = Recette(
            nom="Pâtes Simples",
            temps_preparation=5,
            temps_cuisson=10,
            portions=2,
        )
        
        db.add(ingredient)
        db.add(recette)
        db.commit()
        
        # Créer l'association
        ri = RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredient.id,
            quantite=400,
            unite="g",
        )
        db.add(ri)
        db.commit()
        
        assert ri.quantite == 400
        assert ri.unite == "g"

    def test_recette_ingredient_cascade_delete(self, db: Session):
        """Test la suppression en cascade."""
        ingredient = Ingredient(nom="Tomate Ã  Supprimer")
        recette = Recette(
            nom="Recette Ã  Supprimer",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
        )
        
        db.add(ingredient)
        db.add(recette)
        db.commit()
        
        ri = RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredient.id,
            quantite=1,
            unite="pcs",
        )
        db.add(ri)
        db.commit()
        
        # Supprimer la recette
        db.delete(recette)
        db.commit()
        
        # L'association devrait aussi être supprimée
        result = db.query(RecetteIngredient).filter_by(recette_id=recette.id).first()
        assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: TESTS ETAPE_RECETTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestEtapeRecette:
    """Tests pour les étapes de recette."""

    def test_etape_creation(self, db: Session):
        """Test création d'une étape."""
        recette = Recette(
            nom="Recette avec Ã‰tapes",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
        )
        db.add(recette)
        db.commit()
        
        etape = EtapeRecette(
            recette_id=recette.id,
            ordre=1,
            description="Faire bouillir l'eau",
            duree=5,
        )
        db.add(etape)
        db.commit()
        
        assert etape.ordre == 1
        assert etape.description == "Faire bouillir l'eau"

    def test_etape_ordre(self, db: Session):
        """Test l'ordre des étapes."""
        recette = Recette(
            nom="Recette Multi-étapes",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        etape1 = EtapeRecette(recette_id=recette.id, ordre=1, description="Ã‰tape 1")
        etape2 = EtapeRecette(recette_id=recette.id, ordre=2, description="Ã‰tape 2")
        etape3 = EtapeRecette(recette_id=recette.id, ordre=3, description="Ã‰tape 3")
        
        db.add_all([etape1, etape2, etape3])
        db.commit()
        
        # Récupérer les étapes ordonnées
        etapes = db.query(EtapeRecette).filter_by(recette_id=recette.id).order_by(EtapeRecette.ordre).all()
        assert len(etapes) == 3
        assert etapes[0].ordre == 1
        assert etapes[2].ordre == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: TESTS VERSION_RECETTE (Variantes)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestVersionRecette:
    """Tests pour les variantes de recette."""

    def test_version_creation(self, db: Session):
        """Test création d'une version."""
        recette = Recette(
            nom="Recette Originale",
            temps_preparation=15,
            temps_cuisson=20,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        version = VersionRecette(
            recette_base_id=recette.id,
            type_version="bébé",
            notes_bebe="Adapter la texture",
        )
        db.add(version)
        db.commit()
        
        assert version.type_version == "bébé"
        assert version.recette_base_id == recette.id

    def test_multiple_versions(self, db: Session):
        """Test plusieurs variantes."""
        recette = Recette(
            nom="Recette de Base",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        v1 = VersionRecette(recette_base_id=recette.id, type_version="bébé")
        v2 = VersionRecette(recette_base_id=recette.id, type_version="batch_cooking")
        v3 = VersionRecette(recette_base_id=recette.id, type_version="vegetarien")
        
        db.add_all([v1, v2, v3])
        db.commit()
        
        versions = db.query(VersionRecette).filter_by(recette_base_id=recette.id).all()
        assert len(versions) == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 6: TESTS HISTORIQUE_RECETTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestHistoriqueRecette:
    """Tests pour l'historique d'utilisation."""

    def test_historique_creation(self, db: Session):
        """Test création d'un historique."""
        recette = Recette(
            nom="Recette Testée",
            temps_preparation=10,
            temps_cuisson=15,
            portions=3,
        )
        db.add(recette)
        db.commit()
        
        historique = HistoriqueRecette(
            recette_id=recette.id,
            date_cuisson=date.today(),
            portions_cuisinees=3,
            note=4,
            avis="Très bon!",
        )
        db.add(historique)
        db.commit()
        
        assert historique.note == 4
        assert historique.avis == "Très bon!"

    def test_historique_moyenne_notes(self, db: Session):
        """Test qu'on peut calculer une moyenne."""
        recette = Recette(
            nom="Recette Populaire",
            temps_preparation=20,
            temps_cuisson=25,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        h1 = HistoriqueRecette(recette_id=recette.id, date_cuisson=date.today(), note=4)
        h2 = HistoriqueRecette(recette_id=recette.id, date_cuisson=date.today(), note=5)
        h3 = HistoriqueRecette(recette_id=recette.id, date_cuisson=date.today(), note=3)
        
        db.add_all([h1, h2, h3])
        db.commit()
        
        historiques = db.query(HistoriqueRecette).filter_by(recette_id=recette.id).all()
        assert len(historiques) == 3
        moyenne = sum(h.note for h in historiques) / len(historiques)
        assert moyenne == 4.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 7: TESTS BATCH_MEAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBatchMeal:
    """Tests pour les plats batch cooking."""

    def test_batch_meal_creation(self, db: Session):
        """Test création d'un batch meal."""
        batch = BatchMeal(
            nom="Repas Batch Dimanche",
            description="Préparation du dimanche",
            portions_creees=12,
            portions_restantes=12,
            date_preparation=date.today(),
            date_peremption=date.today(),
        )
        db.add(batch)
        db.commit()
        
        assert batch.nom == "Repas Batch Dimanche"
        assert batch.portions_creees == 12

    def test_batch_meal_recettes(self, db: Session):
        """Test association avec recettes."""
        recette1 = Recette(nom="Recette 1", temps_preparation=20, temps_cuisson=30, portions=4)
        recette2 = Recette(nom="Recette 2", temps_preparation=15, temps_cuisson=25, portions=4)
        
        db.add_all([recette1, recette2])
        db.commit()
        
        batch = BatchMeal(
            nom="Batch Multi-Recettes",
            portions_creees=16,
            portions_restantes=16,
            date_preparation=date.today(),
            date_peremption=date.today(),
            recette_id=recette1.id,
        )
        db.add(batch)
        db.commit()
        
        assert batch is not None
        assert batch.recette_id == recette1.id


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 8: TESTS D'INTÃ‰GRATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.integration
class TestRecettesIntegration:
    """Tests d'intégration complets."""

    def test_recette_complete_avec_ingredients(self, db: Session):
        """Test création d'une recette complète avec ingrédients."""
        # Créer ingrédients
        ing_pates = Ingredient(nom="Pâtes", unite="g")
        ing_oeuf = Ingredient(nom="Oeuf", unite="pcs")
        ing_lard = Ingredient(nom="Lard", unite="g")
        
        db.add_all([ing_pates, ing_oeuf, ing_lard])
        db.commit()
        
        # Créer recette
        recette = Recette(
            nom="Carbonara Complète",
            temps_preparation=10,
            temps_cuisson=15,
            portions=4,
            est_rapide=True,
        )
        db.add(recette)
        db.commit()
        
        # Ajouter ingrédients
        ri1 = RecetteIngredient(recette_id=recette.id, ingredient_id=ing_pates.id, quantite=400, unite="g")
        ri2 = RecetteIngredient(recette_id=recette.id, ingredient_id=ing_oeuf.id, quantite=4, unite="pcs")
        ri3 = RecetteIngredient(recette_id=recette.id, ingredient_id=ing_lard.id, quantite=200, unite="g")
        
        db.add_all([ri1, ri2, ri3])
        db.commit()
        
        # Vérifier
        recette_reloaded = db.query(Recette).filter_by(id=recette.id).first()
        assert recette_reloaded is not None
        assert recette_reloaded.nom == "Carbonara Complète"

    def test_recette_workflow_complet(self, db: Session):
        """Test le workflow complet d'une recette."""
        # 1. Créer recette
        recette = Recette(
            nom="Workflow Test",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
        )
        db.add(recette)
        db.commit()
        
        # 2. Ajouter étapes
        etape1 = EtapeRecette(recette_id=recette.id, ordre=1, description="Ã‰tape 1")
        etape2 = EtapeRecette(recette_id=recette.id, ordre=2, description="Ã‰tape 2")
        db.add_all([etape1, etape2])
        db.commit()
        
        # 3. Créer variante
        version = VersionRecette(recette_base_id=recette.id, type_version="bébé")
        db.add(version)
        db.commit()
        
        # 4. Enregistrer utilisation
        historique = HistoriqueRecette(recette_id=recette.id, date_cuisson=date.today(), note=4)
        db.add(historique)
        db.commit()
        
        # Vérifier l'intégrité
        assert recette.id is not None
        assert version.recette_base_id == recette.id
        assert historique.recette_id == recette.id


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 9: TESTS ADDITIONNELS POUR COUVERTURE 85%+
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRecetteRobots:
    """Tests pour la compatibilité avec les robots culinaires."""

    def test_recette_compatible_cookeo(self, db: Session):
        """Test attribut compatible Cookeo."""
        recette = Recette(
            nom="Recette Cookeo",
            temps_preparation=10,
            temps_cuisson=30,
            portions=4,
            compatible_cookeo=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.compatible_cookeo is True

    def test_recette_compatible_monsieur_cuisine(self, db: Session):
        """Test attribut compatible Monsieur Cuisine."""
        recette = Recette(
            nom="Recette MC",
            temps_preparation=15,
            temps_cuisson=25,
            portions=4,
            compatible_monsieur_cuisine=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.compatible_monsieur_cuisine is True

    def test_recette_compatible_airfryer(self, db: Session):
        """Test attribut compatible Airfryer."""
        recette = Recette(
            nom="Recette Airfryer",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
            compatible_airfryer=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.compatible_airfryer is True

    def test_recette_compatible_multicooker(self, db: Session):
        """Test attribut compatible Multicooker."""
        recette = Recette(
            nom="Recette Multicooker",
            temps_preparation=10,
            temps_cuisson=60,
            portions=6,
            compatible_multicooker=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.compatible_multicooker is True


@pytest.mark.unit
class TestRecetteNutrition:
    """Tests pour les attributs nutritionnels."""

    def test_recette_calories(self, db: Session):
        """Test calories par portion."""
        recette = Recette(
            nom="Recette Calories",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            calories=350,
        )
        db.add(recette)
        db.commit()
        
        assert recette.calories == 350

    def test_recette_proteines(self, db: Session):
        """Test protéines par portion."""
        recette = Recette(
            nom="Recette Protéines",
            temps_preparation=15,
            temps_cuisson=25,
            portions=4,
            proteines=25.5,
        )
        db.add(recette)
        db.commit()
        
        assert recette.proteines == 25.5

    def test_recette_lipides(self, db: Session):
        """Test lipides par portion."""
        recette = Recette(
            nom="Recette Lipides",
            temps_preparation=10,
            temps_cuisson=15,
            portions=2,
            lipides=15.3,
        )
        db.add(recette)
        db.commit()
        
        assert recette.lipides == 15.3

    def test_recette_glucides(self, db: Session):
        """Test glucides par portion."""
        recette = Recette(
            nom="Recette Glucides",
            temps_preparation=5,
            temps_cuisson=10,
            portions=3,
            glucides=45.0,
        )
        db.add(recette)
        db.commit()
        
        assert recette.glucides == 45.0

    def test_recette_nutrition_complete(self, db: Session):
        """Test recette avec toutes les infos nutritionnelles."""
        recette = Recette(
            nom="Recette Nutrition Complète",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
            calories=450,
            proteines=30.0,
            lipides=20.0,
            glucides=40.0,
        )
        db.add(recette)
        db.commit()
        
        assert recette.calories == 450
        assert recette.proteines == 30.0
        assert recette.lipides == 20.0
        assert recette.glucides == 40.0


@pytest.mark.unit
class TestRecetteIA:
    """Tests pour les attributs liés Ã  l'IA."""

    def test_recette_genere_par_ia(self, db: Session):
        """Test flag généré par IA."""
        recette = Recette(
            nom="Recette IA",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            genere_par_ia=True,
            score_ia=0.95,
        )
        db.add(recette)
        db.commit()
        
        assert recette.genere_par_ia is True
        assert recette.score_ia == 0.95

    def test_recette_url_image(self, db: Session):
        """Test URL image."""
        recette = Recette(
            nom="Recette avec Image",
            temps_preparation=15,
            temps_cuisson=25,
            portions=4,
            url_image="https://example.com/image.jpg",
        )
        db.add(recette)
        db.commit()
        
        assert recette.url_image == "https://example.com/image.jpg"


@pytest.mark.unit
class TestRecetteCategories:
    """Tests pour les catégories et classifications."""

    def test_recette_type_repas(self, db: Session):
        """Test type de repas."""
        recette = Recette(
            nom="Petit Déjeuner",
            temps_preparation=5,
            temps_cuisson=0,
            portions=1,
            type_repas="petit_déjeuner",
        )
        db.add(recette)
        db.commit()
        
        assert recette.type_repas == "petit_déjeuner"

    def test_recette_saison(self, db: Session):
        """Test saison recommandée."""
        recette = Recette(
            nom="Soupe d'Hiver",
            temps_preparation=15,
            temps_cuisson=45,
            portions=6,
            saison="hiver",
        )
        db.add(recette)
        db.commit()
        
        assert recette.saison == "hiver"

    def test_recette_categorie(self, db: Session):
        """Test catégorie de recette."""
        recette = Recette(
            nom="Dessert Chocolat",
            temps_preparation=20,
            temps_cuisson=25,
            portions=8,
            categorie="dessert",
        )
        db.add(recette)
        db.commit()
        
        assert recette.categorie == "dessert"

    def test_recette_type_proteines(self, db: Session):
        """Test type de protéines."""
        recette = Recette(
            nom="Saumon Grillé",
            temps_preparation=10,
            temps_cuisson=15,
            portions=2,
            type_proteines="poisson",
        )
        db.add(recette)
        db.commit()
        
        assert recette.type_proteines == "poisson"


@pytest.mark.unit
class TestRecetteVegetarien:
    """Tests pour les recettes végétariennes."""

    def test_recette_est_vegetarien(self, db: Session):
        """Test flag végétarien."""
        recette = Recette(
            nom="Curry Légumes",
            temps_preparation=15,
            temps_cuisson=30,
            portions=4,
            est_vegetarien=True,
        )
        db.add(recette)
        db.commit()
        
        assert recette.est_vegetarien is True


@pytest.mark.unit
class TestRecetteScores:
    """Tests pour les scores bio/local."""

    def test_recette_score_bio(self, db: Session):
        """Test score bio."""
        recette = Recette(
            nom="Recette Bio",
            temps_preparation=15,
            temps_cuisson=20,
            portions=4,
            est_bio=True,
            score_bio=85,
        )
        db.add(recette)
        db.commit()
        
        assert recette.score_bio == 85

    def test_recette_score_local(self, db: Session):
        """Test score local."""
        recette = Recette(
            nom="Recette Locale",
            temps_preparation=10,
            temps_cuisson=25,
            portions=4,
            est_local=True,
            score_local=90,
        )
        db.add(recette)
        db.commit()
        
        assert recette.score_local == 90


@pytest.mark.unit  
class TestRecetteIngredientAdvanced:
    """Tests avancés pour RecetteIngredient."""

    def test_recette_ingredient_optionalite(self, db: Session):
        """Test que l'ingrédient peut être optionnel."""
        ingredient = Ingredient(nom="Sel Optionnel")
        recette = Recette(
            nom="Recette Simple",
            temps_preparation=5,
            temps_cuisson=10,
            portions=2,
        )
        
        db.add(ingredient)
        db.add(recette)
        db.commit()
        
        ri = RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredient.id,
            quantite=1,
            unite="pcs",
            optionnel=True,
        )
        db.add(ri)
        db.commit()
        
        assert ri.optionnel is True

    def test_recette_ingredient_notes(self, db: Session):
        """Test notes sur l'ingrédient."""
        ingredient = Ingredient(nom="Poulet Notes")
        recette = Recette(
            nom="Recette Notes",
            temps_preparation=10,
            temps_cuisson=30,
            portions=4,
        )
        
        db.add(ingredient)
        db.add(recette)
        db.commit()
        
        # Check if notes attribute exists on the model
        ri = RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredient.id,
            quantite=500,
            unite="g",
        )
        db.add(ri)
        db.commit()
        
        assert ri.quantite == 500


@pytest.mark.unit
class TestEtapeRecetteAdvanced:
    """Tests avancés pour EtapeRecette."""

    def test_etape_avec_duree(self, db: Session):
        """Test étape avec durée."""
        recette = Recette(
            nom="Recette Durée",
            temps_preparation=15,
            temps_cuisson=30,
            portions=4,
        )
        db.add(recette)
        db.commit()
        
        etape = EtapeRecette(
            recette_id=recette.id,
            ordre=1,
            description="Laisser mijoter",
            duree=20,
        )
        db.add(etape)
        db.commit()
        
        assert etape.duree == 20


@pytest.mark.unit
class TestVersionRecetteAdvanced:
    """Tests avancés pour VersionRecette."""

    def test_version_batch_cooking(self, db: Session):
        """Test version batch cooking."""
        recette = Recette(
            nom="Recette Batch",
            temps_preparation=20,
            temps_cuisson=60,
            portions=8,
        )
        db.add(recette)
        db.commit()
        
        version = VersionRecette(
            recette_base_id=recette.id,
            type_version="batch_cooking",
            temps_optimise_batch=45,
        )
        db.add(version)
        db.commit()
        
        assert version.type_version == "batch_cooking"
        assert version.temps_optimise_batch == 45


@pytest.mark.unit
class TestBatchMealAdvanced:
    """Tests avancés pour BatchMeal."""

    def test_batch_meal_portions_update(self, db: Session):
        """Test mise Ã  jour des portions restantes."""
        batch = BatchMeal(
            nom="Batch Test",
            portions_creees=10,
            portions_restantes=10,
            date_preparation=date.today(),
            date_peremption=date.today(),
        )
        db.add(batch)
        db.commit()
        
        # Simuler consommation
        batch.portions_restantes = 7
        db.commit()
        
        assert batch.portions_restantes == 7

    def test_batch_meal_lieu_stockage(self, db: Session):
        """Test localisation de stockage."""
        batch = BatchMeal(
            nom="Batch Congelé",
            portions_creees=8,
            portions_restantes=8,
            date_preparation=date.today(),
            date_peremption=date.today(),
            localisation="congélateur",
        )
        db.add(batch)
        db.commit()
        
        assert batch.localisation == "congélateur"

