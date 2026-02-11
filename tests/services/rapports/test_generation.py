"""
Tests pour src/services/rapports/generation.py

Couverture cible: >80%
Teste la génération de rapports PDF stocks, budget, gaspillage et planning.
"""

import pytest
from io import BytesIO
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from src.services.rapports.generation import (
    ServiceRapportsPDF,
    obtenir_service_rapports_pdf,
    RapportsPDFService,
    get_rapports_pdf_service,
)
from src.services.rapports.types import (
    RapportStocks,
    RapportBudget,
    AnalyseGaspillage,
    RapportPlanning,
)
from src.core.errors_base import ErreurValidation, ErreurNonTrouve


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance fraîche du service de rapports PDF."""
    return ServiceRapportsPDF()


@pytest.fixture
def mock_session():
    """Session de base de données mockée."""
    return MagicMock()


@pytest.fixture
def sample_articles_inventaire():
    """Articles d'inventaire pour tests."""
    maintenant = datetime.now()

    articles = []

    # Article normal
    article1 = MagicMock()
    article1.nom = "Tomates"
    article1.categorie = "fruits_legumes"
    article1.quantite = 10
    article1.quantite_min = 5
    article1.prix_unitaire = 2.5
    article1.unite = "kg"
    article1.emplacement = "Réfrigérateur"
    article1.date_peremption = maintenant + timedelta(days=10)
    articles.append(article1)

    # Article faible stock
    article2 = MagicMock()
    article2.nom = "Lait"
    article2.categorie = "produits_laitiers"
    article2.quantite = 1
    article2.quantite_min = 3
    article2.prix_unitaire = 1.2
    article2.unite = "L"
    article2.emplacement = "Réfrigérateur"
    article2.date_peremption = maintenant + timedelta(days=5)
    articles.append(article2)

    # Article périmé
    article3 = MagicMock()
    article3.nom = "Yaourt"
    article3.categorie = "produits_laitiers"
    article3.quantite = 4
    article3.quantite_min = 2
    article3.prix_unitaire = 0.5
    article3.unite = "pièces"
    article3.emplacement = "Réfrigérateur"
    article3.date_peremption = maintenant - timedelta(days=3)  # Périmé
    articles.append(article3)

    # Article sans prix
    article4 = MagicMock()
    article4.nom = "Sel"
    article4.categorie = "epicerie"
    article4.quantite = 1
    article4.quantite_min = 1
    article4.prix_unitaire = None
    article4.unite = "paquet"
    article4.emplacement = "Placard"
    article4.date_peremption = None
    articles.append(article4)

    return articles


@pytest.fixture
def sample_rapport_stocks():
    """Rapport stocks pour tests."""
    return RapportStocks(
        date_rapport=datetime.now(),
        periode_jours=7,
        articles_total=10,
        articles_faible_stock=[
            {
                "nom": "Lait",
                "quantite": 1,
                "quantite_min": 3,
                "unite": "L",
                "emplacement": "Frigo",
            }
        ],
        articles_perimes=[
            {
                "nom": "Yaourt",
                "date_peremption": datetime.now() - timedelta(days=2),
                "jours_perime": 2,
                "quantite": 4,
                "unite": "pièces",
            }
        ],
        valeur_stock_total=150.0,
        categories_resumee={
            "fruits_legumes": {"quantite": 20, "valeur": 50.0, "articles": 5},
            "produits_laitiers": {"quantite": 10, "valeur": 30.0, "articles": 3},
        },
    )


@pytest.fixture
def sample_rapport_budget():
    """Rapport budget pour tests."""
    return RapportBudget(
        date_rapport=datetime.now(),
        periode_jours=30,
        depenses_total=250.0,
        depenses_par_categorie={
            "fruits_legumes": 80.0,
            "viande": 100.0,
            "epicerie": 70.0,
        },
        articles_couteux=[
            {
                "nom": "Boeuf",
                "quantite": 2,
                "unite": "kg",
                "prix_unitaire": 25.0,
                "cout_total": 50.0,
                "categorie": "viande",
            },
            {
                "nom": "Saumon",
                "quantite": 1,
                "unite": "kg",
                "prix_unitaire": 30.0,
                "cout_total": 30.0,
                "categorie": "poisson",
            },
        ],
    )


