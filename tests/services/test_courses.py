"""
Tests unitaires pour CoursesService (src/services/courses.py).

Tests couvrant:
- CRUD articles courses
- Liste de courses avec filtres
- Suggestions IA
- Modèles persistants de courses
- Schéma Pydantic SuggestionCourses
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.services.courses import (
    CoursesService,
    SuggestionCourses,
    get_courses_service,
)
from src.core.models import ArticleCourses, Ingredient


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: TESTS INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCoursesServiceInit:
    """Test initialisation du service."""

    def test_service_initializes_with_article_courses_model(self):
        """Test que le service s'initialise avec ArticleCourses."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()

            assert service.model == ArticleCourses
            assert service.model_name == "ArticleCourses"
            assert service.cache_ttl == 1800

    def test_service_inherits_base_service(self):
        """Test que le service hérite de BaseService."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()

            assert hasattr(service, "create")
            assert hasattr(service, "get_by_id")
            assert hasattr(service, "update")
            assert hasattr(service, "delete")

    def test_factory_returns_service_instance(self):
        """Test que la factory retourne une instance."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = get_courses_service()

            assert isinstance(service, CoursesService)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: TESTS SCHÃ‰MA PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggestionCoursesSchema:
    """Test schéma Pydantic SuggestionCourses."""

    def test_suggestion_courses_valid(self):
        """Test création suggestion valide."""
        suggestion = SuggestionCourses(
            nom="Tomates",
            quantite=2.0,
            unite="kg",
            priorite="haute",
            rayon="Fruits & Légumes",
        )

        assert suggestion.nom == "Tomates"
        assert suggestion.quantite == 2.0
        assert suggestion.priorite == "haute"

    def test_suggestion_courses_nom_min_length(self):
        """Test que nom doit avoir au moins 2 caractères."""
        with pytest.raises(ValueError):
            SuggestionCourses(
                nom="A",  # Trop court
                quantite=1.0,
                unite="kg",
                priorite="haute",
                rayon="Test",
            )

    def test_suggestion_courses_quantite_positive(self):
        """Test que quantite doit être positive."""
        with pytest.raises(ValueError):
            SuggestionCourses(
                nom="Test",
                quantite=0,  # Doit être > 0
                unite="kg",
                priorite="haute",
                rayon="Test",
            )

    def test_suggestion_courses_priorite_valid_values(self):
        """Test que priorite accepte seulement haute/moyenne/basse."""
        for priorite in ["haute", "moyenne", "basse"]:
            suggestion = SuggestionCourses(
                nom="Test",
                quantite=1.0,
                unite="kg",
                priorite=priorite,
                rayon="Test",
            )
            assert suggestion.priorite == priorite

    def test_suggestion_courses_priorite_invalid_value(self):
        """Test que priorite invalide lève une erreur."""
        with pytest.raises(ValueError):
            SuggestionCourses(
                nom="Test",
                quantite=1.0,
                unite="kg",
                priorite="urgente",  # Invalide
                rayon="Test",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: TESTS LISTE DE COURSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestListeCourses:
    """Test shopping list functionality."""
    
    def test_get_liste_courses_returns_list(
        self, courses_service, db
    ):
        """Test retrieving shopping list."""
        result = courses_service.get_liste_courses(db=db)
        
        assert isinstance(result, list)
    
    def test_get_liste_courses_filters_unpurchased(
        self, courses_service, db
    ):
        """Test filtering unpurchased items."""
        result = courses_service.get_liste_courses(achetes=False, db=db)
        
        assert isinstance(result, list)
    
    def test_get_liste_courses_filters_by_priority(
        self, courses_service, db
    ):
        """Test filtering by priority."""
        result = courses_service.get_liste_courses(
            priorite="haute", db=db
        )
        
        assert isinstance(result, list)

    def test_get_liste_courses_with_articles(self, db, ingredient_factory):
        """Test liste avec articles créés."""
        ingredient = ingredient_factory.create(nom="Tomates Test Liste")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=2.0,
            priorite="haute",
            rayon_magasin="Fruits & Légumes",
            achete=False,
        )
        db.add(article)
        db.commit()
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.get_liste_courses(db=db)
            
            assert isinstance(result, list)
            assert len(result) >= 1

    def test_get_liste_courses_returns_expected_fields(self, db, ingredient_factory):
        """Test que get_liste_courses retourne les champs attendus."""
        ingredient = ingredient_factory.create(nom="Tomates Champs")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=2.5,
            priorite="moyenne",
            rayon_magasin="Légumes",
            achete=False,
            notes="Bio si possible",
        )
        db.add(article)
        db.commit()
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.get_liste_courses(db=db)
            
            if result:
                item = result[-1]
                assert "id" in item
                assert "ingredient_id" in item
                assert "ingredient_nom" in item
                assert "quantite_necessaire" in item
                assert "priorite" in item
                assert "rayon_magasin" in item


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: TESTS SUGGESTIONS IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggestionsIA:
    """Test IA shopping suggestions."""
    
    def test_generer_suggestions_ia_method_exists(
        self, courses_service
    ):
        """Test that suggestion method exists."""
        assert hasattr(
            courses_service, 
            'generer_suggestions_ia_depuis_inventaire'
        )
        assert callable(
            courses_service.generer_suggestions_ia_depuis_inventaire
        )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: TESTS MODÃˆLES DE COURSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCoursesServiceModeles:
    """Test modèles de courses persistants."""

    def test_get_modeles_method_exists(self):
        """Test que la méthode get_modeles existe."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            assert hasattr(service, "get_modeles")
            assert callable(service.get_modeles)

    def test_create_modele_method_exists(self):
        """Test que la méthode create_modele existe."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            assert hasattr(service, "create_modele")
            assert callable(service.create_modele)

    def test_delete_modele_method_exists(self):
        """Test que la méthode delete_modele existe."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            assert hasattr(service, "delete_modele")
            assert callable(service.delete_modele)

    def test_appliquer_modele_method_exists(self):
        """Test que la méthode appliquer_modele existe."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            assert hasattr(service, "appliquer_modele")
            assert callable(service.appliquer_modele)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 6: TESTS CRUD ARTICLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCoursesServiceCRUD:
    """Test CRUD articles courses."""

    def test_create_article_courses(self, db, ingredient_factory):
        """Test création article courses."""
        ingredient = ingredient_factory.create(nom="Nouvel Article")
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            data = {
                "ingredient_id": ingredient.id,
                "quantite_necessaire": 3.0,
                "priorite": "haute",
                "rayon_magasin": "Fruits & Légumes",
                "achete": False,
            }
            
            result = service.create(data, db=db)
            
            assert result is not None
            assert result.id is not None
            assert result.quantite_necessaire == 3.0

    def test_get_article_by_id(self, db, ingredient_factory):
        """Test récupération article par ID."""
        ingredient = ingredient_factory.create(nom="Article GetById")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            rayon_magasin="Test",
            achete=False,
        )
        db.add(article)
        db.commit()
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.get_by_id(article.id, db=db)
            
            assert result is not None
            assert result.id == article.id

    def test_update_article_courses(self, db, ingredient_factory):
        """Test mise à jour article courses."""
        ingredient = ingredient_factory.create(nom="Article Update")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=1.0,
            priorite="basse",
            rayon_magasin="Test",
            achete=False,
        )
        db.add(article)
        db.commit()
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.update(
                article.id,
                {"priorite": "haute", "quantite_necessaire": 5.0},
                db=db,
            )
            
            assert result is not None
            assert result.priorite == "haute"
            assert result.quantite_necessaire == 5.0

    def test_delete_article_courses(self, db, ingredient_factory):
        """Test suppression article courses."""
        ingredient = ingredient_factory.create(nom="Article Delete")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            rayon_magasin="Test",
            achete=False,
        )
        db.add(article)
        db.commit()
        article_id = article.id
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.delete(article_id, db=db)
            
            assert result is True
            assert service.get_by_id(article_id, db=db) is None

    def test_marquer_achete(self, db, ingredient_factory):
        """Test marquer article comme acheté."""
        ingredient = ingredient_factory.create(nom="Article Achete")
        
        article = ArticleCourses(
            ingredient_id=ingredient.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            rayon_magasin="Test",
            achete=False,
        )
        db.add(article)
        db.commit()
        
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            result = service.update(article.id, {"achete": True}, db=db)
            
            assert result is not None
            assert result.achete is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 7: TESTS INTÃ‰GRATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.integration
