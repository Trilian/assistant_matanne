"""
Tests complets pour RapportsPDFService.

Ce fichier teste:
- Les schémas Pydantic (RapportStocks, RapportBudget, AnalyseGaspillage, RapportPlanning)
- L'initialisation du service
- Les méthodes de génération de données
- Les méthodes de génération PDF
- Les méthodes de téléchargement
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO

from pydantic import ValidationError


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestRapportStocksSchema:
    """Tests du schéma RapportStocks."""

    def test_import_schema(self):
        """Test import RapportStocks."""
        from src.services.rapports_pdf import RapportStocks
        assert RapportStocks is not None

    def test_default_values(self):
        """Test valeurs par défaut."""
        from src.services.rapports_pdf import RapportStocks
        rapport = RapportStocks()
        
        assert rapport.periode_jours == 7
        assert rapport.articles_total == 0
        assert rapport.articles_faible_stock == []
        assert rapport.articles_perimes == []
        assert rapport.valeur_stock_total == 0.0
        assert rapport.categories_resumee == {}
        assert isinstance(rapport.date_rapport, datetime)

    def test_custom_values(self):
        """Test assignation valeurs personnalisées."""
        from src.services.rapports_pdf import RapportStocks
        
        rapport = RapportStocks(
            periode_jours=30,
            articles_total=50,
            valeur_stock_total=1500.50,
            articles_faible_stock=[{"nom": "Lait", "quantite": 1}],
            articles_perimes=[{"nom": "Pain", "date_peremption": datetime.now()}],
            categories_resumee={"Frais": {"quantite": 10, "valeur": 100.0}}
        )
        
        assert rapport.periode_jours == 30
        assert rapport.articles_total == 50
        assert rapport.valeur_stock_total == 1500.50
        assert len(rapport.articles_faible_stock) == 1
        assert len(rapport.articles_perimes) == 1
        assert "Frais" in rapport.categories_resumee

    def test_periode_validation_min(self):
        """Test validation periode_jours minimum."""
        from src.services.rapports_pdf import RapportStocks
        
        with pytest.raises(ValidationError):
            RapportStocks(periode_jours=0)

    def test_periode_validation_max(self):
        """Test validation periode_jours maximum."""
        from src.services.rapports_pdf import RapportStocks
        
        with pytest.raises(ValidationError):
            RapportStocks(periode_jours=500)

    def test_periode_valid_range(self):
        """Test période valide dans la plage."""
        from src.services.rapports_pdf import RapportStocks
        
        for days in [1, 7, 30, 180, 365]:
            rapport = RapportStocks(periode_jours=days)
            assert rapport.periode_jours == days


class TestRapportBudgetSchema:
    """Tests du schéma RapportBudget."""

    def test_import_schema(self):
        """Test import RapportBudget."""
        from src.services.rapports_pdf import RapportBudget
        assert RapportBudget is not None

    def test_default_values(self):
        """Test valeurs par défaut."""
        from src.services.rapports_pdf import RapportBudget
        rapport = RapportBudget()
        
        assert rapport.periode_jours == 30
        assert rapport.depenses_total == 0.0
        assert rapport.depenses_par_categorie == {}
        assert rapport.evolution_semaine == []
        assert rapport.articles_couteux == []
        assert isinstance(rapport.date_rapport, datetime)

    def test_custom_values(self):
        """Test assignation valeurs personnalisées."""
        from src.services.rapports_pdf import RapportBudget
        
        rapport = RapportBudget(
            periode_jours=60,
            depenses_total=2500.00,
            depenses_par_categorie={"Alimentation": 800.0, "Entretien": 200.0},
            articles_couteux=[{"nom": "Viande", "cout_total": 150.0}]
        )
        
        assert rapport.periode_jours == 60
        assert rapport.depenses_total == 2500.00
        assert len(rapport.depenses_par_categorie) == 2
        assert len(rapport.articles_couteux) == 1

    def test_periode_validation(self):
        """Test validation de la période."""
        from src.services.rapports_pdf import RapportBudget
        
        # Valid
        rapport = RapportBudget(periode_jours=1)
        assert rapport.periode_jours == 1
        
        rapport = RapportBudget(periode_jours=365)
        assert rapport.periode_jours == 365
        
        # Invalid
        with pytest.raises(ValidationError):
            RapportBudget(periode_jours=0)
        
        with pytest.raises(ValidationError):
            RapportBudget(periode_jours=400)


class TestAnalyseGaspillageSchema:
    """Tests du schéma AnalyseGaspillage."""

    def test_import_schema(self):
        """Test import AnalyseGaspillage."""
        from src.services.rapports_pdf import AnalyseGaspillage
        assert AnalyseGaspillage is not None

    def test_default_values(self):
        """Test valeurs par défaut."""
        from src.services.rapports_pdf import AnalyseGaspillage
        analyse = AnalyseGaspillage()
        
        assert analyse.periode_jours == 30
        assert analyse.articles_perimes_total == 0
        assert analyse.valeur_perdue == 0.0
        assert analyse.categories_gaspillage == {}
        assert analyse.recommandations == []
        assert analyse.articles_perimes_detail == []
        assert isinstance(analyse.date_rapport, datetime)

    def test_custom_values(self):
        """Test assignation valeurs personnalisées."""
        from src.services.rapports_pdf import AnalyseGaspillage
        
        analyse = AnalyseGaspillage(
            periode_jours=90,
            articles_perimes_total=10,
            valeur_perdue=75.50,
            categories_gaspillage={"Frais": {"articles": 5, "valeur": 40.0}},
            recommandations=["Améliorer FIFO", "Réduire les achats"],
            articles_perimes_detail=[{"nom": "Yaourt", "jours_perime": 3}]
        )
        
        assert analyse.periode_jours == 90
        assert analyse.articles_perimes_total == 10
        assert analyse.valeur_perdue == 75.50
        assert len(analyse.categories_gaspillage) == 1
        assert len(analyse.recommandations) == 2
        assert len(analyse.articles_perimes_detail) == 1


class TestRapportPlanningSchema:
    """Tests du schéma RapportPlanning."""

    def test_import_schema(self):
        """Test import RapportPlanning."""
        from src.services.rapports_pdf import RapportPlanning
        assert RapportPlanning is not None

    def test_default_values(self):
        """Test valeurs par défaut."""
        from src.services.rapports_pdf import RapportPlanning
        rapport = RapportPlanning()
        
        assert rapport.planning_id == 0
        assert rapport.nom_planning == ""
        assert rapport.semaine_debut is None
        assert rapport.semaine_fin is None
        assert rapport.repas_par_jour == {}
        assert rapport.total_repas == 0
        assert rapport.liste_courses_estimee == []
        assert isinstance(rapport.date_rapport, datetime)

    def test_custom_values(self):
        """Test assignation valeurs personnalisées."""
        from src.services.rapports_pdf import RapportPlanning
        
        now = datetime.now()
        rapport = RapportPlanning(
            planning_id=42,
            nom_planning="Semaine 12",
            semaine_debut=now,
            semaine_fin=now + timedelta(days=7),
            total_repas=14,
            repas_par_jour={"2024-01-01": [{"type": "déjeuner"}]},
            liste_courses_estimee=[{"nom": "Tomates", "quantite": 4}]
        )
        
        assert rapport.planning_id == 42
        assert rapport.nom_planning == "Semaine 12"
        assert rapport.total_repas == 14
        assert len(rapport.repas_par_jour) == 1
        assert len(rapport.liste_courses_estimee) == 1


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION SERVICE
# ═══════════════════════════════════════════════════════════


class TestRapportsPDFServiceInit:
    """Tests d'initialisation du service."""

    def test_import_service(self):
        """Test import du service."""
        from src.services.rapports_pdf import RapportsPDFService
        assert RapportsPDFService is not None

    def test_init_service(self):
        """Test création instance."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        assert service is not None
        assert service.cache_ttl == 3600

    def test_service_has_methods(self):
        """Test que le service a les méthodes attendues."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # Méthodes de données
        assert hasattr(service, 'generer_donnees_rapport_stocks')
        assert hasattr(service, 'generer_donnees_rapport_budget')
        assert hasattr(service, 'generer_analyse_gaspillage')
        assert hasattr(service, 'generer_donnees_rapport_planning')
        
        # Méthodes PDF
        assert hasattr(service, 'generer_pdf_rapport_stocks')
        assert hasattr(service, 'generer_pdf_rapport_budget')
        assert hasattr(service, 'generer_pdf_analyse_gaspillage')
        assert hasattr(service, 'generer_pdf_rapport_planning')
        
        # Méthodes téléchargement
        assert hasattr(service, 'telecharger_rapport_pdf')
        assert hasattr(service, 'telecharger_rapport_planning')


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DONNÉES STOCKS
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportStocks:
    """Tests génération données rapport stocks."""

    def test_empty_database(self):
        """Test avec base de données vide."""
        from src.services.rapports_pdf import RapportsPDFService, RapportStocks
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = []
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert isinstance(result, RapportStocks)
        assert result.articles_total == 0
        assert result.valeur_stock_total == 0.0
        assert result.articles_faible_stock == []
        assert result.articles_perimes == []

    def test_with_articles(self):
        """Test avec articles en stock."""
        from src.services.rapports_pdf import RapportsPDFService, RapportStocks
        
        # Mock articles
        article1 = Mock()
        article1.nom = "Lait"
        article1.quantite = 2
        article1.quantite_min = 3
        article1.prix_unitaire = 1.50
        article1.categorie = "Frais"
        article1.unite = "L"
        article1.emplacement = "Frigo"
        article1.date_peremption = None
        
        article2 = Mock()
        article2.nom = "Yaourt"
        article2.quantite = 5
        article2.quantite_min = 2
        article2.prix_unitaire = 0.80
        article2.categorie = "Frais"
        article2.unite = "unité"
        article2.emplacement = "Frigo"
        article2.date_peremption = datetime.now() - timedelta(days=5)  # Périmé
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article1, article2]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert isinstance(result, RapportStocks)
        assert result.articles_total == 2
        assert result.valeur_stock_total == 7.0  # 2*1.50 + 5*0.80
        assert len(result.articles_faible_stock) == 1  # Lait (2 < 3)
        assert len(result.articles_perimes) == 1  # Yaourt
        assert "Frais" in result.categories_resumee

    def test_articles_faible_stock_sorted(self):
        """Test tri des articles faible stock."""
        from src.services.rapports_pdf import RapportsPDFService
        
        # Articles avec différents ratios quantité/min
        article1 = Mock()
        article1.nom = "Article1"
        article1.quantite = 1
        article1.quantite_min = 10  # ratio: 0.1
        article1.prix_unitaire = 1.0
        article1.categorie = "Cat1"
        article1.unite = "u"
        article1.emplacement = "Stock"
        article1.date_peremption = None
        
        article2 = Mock()
        article2.nom = "Article2"
        article2.quantite = 3
        article2.quantite_min = 5  # ratio: 0.6
        article2.prix_unitaire = 1.0
        article2.categorie = "Cat1"
        article2.unite = "u"
        article2.emplacement = "Stock"
        article2.date_peremption = None
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article2, article1]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        # Premier devrait avoir le plus petit ratio
        assert result.articles_faible_stock[0]["nom"] == "Article1"

    def test_articles_perimes_sorted(self):
        """Test tri des articles périmés par jours."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        article1 = Mock()
        article1.nom = "RecemmentPerime"
        article1.quantite = 1
        article1.quantite_min = 0
        article1.prix_unitaire = 1.0
        article1.categorie = "Cat1"
        article1.unite = "u"
        article1.emplacement = "Stock"
        article1.date_peremption = now - timedelta(days=2)
        
        article2 = Mock()
        article2.nom = "TresPerime"
        article2.quantite = 1
        article2.quantite_min = 0
        article2.prix_unitaire = 1.0
        article2.categorie = "Cat1"
        article2.unite = "u"
        article2.emplacement = "Stock"
        article2.date_peremption = now - timedelta(days=30)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article1, article2]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        # Plus périmé en premier (reverse=True)
        assert result.articles_perimes[0]["nom"] == "TresPerime"
        assert result.articles_perimes[0]["jours_perime"] >= 29

    def test_categorie_summary(self):
        """Test résumé par catégorie."""
        from src.services.rapports_pdf import RapportsPDFService
        
        articles = []
        for i, cat in enumerate(["Frais", "Frais", "Épicerie"]):
            article = Mock()
            article.nom = f"Article{i}"
            article.quantite = 2
            article.quantite_min = 1
            article.prix_unitaire = 10.0
            article.categorie = cat
            article.unite = "u"
            article.emplacement = "Stock"
            article.date_peremption = None
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert "Frais" in result.categories_resumee
        assert "Épicerie" in result.categories_resumee
        assert result.categories_resumee["Frais"]["articles"] == 2
        assert result.categories_resumee["Épicerie"]["articles"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DONNÉES BUDGET
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportBudget:
    """Tests génération données rapport budget."""

    def test_empty_database(self):
        """Test avec base de données vide."""
        from src.services.rapports_pdf import RapportsPDFService, RapportBudget
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = []
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_budget(session=mock_session)
        
        assert isinstance(result, RapportBudget)
        assert result.depenses_total == 0.0
        assert result.depenses_par_categorie == {}
        assert result.articles_couteux == []

    def test_with_articles(self):
        """Test avec articles."""
        from src.services.rapports_pdf import RapportsPDFService, RapportBudget
        
        article1 = Mock()
        article1.nom = "Viande"
        article1.quantite = 2
        article1.prix_unitaire = 15.0  # coût = 30 > 10
        article1.categorie = "Boucherie"
        article1.unite = "kg"
        
        article2 = Mock()
        article2.nom = "Sel"
        article2.quantite = 1
        article2.prix_unitaire = 1.0  # coût = 1 < 10
        article2.categorie = "Épicerie"
        article2.unite = "unité"
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article1, article2]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_budget(session=mock_session)
        
        assert isinstance(result, RapportBudget)
        assert result.depenses_total == 31.0  # 30 + 1
        assert result.depenses_par_categorie["Boucherie"] == 30.0
        assert result.depenses_par_categorie["Épicerie"] == 1.0
        assert len(result.articles_couteux) == 1  # Seulement viande > 10
        assert result.articles_couteux[0]["nom"] == "Viande"

    def test_articles_couteux_sorted(self):
        """Test tri des articles coûteux."""
        from src.services.rapports_pdf import RapportsPDFService
        
        articles = []
        for i, cout in enumerate([50, 20, 100, 15]):
            article = Mock()
            article.nom = f"Article{i}"
            article.quantite = 1
            article.prix_unitaire = float(cout)
            article.categorie = "Cat"
            article.unite = "u"
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_budget(session=mock_session)
        
        # Trié par coût décroissant
        assert result.articles_couteux[0]["cout_total"] == 100.0
        assert result.articles_couteux[1]["cout_total"] == 50.0

    def test_articles_without_price(self):
        """Test articles sans prix."""
        from src.services.rapports_pdf import RapportsPDFService
        
        article = Mock()
        article.nom = "SansPrix"
        article.quantite = 10
        article.prix_unitaire = None
        article.categorie = "Cat"
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_budget(session=mock_session)
        
        assert result.depenses_total == 0.0
        assert result.articles_couteux == []


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE GASPILLAGE
# ═══════════════════════════════════════════════════════════


class TestGenererAnalyseGaspillage:
    """Tests génération analyse gaspillage."""

    def test_empty_database(self):
        """Test sans articles périmés."""
        from src.services.rapports_pdf import RapportsPDFService, AnalyseGaspillage
        
        article = Mock()
        article.nom = "Valide"
        article.quantite = 5
        article.prix_unitaire = 2.0
        article.categorie = "Frais"
        article.unite = "u"
        article.date_peremption = datetime.now() + timedelta(days=30)  # Non périmé
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        assert isinstance(result, AnalyseGaspillage)
        assert result.articles_perimes_total == 0
        assert result.valeur_perdue == 0.0
        assert result.recommandations == []

    def test_with_expired_articles(self):
        """Test avec articles périmés."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        article = Mock()
        article.nom = "YaourtPerime"
        article.quantite = 4
        article.prix_unitaire = 1.50
        article.categorie = "Frais"
        article.unite = "unité"
        article.date_peremption = now - timedelta(days=7)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        assert result.articles_perimes_total == 1
        assert result.valeur_perdue == 6.0  # 4 * 1.50
        assert len(result.articles_perimes_detail) == 1
        assert result.articles_perimes_detail[0]["nom"] == "YaourtPerime"
        assert result.articles_perimes_detail[0]["jours_perime"] >= 6

    def test_recommendations_gaspillage_important(self):
        """Test recommandations pour gaspillage important."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        articles = []
        
        # Plus de 5 articles périmés
        for i in range(10):
            article = Mock()
            article.nom = f"Perime{i}"
            article.quantite = 1
            article.prix_unitaire = 10.0
            article.categorie = "Cat"
            article.unite = "u"
            article.date_peremption = now - timedelta(days=1)
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        # Devrait avoir des recommandations
        assert len(result.recommandations) >= 2

    def test_valeur_perdue_elevee(self):
        """Test recommandation pour valeur perdue élevée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        article = Mock()
        article.nom = "ViandePerimee"
        article.quantite = 5
        article.prix_unitaire = 20.0  # 100€ perdu
        article.categorie = "Boucherie"
        article.unite = "kg"
        article.date_peremption = now - timedelta(days=3)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        assert result.valeur_perdue == 100.0
        # Une recommandation pour valeur > 50€
        assert any("Valeur perdue" in rec for rec in result.recommandations)

    def test_gaspillage_par_categorie(self):
        """Test gaspillage par catégorie."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        articles = []
        
        for i, (cat, prix) in enumerate([("Frais", 5.0), ("Frais", 3.0), ("Boucherie", 20.0)]):
            article = Mock()
            article.nom = f"Article{i}"
            article.quantite = 1
            article.prix_unitaire = prix
            article.categorie = cat
            article.unite = "u"
            article.date_peremption = now - timedelta(days=1)
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        assert "Frais" in result.categories_gaspillage
        assert "Boucherie" in result.categories_gaspillage
        assert result.categories_gaspillage["Frais"]["articles"] == 2
        assert result.categories_gaspillage["Frais"]["valeur"] == 8.0


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DONNÉES PLANNING
# ═══════════════════════════════════════════════════════════


class TestGenererDonneesRapportPlanning:
    """Tests génération données rapport planning."""

    def test_planning_not_found(self):
        """Test planning non trouvé."""
        from src.services.rapports_pdf import RapportsPDFService
        from src.core.errors_base import ErreurNonTrouve
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        
        with pytest.raises(ErreurNonTrouve):
            service.generer_donnees_rapport_planning(planning_id=999, session=mock_session)

    def test_with_planning(self):
        """Test avec planning valide."""
        from src.services.rapports_pdf import RapportsPDFService, RapportPlanning
        
        now = datetime.now()
        
        # Mock planning
        mock_planning = Mock()
        mock_planning.id = 1
        mock_planning.nom = "Semaine 12"
        mock_planning.semaine_debut = now
        mock_planning.semaine_fin = now + timedelta(days=7)
        mock_planning.repas = []
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_planning
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_session)
        
        assert isinstance(result, RapportPlanning)
        assert result.planning_id == 1
        assert result.nom_planning == "Semaine 12"
        assert result.total_repas == 0

    def test_with_repas(self):
        """Test avec repas planifiés."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        # Mock recette
        mock_recette = Mock()
        mock_recette.nom = "Poulet rôti"
        mock_recette.portions = 4
        mock_recette.ingredients = []
        
        # Mock repas
        mock_repas = Mock()
        mock_repas.date_repas = now
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = mock_recette
        mock_repas.portion_ajustee = 6
        mock_repas.prepare = True
        mock_repas.notes = "Test"
        
        # Mock planning
        mock_planning = Mock()
        mock_planning.id = 1
        mock_planning.nom = "Semaine Test"
        mock_planning.semaine_debut = now
        mock_planning.semaine_fin = now + timedelta(days=7)
        mock_planning.repas = [mock_repas]
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_planning
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_session)
        
        assert result.total_repas == 1
        date_key = now.strftime('%Y-%m-%d')
        assert date_key in result.repas_par_jour
        assert result.repas_par_jour[date_key][0]["recette_nom"] == "Poulet rôti"
        assert result.repas_par_jour[date_key][0]["portions"] == 6

    def test_liste_courses_estimee(self):
        """Test création liste courses estimée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        # Mock ingrédient
        mock_ingredient = Mock()
        mock_ingredient.nom = "Tomates"
        mock_ingredient.unite_defaut = "kg"
        
        # Mock recette ingrédient
        mock_ri = Mock()
        mock_ri.ingredient = mock_ingredient
        mock_ri.quantite = 0.5
        mock_ri.unite = "kg"
        
        # Mock recette
        mock_recette = Mock()
        mock_recette.nom = "Salade"
        mock_recette.portions = 4
        mock_recette.ingredients = [mock_ri]
        
        # Mock repas
        mock_repas = Mock()
        mock_repas.date_repas = now
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = mock_recette
        mock_repas.portion_ajustee = None
        mock_repas.prepare = False
        mock_repas.notes = ""
        
        # Mock planning
        mock_planning = Mock()
        mock_planning.id = 1
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = now
        mock_planning.semaine_fin = now + timedelta(days=7)
        mock_planning.repas = [mock_repas]
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_planning
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_session)
        
        assert len(result.liste_courses_estimee) == 1
        assert result.liste_courses_estimee[0]["nom"] == "Tomates"
        assert result.liste_courses_estimee[0]["quantite"] == 0.5


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PDF - SANS APPELS BD
# ═══════════════════════════════════════════════════════════


class TestGenererPDFRapportStocks:
    """Tests génération PDF rapport stocks."""

    def test_pdf_stocks_structure(self):
        """Test structure des données du PDF stocks."""
        from src.services.rapports_pdf import RapportStocks
        
        # Test qu'on peut créer un rapport avec données
        rapport = RapportStocks(
            articles_total=5,
            valeur_stock_total=150.0,
            articles_faible_stock=[
                {"nom": "Lait", "quantite": 1, "quantite_min": 3, "unite": "L", "emplacement": "Frigo"}
            ],
            articles_perimes=[
                {"nom": "Pain", "date_peremption": datetime.now() - timedelta(days=2), "jours_perime": 2, "quantite": 0, "unite": "unité"}
            ],
            categories_resumee={"Frais": {"quantite": 10, "valeur": 100.0, "articles": 3}}
        )
        
        assert rapport.articles_total == 5
        assert len(rapport.articles_faible_stock) == 1


class TestGenererPDFRapportBudget:
    """Tests génération PDF rapport budget."""

    def test_pdf_budget_structure(self):
        """Test structure des données du PDF budget."""
        from src.services.rapports_pdf import RapportBudget
        
        rapport = RapportBudget(
            depenses_total=100.0,
            depenses_par_categorie={"Boucherie": 60.0, "Légumes": 40.0},
            articles_couteux=[
                {"nom": "Viande", "categorie": "Boucherie", "quantite": 1, "unite": "kg", "cout_total": 25.0}
            ]
        )
        
        assert rapport.depenses_total == 100.0
        assert len(rapport.depenses_par_categorie) == 2


class TestGenererPDFAnalyseGaspillage:
    """Tests génération PDF analyse gaspillage."""

    def test_pdf_gaspillage_structure(self):
        """Test structure des données du gaspillage."""
        from src.services.rapports_pdf import AnalyseGaspillage
        
        analyse = AnalyseGaspillage(
            articles_perimes_total=8,
            valeur_perdue=160.0,
            recommandations=["Améliorer FIFO", "Réduire les achats"],
            articles_perimes_detail=[
                {"nom": "Yaourt", "jours_perime": 3, "quantite": 2, "unite": "u", "valeur_perdue": 20.0}
            ],
            categories_gaspillage={"Frais": {"articles": 8, "valeur": 160.0}}
        )
        
        assert analyse.articles_perimes_total == 8
        assert len(analyse.recommandations) == 2


class TestGenererPDFRapportPlanning:
    """Tests génération PDF rapport planning."""

    def test_pdf_planning_structure(self):
        """Test structure des données du planning."""
        from src.services.rapports_pdf import RapportPlanning
        
        now = datetime.now()
        date_key = now.strftime('%Y-%m-%d')
        
        rapport = RapportPlanning(
            planning_id=1,
            nom_planning="Planning Semaine",
            semaine_debut=now,
            semaine_fin=now + timedelta(days=7),
            repas_par_jour={
                date_key: [
                    {"type": "déjeuner", "recette_nom": "Poulet", "portions": 4, "prepare": False, "notes": ""}
                ]
            },
            total_repas=1,
            liste_courses_estimee=[{"nom": "Poulet", "quantite": 1, "unite": "kg"}]
        )
        
        assert rapport.planning_id == 1
        assert rapport.total_repas == 1


# ═══════════════════════════════════════════════════════════
# TESTS TÉLÉCHARGEMENT
# ═══════════════════════════════════════════════════════════


class TestTelechargerRapportPDF:
    """Tests méthode telecharger_rapport_pdf - test de validation."""

    def test_telecharger_type_inconnu(self):
        """Test type de rapport inconnu."""
        from src.services.rapports_pdf import RapportsPDFService
        from src.core.errors_base import ErreurValidation
        
        service = RapportsPDFService()
        
        with pytest.raises(ErreurValidation):
            service.telecharger_rapport_pdf("inconnu")

    def test_service_a_methode_telecharger(self):
        """Test que le service possède les méthodes telecharger."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        assert hasattr(service, "telecharger_rapport_pdf")
        assert hasattr(service, "telecharger_rapport_planning")
        assert callable(service.telecharger_rapport_pdf)


