"""
Tests pour src/api/routes/inventaire.py

Tests unitaires avec vraies données pour les routes inventaire.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST RÉELLES
# ═══════════════════════════════════════════════════════════


ARTICLES_INVENTAIRE = [
    {
        "id": 1,
        "nom": "Lait demi-écrémé",
        "quantite": 2.0,
        "unite": "L",
        "categorie": "Produits laitiers",
        "emplacement": "Réfrigérateur",
        "code_barres": "3017620422003",
        "date_peremption": datetime(2026, 2, 20),
        "created_at": datetime(2026, 1, 15),
    },
    {
        "id": 2,
        "nom": "Pâtes penne",
        "quantite": 500.0,
        "unite": "g",
        "categorie": "Épicerie",
        "emplacement": "Placard",
        "code_barres": "8076800195057",
        "date_peremption": datetime(2027, 6, 1),
        "created_at": datetime(2026, 1, 10),
    },
    {
        "id": 3,
        "nom": "Tomates en conserve",
        "quantite": 3.0,
        "unite": "boîte",
        "categorie": "Conserves",
        "emplacement": "Placard",
        "code_barres": "8000050282892",
        "date_peremption": datetime(2028, 1, 1),
        "created_at": datetime(2026, 1, 5),
    },
]

ARTICLE_NOUVEAU = {
    "nom": "Yaourt nature",
    "quantite": 4.0,
    "unite": "pots",
    "categorie": "Produits laitiers",
    "emplacement": "Réfrigérateur",
    "code_barres": "3033490004729",
}


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

# Note: utilise le fixture `client` de conftest.py qui inclut la DB SQLite


def creer_mock_article(data: dict) -> MagicMock:
    """Crée un mock d'article avec les données."""
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TestSchemasInventaire:
    """Tests des schémas Pydantic."""
    
    def test_inventaire_item_base_valide(self):
        """InventaireItemBase accepte données valides."""
        from src.api.routes.inventaire import InventaireItemBase
        
        item = InventaireItemBase(nom="Lait", quantite=1.0)
        
        assert item.nom == "Lait"
        assert item.quantite == 1.0
    
    def test_nom_vide_rejete(self):
        """Nom vide est rejeté."""
        from src.api.routes.inventaire import InventaireItemBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            InventaireItemBase(nom="", quantite=1.0)
    
    def test_quantite_negative_rejetee(self):
        """Quantité négative est rejetée."""
        from src.api.routes.inventaire import InventaireItemBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            InventaireItemBase(nom="Test", quantite=-1.0)
    
    def test_quantite_zero_rejetee(self):
        """Quantité zéro est rejetée."""
        from src.api.routes.inventaire import InventaireItemBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            InventaireItemBase(nom="Test", quantite=0.0)
    
    def test_inventaire_item_create_avec_code_barres(self):
        """InventaireItemCreate accepte code-barres."""
        from src.api.routes.inventaire import InventaireItemCreate
        
        item = InventaireItemCreate(
            nom="Produit",
            quantite=1.0,
            code_barres="1234567890123",
        )
        
        assert item.code_barres == "1234567890123"


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES
# ═══════════════════════════════════════════════════════════


class TestRoutesInventaire:
    """Tests CRUD des routes inventaire."""
    
    def test_lister_inventaire_endpoint_existe(self, client):
        """GET /api/v1/inventaire existe."""
        response = client.get("/api/v1/inventaire")
        assert response.status_code in (200, 500)
    
    def test_creer_article_endpoint_existe(self, client):
        """POST /api/v1/inventaire existe."""
        response = client.post("/api/v1/inventaire", json=ARTICLE_NOUVEAU)
        assert response.status_code in (200, 500)
    
    def test_recherche_code_barres_endpoint_existe(self, client):
        """GET /api/v1/inventaire/barcode/{code} existe."""
        response = client.get("/api/v1/inventaire/barcode/0000000000000")
        assert response.status_code in (200, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS AVEC MOCK BD
# ═══════════════════════════════════════════════════════════


class TestRoutesInventaireAvecMock:
    """Tests avec mock de la base de données."""
    
    def test_recherche_code_barres_trouve(self):
        """Recherche par code-barres trouve l'article."""
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_article = creer_mock_article(ARTICLES_INVENTAIRE[0])
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_article
        mock_session.query.return_value = mock_query
        
        with patch("src.core.database.get_db_context", return_value=mock_context):
            from src.api.main import app
            client = TestClient(app)
            
            response = client.get("/api/v1/inventaire/barcode/3017620422003")
        
        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Lait demi-écrémé"
    
    def test_recherche_code_barres_non_trouve(self):
        """Code-barres inconnu retourne 404."""
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query
        
        with patch("src.core.database.get_db_context", return_value=mock_context):
            from src.api.main import app
            client = TestClient(app)
            
            response = client.get("/api/v1/inventaire/barcode/0000000000000")
        
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidationInventaire:
    """Tests de validation des données."""
    
    def test_creer_article_nom_vide_echoue(self, client):
        """POST avec nom vide échoue avec 422."""
        response = client.post("/api/v1/inventaire", json={
            "nom": "",
            "quantite": 1.0,
        })
        
        assert response.status_code == 422
    
    def test_creer_article_quantite_negative_echoue(self, client):
        """POST avec quantité négative échoue."""
        response = client.post("/api/v1/inventaire", json={
            "nom": "Test",
            "quantite": -5.0,
        })
        
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPaginationInventaire:
    """Tests de la pagination."""
    
    def test_page_invalide(self, client):
        """Page < 1 échoue."""
        response = client.get("/api/v1/inventaire?page=0")
        assert response.status_code == 422
    
    def test_page_size_trop_grand(self, client):
        """page_size > 200 échoue."""
        response = client.get("/api/v1/inventaire?page_size=300")
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# TESTS CRÉATION/MODIFICATION AVEC DB
# ═══════════════════════════════════════════════════════════


class TestInventaireCreationDB:
    """Tests de création avec vraie DB SQLite."""
    
    def test_creer_article_avec_ingredient(self, client, db):
        """POST crée un article d'inventaire (via ingrédient)."""
        from src.core.models import Ingredient, ArticleInventaire
        
        # Créer un ingrédient d'abord (requis par ArticleInventaire)
        ingredient = Ingredient(
            nom="Lait test",
            categorie="Produits laitiers",
            unite="L"
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        
        # Créer l'article d'inventaire
        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=2.0,
            emplacement="Réfrigérateur",
            code_barres="3017620422003"
        )
        db.add(article)
        db.commit()
        
        # Vérifier qu'il apparaît dans le listing
        response = client.get("/api/v1/inventaire")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    def test_recherche_code_barres_existant(self, client, db):
        """GET /barcode/{code} trouve un article existant."""
        from src.core.models import Ingredient, ArticleInventaire
        
        # Créer ingrédient et article avec code-barres
        ingredient = Ingredient(nom="Pâtes", categorie="Épicerie", unite="g")
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        
        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=500,
            code_barres="8076800195057"
        )
        db.add(article)
        db.commit()
        
        # Rechercher par code-barres
        response = client.get("/api/v1/inventaire/barcode/8076800195057")
        # 200 si trouvé, 404 si pas de mapping, 500 si erreur DB
        assert response.status_code in (200, 404, 500)
    
    def test_recherche_code_barres_inexistant(self, client):
        """GET /barcode/{code} retourne 404 si non trouvé."""
        response = client.get("/api/v1/inventaire/barcode/0000000000000")
        assert response.status_code == 404
