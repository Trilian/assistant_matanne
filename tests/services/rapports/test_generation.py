"""
Tests pour src/services/rapports/generation.py

Tests du service de génération de rapports PDF avec couverture complète.
"""

from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from src.core.exceptions import ErreurNonTrouve, ErreurValidation
from src.services.rapports.generation import (
    ServiceRapportsPDF,
    obtenir_service_rapports_pdf,
)
from src.services.rapports.types import (
    AnalyseGaspillage,
    RapportBudget,
    RapportPlanning,
    RapportStocks,
)


class TestServiceRapportsPDFInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Vérifie que le service peut être créé."""
        service = ServiceRapportsPDF()
        assert service is not None

    def test_service_has_cache_ttl(self):
        """Vérifie que le TTL est configuré."""
        service = ServiceRapportsPDF()
        assert service.cache_ttl == 3600

    def test_service_is_not_crud(self):
        """Vérifie que le service n'hérite plus de BaseService (pas CRUD)."""
        from src.services.core.base import BaseService

        service = ServiceRapportsPDF()
        assert not isinstance(service, BaseService)


class TestRapportStocks:
    """Tests pour le schéma RapportStocks."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        rapport = RapportStocks()
        assert rapport.periode_jours == 7
        assert rapport.articles_total == 0
        assert rapport.articles_faible_stock == []
        assert rapport.articles_perimes == []
        assert rapport.valeur_stock_total == 0.0

    def test_creation_custom_values(self):
        """Vérifie avec des valeurs personnalisées."""
        rapport = RapportStocks(periode_jours=30, articles_total=100, valeur_stock_total=1500.50)
        assert rapport.periode_jours == 30
        assert rapport.articles_total == 100
        assert rapport.valeur_stock_total == 1500.50

    def test_with_articles_faible_stock(self):
        """Test avec liste articles faible stock."""
        rapport = RapportStocks(
            articles_faible_stock=[
                {"nom": "Sel", "quantite": 1, "quantite_min": 5},
                {"nom": "Huile", "quantite": 0.5, "quantite_min": 2},
            ]
        )
        assert len(rapport.articles_faible_stock) == 2


class TestRapportBudget:
    """Tests pour le schéma RapportBudget."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        rapport = RapportBudget()
        assert rapport.depenses_total == 0.0
        assert rapport.periode_jours == 30
        assert rapport.depenses_par_categorie == {}

    def test_creation_with_data(self):
        """Vérifie avec des données."""
        rapport = RapportBudget(
            depenses_total=250.75,
            depenses_par_categorie={"alimentation": 150.0, "entretien": 100.75},
        )
        assert rapport.depenses_total == 250.75
        assert len(rapport.depenses_par_categorie) == 2

    def test_with_articles_couteux(self):
        """Test avec articles coûteux."""
        rapport = RapportBudget(
            articles_couteux=[
                {"nom": "Viande", "cout_total": 50.0},
                {"nom": "Fromage", "cout_total": 25.0},
            ]
        )
        assert len(rapport.articles_couteux) == 2


class TestAnalyseGaspillage:
    """Tests pour le schéma AnalyseGaspillage."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        analyse = AnalyseGaspillage()
        assert analyse.articles_perimes_total == 0
        assert analyse.valeur_perdue == 0.0
        assert analyse.recommandations == []

    def test_creation_with_data(self):
        """Vérifie avec des données."""
        analyse = AnalyseGaspillage(
            articles_perimes_total=5,
            valeur_perdue=45.50,
            recommandations=["Réduire les achats", "Mieux planifier"],
        )
        assert analyse.articles_perimes_total == 5
        assert analyse.valeur_perdue == 45.50
        assert len(analyse.recommandations) == 2

    def test_with_categories_gaspillage(self):
        """Test avec catégories de gaspillage."""
        analyse = AnalyseGaspillage(
            categories_gaspillage={
                "fruits": {"articles": 3, "valeur": 10.0},
                "produits_laitiers": {"articles": 2, "valeur": 8.0},
            }
        )
        assert len(analyse.categories_gaspillage) == 2


class TestRapportPlanning:
    """Tests pour le schéma RapportPlanning."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        rapport = RapportPlanning()
        assert rapport.planning_id == 0
        assert rapport.nom_planning == ""
        assert rapport.total_repas == 0

    def test_creation_with_data(self):
        """Vérifie avec des données."""
        rapport = RapportPlanning(
            planning_id=1,
            nom_planning="Semaine 1",
            semaine_debut=datetime(2024, 1, 15),
            semaine_fin=datetime(2024, 1, 21),
            total_repas=14,
        )
        assert rapport.planning_id == 1
        assert rapport.total_repas == 14