class TestTelechargerRapportPlanning:
    """Tests méthode telecharger_rapport_planning."""

    def test_service_a_methode_telecharger_planning(self):
        """Test que le service possède la méthode telecharger_rapport_planning."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        assert hasattr(service, "telecharger_rapport_planning")
        assert callable(service.telecharger_rapport_planning)


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES PDF
# ═══════════════════════════════════════════════════════════


class TestPDFStyles:
    """Tests des styles PDF et imports."""

    def test_pdf_uses_a4_constant(self):
        """Test que A4 est importable pour le PDF."""
        from reportlab.lib.pagesizes import A4
        
        assert A4 is not None
        assert len(A4) == 2  # (width, height)

    def test_pdf_imports_reportlab(self):
        """Test que ReportLab est disponible."""
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
        
        assert SimpleDocTemplate is not None
        assert Table is not None
        assert colors is not None

    def test_table_style_creation(self):
        """Test création de TableStyle."""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        # Créer une table simple
        data = [["A", "B", "C"], ["1", "2", "3"]]
        table = Table(data)
        
        # Appliquer un style
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ])
        table.setStyle(style)
        
        assert table is not None
        
    def test_pdf_content_validation(self):
        """Test que le module PDF exporte les éléments requis."""
        from src.services.rapports_pdf import (
            RapportsPDFService,
            RapportStocks,
            RapportBudget,
            AnalyseGaspillage,
            RapportPlanning
        )
        
        # Vérifier que tous les éléments sont importables
        assert RapportsPDFService is not None
        assert RapportStocks is not None
        assert RapportBudget is not None


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests des cas limites."""

    def test_article_with_zero_quantity_min(self):
        """Test article avec quantité_min = 0."""
        from src.services.rapports_pdf import RapportsPDFService
        
        article = Mock()
        article.nom = "Test"
        article.quantite = 5
        article.quantite_min = 0  # Division par zéro potentielle
        article.prix_unitaire = 1.0
        article.categorie = "Cat"
        article.unite = "u"
        article.emplacement = "Stock"
        article.date_peremption = None
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        # Ne devrait pas lever d'exception
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        assert result.articles_faible_stock == []

    def test_article_with_none_values(self):
        """Test article avec valeurs None."""
        from src.services.rapports_pdf import RapportsPDFService
        
        article = Mock()
        article.nom = "Test"
        article.quantite = 0
        article.quantite_min = 0
        article.prix_unitaire = None
        article.categorie = "Cat"
        article.unite = "u"
        article.emplacement = None
        article.date_peremption = None
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert result.valeur_stock_total == 0.0

    def test_long_article_names_in_schema(self):
        """Test noms longs dans les schémas."""
        from src.services.rapports_pdf import RapportStocks
        
        # Créer un rapport avec nom long
        rapport = RapportStocks(
            articles_total=1,
            valeur_stock_total=10.0,
            articles_faible_stock=[
                {"nom": "A" * 100, "quantite": 1, "quantite_min": 5, "unite": "u", "emplacement": "Stock"}
            ],
            articles_perimes=[],
            categories_resumee={}
        )
        
        assert len(rapport.articles_faible_stock[0]["nom"]) == 100

    def test_empty_categories(self):
        """Test catégorie vide."""
        from src.services.rapports_pdf import RapportsPDFService
        
        article = Mock()
        article.nom = "Test"
        article.quantite = 5
        article.quantite_min = 1
        article.prix_unitaire = 2.0
        article.categorie = ""  # Catégorie vide
        article.unite = "u"
        article.emplacement = "Stock"
        article.date_peremption = None
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = [article]
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert "" in result.categories_resumee

    def test_special_characters_in_names(self):
        """Test caractères spéciaux dans les noms de schéma."""
        from src.services.rapports_pdf import RapportStocks
        
        # Créer un rapport avec caractères spéciaux
        rapport = RapportStocks(
            articles_total=1,
            valeur_stock_total=5.0,
            articles_faible_stock=[
                {"nom": "Café espresso été", "quantite": 2, "quantite_min": 1, "unite": "u", "emplacement": "Cuisine"}
            ],
            articles_perimes=[],
            categories_resumee={"Boissons": {"quantite": 2, "valeur": 5.0, "articles": 1}}
        )
        
        assert "Café" in rapport.articles_faible_stock[0]["nom"]

    def test_repas_without_recette(self):
        """Test repas sans recette associée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        mock_repas = Mock()
        mock_repas.date_repas = now
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = None  # Pas de recette
        mock_repas.portion_ajustee = None
        mock_repas.prepare = False
        mock_repas.notes = ""
        
        mock_planning = Mock()
        mock_planning.id = 1
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = now
        mock_planning.semaine_fin = now + timedelta(days=7)
        mock_planning.repas = [mock_repas]
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_planning
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_session)
        
        date_key = now.strftime('%Y-%m-%d')
        assert result.repas_par_jour[date_key][0]["recette_nom"] == "Repas libre"

    def test_ingredient_without_ingredient(self):
        """Test RecetteIngredient sans ingrédient."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        
        # Mock RI sans ingrédient
        mock_ri = Mock()
        mock_ri.ingredient = None
        mock_ri.quantite = 1.0
        mock_ri.unite = "u"
        
        mock_recette = Mock()
        mock_recette.nom = "Test"
        mock_recette.portions = 2
        mock_recette.ingredients = [mock_ri]
        
        mock_repas = Mock()
        mock_repas.date_repas = now
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette = mock_recette
        mock_repas.portion_ajustee = None
        mock_repas.prepare = False
        mock_repas.notes = ""
        
        mock_planning = Mock()
        mock_planning.id = 1
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = now
        mock_planning.semaine_fin = now + timedelta(days=7)
        mock_planning.repas = [mock_repas]
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_planning
        mock_session.query.return_value = mock_query
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_planning(planning_id=1, session=mock_session)
        
        # Liste courses devrait être vide car ingrédient None
        assert result.liste_courses_estimee == []


