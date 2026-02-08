"""
Tests pour les méthodes de génération PDF de RapportsPDFService.

Ces tests ciblent les lignes non couvertes en mockant les méthodes de données
et en appelant les méthodes de génération PDF.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from io import BytesIO
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════
# FIXTURES - Data Schemas
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_rapport_stocks():
    """Crée des données de rapport stocks."""
    from src.services.rapports_pdf import RapportStocks
    
    return RapportStocks(
        date_rapport=datetime.now(),
        periode_jours=7,
        articles_total=50,
        articles_faible_stock=[
            {"nom": "Lait", "quantite": 1, "quantite_min": 3, "unite": "L", "emplacement": "Frigo"},
            {"nom": "Pain", "quantite": 0, "quantite_min": 2, "unite": "pcs", "emplacement": "Garde-manger"},
            {"nom": "Beurre", "quantite": 1, "quantite_min": 2, "unite": "pcs", "emplacement": "Frigo"},
        ],
        articles_perimes=[
            {"nom": "Yaourt", "date_peremption": datetime.now() - timedelta(days=2), "jours_perime": 2, "quantite": 4, "unite": "pcs"},
            {"nom": "Crème", "date_peremption": datetime.now() - timedelta(days=1), "jours_perime": 1, "quantite": 1, "unite": "pcs"},
        ],
        valeur_stock_total=156.50,
        categories_resumee={
            "produits_laitiers": {"articles": 12, "quantite": 24, "valeur": 45.00},
            "boulangerie": {"articles": 5, "quantite": 10, "valeur": 12.00},
            "fruits_legumes": {"articles": 20, "quantite": 50, "valeur": 65.00},
            "viandes": {"articles": 8, "quantite": 15, "valeur": 34.50},
        }
    )


@pytest.fixture
def mock_rapport_stocks_minimal():
    """Crée des données minimales de rapport stocks."""
    from src.services.rapports_pdf import RapportStocks
    
    return RapportStocks(
        date_rapport=datetime.now(),
        periode_jours=7,
        articles_total=0,
        articles_faible_stock=[],
        articles_perimes=[],
        valeur_stock_total=0.0,
        categories_resumee={}
    )


@pytest.fixture
def mock_rapport_budget():
    """Crée des données de rapport budget."""
    from src.services.rapports_pdf import RapportBudget
    
    return RapportBudget(
        date_rapport=datetime.now(),
        periode_jours=30,
        depenses_total=523.45,
        depenses_par_categorie={
            "alimentation": 250.00,
            "hygiene": 45.00,
            "entretien": 78.45,
            "autres": 150.00,
        },
        evolution_semaine=[
            {"semaine": "S01", "montant": 125.00},
            {"semaine": "S02", "montant": 145.00},
            {"semaine": "S03", "montant": 110.00},
            {"semaine": "S04", "montant": 143.45},
        ],
        articles_couteux=[
            {"nom": "Côte de boeuf", "categorie": "Viandes", "quantite": 2, "unite": "kg", "cout_total": 35.00},
            {"nom": "Saumon frais", "categorie": "Poissons", "quantite": 1, "unite": "kg", "cout_total": 28.00},
            {"nom": "Champagne", "categorie": "Boissons", "quantite": 1, "unite": "btl", "cout_total": 45.00},
        ]
    )


@pytest.fixture
def mock_rapport_budget_minimal():
    """Crée des données minimales de rapport budget."""
    from src.services.rapports_pdf import RapportBudget
    
    return RapportBudget(
        date_rapport=datetime.now(),
        periode_jours=30,
        depenses_total=0.0,
        depenses_par_categorie={},
        evolution_semaine=[],
        articles_couteux=[]
    )


@pytest.fixture
def mock_analyse_gaspillage():
    """Crée des données d'analyse gaspillage."""
    from src.services.rapports_pdf import AnalyseGaspillage
    
    return AnalyseGaspillage(
        date_rapport=datetime.now(),
        periode_jours=30,
        articles_perimes_total=8,
        valeur_perdue=42.50,
        categories_gaspillage={
            "produits_laitiers": {"articles": 4, "valeur": 18.00},
            "fruits_legumes": {"articles": 3, "valeur": 12.50},
            "viandes": {"articles": 1, "valeur": 12.00},
        },
        recommandations=[
            "Réduire les achats de yaourts",
            "Vérifier les dates avant achat",
            "Mieux planifier les repas",
        ],
        articles_perimes_detail=[
            {"nom": "Yaourt nature", "jours_perime": 5, "quantite": 4, "unite": "pcs", "valeur_perdue": 4.00},
            {"nom": "Salade verte", "jours_perime": 3, "quantite": 1, "unite": "pcs", "valeur_perdue": 2.50},
        ]
    )


