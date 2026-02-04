"""Tests étendus pour logique cuisine - Couverture augmentée."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, MagicMock

# Imports depuis src
from src.domains.cuisine.logic import planificateur_repas_logic
from src.core.models import Recette, Repas, Planning, ArticleCourses


@pytest.mark.unit
class TestPlanificateurRepasLogicExtended:
    """Tests étendus pour planificateur de repas."""
    
    def test_planificateur_repas_semaine_complete(self, test_db: Session):
        """Tester planification complète d'une semaine."""
        # Créer recettes
        recettes = [
            Recette(nom=f"Recette {i}", portions=4, temps_prep=30)
            for i in range(7)
        ]
        test_db.add_all(recettes)
        test_db.commit()
        
        # Planifier la semaine
        today = datetime.now()
        for i in range(7):
            repas = Repas(
                date=today + timedelta(days=i),
                recette_id=recettes[i].id,
                type_repas="diner"
            )
            test_db.add(repas)
        
        test_db.commit()
        
        # Vérifier
        repas_list = test_db.query(Repas).filter(
            Repas.date >= today,
            Repas.date < today + timedelta(days=7)
        ).all()
        
        assert len(repas_list) == 7
    
    def test_planificateur_repas_collision_dates(self, test_db: Session):
        """Tester gestion des collisions de dates."""
        recette = Recette(nom="Burger", portions=2, temps_prep=15)
        test_db.add(recette)
        test_db.commit()
        
        today = datetime.now().date()
        
        # Ajouter deux repas même jour
        repas1 = Repas(date=today, recette_id=recette.id, type_repas="midi")
        repas2 = Repas(date=today, recette_id=recette.id, type_repas="diner")
        
        test_db.add_all([repas1, repas2])
        test_db.commit()
        
        # Vérifier
        count = test_db.query(Repas).filter(Repas.date == today).count()
        assert count == 2
    
    def test_planificateur_repas_sans_recette(self, test_db: Session):
        """Tester repas sans recette (jour vide)."""
        today = datetime.now().date()
        
        repas = Repas(date=today, recette_id=None, type_repas="diner")
        test_db.add(repas)
        test_db.commit()
        
        assert repas.recette_id is None
    
    def test_planificateur_repas_types_differents(self, test_db: Session):
        """Tester différents types de repas."""
        recette = Recette(nom="Salade", portions=1, temps_prep=10)
        test_db.add(recette)
        test_db.commit()
        
        today = datetime.now().date()
        types = ["petit_dej", "midi", "diner", "collation"]
        
        for type_repas in types:
            repas = Repas(date=today, recette_id=recette.id, type_repas=type_repas)
            test_db.add(repas)
        
        test_db.commit()
        
        assert test_db.query(Repas).count() == 4
    
    def test_planificateur_repas_portabilite(self, test_db: Session):
        """Tester modification portabilité recettes."""
        recette = Recette(nom="Pâtes", portions=4, temps_prep=20)
        test_db.add(recette)
        test_db.commit()
        
        # Ajouter repas
        repas = Repas(date=datetime.now().date(), recette_id=recette.id)
        test_db.add(repas)
        test_db.commit()
        
        # Modifier portions
        recette.portions = 6
        test_db.commit()
        
        # Vérifier
        updated_recette = test_db.query(Recette).filter_by(id=recette.id).first()
        assert updated_recette.portions == 6


@pytest.mark.unit
class TestBatchCookingLogicExtended:
    """Tests étendus pour batch cooking."""
    
    def test_batch_cooking_preparation(self, test_db: Session):
        """Tester préparation batch cooking."""
        from src.core.models import BatchMeal
        
        batch = BatchMeal(
            nom="Préparation Dimanche",
            date_planification=datetime.now(),
            statut="en_preparation"
        )
        test_db.add(batch)
        test_db.commit()
        
        assert batch.id is not None
        assert batch.statut == "en_preparation"
    
    def test_batch_cooking_progression_statuts(self, test_db: Session):
        """Tester progression des statuts."""
        from src.core.models import BatchMeal
        
        batch = BatchMeal(nom="Test", date_planification=datetime.now())
        test_db.add(batch)
        test_db.commit()
        
        statuts = ["planifie", "en_preparation", "en_cuisson", "termine"]
        
        for statut in statuts:
            batch.statut = statut
            test_db.commit()
            
            updated = test_db.query(BatchMeal).filter_by(id=batch.id).first()
            assert updated.statut == statut


@pytest.mark.unit
class TestCoursesLogicExtended:
    """Tests étendus pour gestion courses."""
    
    def test_courses_ajout_articles(self, test_db: Session):
        """Tester ajout multiple d'articles."""
        articles = [
            ArticleCourses(nom=f"Article {i}", quantite=i+1, unite="kg")
            for i in range(10)
        ]
        test_db.add_all(articles)
        test_db.commit()
        
        assert test_db.query(ArticleCourses).count() == 10
    
    def test_courses_articles_achetes(self, test_db: Session):
        """Tester marquage articles achetés."""
        article = ArticleCourses(nom="Tomates", quantite=3, unite="kg")
        test_db.add(article)
        test_db.commit()
        
        # Marquer acheté
        article.achete = True
        test_db.commit()
        
        updated = test_db.query(ArticleCourses).filter_by(id=article.id).first()
        assert updated.achete is True
    
    def test_courses_suppression_articles(self, test_db: Session):
        """Tester suppression d'articles."""
        article = ArticleCourses(nom="Sucre", quantite=1, unite="kg")
        test_db.add(article)
        test_db.commit()
        
        article_id = article.id
        
        # Supprimer
        test_db.delete(article)
        test_db.commit()
        
        # Vérifier
        deleted = test_db.query(ArticleCourses).filter_by(id=article_id).first()
        assert deleted is None
    
    def test_courses_quantites_decimales(self, test_db: Session):
        """Tester gestion quantités décimales."""
        article = ArticleCourses(nom="Farine", quantite=0.5, unite="kg")
        test_db.add(article)
        test_db.commit()
        
        retrieved = test_db.query(ArticleCourses).first()
        assert retrieved.quantite == 0.5


@pytest.mark.integration
class TestCoursesVersInventaireLogic:
    """Tests logique transformation courses → inventaire."""
    
    def test_articles_courses_a_inventaire(self, test_db: Session):
        """Tester conversion articles courses en inventaire."""
        from src.core.models import ArticleInventaire
        
        # Créer article courses
        article_c = ArticleCourses(nom="Riz", quantite=2, unite="kg", achete=True)
        test_db.add(article_c)
        test_db.commit()
        
        # Transformer en inventaire
        article_i = ArticleInventaire(
            nom=article_c.nom,
            quantite=article_c.quantite,
            unite=article_c.unite,
            date_ajout=datetime.now()
        )
        test_db.add(article_i)
        test_db.commit()
        
        # Vérifier
        assert test_db.query(ArticleInventaire).count() == 1
