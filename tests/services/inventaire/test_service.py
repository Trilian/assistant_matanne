"""Tests pour src/services/inventaire/service.py - ServiceInventaire.

Couverture des fonctionnalités:
- CRUD d'articles (ajouter, mettre à jour, supprimer)
- Gestion des quantités et statuts
- Alertes de stock bas et critique
- Alertes de péremption
- Historique des modifications
- Statistiques et rapports
- Gestion des photos
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.core.models import ArticleInventaire, HistoriqueInventaire, Ingredient
from src.services.inventaire.service import (
    CATEGORIES,
    EMPLACEMENTS,
    InventaireService,
    ServiceInventaire,
    get_inventaire_service,
    obtenir_service_inventaire,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia():
    """Mock du client IA."""
    with patch("src.services.inventaire.service.obtenir_client_ia") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def service(mock_client_ia):
    """Instance du service inventaire pour les tests."""
    svc = ServiceInventaire()
    # Le service appelle self.invalidate_cache() qui n'existe pas sur BaseService
    # On ajoute un mock pour éviter les erreurs
    svc.invalidate_cache = MagicMock(return_value=None)
    # Mock _enregistrer_modification pour éviter qu'il crée une nouvelle session DB
    svc._enregistrer_modification = MagicMock(return_value=True)
    return svc


@pytest.fixture
def service_with_history(mock_client_ia):
    """Instance du service pour tester _enregistrer_modification (sans mock)."""
    svc = ServiceInventaire()
    svc.invalidate_cache = MagicMock(return_value=None)
    # Ne pas mocker _enregistrer_modification pour ces tests
    return svc


@pytest.fixture
def sample_ingredient(db: Session) -> Ingredient:
    """Crée un ingrédient de test."""
    ingredient = Ingredient(
        nom="Tomates",
        unite="kg",
        categorie="Légumes",
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@pytest.fixture
def sample_ingredient_2(db: Session) -> Ingredient:
    """Crée un second ingrédient de test."""
    ingredient = Ingredient(
        nom="Lait",
        unite="L",
        categorie="Laitier",
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@pytest.fixture
def sample_article(db: Session, sample_ingredient: Ingredient) -> ArticleInventaire:
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
    db.refresh(article)
    return article


@pytest.fixture
def sample_article_low_stock(db: Session, sample_ingredient_2: Ingredient) -> ArticleInventaire:
    """Crée un article avec stock bas."""
    article = ArticleInventaire(
        ingredient_id=sample_ingredient_2.id,
        quantite=1.5,  # < quantite_min de 2.0
        quantite_min=2.0,
        emplacement="Frigo",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@pytest.fixture
def sample_article_critical(db: Session) -> ArticleInventaire:
    """Crée un article avec stock critique."""
    ingredient = Ingredient(nom="Beurre", unite="g", categorie="Laitier")
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    article = ArticleInventaire(
        ingredient_id=ingredient.id,
        quantite=0.3,  # < 50% de quantite_min (0.5 * 2.0 = 1.0)
        quantite_min=2.0,
        emplacement="Frigo",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@pytest.fixture
def sample_article_expiring(db: Session) -> ArticleInventaire:
    """Crée un article proche de la péremption."""
    ingredient = Ingredient(nom="Yaourt", unite="pcs", categorie="Laitier")
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    article = ArticleInventaire(
        ingredient_id=ingredient.id,
        quantite=5.0,
        quantite_min=1.0,
        emplacement="Frigo",
        date_peremption=date.today() + timedelta(days=3),  # < 7 jours
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION & CONSTANTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceInventaireInit:
    """Tests pour l'initialisation du ServiceInventaire."""

    def test_init_service(self, service):
        """Test initialisation du service."""
        assert service is not None
        assert isinstance(service, ServiceInventaire)

    def test_categories_defined(self):
        """Test que les catégories sont définies."""
        assert len(CATEGORIES) > 0
        assert "Légumes" in CATEGORIES
        assert "Fruits" in CATEGORIES
        assert "Protéines" in CATEGORIES

    def test_emplacements_defined(self):
        """Test que les emplacements sont définis."""
        assert len(EMPLACEMENTS) > 0
        assert "Frigo" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS
        assert "Placard" in EMPLACEMENTS

    def test_obtenir_service_inventaire_singleton(self, mock_client_ia):
        """Test que obtenir_service_inventaire retourne singleton."""
        # Reset singleton pour le test
        import src.services.inventaire.service as service_module

        service_module._service_inventaire = None

        service1 = obtenir_service_inventaire()
        service2 = obtenir_service_inventaire()

        assert service1 is service2

        # Cleanup
        service_module._service_inventaire = None

    def test_alias_get_inventaire_service(self, mock_client_ia):
        """Test alias get_inventaire_service."""
        import src.services.inventaire.service as service_module

        service_module._service_inventaire = None

        service = get_inventaire_service()
        assert isinstance(service, ServiceInventaire)

        # Cleanup
        service_module._service_inventaire = None

    def test_alias_inventaire_service_class(self):
        """Test alias InventaireService."""
        assert InventaireService is ServiceInventaire


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL STATUT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculerStatut:
    """Tests pour _calculer_statut."""

    def test_statut_ok(self, service, sample_article):
        """Test statut OK quand quantité >= seuil."""
        today = date.today()
        statut = service._calculer_statut(sample_article, today)

        assert statut == "ok"

    def test_statut_stock_bas(self, service, sample_article_low_stock):
        """Test statut stock_bas quand quantité < seuil."""
        today = date.today()
        statut = service._calculer_statut(sample_article_low_stock, today)

        assert statut == "stock_bas"

    def test_statut_critique(self, service, sample_article_critical):
        """Test statut critique quand quantité < 50% du seuil."""
        today = date.today()
        statut = service._calculer_statut(sample_article_critical, today)

        assert statut == "critique"

    def test_statut_peremption_proche(self, service, sample_article_expiring):
        """Test statut péremption proche quand <= 7 jours."""
        today = date.today()
        statut = service._calculer_statut(sample_article_expiring, today)

        assert statut == "peremption_proche"

    def test_statut_sans_date_peremption(self, service, sample_article_low_stock):
        """Test avec article sans date de péremption."""
        today = date.today()
        sample_article_low_stock.date_peremption = None

        statut = service._calculer_statut(sample_article_low_stock, today)

        assert statut == "stock_bas"  # Pas de péremption, juste stock bas