@pytest.fixture
def mock_analyse_gaspillage_minimal():
    """Crée des données minimales d'analyse gaspillage."""
    from src.services.rapports_pdf import AnalyseGaspillage
    
    return AnalyseGaspillage(
        date_rapport=datetime.now(),
        periode_jours=30,
        articles_perimes_total=0,
        valeur_perdue=0.0,
        categories_gaspillage={},
        recommandations=[],
        articles_perimes_detail=[]
    )


@pytest.fixture
def mock_rapport_planning():
    """Crée des données de rapport planning."""
    from src.services.rapports_pdf import RapportPlanning
    
    now = datetime.now()
    debut = now - timedelta(days=now.weekday())
    
    # Date keys in ISO format
    lundi = debut.strftime('%Y-%m-%d')
    mardi = (debut + timedelta(days=1)).strftime('%Y-%m-%d')
    mercredi = (debut + timedelta(days=2)).strftime('%Y-%m-%d')
    
    return RapportPlanning(
        date_rapport=now,
        planning_id=1,
        nom_planning="Menu Semaine 4",
        semaine_debut=debut,
        semaine_fin=debut + timedelta(days=6),
        repas_par_jour={
            lundi: [
                {"type": "déjeuner", "recette_nom": "Salade composée", "portions": 4, "prepare": False},
                {"type": "dîner", "recette_nom": "Pâtes carbonara", "portions": 4, "prepare": True}
            ],
            mardi: [
                {"type": "déjeuner", "recette_nom": "Quiche lorraine", "portions": 6, "prepare": False},
                {"type": "dîner", "recette_nom": "Soupe de légumes", "portions": 4, "prepare": False}
            ],
            mercredi: [
                {"type": "déjeuner", "recette_nom": "Poulet rôti", "portions": 4, "prepare": False}
            ],
        },
        total_repas=5,
        liste_courses_estimee=[
            {"nom": "Poulet", "quantite": 1, "unite": "kg"},
            {"nom": "Pâtes", "quantite": 500, "unite": "g"},
            {"nom": "Lardons", "quantite": 200, "unite": "g"},
            {"nom": "Crème fraîche", "quantite": 25, "unite": "cl"},
        ]
    )


@pytest.fixture
def mock_rapport_planning_minimal():
    """Crée des données minimales de rapport planning."""
    from src.services.rapports_pdf import RapportPlanning
    
    return RapportPlanning(
        date_rapport=datetime.now(),
        planning_id=0,
        nom_planning="",
        semaine_debut=None,
        semaine_fin=None,
        repas_par_jour={},
        total_repas=0,
        liste_courses_estimee=[]
    )