class TestCoursesIntegration:
    """Integration tests for shopping."""
    
    def test_shopping_workflow(
        self, courses_service, db
    ):
        """Test complete shopping workflow."""
        items = courses_service.get_liste_courses(db=db)
        
        assert isinstance(items, list)

    def test_workflow_complet_courses(self, db, ingredient_factory):
        """Test workflow complet courses - création et lecture."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            # Créer ingrédient
            ingredient = ingredient_factory.create(nom="Workflow Ingredient Unique")
            
            # Créer article directement en DB
            article = ArticleCourses(
                ingredient_id=ingredient.id,
                quantite_necessaire=2.0,
                priorite="haute",
                rayon_magasin="Test Workflow",
                achete=False,
            )
            db.add(article)
            db.commit()
            article_id = article.id
            
            # Vérifier dans la liste (test principal)
            liste = service.get_liste_courses(db=db)
            articles_ids = [item["id"] for item in liste]
            assert article_id in articles_ids, f"Article {article_id} devrait être dans {articles_ids}"
            
            # Nettoyer
            db.delete(article)
            db.commit()

    def test_filtres_combines(self, db, ingredient_factory):
        """Test filtres combinés."""
        with patch("src.services.courses.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            service = CoursesService()
            
            ingredient = ingredient_factory.create(nom="Filtre Combine")
            
            # Créer plusieurs articles
            articles_data = [
                {"priorite": "haute", "achete": False},
                {"priorite": "haute", "achete": True},
                {"priorite": "basse", "achete": False},
            ]
            
            for data in articles_data:
                article = ArticleCourses(
                    ingredient_id=ingredient.id,
                    quantite_necessaire=1.0,
                    rayon_magasin="Test",
                    **data,
                )
                db.add(article)
            db.commit()
            
            # Filtrer: haute priorité ET non acheté
            result = service.get_liste_courses(
                achetes=False,
                priorite="haute",
                db=db,
            )
            
            assert all(
                item["priorite"] == "haute" and not item["achete"]
                for item in result
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 8: TESTS FIXTURES EXISTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCoursesFixtures:
    """Test avec les fixtures existantes."""

    def test_sample_articles_fixture(self, sample_articles):
        """Test que la fixture sample_articles est valide."""
        assert isinstance(sample_articles, list)
        assert len(sample_articles) >= 2
        
        for article in sample_articles:
            assert "id" in article
            assert "ingredient_nom" in article
            assert "quantite_necessaire" in article
            assert "priorite" in article

    def test_sample_suggestions_fixture(self, sample_suggestions):
        """Test que la fixture sample_suggestions est valide."""
        assert isinstance(sample_suggestions, list)
        assert len(sample_suggestions) >= 3
        
        for suggestion in sample_suggestions:
            assert hasattr(suggestion, "nom")
            assert hasattr(suggestion, "quantite")
            assert hasattr(suggestion, "priorite")

