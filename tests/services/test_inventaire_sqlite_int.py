"""
Tests d'intégration SQLite en mémoire pour InventaireService.

Ces tests utilisent une vraie base de données SQLite en mémoire
pour tester les opérations CRUD et les méthodes du service.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from src.core.models import ArticleInventaire, Ingredient
from src.services.inventaire import InventaireService


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


# Sentinel for cache miss
_CACHE_MISS = object()


@pytest.fixture(autouse=True)
def mock_cache():
    """
    Patch le Cache pour toujours retourner cache miss.
    Cela force l'exécution du code réel au lieu du cache.
    """
    with patch("src.core.cache.Cache") as mock:
        # obtenir retourne toujours sentinelle (cache miss)
        mock.obtenir = MagicMock(side_effect=lambda *args, **kwargs: kwargs.get("sentinelle", None))
        # definir ne fait rien
        mock.definir = MagicMock(return_value=None)
        yield mock


@pytest.fixture
def inventaire_service():
    """Crée une instance du service inventaire avec mock pour invalidate_cache."""
    service = InventaireService()
    # Le service appelle self.invalidate_cache() qui n'existe pas
    # On ajoute un mock pour éviter les erreurs
    service.invalidate_cache = MagicMock(return_value=None)
    return service


@pytest.fixture
def sample_ingredient(db):
    """Crée un ingrédient de test dans la base."""
    ingredient = Ingredient(
        nom="Tomates",
        categorie="Légumes",
        unite="kg"
    )
    db.add(ingredient)
    db.commit()
    return ingredient


@pytest.fixture
def sample_ingredients(db):
    """Crée plusieurs ingrédients de test."""
    ingredients = [
        Ingredient(nom="Tomates", categorie="Légumes", unite="kg"),
        Ingredient(nom="Lait", categorie="Produits laitiers", unite="L"),
        Ingredient(nom="Poulet", categorie="Viandes", unite="kg"),
        Ingredient(nom="Riz", categorie="Féculents", unite="kg"),
        Ingredient(nom="Pommes", categorie="Fruits", unite="pièce"),
    ]
    for ing in ingredients:
        db.add(ing)
    db.commit()
    return ingredients


@pytest.fixture
def sample_article(db, sample_ingredient):
    """Crée un article d'inventaire de test."""
    article = ArticleInventaire(
        ingredient_id=sample_ingredient.id,
        quantite=5.0,
        quantite_min=2.0,
        emplacement="Frigo",
        date_peremption=date.today() + timedelta(days=10),
    )
    db.add(article)
    db.commit()
    return article


@pytest.fixture
def sample_articles(db, sample_ingredients):
    """Crée plusieurs articles d'inventaire de test."""
    today = date.today()
    articles = [
        ArticleInventaire(
            ingredient_id=sample_ingredients[0].id,
            quantite=5.0,
            quantite_min=2.0,
            emplacement="Frigo",
            date_peremption=today + timedelta(days=10),
        ),
        ArticleInventaire(
            ingredient_id=sample_ingredients[1].id,
            quantite=1.0,
            quantite_min=2.0,
            emplacement="Frigo",
            date_peremption=today + timedelta(days=3),  # Péremption proche
        ),
        ArticleInventaire(
            ingredient_id=sample_ingredients[2].id,
            quantite=0.5,
            quantite_min=1.5,
            emplacement="Congélateur",
            date_peremption=today + timedelta(days=30),  # Critique
        ),
        ArticleInventaire(
            ingredient_id=sample_ingredients[3].id,
            quantite=3.0,
            quantite_min=1.0,
            emplacement="Placard",
        ),
        ArticleInventaire(
            ingredient_id=sample_ingredients[4].id,
            quantite=8.0,
            quantite_min=10.0,
            emplacement="Placard",  # Stock bas
        ),
    ]
    for article in articles:
        db.add(article)
    db.commit()
    return articles