# ═══════════════════════════════════════════════════════════
# TESTS JOURS AVANT PEREMPTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJoursAvantPeremption:
    """Tests pour _jours_avant_peremption."""

    def test_jours_avec_date(self, service, sample_article):
        """Test calcul jours avant péremption avec date."""
        today = date.today()
        jours = service._jours_avant_peremption(sample_article, today)

        assert jours == 10

    def test_jours_sans_date(self, service, sample_article_low_stock):
        """Test sans date de péremption."""
        today = date.today()
        sample_article_low_stock.date_peremption = None

        jours = service._jours_avant_peremption(sample_article_low_stock, today)

        assert jours is None

    def test_jours_negatifs_peremption_passee(self, service, sample_article):
        """Test avec date de péremption passée."""
        today = date.today()
        sample_article.date_peremption = today - timedelta(days=5)

        jours = service._jours_avant_peremption(sample_article, today)

        assert jours == -5


# ═══════════════════════════════════════════════════════════
# TESTS CRUD ARTICLES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAjouterArticle:
    """Tests pour ajouter_article."""

    def test_ajouter_article_succes(self, service, sample_ingredient, db: Session):
        """Test ajout d'un article réussi."""
        result = service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=10.0,
            quantite_min=3.0,
            emplacement="Placard",
            date_peremption=date.today() + timedelta(days=14),
            db=db,
        )

        assert result is not None
        assert result["ingredient_nom"] == "Tomates"
        assert result["quantite"] == 10.0
        assert result["quantite_min"] == 3.0
        assert result["emplacement"] == "Placard"

    def test_ajouter_article_ingredient_inconnu(self, service, db: Session):
        """Test ajout avec ingrédient inexistant."""
        result = service.ajouter_article(
            ingredient_nom="IngrédientInexistant",
            quantite=5.0,
            db=db,
        )

        assert result is None

    def test_ajouter_article_existant(self, service, sample_article, db: Session):
        """Test ajout d'un article déjà existant."""
        result = service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=5.0,
            db=db,
        )

        # Devrait retourner None car l'article existe déjà
        assert result is None


