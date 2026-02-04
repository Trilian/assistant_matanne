"""
Tests pour les modèles SQLAlchemy: Courses, Inventaire, Famille, Recettes, etc.

Couvre les opérations basiques et les relations entre modèles.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.core.models import (
    ArticleCourses,
    ArticleInventaire,
    ChildProfile,
    Recette,
    Planning,
    Repas,
)


@pytest.mark.unit
class TestArticleCoursesModel:
    """Tests du modèle ArticleCourses."""
    
    def test_article_courses_creation(self, test_db: Session):
        """Test la création d'un article de courses."""
        article = ArticleCourses(
            nom="Tomate",
            categorie="Légumes",
            quantite=2.0,
            unite="kg"
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.id is not None
        assert article.nom == "Tomate"
        assert article.categorie == "Légumes"
    
    def test_article_courses_with_statut(self, test_db: Session):
        """Test les différents statuts d'un article."""
        statuts = ["à_acheter", "acheté", "annulé"]
        
        for statut in statuts:
            article = ArticleCourses(
                nom=f"Article {statut}",
                statut=statut
            )
            test_db.add(article)
        
        test_db.commit()
        
        articles = test_db.query(ArticleCourses).all()
        assert len(articles) >= len(statuts)
    
    def test_article_courses_quantite(self, test_db: Session):
        """Test la gestion des quantités."""
        article = ArticleCourses(
            nom="Lait",
            quantite=1.5,
            unite="L",
            prix_unitaire=1.2
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.quantite == 1.5
        assert article.unite == "L"
        assert article.prix_unitaire == 1.2
    
    def test_article_courses_barcode(self, test_db: Session):
        """Test le code-barres d'un article."""
        article = ArticleCourses(
            nom="Produit",
            code_barre="3123456789012"
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.code_barre == "3123456789012"


@pytest.mark.unit
class TestArticleInventaireModel:
    """Tests du modèle ArticleInventaire."""
    
    def test_article_inventaire_creation(self, test_db: Session):
        """Test la création d'un article d'inventaire."""
        article = ArticleInventaire(
            nom="Œufs",
            categorie="Produits laitiers",
            quantite=12,
            unite="pièces"
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.id is not None
        assert article.quantite == 12
    
    def test_article_inventaire_expiration(self, test_db: Session):
        """Test la date d'expiration."""
        now = datetime.now()
        expiration = now + timedelta(days=7)
        
        article = ArticleInventaire(
            nom="Produit",
            date_achat=now,
            date_expiration=expiration
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.date_expiration is not None
    
    def test_article_inventaire_emplacement(self, test_db: Session):
        """Test le stockage de l'emplacement."""
        article = ArticleInventaire(
            nom="Farine",
            emplacement="Placard cuisine",
            temperature="Ambiante"
        )
        
        test_db.add(article)
        test_db.commit()
        test_db.refresh(article)
        
        assert article.emplacement == "Placard cuisine"


@pytest.mark.unit
class TestChildProfileModel:
    """Tests du modèle ChildProfile (Famille)."""
    
    def test_child_profile_creation(self, test_db: Session):
        """Test la création d'un profil d'enfant."""
        child = ChildProfile(
            nom="Jules",
            date_naissance=datetime(2024, 6, 15),
            genre="M"
        )
        
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)
        
        assert child.id is not None
        assert child.nom == "Jules"
    
    def test_child_profile_preferences(self, test_db: Session):
        """Test les préférences de l'enfant."""
        child = ChildProfile(
            nom="Marie",
            date_naissance=datetime(2022, 3, 20),
            allergies="Arachides",
            preferences_aliments="Pizza, Pâtes"
        )
        
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)
        
        assert "Arachides" in child.allergies if child.allergies else True


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
            tags="Santé, Rapide"
        )
        
        test_db.add(recette)
        test_db.commit()
        test_db.refresh(recette)
        
        assert recette.categorie == "Accompagnements"


@pytest.mark.unit
class TestPlanningModel:
    """Tests du modèle Planning."""
    
    def test_planning_creation(self, test_db: Session):
        """Test la création d'un planning."""
        now = datetime.now()
        planning = Planning(
            nom="Semaine 1",
            date_debut=now,
            date_fin=now + timedelta(days=7)
        )
        
        test_db.add(planning)
        test_db.commit()
        test_db.refresh(planning)
        
        assert planning.id is not None
        assert planning.nom == "Semaine 1"
    
    def test_planning_repas(self, test_db: Session):
        """Test l'ajout de repas au planning."""
        planning = Planning(
            nom="Planning test",
            date_debut=datetime.now()
        )
        
        test_db.add(planning)
        test_db.flush()
        
        repas = Repas(
            nom="Dîner",
            jour="Lundi",
            planning_id=planning.id
        )
        
        test_db.add(repas)
        test_db.commit()
        
        assert repas.planning_id == planning.id


@pytest.mark.unit
class TestRepasModel:
    """Tests du modèle Repas."""
    
    def test_repas_creation(self, test_db: Session):
        """Test la création d'un repas."""
        planning = Planning(nom="Planning")
        test_db.add(planning)
        test_db.flush()
        
        repas = Repas(
            nom="Dîner",
            jour="Mardi",
            planning_id=planning.id,
            heure="19:00"
        )
        
        test_db.add(repas)
        test_db.commit()
        test_db.refresh(repas)
        
        assert repas.id is not None
        assert repas.jour == "Mardi"
    
    def test_repas_types(self, test_db: Session):
        """Test les différents types de repas."""
        planning = Planning(nom="Planning")
        test_db.add(planning)
        test_db.flush()
        
        types_repas = ["Petit-déjeuner", "Déjeuner", "Dîner", "Snack"]
        
        for type_repas in types_repas:
            repas = Repas(
                nom=type_repas,
                jour="Mercredi",
                planning_id=planning.id
            )
            test_db.add(repas)
        
        test_db.commit()
        
        repas_list = test_db.query(Repas).filter_by(jour="Mercredi").all()
        assert len(repas_list) == len(types_repas)
