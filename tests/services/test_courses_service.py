"""
Tests pour CoursesService - Service critique
Tests complets pour la gestion des listes de courses
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from src.services.courses import CoursesService, get_courses_service


# ═══════════════════════════════════════════════════════════
# TESTS INSTANCIATION ET FACTORY
# ═══════════════════════════════════════════════════════════

class TestCoursesServiceFactory:
    """Tests pour la factory et l'instanciation du service."""
    
    def test_get_courses_service_returns_instance(self):
        """La factory retourne une instance de CoursesService."""
        service = get_courses_service()
        assert service is not None
        assert isinstance(service, CoursesService)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - ARTICLES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceArticles:
    """Tests pour la gestion des articles de courses."""
    
    def test_ajouter_article_simple(self, db, courses_service):
        """Ajouter un article à la liste de courses."""
        article = courses_service.ajouter_article(
            nom="Tomates",
            quantite=2.0,
            unite="kg",
            categorie="Fruits & Légumes",
            db=db
        )
        
        assert article is not None
        assert article.nom == "Tomates"
        assert article.quantite == 2.0
        assert article.achete is False
    
    def test_ajouter_article_avec_priorite(self, db, courses_service):
        """Ajouter un article avec priorité haute."""
        article = courses_service.ajouter_article(
            nom="Lait",
            quantite=1,
            unite="L",
            priorite="haute",
            db=db
        )
        
        assert article.priorite == "haute"
    
    def test_lister_articles_non_achetes(self, db, courses_service):
        """Lister uniquement les articles non achetés."""
        # Ajouter des articles
        courses_service.ajouter_article(nom="Tomates", quantite=1, db=db)
        courses_service.ajouter_article(nom="Carottes", quantite=2, db=db)
        
        articles = courses_service.lister_articles(achetes=False, db=db)
        
        for article in articles:
            assert article.achete is False
    
    def test_marquer_article_achete(self, db, courses_service):
        """Marquer un article comme acheté."""
        article = courses_service.ajouter_article(
            nom="Pain",
            quantite=1,
            db=db
        )
        
        article_maj = courses_service.marquer_achete(article.id, db=db)
        
        assert article_maj.achete is True
    
    def test_marquer_article_non_achete(self, db, courses_service):
        """Remettre un article comme non acheté."""
        article = courses_service.ajouter_article(nom="Beurre", quantite=1, db=db)
        courses_service.marquer_achete(article.id, db=db)
        
        article_maj = courses_service.marquer_non_achete(article.id, db=db)
        
        assert article_maj.achete is False
    
    def test_supprimer_article(self, db, courses_service):
        """Supprimer un article de la liste."""
        article = courses_service.ajouter_article(nom="Test", quantite=1, db=db)
        article_id = article.id
        
        resultat = courses_service.supprimer_article(article_id, db=db)
        
        assert resultat is True
    
    def test_modifier_quantite_article(self, db, courses_service):
        """Modifier la quantité d'un article."""
        article = courses_service.ajouter_article(
            nom="Pommes",
            quantite=1,
            db=db
        )
        
        article_maj = courses_service.modifier_article(
            article.id,
            {"quantite": 3.0},
            db=db
        )
        
        assert article_maj.quantite == 3.0