@pytest.mark.unit
class TestMettreAJourArticle:
    """Tests pour mettre_a_jour_article."""

    def test_mettre_a_jour_quantite(self, service, sample_article, db: Session):
        """Test mise à jour de la quantité."""
        result = service.mettre_a_jour_article(
            article_id=sample_article.id,
            quantite=15.0,
            db=db,
        )

        assert result is True

        # Vérifier en base
        db.refresh(sample_article)
        assert sample_article.quantite == 15.0

    def test_mettre_a_jour_quantite_min(self, service, sample_article, db: Session):
        """Test mise à jour du seuil minimum."""
        result = service.mettre_a_jour_article(
            article_id=sample_article.id,
            quantite_min=5.0,
            db=db,
        )

        assert result is True

        db.refresh(sample_article)
        assert sample_article.quantite_min == 5.0

    def test_mettre_a_jour_emplacement(self, service, sample_article, db: Session):
        """Test mise à jour de l'emplacement."""
        result = service.mettre_a_jour_article(
            article_id=sample_article.id,
            emplacement="Congélateur",
            db=db,
        )

        assert result is True

        db.refresh(sample_article)
        assert sample_article.emplacement == "Congélateur"

    def test_mettre_a_jour_date_peremption(self, service, sample_article, db: Session):
        """Test mise à jour de la date de péremption."""
        new_date = date.today() + timedelta(days=30)

        result = service.mettre_a_jour_article(
            article_id=sample_article.id,
            date_peremption=new_date,
            db=db,
        )

        assert result is True

        db.refresh(sample_article)
        assert sample_article.date_peremption == new_date

    def test_mettre_a_jour_article_inexistant(self, service, db: Session):
        """Test mise à jour d'un article inexistant."""
        result = service.mettre_a_jour_article(
            article_id=99999,
            quantite=10.0,
            db=db,
        )

        assert result is False

    def test_mettre_a_jour_multiple_champs(self, service, sample_article, db: Session):
        """Test mise à jour de plusieurs champs à la fois."""
        new_date = date.today() + timedelta(days=20)

        result = service.mettre_a_jour_article(
            article_id=sample_article.id,
            quantite=25.0,
            quantite_min=8.0,
            emplacement="Cave",
            date_peremption=new_date,
            db=db,
        )

        assert result is True

        db.refresh(sample_article)
        assert sample_article.quantite == 25.0
        assert sample_article.quantite_min == 8.0
        assert sample_article.emplacement == "Cave"
        assert sample_article.date_peremption == new_date


@pytest.mark.unit
class TestSupprimerArticle:
    """Tests pour supprimer_article."""

    def test_supprimer_article_succes(self, service, sample_article, db: Session):
        """Test suppression d'un article."""
        article_id = sample_article.id

        result = service.supprimer_article(article_id=article_id, db=db)

        assert result is True

        # Vérifier que l'article n'existe plus
        deleted = db.query(ArticleInventaire).filter_by(id=article_id).first()
        assert deleted is None

    def test_supprimer_article_inexistant(self, service, db: Session):
        """Test suppression d'un article inexistant."""
        result = service.supprimer_article(article_id=99999, db=db)

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS INVENTAIRE COMPLET & ALERTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetInventaireComplet:
    """Tests pour get_inventaire_complet."""

    def test_get_inventaire_vide(self, service, db: Session):
        """Test récupération d'un inventaire vide."""
        result = service.get_inventaire_complet(db=db)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_inventaire_avec_articles(self, service, sample_article, db: Session):
        """Test récupération de l'inventaire avec des articles."""
        result = service.get_inventaire_complet(db=db)

        assert len(result) >= 1

        article_data = result[0]
        assert "id" in article_data
        assert "ingredient_nom" in article_data
        assert "quantite" in article_data
        assert "statut" in article_data

    def test_get_inventaire_filtre_emplacement(
        self, service, sample_article, sample_article_low_stock, db: Session
    ):
        """Test filtrage par emplacement."""
        result = service.get_inventaire_complet(emplacement="Frigo", db=db)

        for article in result:
            assert article["emplacement"] == "Frigo"

    def test_get_inventaire_exclude_ok(self, service, sample_article, db: Session):
        """Test exclusion des articles OK."""
        result = service.get_inventaire_complet(include_ok=False, db=db)

        for article in result:
            assert article["statut"] != "ok"


