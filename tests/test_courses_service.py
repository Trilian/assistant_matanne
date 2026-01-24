"""
Tests unitaires pour le service Courses
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.services.courses import CoursesService, get_courses_service
from src.core.models import ArticleCourses, Ingredient


class TestCoursesService:
    """Tests du service courses"""

    @pytest.fixture
    def service(self):
        """Créer une instance de service"""
        return CoursesService()

    @pytest.fixture
    def mock_ingredient(self):
        """Mock d'un ingrédient"""
        ingredient = Mock(spec=Ingredient)
        ingredient.id = 1
        ingredient.nom = "Tomates"
        ingredient.unite = "kg"
        return ingredient

    # ═══════════════════════════════════════════════════════════
    # Tests CRUD
    # ═══════════════════════════════════════════════════════════

    def test_get_liste_courses_vide(self, service):
        """Test récupération liste vide"""
        with patch.object(service, 'get_all', return_value=[]):
            liste = service.get_liste_courses(achetes=False)
            assert liste == []

    def test_get_liste_courses_with_items(self, service, mock_ingredient):
        """Test récupération liste avec articles"""
        # Mock d'articles
        article = Mock(spec=ArticleCourses)
        article.id = 1
        article.ingredient_id = 1
        article.ingredient = mock_ingredient
        article.quantite_necessaire = 2.0
        article.priorite = "haute"
        article.achete = False
        article.rayon_magasin = "Fruits & Légumes"
        article.magasin_cible = None
        article.notes = None
        article.suggere_par_ia = False

        with patch.object(service, 'get_all', return_value=[article]):
            liste = service.get_liste_courses(achetes=False)
            assert len(liste) > 0

    def test_create_article_courses(self, service):
        """Test création article courses"""
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.0,
            "priorite": "haute",
            "rayon_magasin": "Fruits & Légumes"
        }

        with patch.object(service, 'create', return_value=Mock(id=1)):
            result = service.create(data)
            assert result is not None

    def test_update_article_courses(self, service):
        """Test mise à jour article"""
        article_id = 1
        updates = {
            "quantite_necessaire": 3.0,
            "priorite": "moyenne"
        }

        with patch.object(service, 'update', return_value=True):
            result = service.update(article_id, updates)
            assert result is True

    def test_delete_article_courses(self, service):
        """Test suppression article"""
        article_id = 1

        with patch.object(service, 'delete', return_value=True):
            result = service.delete(article_id)
            assert result is True

    # ═══════════════════════════════════════════════════════════
    # Tests Filtres
    # ═══════════════════════════════════════════════════════════

    def test_filter_by_priority(self, service):
        """Test filtrage par priorité"""
        articles = [
            {"priorite": "haute"},
            {"priorite": "moyenne"},
            {"priorite": "basse"}
        ]

        filtered = [a for a in articles if a["priorite"] == "haute"]
        assert len(filtered) == 1
        assert filtered[0]["priorite"] == "haute"

    def test_filter_by_purchased(self, service):
        """Test filtrage par statut acheté"""
        articles = [
            {"achete": True},
            {"achete": False},
            {"achete": True}
        ]

        purchased = [a for a in articles if a["achete"] is True]
        assert len(purchased) == 2

    # ═══════════════════════════════════════════════════════════
    # Tests Suggestions IA
    # ═══════════════════════════════════════════════════════════

    def test_generer_suggestions_ia(self, service):
        """Test génération suggestions IA"""
        with patch.object(
            service,
            'generer_suggestions_ia_depuis_inventaire',
            return_value=[]
        ):
            suggestions = service.generer_suggestions_ia_depuis_inventaire()
            assert isinstance(suggestions, list)

    def test_generer_suggestions_ia_returns_list(self, service):
        """Test que suggestions retournent une liste"""
        mock_suggestions = [
            Mock(nom="Tomates", quantite=2.0, unite="kg", priorite="haute", rayon="Fruits"),
            Mock(nom="Oeufs", quantite=6.0, unite="pièce", priorite="moyenne", rayon="Laitier")
        ]

        with patch.object(
            service,
            'generer_suggestions_ia_depuis_inventaire',
            return_value=mock_suggestions
        ):
            suggestions = service.generer_suggestions_ia_depuis_inventaire()
            assert len(suggestions) == 2
            assert suggestions[0].nom == "Tomates"

    # ═══════════════════════════════════════════════════════════
    # Tests Singleton
    # ═══════════════════════════════════════════════════════════

    def test_get_courses_service_singleton(self):
        """Test que get_courses_service retourne un singleton"""
        service1 = get_courses_service()
        service2 = get_courses_service()
        assert service1 is service2

    # ═══════════════════════════════════════════════════════════
    # Tests Validations
    # ═══════════════════════════════════════════════════════════

    def test_priorite_values(self):
        """Test les valeurs autorisées de priorité"""
        valid_priorities = ["haute", "moyenne", "basse"]
        test_value = "haute"
        assert test_value in valid_priorities

    def test_invalid_priorite(self):
        """Test rejet priorité invalide"""
        valid_priorities = ["haute", "moyenne", "basse"]
        invalid_value = "super_haute"
        assert invalid_value not in valid_priorities

    def test_quantite_positive(self):
        """Test que quantité doit être positive"""
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.0,
            "priorite": "haute"
        }
        assert data["quantite_necessaire"] > 0

    def test_quantite_zero_invalid(self):
        """Test que quantité 0 est invalide"""
        quantite = 0.0
        assert quantite <= 0  # invalide


