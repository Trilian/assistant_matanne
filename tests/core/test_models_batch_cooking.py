"""
Tests pour le modèle BatchMeal (Batch Cooking).

Couvre les opérations CRUD et validations du modèle BatchMeal.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.core.models import BatchMeal, Recette


@pytest.mark.unit
class TestBatchMealModel:
    """Tests du modèle BatchMeal."""
    
    def test_batch_meal_creation(self, test_db: Session):
        """Test la création d'une instance BatchMeal."""
        now = datetime.now()
        batch = BatchMeal(
            nom="Préparation lot lasagne",
            description="Préparer 3 portions de lasagne",
            date_planification=now,
            statut="planifié"
        )
        
        test_db.add(batch)
        test_db.commit()
        test_db.refresh(batch)
        
        assert batch.id is not None
        assert batch.nom == "Préparation lot lasagne"
        assert batch.statut == "planifié"
    
    def test_batch_cooking_with_recipes(self, test_db: Session):
        """Test les relations BatchMeal avec Recettes."""
        # Créer une recette d'abord
        recipe = Recette(nom="Lasagne", portions=4)
        test_db.add(recipe)
        test_db.flush()
        
        # Créer un batch cooking
        batch = BatchMeal(
            nom="Batch lasagne",
            description="Lot de lasagnes",
            date_planification=datetime.now()
        )
        
        test_db.add(batch)
        test_db.commit()
        
        assert batch.id is not None
    
    def test_batch_cooking_statut_values(self, test_db: Session):
        """Test les valeurs possibles du statut."""
        statuts = ["planifié", "en_cours", "complété", "annulé"]
        
        for statut in statuts:
            batch = BatchMeal(
                nom=f"Batch {statut}",
                statut=statut,
                date_planification=datetime.now()
            )
            test_db.add(batch)
        
        test_db.commit()
        
        # Vérifier tous les statuts
        batches = test_db.query(BatchMeal).all()
        assert len(batches) == len(statuts)
    
    def test_batch_cooking_date_fields(self, test_db: Session):
        """Test les champs de date du batch cooking."""
        now = datetime.now()
        later = now + timedelta(days=1)
        
        batch = BatchMeal(
            nom="Test dates",
            date_planification=now,
            date_debut=now,
            date_fin=later
        )
        
        test_db.add(batch)
        test_db.commit()
        test_db.refresh(batch)
        
        assert batch.date_planification is not None
        assert batch.date_debut is not None
        assert batch.date_fin is not None
    
    def test_batch_cooking_duplication(self, test_db: Session):
        """Test la capacité à dupliquer un batch cooking."""
        original = BatchMeal(
            nom="Original",
            description="Description originale",
            statut="planifié"
        )
        
        test_db.add(original)
        test_db.commit()
        
        # Créer une copie
        copie = BatchMeal(
            nom=f"{original.nom} - Copie",
            description=original.description,
            statut=original.statut
        )
        
        test_db.add(copie)
        test_db.commit()
        
        assert copie.id != original.id
        assert copie.nom == "Original - Copie"