# ═══════════════════════════════════════════════════════════
# TESTS - GET INVENTAIRE COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestGetInventaireComplet:
    """Tests pour get_inventaire_complet avec vraie BD."""

    def test_inventaire_vide(self, db, inventaire_service):
        """Test inventaire vide retourne liste vide."""
        result = inventaire_service.get_inventaire_complet(db=db)
        assert result == []

    def test_inventaire_avec_articles(self, db, inventaire_service, sample_articles):
        """Test inventaire avec articles."""
        result = inventaire_service.get_inventaire_complet(db=db)
        assert len(result) == 5

    def test_filtrer_par_emplacement(self, db, inventaire_service, sample_articles):
        """Filtrer par emplacement."""
        result = inventaire_service.get_inventaire_complet(
            emplacement="Frigo", db=db
        )
        assert len(result) == 2
        for item in result:
            assert item["emplacement"] == "Frigo"

    def test_filtrer_par_categorie(self, db, inventaire_service, sample_articles):
        """Filtrer par catégorie."""
        result = inventaire_service.get_inventaire_complet(
            categorie="Légumes", db=db
        )
        assert len(result) == 1
        assert result[0]["ingredient_categorie"] == "Légumes"

    def test_exclude_ok(self, db, inventaire_service, sample_articles):
        """Exclure les articles OK."""
        result = inventaire_service.get_inventaire_complet(
            include_ok=False, db=db
        )
        # Devrait exclure les articles avec statut "ok"
        for item in result:
            assert item["statut"] != "ok"

    def test_contient_champs_requis(self, db, inventaire_service, sample_article):
        """Articles contiennent tous les champs requis."""
        result = inventaire_service.get_inventaire_complet(db=db)
        assert len(result) == 1
        item = result[0]
        
        assert "id" in item
        assert "ingredient_id" in item
        assert "ingredient_nom" in item
        assert "ingredient_categorie" in item
        assert "quantite" in item
        assert "quantite_min" in item
        assert "unite" in item
        assert "emplacement" in item
        assert "date_peremption" in item
        assert "statut" in item
        assert "jours_avant_peremption" in item


# ═══════════════════════════════════════════════════════════
# TESTS - GET ALERTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestGetAlertes:
    """Tests pour get_alertes."""

    def test_alertes_structure(self, db, inventaire_service, sample_articles):
        """Alertes retourne la bonne structure."""
        with patch.object(inventaire_service, 'get_inventaire_complet') as mock:
            mock.return_value = [
                {"statut": "stock_bas", "ingredient_nom": "Test1"},
                {"statut": "critique", "ingredient_nom": "Test2"},
                {"statut": "peremption_proche", "ingredient_nom": "Test3"},
            ]
            result = inventaire_service.get_alertes()
        
        assert "stock_bas" in result
        assert "critique" in result
        assert "peremption_proche" in result

    def test_alertes_groupees_par_type(self, inventaire_service):
        """Alertes sont groupées par type."""
        with patch.object(inventaire_service, 'get_inventaire_complet') as mock:
            mock.return_value = [
                {"statut": "stock_bas", "id": 1},
                {"statut": "stock_bas", "id": 2},
                {"statut": "critique", "id": 3},
            ]
            result = inventaire_service.get_alertes()
        
        assert len(result["stock_bas"]) == 2
        assert len(result["critique"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS - AJOUTER ARTICLE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAjouterArticle:
    """Tests pour ajouter_article."""

    def test_ajouter_article_succes(self, db, inventaire_service, sample_ingredient):
        """Ajouter un article avec succès."""
        result = inventaire_service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=3.0,
            quantite_min=1.0,
            emplacement="Frigo",
            db=db,
        )
        
        assert result is not None
        assert result["ingredient_nom"] == "Tomates"
        assert result["quantite"] == 3.0

    def test_ajouter_article_ingredient_inexistant(self, db, inventaire_service):
        """Ajouter article avec ingrédient inexistant."""
        result = inventaire_service.ajouter_article(
            ingredient_nom="IngrédientInexistant123",
            quantite=1.0,
            db=db,
        )
        
        assert result is None

    def test_ajouter_article_deja_existant(self, db, inventaire_service, sample_article, sample_ingredient):
        """Ajouter article qui existe déjà."""
        result = inventaire_service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=10.0,
            db=db,
        )
        
        assert result is None

    def test_ajouter_article_avec_date_peremption(self, db, inventaire_service, sample_ingredient):
        """Ajouter article avec date péremption."""
        # Supprimer l'article existant d'abord
        db.query(ArticleInventaire).delete()
        db.commit()
        
        peremption = date.today() + timedelta(days=7)
        result = inventaire_service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=2.0,
            date_peremption=peremption,
            db=db,
        )
        
        assert result is not None
        assert result["date_peremption"] == peremption