# ═══════════════════════════════════════════════════════════
# TESTS - generer_pdf_rapport_stocks (lignes 206-372)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGenererPDFRapportStocks:
    """Tests pour generer_pdf_rapport_stocks."""

    def test_generer_pdf_rapport_stocks_complet(self, mock_rapport_stocks):
        """Test génération PDF rapport stocks avec données complètes."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # Mock la méthode qui récupère les données
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            # Mock session - MUST be passed as keyword argument
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read(4)
        assert content == b'%PDF'

    def test_generer_pdf_rapport_stocks_vide(self, mock_rapport_stocks_minimal):
        """Test génération PDF rapport stocks sans données."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks_minimal):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_stocks_periode_differente(self, mock_rapport_stocks):
        """Test génération PDF rapport stocks avec période différente."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_rapport_stocks.periode_jours = 30
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(30, session=mock_session)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS - generer_pdf_rapport_budget (lignes 447-581)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGenererPDFRapportBudget:
    """Tests pour generer_pdf_rapport_budget."""

    def test_generer_pdf_rapport_budget_complet(self, mock_rapport_budget):
        """Test génération PDF rapport budget avec données complètes."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read(4)
        assert content == b'%PDF'

    def test_generer_pdf_rapport_budget_vide(self, mock_rapport_budget_minimal):
        """Test génération PDF rapport budget sans données."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget_minimal):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_budget_categories_multiples(self, mock_rapport_budget):
        """Test génération PDF rapport budget avec beaucoup de catégories."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # Ajouter plus de catégories
        mock_rapport_budget.depenses_par_categorie.update({
            "boissons": 65.00,
            "surgelés": 45.00,
            "épicerie": 120.00,
        })
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_budget_periode_courte(self, mock_rapport_budget):
        """Test génération PDF rapport budget période courte."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_rapport_budget.periode_jours = 7
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(7, session=mock_session)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS - generer_pdf_analyse_gaspillage (lignes 670-820)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGenererPDFAnalyseGaspillage:
    """Tests pour generer_pdf_analyse_gaspillage."""

    def test_generer_pdf_analyse_gaspillage_complet(self, mock_analyse_gaspillage):
        """Test génération PDF analyse gaspillage avec données complètes."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read(4)
        assert content == b'%PDF'

    def test_generer_pdf_analyse_gaspillage_vide(self, mock_analyse_gaspillage_minimal):
        """Test génération PDF analyse gaspillage sans données."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage_minimal):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)

    def test_generer_pdf_analyse_gaspillage_recommandations(self, mock_analyse_gaspillage):
        """Test génération PDF avec recommandations multiples."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # Ajouter plus de recommandations
        mock_analyse_gaspillage.recommandations.extend([
            "Congeler les restes",
            "Faire des conserves",
            "Utiliser les restes créativement",
        ])
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_analyse_gaspillage_valeur_elevee(self, mock_analyse_gaspillage):
        """Test génération PDF avec valeur perdue élevée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_analyse_gaspillage.valeur_perdue = 250.00
        mock_analyse_gaspillage.articles_perimes_total = 45
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS - generer_pdf_rapport_planning (lignes 959-1127)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGenererPDFRapportPlanning:
    """Tests pour generer_pdf_rapport_planning."""

    def test_generer_pdf_rapport_planning_complet(self, mock_rapport_planning):
        """Test génération PDF rapport planning avec données complètes."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        result.seek(0)
        content = result.read(4)
        assert content == b'%PDF'

    def test_generer_pdf_rapport_planning_vide(self, mock_rapport_planning_minimal):
        """Test génération PDF rapport planning sans données."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning_minimal):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert result is not None
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_planning_avec_date(self, mock_rapport_planning):
        """Test génération PDF rapport planning avec date spécifiée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_planning_tous_jours(self, mock_rapport_planning):
        """Test génération PDF rapport planning avec tous les jours."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        now = datetime.now()
        debut = now - timedelta(days=now.weekday())
        
        # Use date string keys with proper repas format
        mock_rapport_planning.repas_par_jour = {
            debut.strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 1", "portions": 4, "prepare": False}],
            (debut + timedelta(days=1)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 2", "portions": 4, "prepare": False}],
            (debut + timedelta(days=2)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 3", "portions": 4, "prepare": False}],
            (debut + timedelta(days=3)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 4", "portions": 4, "prepare": False}],
            (debut + timedelta(days=4)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 5", "portions": 4, "prepare": False}],
            (debut + timedelta(days=5)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 6", "portions": 4, "prepare": False}, 
                       {"type": "dîner", "recette_nom": "Recette 7", "portions": 4, "prepare": True}],
            (debut + timedelta(days=6)).strftime('%Y-%m-%d'): [{"type": "déjeuner", "recette_nom": "Recette 8", "portions": 4, "prepare": True}],
        }
        mock_rapport_planning.total_repas = 9
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_generer_pdf_rapport_planning_liste_courses_longue(self, mock_rapport_planning):
        """Test génération PDF rapport planning avec longue liste courses."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # Ajouter beaucoup d'ingrédients
        mock_rapport_planning.liste_courses_estimee = [
            {"nom": f"Ingrédient {i}", "quantite": i * 100, "unite": "g"}
            for i in range(1, 20)
        ]
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS - Méthodes utilitaires et factory
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRapportsPDFUtilitaires:
    """Tests pour les méthodes utilitaires."""

    def test_service_instantiation(self):
        """Test instanciation du service."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        assert service is not None

    def test_factory_function(self):
        """Test factory function get_rapports_pdf_service."""
        import src.services.rapports_pdf as module
        from src.services.rapports_pdf import get_rapports_pdf_service
        
        # Reset singleton for isolated test
        module._rapports_pdf_service_instance = None
        
        service = get_rapports_pdf_service()
        assert service is not None

    def test_factory_returns_same_instance(self):
        """Test factory retourne la même instance (singleton)."""
        import src.services.rapports_pdf as module
        from src.services.rapports_pdf import get_rapports_pdf_service
        
        # Reset singleton
        module._rapports_pdf_service_instance = None
        
        service1 = get_rapports_pdf_service()
        service2 = get_rapports_pdf_service()
        
        assert service1 is service2

    def test_schemas_exports(self):
        """Test export des schémas Pydantic."""
        from src.services.rapports_pdf import (
            RapportStocks,
            RapportBudget,
            AnalyseGaspillage,
            RapportPlanning,
        )
        
        # Vérifier que les schémas peuvent être instanciés
        stocks = RapportStocks()
        budget = RapportBudget()
        gaspillage = AnalyseGaspillage()
        planning = RapportPlanning()
        
        assert stocks.articles_total == 0
        assert budget.depenses_total == 0.0
        assert gaspillage.valeur_perdue == 0.0
        assert planning.total_repas == 0


# ═══════════════════════════════════════════════════════════
# TESTS - Validation données intermédiaires
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGenererDonneesRapport:
    """Tests pour les méthodes de génération de données."""

    def test_generer_donnees_rapport_stocks_avec_session(self):
        """Test génération données stocks avec session mockée."""
        from src.services.rapports_pdf import RapportsPDFService, RapportStocks
        
        service = RapportsPDFService()
        
        # Mock session et query
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        
        result = service.generer_donnees_rapport_stocks(7, session=mock_session)
        
        assert isinstance(result, RapportStocks)

    def test_generer_donnees_rapport_budget_avec_session(self):
        """Test génération données budget avec session mockée."""
        from src.services.rapports_pdf import RapportsPDFService, RapportBudget
        
        service = RapportsPDFService()
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        
        result = service.generer_donnees_rapport_budget(30, session=mock_session)
        
        assert isinstance(result, RapportBudget)


# ═══════════════════════════════════════════════════════════
# TESTS - Gestion des cas limites
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit  
class TestCasLimites:
    """Tests pour les cas limites."""

    def test_rapport_stocks_valeur_tres_elevee(self, mock_rapport_stocks):
        """Test rapport stocks avec valeur très élevée."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_rapport_stocks.valeur_stock_total = 99999.99
        mock_rapport_stocks.articles_total = 500
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_rapport_budget_depenses_zero(self, mock_rapport_budget_minimal):
        """Test rapport budget avec dépenses zéro."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget_minimal):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_gaspillage_sans_recommandations(self, mock_analyse_gaspillage):
        """Test analyse gaspillage sans recommandations."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_analyse_gaspillage.recommandations = []
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_planning_nom_long(self, mock_rapport_planning):
        """Test planning avec nom très long."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        mock_rapport_planning.nom_planning = "Menu de la semaine avec des plats traditionnels et modernes pour toute la famille"
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_planning_notes_speciales(self, mock_rapport_planning):
        """Test planning avec notes contenant caractères spéciaux."""
        from src.services.rapports_pdf import RapportsPDFService
        from datetime import datetime, timedelta
        
        service = RapportsPDFService()
        now = datetime.now()
        debut = now - timedelta(days=now.weekday())
        lundi = debut.strftime('%Y-%m-%d')
        
        mock_rapport_planning.repas_par_jour = {
            lundi: [
                {"type": "déjeuner", "recette_nom": "Bœuf bourguignon", "portions": 4, "prepare": False},
                {"type": "dîner", "recette_nom": "Crêpes & compagnie", "portions": 4, "prepare": True}
            ],
        }
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        assert isinstance(result, BytesIO)


# ═══════════════════════════════════════════════════════════
# TESTS - Validation PDF valide
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPDFValidation:
    """Tests validant que les PDFs générés sont valides."""

    def test_pdf_stocks_contient_eof(self, mock_rapport_stocks):
        """Test PDF stocks contient marqueur EOF."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        result.seek(0)
        content = result.read()
        assert b'%%EOF' in content[-20:]

    def test_pdf_budget_contient_eof(self, mock_rapport_budget):
        """Test PDF budget contient marqueur EOF."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        result.seek(0)
        content = result.read()
        assert b'%%EOF' in content[-20:]

    def test_pdf_gaspillage_contient_eof(self, mock_analyse_gaspillage):
        """Test PDF gaspillage contient marqueur EOF."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        result.seek(0)
        content = result.read()
        assert b'%%EOF' in content[-20:]

    def test_pdf_planning_contient_eof(self, mock_rapport_planning):
        """Test PDF planning contient marqueur EOF."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        mock_session = MagicMock()
        with patch.object(service, 'generer_donnees_rapport_planning', return_value=mock_rapport_planning):
            result = service.generer_pdf_rapport_planning(1, session=mock_session)
        
        result.seek(0)
        content = result.read()
        assert b'%%EOF' in content[-20:]


# ═══════════════════════════════════════════════════════════
# TESTS - Données volumineuses
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestDonneesVolumineuses:
    """Tests avec données volumineuses."""

    def test_stocks_beaucoup_articles_faible_stock(self, mock_rapport_stocks):
        """Test rapport stocks avec beaucoup d'articles faible stock."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # 50 articles faible stock
        mock_rapport_stocks.articles_faible_stock = [
            {"nom": f"Article {i}", "quantite": i % 3, "quantite_min": 5, "unite": "kg", "emplacement": "Frigo"}
            for i in range(50)
        ]
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_stocks_beaucoup_articles_perimes(self, mock_rapport_stocks):
        """Test rapport stocks avec beaucoup d'articles périmés."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # 30 articles périmés - date_peremption as datetime object
        mock_rapport_stocks.articles_perimes = [
            {"nom": f"Périmé {i}", "date_peremption": datetime.now() - timedelta(days=i), "jours_perime": i, "quantite": 1, "unite": "kg"}
            for i in range(1, 31)
        ]
        
        with patch.object(service, 'generer_donnees_rapport_stocks', return_value=mock_rapport_stocks):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_stocks(7, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_budget_beaucoup_categories(self, mock_rapport_budget):
        """Test rapport budget avec beaucoup de catégories."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # 15 catégories
        mock_rapport_budget.depenses_par_categorie = {
            f"categorie_{i}": 50.0 + i * 10
            for i in range(15)
        }
        
        with patch.object(service, 'generer_donnees_rapport_budget', return_value=mock_rapport_budget):
            mock_session = MagicMock()
            result = service.generer_pdf_rapport_budget(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

    def test_gaspillage_beaucoup_articles_detail(self, mock_analyse_gaspillage):
        """Test analyse gaspillage avec beaucoup de détails."""
        from src.services.rapports_pdf import RapportsPDFService
        
        service = RapportsPDFService()
        
        # 40 articles périmés
        mock_analyse_gaspillage.articles_perimes_detail = [
            {"nom": f"Article périmé {i}", "quantite": i, "jours_perime": i, "unite": "kg", "valeur_perdue": i * 2.5}
            for i in range(1, 41)
        ]
        
        with patch.object(service, 'generer_analyse_gaspillage', return_value=mock_analyse_gaspillage):
            mock_session = MagicMock()
            result = service.generer_pdf_analyse_gaspillage(30, session=mock_session)
        
        assert isinstance(result, BytesIO)