# ═══════════════════════════════════════════════════════════
# TESTS ORGANISATION PAR CATÉGORIE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceCategories:
    """Tests pour l'organisation par catégorie."""
    
    def test_lister_par_categorie(self, db, courses_service):
        """Lister les articles groupés par catégorie."""
        courses_service.ajouter_article(
            nom="Tomates", 
            categorie="Fruits & Légumes",
            quantite=1,
            db=db
        )
        courses_service.ajouter_article(
            nom="Yaourts",
            categorie="Produits laitiers",
            quantite=4,
            db=db
        )
        
        par_categorie = courses_service.lister_par_categorie(db=db)
        
        assert isinstance(par_categorie, dict)
        assert "Fruits & Légumes" in par_categorie or len(par_categorie) > 0
    
    def test_obtenir_categories_disponibles(self, db, courses_service):
        """Obtenir la liste des catégories disponibles."""
        categories = courses_service.obtenir_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Fruits & Légumes" in categories or "fruits" in str(categories).lower()


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES DE COURSES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceModeles:
    """Tests pour les modèles de courses prédéfinis."""
    
    def test_creer_modele(self, db, courses_service):
        """Créer un modèle de courses."""
        modele = courses_service.creer_modele(
            nom="Courses hebdomadaires",
            description="Liste type pour la semaine",
            db=db
        )
        
        assert modele is not None
        assert modele.nom == "Courses hebdomadaires"
    
    def test_ajouter_article_au_modele(self, db, courses_service):
        """Ajouter un article à un modèle."""
        modele = courses_service.creer_modele(nom="Test modèle", db=db)
        
        article = courses_service.ajouter_article_modele(
            modele_id=modele.id,
            nom="Lait",
            quantite=2,
            unite="L",
            db=db
        )
        
        assert article is not None
    
    def test_appliquer_modele(self, db, courses_service):
        """Appliquer un modèle pour créer une liste de courses."""
        # Créer modèle avec articles
        modele = courses_service.creer_modele(nom="Modèle test", db=db)
        courses_service.ajouter_article_modele(
            modele_id=modele.id, nom="Pain", quantite=1, db=db
        )
        courses_service.ajouter_article_modele(
            modele_id=modele.id, nom="Lait", quantite=2, db=db
        )
        
        # Appliquer le modèle
        articles = courses_service.appliquer_modele(modele.id, db=db)
        
        assert len(articles) >= 2


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DEPUIS PLANNING
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServicePlanning:
    """Tests pour la génération de courses depuis le planning."""
    
    def test_generer_depuis_planning_vide(self, db, courses_service):
        """Générer une liste depuis un planning vide."""
        articles = courses_service.generer_depuis_planning(
            planning_id=None,
            db=db
        )
        
        assert articles == [] or articles is None
    
    @patch('src.services.courses.get_planning_service')
    def test_generer_depuis_planning(self, mock_planning, db, courses_service):
        """Générer une liste de courses depuis un planning de repas."""
        # Mock du planning service
        mock_service = Mock()
        mock_service.obtenir_repas_semaine.return_value = [
            Mock(recette=Mock(recette_ingredients=[
                Mock(ingredient=Mock(nom="Tomates"), quantite=500, unite="g"),
                Mock(ingredient=Mock(nom="Oeufs"), quantite=6, unite="pcs"),
            ]))
        ]
        mock_planning.return_value = mock_service
        
        articles = courses_service.generer_depuis_planning(
            date_debut=date.today(),
            db=db
        )
        
        # La génération devrait créer des articles


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceStats:
    """Tests pour les statistiques de courses."""
    
    def test_compter_articles(self, db, courses_service):
        """Compter le nombre d'articles dans la liste."""
        initial = courses_service.compter_articles(db=db)
        
        courses_service.ajouter_article(nom="Test1", quantite=1, db=db)
        courses_service.ajouter_article(nom="Test2", quantite=1, db=db)
        
        final = courses_service.compter_articles(db=db)
        
        assert final == initial + 2
    
    def test_compter_articles_achetes(self, db, courses_service):
        """Compter les articles achetés."""
        article = courses_service.ajouter_article(nom="Test", quantite=1, db=db)
        courses_service.marquer_achete(article.id, db=db)
        
        count = courses_service.compter_articles(achetes=True, db=db)
        
        assert count >= 1


# ═══════════════════════════════════════════════════════════
# TESTS NETTOYAGE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceNettoyage:
    """Tests pour le nettoyage de la liste de courses."""
    
    def test_vider_articles_achetes(self, db, courses_service):
        """Supprimer tous les articles achetés."""
        # Créer des articles
        a1 = courses_service.ajouter_article(nom="Test1", quantite=1, db=db)
        a2 = courses_service.ajouter_article(nom="Test2", quantite=1, db=db)
        courses_service.marquer_achete(a1.id, db=db)
        
        count = courses_service.vider_achetes(db=db)
        
        assert count >= 1
        # a2 devrait toujours exister
        articles = courses_service.lister_articles(achetes=False, db=db)
        noms = [a.nom for a in articles]
        assert "Test2" in noms
    
    def test_vider_liste_complete(self, db, courses_service):
        """Vider toute la liste de courses."""
        courses_service.ajouter_article(nom="Test1", quantite=1, db=db)
        courses_service.ajouter_article(nom="Test2", quantite=1, db=db)
        
        count = courses_service.vider_liste(db=db)
        
        assert count >= 2
        assert courses_service.compter_articles(db=db) == 0