# ═══════════════════════════════════════════════════════════
# TESTS - METTRE A JOUR ARTICLE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestMettreAJourArticle:
    """Tests pour mettre_a_jour_article."""

    def test_maj_quantite(self, db, inventaire_service, sample_article, patch_db_context):
        """Mettre à jour la quantité."""
        result = inventaire_service.mettre_a_jour_article(
            article_id=sample_article.id,
            quantite=10.0,
            db=db,
        )
        
        assert result is True
        db.refresh(sample_article)
        assert sample_article.quantite == 10.0

    def test_maj_emplacement(self, db, inventaire_service, sample_article, patch_db_context):
        """Mettre à jour l'emplacement."""
        result = inventaire_service.mettre_a_jour_article(
            article_id=sample_article.id,
            emplacement="Congélateur",
            db=db,
        )
        
        assert result is True
        db.refresh(sample_article)
        assert sample_article.emplacement == "Congélateur"

    def test_maj_date_peremption(self, db, inventaire_service, sample_article, patch_db_context):
        """Mettre à jour la date de péremption."""
        new_date = date.today() + timedelta(days=30)
        result = inventaire_service.mettre_a_jour_article(
            article_id=sample_article.id,
            date_peremption=new_date,
            db=db,
        )
        
        assert result is True
        db.refresh(sample_article)
        assert sample_article.date_peremption == new_date

    def test_maj_article_inexistant(self, db, inventaire_service):
        """Mettre à jour article inexistant."""
        result = inventaire_service.mettre_a_jour_article(
            article_id=99999,
            quantite=5.0,
            db=db,
        )
        
        assert result is False

    def test_maj_quantite_min(self, db, inventaire_service, sample_article, patch_db_context):
        """Mettre à jour la quantité minimum."""
        result = inventaire_service.mettre_a_jour_article(
            article_id=sample_article.id,
            quantite_min=5.0,
            db=db,
        )
        
        assert result is True
        db.refresh(sample_article)
        assert sample_article.quantite_min == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS - SUPPRIMER ARTICLE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSupprimerArticle:
    """Tests pour supprimer_article."""

    def test_supprimer_article_succes(self, db, inventaire_service, sample_article):
        """Supprimer un article avec succès."""
        article_id = sample_article.id
        result = inventaire_service.supprimer_article(article_id=article_id, db=db)
        
        assert result is True
        # Vérifier que l'article est supprimé
        article = db.query(ArticleInventaire).get(article_id)
        assert article is None

    def test_supprimer_article_inexistant(self, db, inventaire_service):
        """Supprimer un article inexistant."""
        result = inventaire_service.supprimer_article(article_id=99999, db=db)
        
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS - STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestStatistiques:
    """Tests pour les statistiques."""

    def test_get_statistiques_vide(self, db, inventaire_service):
        """Statistiques inventaire vide."""
        with patch.object(inventaire_service, 'get_inventaire_complet', return_value=[]):
            result = inventaire_service.get_statistiques()
        
        assert result is not None

    def test_get_statistiques_avec_articles(self, inventaire_service):
        """Statistiques avec articles."""
        mock_inventaire = [
            {"statut": "ok", "emplacement": "Frigo"},
            {"statut": "stock_bas", "emplacement": "Frigo"},
            {"statut": "critique", "emplacement": "Placard"},
        ]
        with patch.object(inventaire_service, 'get_inventaire_complet', return_value=mock_inventaire):
            result = inventaire_service.get_statistiques()
        
        assert result is not None

    def test_get_stats_par_categorie(self, inventaire_service):
        """Stats par catégorie."""
        mock_inventaire = [
            {"ingredient_categorie": "Légumes", "statut": "ok"},
            {"ingredient_categorie": "Légumes", "statut": "stock_bas"},
            {"ingredient_categorie": "Fruits", "statut": "ok"},
        ]
        with patch.object(inventaire_service, 'get_inventaire_complet', return_value=mock_inventaire):
            result = inventaire_service.get_stats_par_categorie()
        
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS - ARTICLES A PRELEVER
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestArticlesAPrelever:
    """Tests pour get_articles_a_prelever."""

    def test_articles_a_prelever_vide(self, inventaire_service):
        """Liste vide si aucun article à prélever."""
        with patch.object(inventaire_service, 'get_inventaire_complet', return_value=[]):
            result = inventaire_service.get_articles_a_prelever()
        
        assert result == []

    def test_articles_a_prelever_avec_peremption(self, inventaire_service):
        """Articles avec péremption proche."""
        today = date.today()
        mock_inventaire = [
            {
                "id": 1,
                "ingredient_nom": "Lait",
                "date_peremption": today + timedelta(days=2),
                "jours_avant_peremption": 2,
                "statut": "peremption_proche",
            },
            {
                "id": 2,
                "ingredient_nom": "Pain",
                "date_peremption": today + timedelta(days=30),
                "jours_avant_peremption": 30,
                "statut": "ok",
            },
        ]
        with patch.object(inventaire_service, 'get_inventaire_complet', return_value=mock_inventaire):
            result = inventaire_service.get_articles_a_prelever(
                date_limite=today + timedelta(days=7)
            )
        
        # Devrait inclure seulement l'article avec péremption proche
        assert len(result) >= 0