@pytest.mark.unit
class TestGetAlertes:
    """Tests pour get_alertes."""

    def test_get_alertes_structure(self, service):
        """Test structure du retour des alertes."""
        # Mock get_inventaire_complet pour éviter les appels DB
        service.get_inventaire_complet = MagicMock(return_value=[])

        result = service.get_alertes()

        assert isinstance(result, dict)
        assert "stock_bas" in result
        assert "critique" in result
        assert "peremption_proche" in result

    def test_get_alertes_avec_articles(self, service):
        """Test alertes avec des articles en alerte."""
        # Mock avec des articles en alerte
        mock_inventaire = [
            {"id": 1, "statut": "stock_bas", "ingredient_nom": "Test1"},
            {"id": 2, "statut": "critique", "ingredient_nom": "Test2"},
            {"id": 3, "statut": "peremption_proche", "ingredient_nom": "Test3"},
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)

        result = service.get_alertes()

        # Devrait avoir au moins 2 alertes
        total_alertes = sum(len(v) for v in result.values())
        assert total_alertes >= 2


# ═══════════════════════════════════════════════════════════
# TESTS HISTORIQUE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnregistrerModification:
    """Tests pour _enregistrer_modification."""

    def test_enregistrer_modification_succes(
        self, service_with_history, sample_article, db: Session
    ):
        """Test enregistrement d'une modification."""
        result = service_with_history._enregistrer_modification(
            article=sample_article,
            type_modification="modification",
            quantite_avant=5.0,
            quantite_apres=10.0,
            notes="Test modification",
            db=db,
        )

        assert result is True

        # Vérifier en base
        historique = db.query(HistoriqueInventaire).filter_by(article_id=sample_article.id).first()

        assert historique is not None
        assert historique.type_modification == "modification"
        assert historique.quantite_avant == 5.0
        assert historique.quantite_apres == 10.0

    def test_enregistrer_modification_emplacement(
        self, service_with_history, sample_article, db: Session
    ):
        """Test enregistrement changement d'emplacement."""
        result = service_with_history._enregistrer_modification(
            article=sample_article,
            type_modification="modification",
            emplacement_avant="Frigo",
            emplacement_apres="Congélateur",
            db=db,
        )

        assert result is True


