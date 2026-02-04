"""
Phase 16 - Ciblage domains, ui, services pour +3-5% couverture
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.core.models.recettes import Recette, Ingredient, RecetteIngredient
from src.core.models.planning import Planning, Repas
from src.core.models.courses import ArticleCourses
from src.core.models.inventaire import ArticleInventaire


class TestRecetteBasic:
    """Recette model tests"""
    
    def test_recette_creation(self, db: Session):
        """Créer une recette"""
        r = Recette(
            nom="Pâtes", 
            description="Pâtes simples", 
            difficulte="facile",
            temps_preparation=15,
            temps_cuisson=10,
            portions=4
        )
        db.add(r)
        db.commit()
        assert r.id is not None
    
    def test_recette_with_ingredients(self, db: Session):
        """Recette avec ingrédients"""
        ing = Ingredient(nom="Tomate", categorie="Légume", unite="pcs")
        db.add(ing)
        db.flush()
        
        r = Recette(
            nom="Sauce Tomate", 
            description="Sauce simple", 
            difficulte="facile",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4
        )
        db.add(r)
        db.flush()
        
        ri = RecetteIngredient(
            recette_id=r.id,
            ingredient_id=ing.id,
            quantite=5,
            unite="pcs"
        )
        db.add(ri)
        db.commit()
        assert len(r.ingredients) == 1
    
    def test_recette_query(self, db: Session):
        """Interroger recette"""
        r = Recette(
            nom="Riz", 
            description="Riz blanc", 
            difficulte="facile",
            temps_preparation=5,
            temps_cuisson=20,
            portions=4
        )
        db.add(r)
        db.commit()
        
        found = db.query(Recette).filter_by(nom="Riz").first()
        assert found is not None


class TestPlanningBasic:
    """Planning model tests"""
    
    def test_planning_creation(self, db: Session):
        """Créer un planning"""
        today = date.today()
        p = Planning(
            nom="Semaine",
            semaine_debut=today,
            semaine_fin=today + timedelta(days=6),
            actif=True
        )
        db.add(p)
        db.commit()
        assert p.id is not None
    
    def test_planning_with_repas(self, db: Session):
        """Planning avec repas"""
        today = date.today()
        p = Planning(
            nom="Semaine avec repas",
            semaine_debut=today,
            semaine_fin=today + timedelta(days=6)
        )
        db.add(p)
        db.flush()
        
        rep = Repas(
            planning_id=p.id,
            date_repas=today,
            type_repas="déjeuner",
            prepare=False
        )
        db.add(rep)
        db.commit()
        assert len(p.repas) == 1


class TestArticlesBasic:
    """Articles tests"""
    
    def test_article_courses(self, db: Session):
        """Créer article courses"""
        ing = Ingredient(nom="Lait", categorie="Produits frais", unite="L")
        db.add(ing)
        db.flush()
        
        a = ArticleCourses(
            ingredient_id=ing.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            achete=False
        )
        db.add(a)
        db.commit()
        assert a.id is not None
    
    def test_article_inventaire(self, db: Session):
        """Créer article inventaire"""
        ing = Ingredient(nom="Farine", categorie="Secs", unite="g")
        db.add(ing)
        db.flush()
        
        a = ArticleInventaire(
            ingredient_id=ing.id,
            quantite=1000,
            quantite_min=200
        )
        db.add(a)
        db.commit()
        assert a.quantite == 1000