@pytest.fixture
def sample_analyse_gaspillage():
    """Analyse gaspillage pour tests."""
    return AnalyseGaspillage(
        date_rapport=datetime.now(),
        periode_jours=30,
        articles_perimes_total=3,
        valeur_perdue=25.0,
        categories_gaspillage={
            "produits_laitiers": {"articles": 2, "valeur": 15.0},
            "fruits_legumes": {"articles": 1, "valeur": 10.0},
        },
        recommandations=[
            "⚠️ Gaspillage important détecté",
            "📅 Mettre en place un FIFO",
        ],
        articles_perimes_detail=[
            {
                "nom": "Yaourt",
                "date_peremption": datetime.now() - timedelta(days=2),
                "jours_perime": 2,
                "quantite": 4,
                "unite": "pièces",
                "valeur_perdue": 2.0,
            }
        ],
    )


@pytest.fixture
def mock_planning():
    """Planning mocké pour tests."""
    mock_planning = MagicMock()
    mock_planning.id = 1
    mock_planning.nom = "Planning Semaine"
    mock_planning.semaine_debut = datetime.now() - timedelta(days=3)
    mock_planning.semaine_fin = datetime.now() + timedelta(days=4)

    # Mock repas
    mock_repas = MagicMock()
    mock_repas.date_repas = datetime.now()
    mock_repas.type_repas = "déjeuner"
    mock_repas.prepare = False
    mock_repas.notes = "Notes test"
    mock_repas.portion_ajustee = 4

    # Mock recette du repas
    mock_recette = MagicMock()
    mock_recette.nom = "Poulet rôti"
    mock_recette.portions = 4

    # Mock ingrédients
    mock_ri = MagicMock()
    mock_ri.quantite = 500
    mock_ri.unite = "g"
    mock_ingredient = MagicMock()
    mock_ingredient.nom = "Poulet"
    mock_ingredient.unite_defaut = "g"
    mock_ri.ingredient = mock_ingredient
    mock_recette.ingredients = [mock_ri]

    mock_repas.recette = mock_recette
    mock_planning.repas = [mock_repas]

    return mock_planning


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


class TestServiceRapportsPDFInit:
    """Tests d'initialisation du service."""

    def test_init_creates_service(self, service):
        """Test que l'init crée le service correctement."""
        assert service is not None
        assert service.cache_ttl == 3600

    def test_init_base_service(self, service):
        """Test que le service hérite de BaseService."""
        from src.services.base import BaseService

        assert isinstance(service, BaseService)


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT STOCKS - DONNÉES
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportStocks:
    """Tests de génération des données pour rapport stocks."""

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_stocks_success(
        self, mock_db_ctx, service, sample_articles_inventaire
    ):
        """Test génération données rapport stocks réussie."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_articles_inventaire

        # Le décorateur injecte la session
        result = service.generer_donnees_rapport_stocks(
            periode_jours=7, session=mock_session
        )

        assert isinstance(result, RapportStocks)
        assert result.articles_total == 4
        assert result.periode_jours == 7
        assert len(result.articles_faible_stock) >= 1  # Article Lait
        assert len(result.articles_perimes) >= 1  # Article Yaourt

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_stocks_vide(self, mock_db_ctx, service):
        """Test génération données rapport stocks vide."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []

        result = service.generer_donnees_rapport_stocks(
            periode_jours=7, session=mock_session
        )

        assert isinstance(result, RapportStocks)
        assert result.articles_total == 0
        assert result.articles_faible_stock == []
        assert result.articles_perimes == []
        assert result.valeur_stock_total == 0.0

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_stocks_categories(
        self, mock_db_ctx, service, sample_articles_inventaire
    ):
        """Test que les catégories sont correctement agrégées."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_articles_inventaire

        result = service.generer_donnees_rapport_stocks(
            periode_jours=7, session=mock_session
        )

        assert "fruits_legumes" in result.categories_resumee
        assert "produits_laitiers" in result.categories_resumee
        assert result.categories_resumee["fruits_legumes"]["articles"] == 1

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_stocks_tri(
        self, mock_db_ctx, service, sample_articles_inventaire
    ):
        """Test que les articles sont triés correctement."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_articles_inventaire

        result = service.generer_donnees_rapport_stocks(
            periode_jours=7, session=mock_session
        )

        # Articles faible stock triés par ratio quantité/quantité_min
        if len(result.articles_faible_stock) > 1:
            ratios = [
                a["quantite"] / a["quantite_min"]
                for a in result.articles_faible_stock
                if a["quantite_min"] > 0
            ]
            assert ratios == sorted(ratios)


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT STOCKS - PDF
# ═══════════════════════════════════════════════════════════