class TestServiceRapportsPDFStocks:
    """Tests de génération rapport stocks."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceRapportsPDF()

    def test_generer_donnees_rapport_stocks_empty(self, service):
        """Vérifie avec aucun article."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []

        result = service.generer_donnees_rapport_stocks(periode_jours=7, session=mock_db)
        assert isinstance(result, RapportStocks)
        assert result.articles_total == 0

    def test_generer_donnees_rapport_stocks_with_articles(self, service):
        """Vérifie avec des articles mockés."""
        mock_db = MagicMock()

        mock_article = MagicMock()
        mock_article.quantite = 5
        mock_article.quantite_min = 10
        mock_article.prix_unitaire = 2.50
        mock_article.categorie = "épicerie"
        mock_article.date_peremption = datetime.now() - timedelta(days=1)
        mock_article.nom = "Article test"
        mock_article.unite = "pcs"
        mock_article.emplacement = "Placard"

        mock_db.query.return_value.all.return_value = [mock_article]

        result = service.generer_donnees_rapport_stocks(periode_jours=7, session=mock_db)

        assert result.articles_total == 1
        assert result.valeur_stock_total == 12.50
        assert len(result.articles_faible_stock) == 1
        assert len(result.articles_perimes) == 1

    def test_generer_donnees_rapport_stocks_article_sans_prix(self, service):
        """Test article sans prix unitaire."""
        mock_db = MagicMock()

        mock_article = MagicMock()
        mock_article.quantite = 5
        mock_article.quantite_min = 3
        mock_article.prix_unitaire = None
        mock_article.categorie = "divers"
        mock_article.date_peremption = None
        mock_article.nom = "Article sans prix"
        mock_article.unite = "pcs"
        mock_article.emplacement = "Frigo"

        mock_db.query.return_value.all.return_value = [mock_article]

        result = service.generer_donnees_rapport_stocks(session=mock_db)
        assert result.articles_total == 1
        assert result.valeur_stock_total == 0.0

    def test_generer_donnees_rapport_stocks_quantite_zero(self, service):
        """Test article avec quantité zéro (pas faible stock)."""
        mock_db = MagicMock()

        mock_article = MagicMock()
        mock_article.quantite = 0
        mock_article.quantite_min = 5
        mock_article.prix_unitaire = 10.0
        mock_article.categorie = "épicerie"
        mock_article.date_peremption = None
        mock_article.nom = "Article vide"
        mock_article.unite = "pcs"
        mock_article.emplacement = "Placard"

        mock_db.query.return_value.all.return_value = [mock_article]

        result = service.generer_donnees_rapport_stocks(session=mock_db)
        # Quantité 0 n'est pas en "faible stock" selon la logique
        assert result.articles_faible_stock == []

    def test_generer_pdf_rapport_stocks(self, service):
        """Vérifie la génération PDF du rapport stocks."""
        # Mock les données pour éviter l'appel DB
        mock_rapport = RapportStocks(
            articles_total=0,
            valeur_stock_total=0.0,
            articles_faible_stock=[],
            articles_perimes=[],
            categories_resumee={},
        )
        with patch.object(service, "generer_donnees_rapport_stocks", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_stocks(periode_jours=7, session=mock_db)
            assert isinstance(result, BytesIO)
            assert result.getvalue()

    def test_generer_pdf_rapport_stocks_complet(self, service):
        """Test PDF stocks avec données complètes."""
        mock_rapport = RapportStocks(
            articles_total=2,
            valeur_stock_total=25.0,
            articles_faible_stock=[
                {
                    "nom": "Pommes",
                    "quantite": 2,
                    "quantite_min": 10,
                    "unite": "kg",
                    "emplacement": "Frigo",
                }
            ],
            articles_perimes=[
                {
                    "nom": "Yaourt",
                    "date_peremption": datetime.now() - timedelta(days=5),
                    "jours_perime": 5,
                    "quantite": 1,
                    "unite": "pcs",
                }
            ],
            categories_resumee={"fruits": {"articles": 1, "quantite": 2, "valeur": 10.0}},
        )
        with patch.object(service, "generer_donnees_rapport_stocks", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_stocks(session=mock_db)
            assert isinstance(result, BytesIO)
            assert len(result.getvalue()) > 0


class TestServiceRapportsPDFBudget:
    """Tests de génération rapport budget."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceRapportsPDF()

    def test_generer_donnees_rapport_budget_empty(self, service):
        """Test rapport budget sans articles."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []

        result = service.generer_donnees_rapport_budget(periode_jours=30, session=mock_db)
        assert isinstance(result, RapportBudget)
        assert result.depenses_total == 0.0

    def test_generer_donnees_rapport_budget_with_articles(self, service):
        """Test rapport budget avec articles."""
        mock_db = MagicMock()

        mock_article1 = MagicMock()
        mock_article1.quantite = 2
        mock_article1.prix_unitaire = 15.0  # cout = 30, > 10 donc coûteux
        mock_article1.categorie = "viande"
        mock_article1.nom = "Poulet"
        mock_article1.unite = "kg"

        mock_article2 = MagicMock()
        mock_article2.quantite = 5
        mock_article2.prix_unitaire = 1.0  # cout = 5, pas coûteux
        mock_article2.categorie = "fruits"
        mock_article2.nom = "Bananes"
        mock_article2.unite = "kg"

        mock_db.query.return_value.all.return_value = [mock_article1, mock_article2]

        result = service.generer_donnees_rapport_budget(session=mock_db)
        assert result.depenses_total == 35.0
        assert len(result.articles_couteux) == 1
        assert "viande" in result.depenses_par_categorie

    def test_generer_pdf_rapport_budget(self, service):
        """Test génération PDF budget."""
        mock_rapport = RapportBudget(
            depenses_total=0.0, depenses_par_categorie={}, articles_couteux=[]
        )
        with patch.object(service, "generer_donnees_rapport_budget", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_budget(session=mock_db)
            assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_budget_complet(self, service):
        """Test PDF budget avec données."""
        mock_rapport = RapportBudget(
            depenses_total=100.0,
            depenses_par_categorie={"épicerie": 60.0, "viande": 40.0},
            articles_couteux=[
                {
                    "nom": "Huile olive",
                    "categorie": "épicerie",
                    "quantite": 3,
                    "unite": "L",
                    "cout_total": 60.0,
                }
            ],
        )
        with patch.object(service, "generer_donnees_rapport_budget", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_budget(session=mock_db)
            assert isinstance(result, BytesIO)


class TestServiceRapportsPDFGaspillage:
    """Tests de génération analyse gaspillage."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceRapportsPDF()

    def test_generer_analyse_gaspillage_empty(self, service):
        """Test analyse gaspillage sans articles périmés."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []

        result = service.generer_analyse_gaspillage(session=mock_db)
        assert isinstance(result, AnalyseGaspillage)
        assert result.articles_perimes_total == 0
        assert result.valeur_perdue == 0.0

    def test_generer_analyse_gaspillage_with_expired(self, service):
        """Test analyse avec articles périmés."""
        mock_db = MagicMock()

        mock_article = MagicMock()
        mock_article.quantite = 2
        mock_article.prix_unitaire = 5.0
        mock_article.categorie = "produits_laitiers"
        mock_article.date_peremption = datetime.now() - timedelta(days=3)
        mock_article.nom = "Lait"
        mock_article.unite = "L"

        mock_db.query.return_value.all.return_value = [mock_article]

        result = service.generer_analyse_gaspillage(session=mock_db)
        assert result.articles_perimes_total == 1
        assert result.valeur_perdue == 10.0

    def test_generer_analyse_gaspillage_recommandations(self, service):
        """Test génération recommandations gaspillage."""
        mock_db = MagicMock()

        # 6 articles périmés pour déclencher recommandation
        articles = []
        for i in range(6):
            mock_article = MagicMock()
            mock_article.quantite = 1
            mock_article.prix_unitaire = 10.0
            mock_article.categorie = f"cat{i}"
            mock_article.date_peremption = datetime.now() - timedelta(days=i + 1)
            mock_article.nom = f"Article{i}"
            mock_article.unite = "pcs"
            articles.append(mock_article)

        mock_db.query.return_value.all.return_value = articles

        result = service.generer_analyse_gaspillage(session=mock_db)
        assert result.articles_perimes_total == 6
        assert result.valeur_perdue == 60.0
        assert len(result.recommandations) >= 2  # Plusieurs recommandations

    def test_generer_analyse_gaspillage_sans_prix(self, service):
        """Test gaspillage article sans prix."""
        mock_db = MagicMock()

        mock_article = MagicMock()
        mock_article.quantite = 1
        mock_article.prix_unitaire = None
        mock_article.categorie = "divers"
        mock_article.date_peremption = datetime.now() - timedelta(days=1)
        mock_article.nom = "Article sans prix"
        mock_article.unite = "pcs"

        mock_db.query.return_value.all.return_value = [mock_article]

        result = service.generer_analyse_gaspillage(session=mock_db)
        assert result.articles_perimes_total == 1
        assert result.valeur_perdue == 0.0

    def test_generer_pdf_analyse_gaspillage(self, service):
        """Test génération PDF gaspillage."""
        mock_analyse = AnalyseGaspillage(
            articles_perimes_total=0,
            valeur_perdue=0.0,
            recommandations=[],
            categories_gaspillage={},
            articles_perimes_detail=[],
        )
        with patch.object(service, "generer_analyse_gaspillage", return_value=mock_analyse):
            mock_db = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(session=mock_db)
            assert isinstance(result, BytesIO)

    def test_generer_pdf_analyse_gaspillage_complet(self, service):
        """Test PDF gaspillage avec données."""
        mock_analyse = AnalyseGaspillage(
            articles_perimes_total=1,
            valeur_perdue=24.0,
            recommandations=["Réduire les achats"],
            categories_gaspillage={"fruits": {"articles": 1, "valeur": 24.0}},
            articles_perimes_detail=[
                {
                    "nom": "Fraises",
                    "jours_perime": 7,
                    "quantite": 3,
                    "unite": "barquette",
                    "valeur_perdue": 24.0,
                }
            ],
        )
        with patch.object(service, "generer_analyse_gaspillage", return_value=mock_analyse):
            mock_db = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(session=mock_db)
            assert isinstance(result, BytesIO)
            assert len(result.getvalue()) > 0


class TestServiceRapportsPDFPlanning:
    """Tests de génération rapport planning."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceRapportsPDF()

    def test_generer_donnees_rapport_planning_not_found(self, service):
        """Test planning non trouvé."""
        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(ErreurNonTrouve):
            service.generer_donnees_rapport_planning(planning_id=999, session=mock_db)

    def test_generer_donnees_rapport_planning_success(self, service):
        """Test génération données planning."""
        mock_db = MagicMock()

        # Mock ingredient
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomate"
        mock_ingredient.unite_defaut = "kg"

        # Mock RecetteIngredient
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient
        mock_ri.quantite = 500
        mock_ri.unite = "g"

        # Mock recette
        mock_recette = MagicMock()
        mock_recette.nom = "Salade"
        mock_recette.portions = 4
        mock_recette.ingredients = [mock_ri]

        # Mock repas
        mock_repas = MagicMock()
        mock_repas.date_repas = datetime.now()
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = mock_recette
        mock_repas.portion_ajustee = None
        mock_repas.prepare = False
        mock_repas.notes = "Test"

        # Mock planning
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Semaine Test"
        mock_planning.semaine_debut = datetime(2024, 1, 15)
        mock_planning.semaine_fin = datetime(2024, 1, 21)
        mock_planning.repas = [mock_repas]

        mock_db.query.return_value.options.return_value.filter_by.return_value.first.return_value = mock_planning

        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_db)
        assert isinstance(result, RapportPlanning)
        assert result.planning_id == 1
        assert result.total_repas == 1

    def test_generer_pdf_rapport_planning(self, service):
        """Test génération PDF planning."""
        mock_rapport = RapportPlanning(
            planning_id=1,
            nom_planning="Planning Test",
            semaine_debut=datetime(2024, 1, 15),
            semaine_fin=datetime(2024, 1, 21),
            total_repas=0,
            repas_par_jour={},
            liste_courses_estimee=[],
        )
        with patch.object(service, "generer_donnees_rapport_planning", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_planning(planning_id=1, session=mock_db)
            assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_planning_complet(self, service):
        """Test PDF planning avec repas."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        mock_rapport = RapportPlanning(
            planning_id=1,
            nom_planning="Planning Complet",
            semaine_debut=datetime(2024, 1, 15),
            semaine_fin=datetime(2024, 1, 21),
            total_repas=2,
            repas_par_jour={
                date_str: [
                    {
                        "type": "déjeuner",
                        "recette_nom": "Salade",
                        "portions": 4,
                        "prepare": True,
                        "notes": "Test",
                    },
                    {
                        "type": "dîner",
                        "recette_nom": "Soupe",
                        "portions": 2,
                        "prepare": False,
                        "notes": "",
                    },
                ]
            },
            liste_courses_estimee=[
                {"nom": "Tomate", "quantite": 500, "unite": "g"},
                {"nom": "Oignon", "quantite": 2, "unite": "pcs"},
            ],
        )
        with patch.object(service, "generer_donnees_rapport_planning", return_value=mock_rapport):
            mock_db = MagicMock()
            result = service.generer_pdf_rapport_planning(planning_id=1, session=mock_db)
            assert isinstance(result, BytesIO)
            assert len(result.getvalue()) > 0


class TestTelechargerRapport:
    """Tests des fonctions téléchargement."""

    @pytest.fixture
    def service(self):
        """Fixture pour le service."""
        return ServiceRapportsPDF()

    def test_telecharger_rapport_pdf_stocks(self, service):
        """Test téléchargement rapport stocks."""
        with patch.object(service, "generer_pdf_rapport_stocks") as mock_gen:
            mock_gen.return_value = BytesIO(b"PDF content")

            pdf, filename = service.telecharger_rapport_pdf(type_rapport="stocks")

            assert isinstance(pdf, BytesIO)
            assert "rapport_stocks_" in filename
            assert filename.endswith(".pdf")

    def test_telecharger_rapport_pdf_budget(self, service):
        """Test téléchargement rapport budget."""
        with patch.object(service, "generer_pdf_rapport_budget") as mock_gen:
            mock_gen.return_value = BytesIO(b"PDF content")

            pdf, filename = service.telecharger_rapport_pdf(type_rapport="budget", periode_jours=60)

            assert isinstance(pdf, BytesIO)
            assert "rapport_budget_" in filename

    def test_telecharger_rapport_pdf_gaspillage(self, service):
        """Test téléchargement rapport gaspillage."""
        with patch.object(service, "generer_pdf_analyse_gaspillage") as mock_gen:
            mock_gen.return_value = BytesIO(b"PDF content")

            pdf, filename = service.telecharger_rapport_pdf(type_rapport="gaspillage")

            assert isinstance(pdf, BytesIO)
            assert "analyse_gaspillage_" in filename

    def test_telecharger_rapport_pdf_invalid_type(self, service):
        """Test type de rapport invalide."""
        with pytest.raises(ErreurValidation):
            service.telecharger_rapport_pdf(type_rapport="invalid")

    def test_telecharger_rapport_planning(self, service):
        """Test téléchargement rapport planning."""
        with patch.object(service, "generer_pdf_rapport_planning") as mock_gen:
            mock_gen.return_value = BytesIO(b"PDF content")

            pdf, filename = service.telecharger_rapport_planning(planning_id=1)

            assert isinstance(pdf, BytesIO)
            assert "planning_semaine_" in filename


class TestFactoryFunctions:
    """Tests des fonctions factory et alias."""

    def test_obtenir_service_rapports_pdf(self):
        """Test obtenir_service_rapports_pdf retourne singleton."""
        import src.services.rapports.generation as module

        module._service_rapports_pdf = None

        service1 = obtenir_service_rapports_pdf()
        service2 = obtenir_service_rapports_pdf()
        assert service1 is service2
        assert isinstance(service1, ServiceRapportsPDF)