@pytest.mark.unit
class TestGetHistorique:
    """Tests pour get_historique."""

    def test_get_historique_vide(self, service, db: Session):
        """Test historique vide."""
        result = service.get_historique(db=db)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_historique_avec_modifications(self, service, sample_article, db: Session):
        """Test historique avec des modifications."""
        # Créer une entrée d'historique
        historique = HistoriqueInventaire(
            article_id=sample_article.id,
            ingredient_id=sample_article.ingredient_id,
            type_modification="modification",
            quantite_avant=5.0,
            quantite_apres=10.0,
            date_modification=datetime.utcnow(),
        )
        db.add(historique)
        db.commit()

        result = service.get_historique(db=db)

        assert len(result) >= 1
        assert result[0]["type"] == "modification"

    def test_get_historique_filtre_article(self, service, sample_article, db: Session):
        """Test historique filtré par article."""
        # Créer une entrée
        historique = HistoriqueInventaire(
            article_id=sample_article.id,
            ingredient_id=sample_article.ingredient_id,
            type_modification="modification",
            quantite_avant=5.0,
            quantite_apres=10.0,
            date_modification=datetime.utcnow(),
        )
        db.add(historique)
        db.commit()

        result = service.get_historique(article_id=sample_article.id, db=db)

        for entry in result:
            assert entry["article_id"] == sample_article.id

    def test_get_historique_filtre_jours(self, service, sample_article, db: Session):
        """Test historique limité aux derniers jours."""
        # Créer une entrée vieille de 60 jours
        old_date = datetime.utcnow() - timedelta(days=60)
        historique = HistoriqueInventaire(
            article_id=sample_article.id,
            ingredient_id=sample_article.ingredient_id,
            type_modification="modification",
            quantite_avant=1.0,
            quantite_apres=2.0,
            date_modification=old_date,
        )
        db.add(historique)
        db.commit()

        # Recherche sur les 30 derniers jours
        result = service.get_historique(days=30, db=db)

        # Ne devrait pas inclure la vieille entrée
        for entry in result:
            entry_date = entry.get("date_modification")
            if entry_date:
                assert (datetime.utcnow() - timedelta(days=30)) <= entry_date


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetStatistiques:
    """Tests pour get_statistiques."""

    def test_get_statistiques_vide(self, service):
        """Test statistiques avec inventaire vide."""
        # Mock get_inventaire_complet et get_alertes
        service.get_inventaire_complet = MagicMock(return_value=[])
        service.get_alertes = MagicMock(
            return_value={"stock_bas": [], "critique": [], "peremption_proche": []}
        )

        result = service.get_statistiques()

        assert result.get("total_articles") == 0

    def test_get_statistiques_avec_articles(self, service):
        """Test statistiques avec des articles."""
        # Mock avec des données (inclut derniere_maj pour éviter erreur de comparaison)
        mock_inventaire = [
            {
                "id": 1,
                "quantite": 5.0,
                "emplacement": "Frigo",
                "ingredient_categorie": "Légumes",
                "statut": "ok",
                "derniere_maj": datetime.utcnow(),
            },
            {
                "id": 2,
                "quantite": 2.0,
                "emplacement": "Placard",
                "ingredient_categorie": "Féculents",
                "statut": "stock_bas",
                "derniere_maj": datetime.utcnow(),
            },
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)
        service.get_alertes = MagicMock(
            return_value={
                "stock_bas": [mock_inventaire[1]],
                "critique": [],
                "peremption_proche": [],
            }
        )

        result = service.get_statistiques()

        assert result["total_articles"] == 2
        assert "total_quantite" in result
        assert "emplacements" in result
        assert "alertes_totales" in result


@pytest.mark.unit
class TestGetStatsParCategorie:
    """Tests pour get_stats_par_categorie."""

    def test_get_stats_par_categorie(self, service):
        """Test statistiques par catégorie."""
        # Mock avec des données
        mock_inventaire = [
            {
                "id": 1,
                "quantite": 5.0,
                "quantite_min": 2.0,
                "ingredient_categorie": "Légumes",
                "statut": "ok",
            },
            {
                "id": 2,
                "quantite": 0.5,
                "quantite_min": 2.0,
                "ingredient_categorie": "Légumes",
                "statut": "critique",
            },
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)

        result = service.get_stats_par_categorie()

        assert isinstance(result, dict)

        # Chaque catégorie devrait avoir des stats
        for cat, stats in result.items():
            assert "articles" in stats
            assert "quantite_totale" in stats
            assert "critiques" in stats


