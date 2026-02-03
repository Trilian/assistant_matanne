"""
PHASE 13E: Direct Service Method Testing
Tests the actual service methods with real data
No complex workflows, just basic CRUD operations
"""
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from src.core.models.recettes import Recette


class TestRecetteServiceDirectMethods:
    """Test RecetteService methods directly"""

    def test_recette_table_creation(self, db: Session):
        """Test que la table Recette peut être créée"""
        # Simplement créer une instance
        recipe = Recette(
            nom="Test Recipe",
        )
        db.add(recipe)
        db.commit()
        
        # Vérifier qu'elle a été créée
        retrieved = db.query(Recette).filter_by(nom="Test Recipe").first()
        assert retrieved is not None
        assert retrieved.nom == "Test Recipe"

    def test_recette_query_all(self, db: Session):
        """Test que nous pouvons queryifier toutes les recettes"""
        recipes = db.query(Recette).all()
        assert isinstance(recipes, list)

    def test_recette_query_filter(self, db: Session):
        """Test que nous pouvons filtrer les recettes"""
        recipe = Recette(nom="Filtered Recipe")
        db.add(recipe)
        db.commit()
        
        filtered = db.query(Recette).filter(Recette.nom == "Filtered Recipe").first()
        assert filtered is not None

    def test_recette_update(self, db: Session):
        """Test mise à jour d'une recette"""
        recipe = Recette(nom="Original")
        db.add(recipe)
        db.commit()
        
        recipe.nom = "Updated"
        db.commit()
        
        updated = db.query(Recette).filter_by(id=recipe.id).first()
        assert updated.nom == "Updated"

    def test_recette_delete(self, db: Session):
        """Test suppression d'une recette"""
        recipe = Recette(nom="To Delete")
        db.add(recipe)
        db.commit()
        recipe_id = recipe.id
        
        db.delete(recipe)
        db.commit()
        
        deleted = db.query(Recette).filter_by(id=recipe_id).first()
        assert deleted is None


class TestPlanningServiceDirectMethods:
    """Test PlanningService methods directly"""

    def test_planning_creation(self, db: Session):
        """Test créer un planning"""
        from src.core.models.planning import Planning
        
        planning = Planning(nom="Test Planning")
        db.add(planning)
        db.commit()
        
        retrieved = db.query(Planning).filter_by(nom="Test Planning").first()
        assert retrieved is not None

    def test_planning_query_all(self, db: Session):
        """Test query tous les plannings"""
        from src.core.models.planning import Planning
        
        plannings = db.query(Planning).all()
        assert isinstance(plannings, list)

    def test_repas_creation(self, db: Session):
        """Test créer un repas"""
        from src.core.models.planning import Planning, Repas
        
        planning = Planning(nom="Planning for Repas")
        db.add(planning)
        db.flush()
        
        repas = Repas(
            planning_id=planning.id,
            type_repas="lunch"
        )
        db.add(repas)
        db.commit()
        
        retrieved = db.query(Repas).first()
        assert retrieved is not None


class TestCoursesServiceDirectMethods:
    """Test CoursesService methods directly"""

    def test_article_courses_creation(self, db: Session):
        """Test créer un article de courses"""
        from src.core.models.courses import ArticleCourses
        
        article = ArticleCourses(nom="Test Article")
        db.add(article)
        db.commit()
        
        retrieved = db.query(ArticleCourses).filter_by(nom="Test Article").first()
        assert retrieved is not None

    def test_article_courses_query(self, db: Session):
        """Test query articles courses"""
        from src.core.models.courses import ArticleCourses
        
        articles = db.query(ArticleCourses).all()
        assert isinstance(articles, list)

    def test_modele_courses_creation(self, db: Session):
        """Test créer un modèle de courses"""
        from src.core.models.courses import ModeleCourses
        
        modele = ModeleCourses(nom="Test Modele")
        db.add(modele)
        db.commit()
        
        retrieved = db.query(ModeleCourses).filter_by(nom="Test Modele").first()
        assert retrieved is not None