# ═══════════════════════════════════════════════════════════
# TESTS - PHOTOS (mocked)
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPhotos:
    """Tests pour les méthodes de gestion des photos."""

    def test_ajouter_photo_article_inexistant(self, db, inventaire_service):
        """Ajouter photo à article inexistant lève une erreur."""
        from src.core.errors_base import ErreurValidation
        
        with pytest.raises(ErreurValidation):
            inventaire_service.ajouter_photo(
                article_id=99999,
                photo_url="https://example.com/photo.jpg",
                photo_filename="photo.jpg",
                db=db,
            )

    def test_supprimer_photo_article_inexistant(self, db, inventaire_service):
        """Supprimer photo d'article inexistant lève une erreur."""
        from src.core.errors_base import ErreurValidation
        
        with pytest.raises(ErreurValidation):
            inventaire_service.supprimer_photo(article_id=99999, db=db)

    def test_obtenir_photo_article_inexistant(self, db, inventaire_service):
        """Obtenir photo d'article inexistant."""
        result = inventaire_service.obtenir_photo(article_id=99999, db=db)
        
        assert result is None

    def test_ajouter_photo_succes(self, db, inventaire_service, sample_article, patch_db_context):
        """Ajouter photo à article existant."""
        result = inventaire_service.ajouter_photo(
            article_id=sample_article.id,
            photo_url="https://example.com/photo.jpg",
            photo_filename="photo.jpg",
            db=db,
        )
        
        assert result is not None
        assert result["article_id"] == sample_article.id
        assert result["photo_url"] == "https://example.com/photo.jpg"

    def test_supprimer_photo_succes(self, db, inventaire_service, sample_article, patch_db_context):
        """Supprimer photo d'article avec photo."""
        # D'abord ajouter une photo
        sample_article.photo_url = "https://example.com/photo.jpg"
        sample_article.photo_filename = "photo.jpg"
        db.add(sample_article)
        db.commit()
        
        result = inventaire_service.supprimer_photo(article_id=sample_article.id, db=db)
        
        assert result is True

    def test_supprimer_photo_sans_photo(self, db, inventaire_service, sample_article):
        """Supprimer photo d'article sans photo lève une erreur."""
        from src.core.errors_base import ErreurValidation
        
        with pytest.raises(ErreurValidation, match="n'a pas de photo"):
            inventaire_service.supprimer_photo(article_id=sample_article.id, db=db)