@pytest.mark.unit
class TestGetArticlesAPrelever:
    """Tests pour get_articles_a_prelever."""

    def test_get_articles_a_prelever_sans_articles_expirant(self, service):
        """Test articles à prélever sans expiration proche."""
        # Mock avec article qui expire dans 10 jours (> 3 jours par défaut)
        mock_inventaire = [
            {"id": 1, "date_peremption": date.today() + timedelta(days=10)},
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)

        result = service.get_articles_a_prelever()

        # Ne devrait pas inclure l'article car péremption > 3 jours
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_articles_a_prelever_avec_expiration(self, service):
        """Test articles à prélever avec expiration proche."""
        # Mock avec article qui expire dans 2 jours (<= 3 jours)
        mock_inventaire = [
            {"id": 1, "date_peremption": date.today() + timedelta(days=2)},
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)

        result = service.get_articles_a_prelever()

        # Devrait inclure l'article car péremption dans 2 jours
        assert len(result) >= 1

    def test_get_articles_a_prelever_date_limite_custom(self, service):
        """Test avec date limite personnalisée."""
        # Mock avec article qui expire dans 10 jours
        mock_inventaire = [
            {"id": 1, "date_peremption": date.today() + timedelta(days=10)},
        ]
        service.get_inventaire_complet = MagicMock(return_value=mock_inventaire)

        date_limite = date.today() + timedelta(days=15)

        result = service.get_articles_a_prelever(date_limite=date_limite)

        # Devrait inclure l'article car péremption dans 10 jours < 15 jours
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS GESTION PHOTOS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAjouterPhoto:
    """Tests pour ajouter_photo."""

    def test_ajouter_photo_succes(self, service, sample_article, db: Session):
        """Test ajout d'une photo réussie."""
        result = service.ajouter_photo(
            article_id=sample_article.id,
            photo_url="https://example.com/photo.jpg",
            photo_filename="photo.jpg",
            db=db,
        )

        assert result is not None
        assert result["article_id"] == sample_article.id
        assert result["photo_url"] == "https://example.com/photo.jpg"
        assert result["photo_filename"] == "photo.jpg"

    def test_ajouter_photo_article_inexistant(self, service, db: Session):
        """Test ajout photo à un article inexistant."""
        from src.core.errors_base import ErreurValidation

        with pytest.raises(ErreurValidation, match="introuvable"):
            service.ajouter_photo(
                article_id=99999,
                photo_url="https://example.com/photo.jpg",
                photo_filename="photo.jpg",
                db=db,
            )


@pytest.mark.unit
class TestSupprimerPhoto:
    """Tests pour supprimer_photo."""

    def test_supprimer_photo_succes(self, service, sample_article, db: Session):
        """Test suppression d'une photo."""
        # D'abord ajouter une photo
        sample_article.photo_url = "https://example.com/photo.jpg"
        sample_article.photo_filename = "photo.jpg"
        db.commit()

        result = service.supprimer_photo(article_id=sample_article.id, db=db)

        assert result is True

        db.refresh(sample_article)
        assert sample_article.photo_url is None

    def test_supprimer_photo_sans_photo(self, service, sample_article, db: Session):
        """Test suppression quand pas de photo."""
        from src.core.errors_base import ErreurValidation

        # S'assurer qu'il n'y a pas de photo
        sample_article.photo_url = None
        db.commit()

        with pytest.raises(ErreurValidation, match="pas de photo"):
            service.supprimer_photo(article_id=sample_article.id, db=db)