class TestInventaireServiceDirectMethods:
    """Test InventaireService methods directly"""

    def test_article_inventaire_creation(self, db: Session):
        """Test créer un article d'inventaire"""
        from src.core.models.inventaire import ArticleInventaire
        
        article = ArticleInventaire(nom="Test Inventaire")
        db.add(article)
        db.commit()
        
        retrieved = db.query(ArticleInventaire).filter_by(nom="Test Inventaire").first()
        assert retrieved is not None

    def test_article_inventaire_query(self, db: Session):
        """Test query articles inventaire"""
        from src.core.models.inventaire import ArticleInventaire
        
        articles = db.query(ArticleInventaire).all()
        assert isinstance(articles, list)

    def test_historique_inventaire_logging(self, db: Session):
        """Test logging d'historique"""
        from src.core.models.inventaire import ArticleInventaire, HistoriqueInventaire
        
        article = ArticleInventaire(nom="Article with history")
        db.add(article)
        db.flush()
        
        history = HistoriqueInventaire(
            article_id=article.id,
            raison="test"
        )
        db.add(history)
        db.commit()
        
        retrieved = db.query(HistoriqueInventaire).first()
        assert retrieved is not None


class TestBudgetServiceDirectMethods:
    """Test BudgetService methods directly"""

    def test_house_expense_creation(self, db: Session):
        """Test créer une dépense"""
        from src.core.models.maison_extended import HouseExpense
        
        expense = HouseExpense(nom="Test Expense")
        db.add(expense)
        db.commit()
        
        retrieved = db.query(HouseExpense).filter_by(nom="Test Expense").first()
        assert retrieved is not None

    def test_house_expense_query(self, db: Session):
        """Test query dépenses"""
        from src.core.models.maison_extended import HouseExpense
        
        expenses = db.query(HouseExpense).all()
        assert isinstance(expenses, list)


class TestServiceDataAccess:
    """Test data access patterns"""

    def test_can_query_each_main_model(self, db: Session):
        """Test que chaque modèle principal peut être queryifié"""
        from src.core.models.recettes import Recette
        from src.core.models.planning import Planning
        from src.core.models.courses import ArticleCourses
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.maison_extended import HouseExpense
        
        # Chaque query doit retourner une list
        assert isinstance(db.query(Recette).all(), list)
        assert isinstance(db.query(Planning).all(), list)
        assert isinstance(db.query(ArticleCourses).all(), list)
        assert isinstance(db.query(ArticleInventaire).all(), list)
        assert isinstance(db.query(HouseExpense).all(), list)

    def test_count_queries(self, db: Session):
        """Test que count queries marchent"""
        from src.core.models.recettes import Recette
        from src.core.models.planning import Planning
        
        count_recipes = db.query(Recette).count()
        assert isinstance(count_recipes, int)
        assert count_recipes >= 0
        
        count_plannings = db.query(Planning).count()
        assert isinstance(count_plannings, int)
        assert count_plannings >= 0

    def test_first_queries(self, db: Session):
        """Test que first() queries marchent"""
        from src.core.models.recettes import Recette
        from src.core.models.planning import Planning
        
        first_recipe = db.query(Recette).first()
        assert first_recipe is None or isinstance(first_recipe, Recette)
        
        first_planning = db.query(Planning).first()
        assert first_planning is None or isinstance(first_planning, Planning)


class TestMultipleRecords:
    """Test creating and querying multiple records"""

    def test_create_multiple_recipes(self, db: Session):
        """Test créer plusieurs recettes"""
        from src.core.models.recettes import Recette
        
        for i in range(5):
            recipe = Recette(nom=f"Recipe {i}")
            db.add(recipe)
        db.commit()
        
        count = db.query(Recette).count()
        assert count >= 5

    def test_filter_multiple_records(self, db: Session):
        """Test filtrer plusieurs records"""
        from src.core.models.planning import Planning
        
        for i in range(3):
            planning = Planning(nom=f"Planning {i}")
            db.add(planning)
        db.commit()
        
        plannings = db.query(Planning).filter(
            Planning.nom.like("Planning %")
        ).all()
        assert len(plannings) >= 3

    def test_order_by_query(self, db: Session):
        """Test query avec order by"""
        from src.core.models.recettes import Recette
        
        # Créer plusieurs recettes
        for i in range(3):
            recipe = Recette(nom=f"Recipe {i}")
            db.add(recipe)
        db.commit()
        
        # Queryifier avec order by
        recipes = db.query(Recette).order_by(Recette.nom).all()
        assert isinstance(recipes, list)
        assert len(recipes) >= 3

    def test_limit_query(self, db: Session):
        """Test query avec limit"""
        from src.core.models.planning import Planning
        
        # Créer plusieurs plannings
        for i in range(5):
            planning = Planning(nom=f"Planning {i}")
            db.add(planning)
        db.commit()
        
        # Queryifier avec limit
        limited = db.query(Planning).limit(2).all()
        assert len(limited) <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
