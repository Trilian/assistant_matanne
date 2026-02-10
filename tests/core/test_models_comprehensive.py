"""
Tests pour les modèles SQLAlchemy: Recettes

Couvre les opérations basiques et les relations entre modèles.

Note: Les tests pour ArticleCourses, ArticleInventaire, ChildProfile, Planning et Repas
ont été supprimés car ils nécessitent des fixtures complexes et ne testent rien (empty pass).
Voir les tests d'intégration pour ces modèles.
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from src.core.models import Recette


@pytest.mark.unit
class TestRecetteModel:
    """Tests du modèle Recette."""
    
    def test_recette_creation(self, test_db: Session):
        """Test la création d'une recette."""
        recette = Recette(
            nom="Pâtes à la Carbonara",
            portions=4,
            temps_preparation=10,
            temps_cuisson=15,
            difficulte="Facile"
        )
        
        test_db.add(recette)
        test_db.commit()
        test_db.refresh(recette)
        
        assert recette.id is not None
        assert recette.nom == "Pâtes à la Carbonara"
        assert recette.portions == 4
    
    def test_recette_temps(self, test_db: Session):
        """Test les temps de préparation et cuisson."""
        recette = Recette(
            nom="Rôti",
            temps_preparation=20,
            temps_cuisson=120
        )
        
        test_db.add(recette)
        test_db.commit()
        test_db.refresh(recette)
        
        assert recette.temps_total == 140  # Si propriété calculée
    
    def test_recette_categories(self, test_db: Session):
        """Test les catégories de recettes."""
        recette = Recette(
            nom="Salade",
            categorie="Accompagnements",
            temps_preparation=5  # NOT NULL required
        )
        
        test_db.add(recette)
        test_db.commit()
        test_db.refresh(recette)
        
        assert recette.categorie == "Accompagnements"