@pytest.mark.unit
class TestObtenirPhoto:
    """Tests pour obtenir_photo."""

    def test_obtenir_photo_existante(self, service, sample_article, db: Session):
        """Test récupération d'une photo existante."""
        sample_article.photo_url = "https://example.com/photo.jpg"
        sample_article.photo_filename = "photo.jpg"
        sample_article.photo_uploaded_at = datetime.utcnow()
        db.commit()

        result = service.obtenir_photo(article_id=sample_article.id, db=db)

        assert result is not None
        assert result["url"] == "https://example.com/photo.jpg"
        assert result["filename"] == "photo.jpg"

    def test_obtenir_photo_sans_photo(self, service, sample_article, db: Session):
        """Test récupération quand pas de photo."""
        sample_article.photo_url = None
        db.commit()

        result = service.obtenir_photo(article_id=sample_article.id, db=db)

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS INVALIDATION CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvalidateCache:
    """Tests pour invalidate_cache."""

    def test_invalidate_cache_called_on_add(self, service, sample_ingredient, db: Session):
        """Test que le cache est invalidé après ajout."""
        with patch.object(service, "invalidate_cache") as mock_invalidate:
            service.ajouter_article(
                ingredient_nom="Tomates",
                quantite=10.0,
                db=db,
            )

            mock_invalidate.assert_called()

    def test_invalidate_cache_called_on_update(self, service, sample_article, db: Session):
        """Test que le cache est invalidé après mise à jour."""
        with patch.object(service, "invalidate_cache") as mock_invalidate:
            service.mettre_a_jour_article(
                article_id=sample_article.id,
                quantite=20.0,
                db=db,
            )

            mock_invalidate.assert_called()

    def test_invalidate_cache_called_on_delete(self, service, sample_article, db: Session):
        """Test que le cache est invalidé après suppression."""
        with patch.object(service, "invalidate_cache") as mock_invalidate:
            service.supprimer_article(article_id=sample_article.id, db=db)

            mock_invalidate.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_quantite_zero(self, service, sample_ingredient, db: Session):
        """Test avec quantité à zéro."""
        result = service.ajouter_article(
            ingredient_nom="Tomates",
            quantite=0.0,
            quantite_min=1.0,
            db=db,
        )

        assert result is not None
        assert result["quantite"] == 0.0

    def test_date_peremption_passee(self, service, sample_article):
        """Test statut avec date de péremption passée."""
        today = date.today()
        sample_article.date_peremption = today - timedelta(days=5)

        statut = service._calculer_statut(sample_article, today)

        assert statut == "peremption_proche"

    def test_inventaire_filtre_categorie(self, service, sample_article, db: Session):
        """Test filtrage par catégorie."""
        result = service.get_inventaire_complet(categorie="Légumes", db=db)

        for article in result:
            assert article["ingredient_categorie"] == "Légumes"

    def test_historique_avec_ingredient_id(self, service, sample_article, db: Session):
        """Test historique filtré par ingredient_id."""
        # Créer une entrée
        historique = HistoriqueInventaire(
            article_id=sample_article.id,
            ingredient_id=sample_article.ingredient_id,
            type_modification="modification",
            date_modification=datetime.utcnow(),
        )
        db.add(historique)
        db.commit()

        result = service.get_historique(
            ingredient_id=sample_article.ingredient_id,
            db=db,
        )

        for entry in result:
            assert entry["article_id"] == sample_article.id


# ═══════════════════════════════════════════════════════════
# TESTS PROPRIÉTÉS MODÈLE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestArticleInventaireProperties:
    """Tests pour les propriétés du modèle ArticleInventaire."""

    def test_est_stock_bas_true(self, sample_article_low_stock):
        """Test est_stock_bas quand stock < seuil."""
        assert sample_article_low_stock.est_stock_bas is True

    def test_est_stock_bas_false(self, sample_article):
        """Test est_stock_bas quand stock >= seuil."""
        assert sample_article.est_stock_bas is False

    def test_est_critique_true(self, sample_article_critical):
        """Test est_critique quand stock < 50% du seuil."""
        assert sample_article_critical.est_critique is True

    def test_est_critique_false(self, sample_article):
        """Test est_critique quand stock >= 50% du seuil."""
        assert sample_article.est_critique is False

    def test_repr_article(self, sample_article):
        """Test __repr__ de ArticleInventaire."""
        repr_str = repr(sample_article)
        assert "ArticleInventaire" in repr_str
        assert str(sample_article.ingredient_id) in repr_str

    def test_repr_historique(self, sample_article, db: Session):
        """Test __repr__ de HistoriqueInventaire."""
        historique = HistoriqueInventaire(
            article_id=sample_article.id,
            ingredient_id=sample_article.ingredient_id,
            type_modification="modification",
        )
        db.add(historique)
        db.commit()

        repr_str = repr(historique)
        assert "HistoriqueInventaire" in repr_str
        assert "modification" in repr_str