class TestGenererPDFRapportStocks:
    """Tests de génération PDF pour rapport stocks."""

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_stocks")
    def test_generer_pdf_rapport_stocks_success(self, mock_donnees, service):
        """Test génération PDF rapport stocks réussie."""
        mock_donnees.return_value = RapportStocks(
            periode_jours=7,
            articles_total=5,
            valeur_stock_total=100.0,
            articles_faible_stock=[
                {
                    "nom": "Test",
                    "quantite": 1,
                    "quantite_min": 5,
                    "unite": "u",
                    "emplacement": "A",
                }
            ],
            articles_perimes=[
                {
                    "nom": "Périmé",
                    "date_peremption": datetime.now() - timedelta(days=2),
                    "jours_perime": 2,
                    "quantite": 1,
                    "unite": "u",
                }
            ],
            categories_resumee={"test": {"quantite": 5, "valeur": 50.0, "articles": 2}},
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_stocks(periode_jours=7, session=mock_session)

        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read()
        assert content[:4] == b"%PDF"

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_stocks")
    def test_generer_pdf_rapport_stocks_vide(self, mock_donnees, service):
        """Test génération PDF rapport stocks vide."""
        mock_donnees.return_value = RapportStocks(
            periode_jours=7,
            articles_total=0,
            valeur_stock_total=0.0,
            articles_faible_stock=[],
            articles_perimes=[],
            categories_resumee={},
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_stocks(periode_jours=7, session=mock_session)

        assert isinstance(result, BytesIO)

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_stocks")
    def test_generer_pdf_rapport_stocks_beaucoup_articles(self, mock_donnees, service):
        """Test génération PDF avec beaucoup d'articles."""
        mock_donnees.return_value = RapportStocks(
            periode_jours=7,
            articles_total=100,
            valeur_stock_total=5000.0,
            articles_faible_stock=[
                {
                    "nom": f"Item {i}",
                    "quantite": 1,
                    "quantite_min": 5,
                    "unite": "u",
                    "emplacement": "A",
                }
                for i in range(20)
            ],
            articles_perimes=[
                {
                    "nom": f"Périmé {i}",
                    "date_peremption": datetime.now() - timedelta(days=i),
                    "jours_perime": i,
                    "quantite": 1,
                    "unite": "u",
                }
                for i in range(15)
            ],
            categories_resumee={
                f"cat_{i}": {"quantite": 10, "valeur": 100.0, "articles": 5}
                for i in range(5)
            },
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_stocks(periode_jours=7, session=mock_session)

        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT BUDGET - DONNÉES
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportBudget:
    """Tests de génération des données pour rapport budget."""

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_budget_success(
        self, mock_db_ctx, service, sample_articles_inventaire
    ):
        """Test génération données rapport budget réussie."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_articles_inventaire

        result = service.generer_donnees_rapport_budget(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, RapportBudget)
        assert result.periode_jours == 30
        assert result.depenses_total > 0

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_budget_vide(self, mock_db_ctx, service):
        """Test génération données rapport budget vide."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []

        result = service.generer_donnees_rapport_budget(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, RapportBudget)
        assert result.depenses_total == 0.0

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_budget_articles_couteux(
        self, mock_db_ctx, service
    ):
        """Test que les articles coûteux sont identifiés."""
        # Articles avec coût > 10
        expensive = MagicMock()
        expensive.nom = "Produit cher"
        expensive.categorie = "autre"
        expensive.quantite = 5
        expensive.unite = "u"
        expensive.prix_unitaire = 20.0  # Coût total = 100

        cheap = MagicMock()
        cheap.nom = "Produit pas cher"
        cheap.categorie = "autre"
        cheap.quantite = 2
        cheap.unite = "u"
        cheap.prix_unitaire = 2.0  # Coût total = 4

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [expensive, cheap]

        result = service.generer_donnees_rapport_budget(
            periode_jours=30, session=mock_session
        )

        assert len(result.articles_couteux) == 1  # Seulement l'article > 10€
        assert result.articles_couteux[0]["nom"] == "Produit cher"


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT BUDGET - PDF
# ═══════════════════════════════════════════════════════════


class TestGenererPDFRapportBudget:
    """Tests de génération PDF pour rapport budget."""

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_budget")
    def test_generer_pdf_rapport_budget_success(self, mock_donnees, service):
        """Test génération PDF rapport budget réussie."""
        mock_donnees.return_value = RapportBudget(
            periode_jours=30,
            depenses_total=500.0,
            depenses_par_categorie={
                "fruits_legumes": 150.0,
                "viande": 200.0,
                "epicerie": 150.0,
            },
            articles_couteux=[
                {
                    "nom": "Boeuf",
                    "categorie": "viande",
                    "quantite": 2,
                    "unite": "kg",
                    "cout_total": 50.0,
                }
            ],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_budget(periode_jours=30, session=mock_session)

        assert isinstance(result, BytesIO)
        result.seek(0)
        assert result.read()[:4] == b"%PDF"

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_budget")
    def test_generer_pdf_rapport_budget_vide(self, mock_donnees, service):
        """Test génération PDF rapport budget vide."""
        mock_donnees.return_value = RapportBudget(
            periode_jours=30,
            depenses_total=0.0,
            depenses_par_categorie={},
            articles_couteux=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_budget(periode_jours=30, session=mock_session)

        assert isinstance(result, BytesIO)

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_budget")
    def test_generer_pdf_rapport_budget_pourcentages(self, mock_donnees, service):
        """Test calcul des pourcentages dans le PDF."""
        mock_donnees.return_value = RapportBudget(
            periode_jours=30,
            depenses_total=100.0,
            depenses_par_categorie={
                "cat1": 50.0,
                "cat2": 30.0,
                "cat3": 20.0,
            },
            articles_couteux=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_budget(periode_jours=30, session=mock_session)

        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE GASPILLAGE - DONNÉES
# ═══════════════════════════════════════════════════════════


class TestGenererAnalyseGaspillage:
    """Tests de génération de l'analyse gaspillage."""

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_analyse_gaspillage_success(
        self, mock_db_ctx, service, sample_articles_inventaire
    ):
        """Test génération analyse gaspillage réussie."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_articles_inventaire

        result = service.generer_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, AnalyseGaspillage)
        assert result.articles_perimes_total >= 1

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_analyse_gaspillage_vide(self, mock_db_ctx, service):
        """Test génération analyse gaspillage sans articles."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []

        result = service.generer_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, AnalyseGaspillage)
        assert result.articles_perimes_total == 0
        assert result.valeur_perdue == 0.0

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_analyse_gaspillage_recommandations(self, mock_db_ctx, service):
        """Test que les recommandations sont générées."""
        # 10 articles périmés avec valeur > 50€
        articles_perimes = []
        for i in range(10):
            article = MagicMock()
            article.nom = f"Périmé {i}"
            article.categorie = "test"
            article.quantite = 5
            article.prix_unitaire = 10.0
            article.date_peremption = datetime.now() - timedelta(days=i + 1)
            articles_perimes.append(article)

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = articles_perimes

        result = service.generer_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        # Devrait avoir les 3 recommandations
        assert len(result.recommandations) >= 2
        assert result.articles_perimes_total > 5
        assert result.valeur_perdue > 50

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_analyse_gaspillage_sans_prix(self, mock_db_ctx, service):
        """Test analyse avec articles sans prix unitaire."""
        article = MagicMock()
        article.nom = "Sans prix"
        article.categorie = "test"
        article.quantite = 1
        article.prix_unitaire = None
        article.date_peremption = datetime.now() - timedelta(days=1)

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [article]

        result = service.generer_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert result.articles_perimes_total == 1
        assert result.valeur_perdue == 0.0


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE GASPILLAGE - PDF
# ═══════════════════════════════════════════════════════════


class TestGenererPDFAnalyseGaspillage:
    """Tests de génération PDF pour analyse gaspillage."""

    @patch.object(ServiceRapportsPDF, "generer_analyse_gaspillage")
    def test_generer_pdf_analyse_gaspillage_success(self, mock_analyse, service):
        """Test génération PDF analyse gaspillage réussie."""
        mock_analyse.return_value = AnalyseGaspillage(
            periode_jours=30,
            articles_perimes_total=5,
            valeur_perdue=75.0,
            categories_gaspillage={
                "produits_laitiers": {"articles": 3, "valeur": 45.0},
                "fruits_legumes": {"articles": 2, "valeur": 30.0},
            },
            recommandations=["Améliorer la rotation des stocks"],
            articles_perimes_detail=[
                {
                    "nom": "Yaourt",
                    "jours_perime": 2,
                    "quantite": 4,
                    "unite": "pièces",
                    "valeur_perdue": 2.0,
                }
            ],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, BytesIO)
        result.seek(0)
        assert result.read()[:4] == b"%PDF"

    @patch.object(ServiceRapportsPDF, "generer_analyse_gaspillage")
    def test_generer_pdf_analyse_gaspillage_vide(self, mock_analyse, service):
        """Test génération PDF analyse gaspillage vide."""
        mock_analyse.return_value = AnalyseGaspillage(
            periode_jours=30,
            articles_perimes_total=0,
            valeur_perdue=0.0,
            categories_gaspillage={},
            recommandations=[],
            articles_perimes_detail=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestTelechargerRapportPDF:
    """Tests de la méthode telecharger_rapport_pdf."""

    @patch.object(ServiceRapportsPDF, "generer_pdf_rapport_stocks")
    def test_telecharger_rapport_stocks(self, mock_pdf, service):
        """Test téléchargement rapport stocks."""
        mock_pdf.return_value = BytesIO(b"%PDF-test")

        pdf, filename = service.telecharger_rapport_pdf("stocks", periode_jours=7)

        assert isinstance(pdf, BytesIO)
        assert "rapport_stocks_" in filename
        assert filename.endswith(".pdf")

    @patch.object(ServiceRapportsPDF, "generer_pdf_rapport_budget")
    def test_telecharger_rapport_budget(self, mock_pdf, service):
        """Test téléchargement rapport budget."""
        mock_pdf.return_value = BytesIO(b"%PDF-test")

        pdf, filename = service.telecharger_rapport_pdf("budget", periode_jours=30)

        assert isinstance(pdf, BytesIO)
        assert "rapport_budget_" in filename
        assert filename.endswith(".pdf")

    @patch.object(ServiceRapportsPDF, "generer_pdf_analyse_gaspillage")
    def test_telecharger_rapport_gaspillage(self, mock_pdf, service):
        """Test téléchargement rapport gaspillage."""
        mock_pdf.return_value = BytesIO(b"%PDF-test")

        pdf, filename = service.telecharger_rapport_pdf("gaspillage", periode_jours=30)

        assert isinstance(pdf, BytesIO)
        assert "analyse_gaspillage_" in filename
        assert filename.endswith(".pdf")

    def test_telecharger_rapport_type_inconnu(self, service):
        """Test erreur pour type de rapport inconnu."""
        with pytest.raises(ErreurValidation, match="Type de rapport inconnu"):
            service.telecharger_rapport_pdf("inconnu", periode_jours=30)


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT PLANNING
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportPlanning:
    """Tests de génération des données pour rapport planning."""

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_planning_success(
        self, mock_db_ctx, service, mock_planning
    ):
        """Test génération données rapport planning réussie."""
        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = (
            mock_planning
        )

        result = service.generer_donnees_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert isinstance(result, RapportPlanning)
        assert result.planning_id == 1
        assert result.total_repas >= 1

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_planning_not_found(self, mock_db_ctx, service):
        """Test erreur planning non trouvé."""
        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = (
            None
        )

        with pytest.raises(ErreurNonTrouve, match="non trouvé"):
            service.generer_donnees_rapport_planning(
                planning_id=999, session=mock_session
            )

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_planning_liste_courses(
        self, mock_db_ctx, service, mock_planning
    ):
        """Test que la liste de courses est estimée."""
        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = (
            mock_planning
        )

        result = service.generer_donnees_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert len(result.liste_courses_estimee) >= 1
        assert result.liste_courses_estimee[0]["nom"] == "Poulet"

    @patch("src.services.rapports.generation.obtenir_contexte_db")
    def test_generer_donnees_rapport_planning_repas_sans_recette(
        self, mock_db_ctx, service
    ):
        """Test planning avec repas sans recette."""
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning"
        mock_planning.semaine_debut = datetime.now()
        mock_planning.semaine_fin = datetime.now() + timedelta(days=6)

        mock_repas = MagicMock()
        mock_repas.date_repas = datetime.now()
        mock_repas.type_repas = "déjeuner"
        mock_repas.prepare = False
        mock_repas.notes = ""
        mock_repas.portion_ajustee = None
        mock_repas.recette = None
        mock_planning.repas = [mock_repas]

        mock_session = MagicMock()
        mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = (
            mock_planning
        )

        result = service.generer_donnees_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert result.total_repas == 1


# ═══════════════════════════════════════════════════════════
# TESTS RAPPORT PLANNING - PDF
# ═══════════════════════════════════════════════════════════


class TestGenererPDFRapportPlanning:
    """Tests de génération PDF pour rapport planning."""

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_planning")
    def test_generer_pdf_rapport_planning_success(self, mock_donnees, service):
        """Test génération PDF rapport planning réussie."""
        mock_donnees.return_value = RapportPlanning(
            planning_id=1,
            nom_planning="Ma Semaine",
            semaine_debut=datetime.now(),
            semaine_fin=datetime.now() + timedelta(days=6),
            repas_par_jour={
                datetime.now().strftime("%Y-%m-%d"): [
                    {
                        "type": "déjeuner",
                        "recette_nom": "Poulet",
                        "portions": 4,
                        "prepare": False,
                        "notes": "",
                    }
                ]
            },
            total_repas=1,
            liste_courses_estimee=[
                {"nom": "Poulet", "quantite": 500, "unite": "g"}
            ],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert isinstance(result, BytesIO)
        result.seek(0)
        assert result.read()[:4] == b"%PDF"

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_planning")
    def test_generer_pdf_rapport_planning_vide(self, mock_donnees, service):
        """Test génération PDF rapport planning vide."""
        mock_donnees.return_value = RapportPlanning(
            planning_id=1,
            nom_planning="Planning Vide",
            semaine_debut=None,
            semaine_fin=None,
            repas_par_jour={},
            total_repas=0,
            liste_courses_estimee=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert isinstance(result, BytesIO)

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_planning")
    def test_generer_pdf_rapport_planning_tous_types_repas(self, mock_donnees, service):
        """Test génération PDF avec tous les types de repas."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        mock_donnees.return_value = RapportPlanning(
            planning_id=1,
            nom_planning="Semaine Complète",
            semaine_debut=datetime.now(),
            semaine_fin=datetime.now() + timedelta(days=6),
            repas_par_jour={
                date_str: [
                    {
                        "type": "petit_déjeuner",
                        "recette_nom": "Céréales",
                        "portions": 2,
                        "prepare": True,
                        "notes": "",
                    },
                    {
                        "type": "déjeuner",
                        "recette_nom": "Poulet",
                        "portions": 4,
                        "prepare": False,
                        "notes": "",
                    },
                    {
                        "type": "goûter",
                        "recette_nom": "Gâteau",
                        "portions": 2,
                        "prepare": True,
                        "notes": "",
                    },
                    {
                        "type": "dîner",
                        "recette_nom": "Soupe",
                        "portions": 4,
                        "prepare": False,
                        "notes": "",
                    },
                ]
            },
            total_repas=4,
            liste_courses_estimee=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_planning(
            planning_id=1, session=mock_session
        )

        assert isinstance(result, BytesIO)


class TestTelechargerRapportPlanning:
    """Tests de la méthode telecharger_rapport_planning."""

    @patch.object(ServiceRapportsPDF, "generer_pdf_rapport_planning")
    def test_telecharger_rapport_planning(self, mock_pdf, service):
        """Test téléchargement rapport planning."""
        mock_pdf.return_value = BytesIO(b"%PDF-test")

        pdf, filename = service.telecharger_rapport_planning(planning_id=1)

        assert isinstance(pdf, BytesIO)
        assert "planning_semaine_" in filename
        assert filename.endswith(".pdf")


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY / SINGLETON
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests de la factory function."""

    def test_obtenir_service_rapports_pdf(self):
        """Test que la factory retourne une instance."""
        # Reset singleton
        import src.services.rapports.generation as module

        module._service_rapports_pdf = None

        service = obtenir_service_rapports_pdf()
        assert isinstance(service, ServiceRapportsPDF)

    def test_obtenir_service_rapports_pdf_singleton(self):
        """Test que la factory retourne toujours la même instance."""
        service1 = obtenir_service_rapports_pdf()
        service2 = obtenir_service_rapports_pdf()
        assert service1 is service2


class TestAliasRetrocompatibilite:
    """Tests des alias de rétrocompatibilité."""

    def test_rapports_pdf_service_alias(self):
        """Test alias RapportsPDFService."""
        assert RapportsPDFService is ServiceRapportsPDF

    def test_get_rapports_pdf_service_alias(self):
        """Test alias get_rapports_pdf_service."""
        assert get_rapports_pdf_service is obtenir_service_rapports_pdf


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


class TestCasLimites:
    """Tests des cas limites et valeurs extrêmes."""

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_stocks")
    def test_pdf_stocks_noms_longs(self, mock_donnees, service):
        """Test génération PDF avec noms très longs."""
        mock_donnees.return_value = RapportStocks(
            periode_jours=7,
            articles_total=1,
            valeur_stock_total=100.0,
            articles_faible_stock=[
                {
                    "nom": "A" * 100,  # Nom très long
                    "quantite": 1,
                    "quantite_min": 5,
                    "unite": "u",
                    "emplacement": "B" * 50,
                }
            ],
            articles_perimes=[
                {
                    "nom": "C" * 100,
                    "date_peremption": datetime.now(),
                    "jours_perime": 1,
                    "quantite": 1,
                    "unite": "u",
                }
            ],
            categories_resumee={},
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_stocks(periode_jours=7, session=mock_session)

        assert isinstance(result, BytesIO)

    @patch.object(ServiceRapportsPDF, "generer_donnees_rapport_budget")
    def test_pdf_budget_depenses_zero(self, mock_donnees, service):
        """Test génération PDF avec dépenses à zéro."""
        mock_donnees.return_value = RapportBudget(
            periode_jours=30,
            depenses_total=0.0,
            depenses_par_categorie={"test": 0.0},
            articles_couteux=[],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_rapport_budget(periode_jours=30, session=mock_session)

        assert isinstance(result, BytesIO)

    @patch.object(ServiceRapportsPDF, "generer_analyse_gaspillage")
    def test_pdf_gaspillage_articles_nombreux(self, mock_analyse, service):
        """Test génération PDF avec beaucoup d'articles périmés."""
        mock_analyse.return_value = AnalyseGaspillage(
            periode_jours=30,
            articles_perimes_total=50,
            valeur_perdue=500.0,
            categories_gaspillage={
                f"cat_{i}": {"articles": 5, "valeur": 50.0} for i in range(10)
            },
            recommandations=["Recommandation" for _ in range(10)],
            articles_perimes_detail=[
                {
                    "nom": f"Item {i}",
                    "jours_perime": i,
                    "quantite": 1,
                    "unite": "u",
                    "valeur_perdue": 10.0,
                }
                for i in range(30)
            ],
        )

        mock_session = MagicMock()
        result = service.generer_pdf_analyse_gaspillage(
            periode_jours=30, session=mock_session
        )

        assert isinstance(result, BytesIO)