# ═══════════════════════════════════════════════════════════
# TESTS PERFORMANCE
# ═══════════════════════════════════════════════════════════


class TestPerformance:
    """Tests de performance."""

    def test_many_articles(self):
        """Test avec beaucoup d'articles."""
        from src.services.rapports_pdf import RapportsPDFService
        
        articles = []
        for i in range(100):
            article = Mock()
            article.nom = f"Article{i}"
            article.quantite = i % 10
            article.quantite_min = 5
            article.prix_unitaire = float(i * 0.5)
            article.categorie = f"Cat{i % 5}"
            article.unite = "u"
            article.emplacement = "Stock"
            article.date_peremption = None
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_donnees_rapport_stocks(session=mock_session)
        
        assert result.articles_total == 100
        assert len(result.categories_resumee) == 5

    def test_many_expired_articles(self):
        """Test avec beaucoup d'articles périmés."""
        from src.services.rapports_pdf import RapportsPDFService
        
        now = datetime.now()
        articles = []
        
        for i in range(50):
            article = Mock()
            article.nom = f"Perime{i}"
            article.quantite = 1
            article.quantite_min = 0
            article.prix_unitaire = 1.0
            article.categorie = f"Cat{i % 3}"
            article.unite = "u"
            article.emplacement = "Stock"
            article.date_peremption = now - timedelta(days=i+1)
            articles.append(article)
        
        mock_session = Mock()
        mock_session.query.return_value.all.return_value = articles
        
        service = RapportsPDFService()
        result = service.generer_analyse_gaspillage(session=mock_session)
        
        assert result.articles_perimes_total == 50
        assert result.valeur_perdue == 50.0