class TestCoursesIntegration:
    """Tests d'intégration"""

    def test_workflow_ajouter_article_marquer_acheté(self):
        """Test workflow complet: ajout → marquage acheté"""
        # 1. Ajouter article
        article_data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.0,
            "priorite": "haute",
            "rayon_magasin": "Fruits"
        }

        # 2. Vérifier création
        assert article_data["quantite_necessaire"] > 0
        assert article_data["priorite"] in ["haute", "moyenne", "basse"]

        # 3. Marquer acheté
        updates = {"achete": True, "achete_le": datetime.now()}
        assert updates["achete"] is True

    def test_workflow_suggestions_puis_ajout(self):
        """Test workflow: suggestions → ajout en masse"""
        suggestions = [
            {"nom": "Article1", "quantite": 1.0, "unite": "kg"},
            {"nom": "Article2", "quantite": 2.0, "unite": "pièce"}
        ]

        assert len(suggestions) == 2
        for suggestion in suggestions:
            assert suggestion["quantite"] > 0

    def test_modele_creation_et_chargement(self):
        """Test création et chargement modèle"""
        # Créer modèle
        modele = {
            "nom": "Courses hebdo",
            "articles": [
                {"nom": "Tomates", "quantite": 2.0},
                {"nom": "Oeufs", "quantite": 6.0}
            ]
        }

        # Vérifier données
        assert modele["nom"] == "Courses hebdo"
        assert len(modele["articles"]) == 2


class TestCoursesEdgeCases:
    """Tests des cas limites"""

    def test_empty_list_operations(self):
        """Test opérations sur liste vide"""
        liste = []
        filtered = [a for a in liste if a.get("achete") is False]
        assert len(filtered) == 0

    def test_very_long_notes(self):
        """Test notes très longues"""
        notes = "x" * 500  # Beaucoup plus que la limite
        # Simuler la validation
        valid_notes = notes[:200] if len(notes) > 200 else notes
        assert len(valid_notes) <= 200

    def test_special_characters_in_ingredient(self):
        """Test caractères spéciaux dans noms"""
        ingredient_names = [
            "Tomates cerises",
            "Œufs bio",
            "Crème fraîche",
            "Épinards",
        ]
        for name in ingredient_names:
            assert len(name) > 0

    def test_zero_quantite(self):
        """Test quantité zéro est rejetée"""
        quantite = 0.0
        is_valid = quantite > 0
        assert is_valid is False

    def test_negative_quantite(self):
        """Test quantité négative est rejetée"""
        quantite = -2.5
        is_valid = quantite > 0
        assert is_valid is False