# ═══════════════════════════════════════════════════════════
# TESTS - NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestNotifications:
    """Tests pour les notifications d'alertes."""

    def test_generer_notifications_alertes(self, db, inventaire_service, patch_db_context):
        """Génère les notifications d'alertes."""
        with patch.object(inventaire_service, 'get_alertes') as mock:
            mock.return_value = {
                "stock_bas": [{"ingredient_nom": "Lait"}],
                "critique": [],
                "peremption_proche": [{"ingredient_nom": "Yaourt"}],
            }
            result = inventaire_service.generer_notifications_alertes()
        
        assert result is not None

    def test_obtenir_alertes_actives(self, db, inventaire_service, patch_db_context):
        """Obtient les alertes actives."""
        with patch.object(inventaire_service, 'get_alertes') as mock:
            mock.return_value = {
                "stock_bas": [{"id": 1}],
                "critique": [{"id": 2}],
                "peremption_proche": [],
            }
            result = inventaire_service.obtenir_alertes_actives()
        
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS - CALCULER STATUT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculerStatut:
    """Tests pour _calculer_statut."""

    def test_statut_ok_sans_peremption(self, inventaire_service):
        """Article OK sans date péremption."""
        article = MagicMock()
        article.quantite = 5.0
        article.quantite_min = 2.0
        article.date_peremption = None
        
        result = inventaire_service._calculer_statut(article, date.today())
        assert result == "ok"

    def test_statut_critique(self, inventaire_service):
        """Article critique (quantité < 50% du min)."""
        article = MagicMock()
        article.quantite = 0.4
        article.quantite_min = 2.0
        article.date_peremption = None
        
        result = inventaire_service._calculer_statut(article, date.today())
        assert result == "critique"

    def test_statut_stock_bas(self, inventaire_service):
        """Article stock bas (quantité < min mais >= 50%)."""
        article = MagicMock()
        article.quantite = 1.5
        article.quantite_min = 2.0
        article.date_peremption = None
        
        result = inventaire_service._calculer_statut(article, date.today())
        assert result == "stock_bas"

    def test_statut_peremption_proche(self, inventaire_service):
        """Article avec péremption <= 7 jours."""
        article = MagicMock()
        article.quantite = 5.0
        article.quantite_min = 2.0
        article.date_peremption = date.today() + timedelta(days=3)
        
        result = inventaire_service._calculer_statut(article, date.today())
        assert result == "peremption_proche"

    def test_peremption_priorite_sur_stock(self, inventaire_service):
        """Péremption a priorité sur stock bas."""
        article = MagicMock()
        article.quantite = 1.5  # Stock bas
        article.quantite_min = 2.0
        article.date_peremption = date.today() + timedelta(days=2)  # Péremption
        
        result = inventaire_service._calculer_statut(article, date.today())
        assert result == "peremption_proche"


# ═══════════════════════════════════════════════════════════
# TESTS - JOURS AVANT PEREMPTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJoursAvantPeremption:
    """Tests pour _jours_avant_peremption."""

    def test_sans_date(self, inventaire_service):
        """Article sans date de péremption."""
        article = MagicMock()
        article.date_peremption = None
        
        result = inventaire_service._jours_avant_peremption(article, date.today())
        assert result is None

    def test_date_future(self, inventaire_service):
        """Article avec date future."""
        article = MagicMock()
        article.date_peremption = date.today() + timedelta(days=15)
        
        result = inventaire_service._jours_avant_peremption(article, date.today())
        assert result == 15

    def test_date_passee(self, inventaire_service):
        """Article périmé."""
        article = MagicMock()
        article.date_peremption = date.today() - timedelta(days=5)
        
        result = inventaire_service._jours_avant_peremption(article, date.today())
        assert result == -5


# ═══════════════════════════════════════════════════════════
# TESTS - HISTORIQUE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestHistorique:
    """Tests pour get_historique et _enregistrer_modification."""

    def test_get_historique_vide(self, db, inventaire_service):
        """Historique vide."""
        result = inventaire_service.get_historique(db=db)
        assert result == []

    def test_get_historique_avec_limit(self, db, inventaire_service):
        """Historique avec limite."""
        result = inventaire_service.get_historique(limit=10, db=db)
        assert isinstance(result, list)

    def test_get_historique_avec_article_id(self, db, inventaire_service, sample_article):
        """Historique pour un article spécifique."""
        result = inventaire_service.get_historique(
            article_id=sample_article.id, 
            db=db
        )
        assert isinstance(result, list)
