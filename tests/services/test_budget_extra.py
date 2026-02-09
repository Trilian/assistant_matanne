"""
Tests supplementaires pour budget.py - couvre les methodes manquantes.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date
from decimal import Decimal

from src.services.budget import (
    BudgetService,
    CategorieDepense,
    Depense,
    FactureMaison,
    FrequenceRecurrence,
    get_budget_service,
    DEFAULT_USER_ID,
)


class TestDefinirBudgetsBatch:
    """Tests pour definir_budgets_batch()."""
    
    def test_definir_budgets_batch_new_budget(self):
        """Test definir plusieurs budgets quand aucun n'existe."""
        service = BudgetService()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        budgets = {
            CategorieDepense.ALIMENTATION: 600.0,
            CategorieDepense.COURSES: 200.0,
        }
        
        service.definir_budgets_batch(budgets, mois=1, annee=2024, db=mock_db)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_definir_budgets_batch_existing_budget(self):
        """Test definir plusieurs budgets quand un budget existe."""
        service = BudgetService()
        mock_db = MagicMock()
        existing_budget = MagicMock()
        existing_budget.budgets_par_categorie = {"transport": 100.0}
        mock_db.query.return_value.filter.return_value.first.return_value = existing_budget
        
        budgets = {
            CategorieDepense.ALIMENTATION: 600.0,
            CategorieDepense.COURSES: 200.0,
        }
        
        service.definir_budgets_batch(budgets, mois=1, annee=2024, db=mock_db)
        
        # Doit avoir mis a jour les budgets
        assert CategorieDepense.ALIMENTATION.value in existing_budget.budgets_par_categorie
        mock_db.commit.assert_called_once()
    
    def test_definir_budgets_batch_default_date(self):
        """Test avec date par defaut (mois/annee courants)."""
        service = BudgetService()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        budgets = {CategorieDepense.SANTE: 300.0}
        
        # Pas de mois/annee specifies
        service.definir_budgets_batch(budgets, db=mock_db)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestGetResumeMensuel:
    """Tests pour get_resume_mensuel()."""
    
    def test_get_resume_mensuel_sans_depenses(self):
        """Test resume quand pas de depenses."""
        service = BudgetService()
        mock_db = MagicMock()
        
        # Mock get_depenses_mois pour retourner liste vide
        with patch.object(service, 'get_depenses_mois', return_value=[]):
            with patch.object(service, 'get_tous_budgets', return_value={}):
                resume = service.get_resume_mensuel(mois=1, annee=2024, db=mock_db)
        
        assert resume.total_depenses == 0
        assert resume.total_budget == 0
    
    def test_get_resume_mensuel_avec_depenses(self):
        """Test resume avec depenses."""
        service = BudgetService()
        mock_db = MagicMock()
        
        depenses = [
            Depense(
                montant=100.0,
                description="Test",
                categorie=CategorieDepense.ALIMENTATION,
                date_depense=date(2024, 1, 15),
            ),
            Depense(
                montant=50.0,
                description="Test2",
                categorie=CategorieDepense.ALIMENTATION,
                date_depense=date(2024, 1, 16),
            ),
        ]
        
        budgets = {CategorieDepense.ALIMENTATION: 200.0}
        
        with patch.object(service, 'get_depenses_mois', return_value=depenses):
            with patch.object(service, 'get_tous_budgets', return_value=budgets):
                resume = service.get_resume_mensuel(mois=1, annee=2024, db=mock_db)
        
        assert resume.total_depenses == 150.0
    
    def test_get_resume_mensuel_budget_depasse(self):
        """Test resume avec budget depasse."""
        service = BudgetService()
        mock_db = MagicMock()
        
        depenses = [
            Depense(
                montant=300.0,
                description="Gros achat",
                categorie=CategorieDepense.ALIMENTATION,
                date_depense=date(2024, 1, 15),
            ),
        ]
        
        budgets = {CategorieDepense.ALIMENTATION: 200.0}
        
        with patch.object(service, 'get_depenses_mois', return_value=depenses):
            with patch.object(service, 'get_tous_budgets', return_value=budgets):
                resume = service.get_resume_mensuel(mois=1, annee=2024, db=mock_db)
        
        # La categorie alimentation est depassee
        assert CategorieDepense.ALIMENTATION.value in resume.categories_depassees
    
    def test_get_resume_mensuel_budget_a_risque(self):
        """Test resume avec budget a risque (>80%)."""
        service = BudgetService()
        mock_db = MagicMock()
        
        depenses = [
            Depense(
                montant=170.0,  # 85% de 200
                description="Achat",
                categorie=CategorieDepense.ALIMENTATION,
                date_depense=date(2024, 1, 15),
            ),
        ]
        
        budgets = {CategorieDepense.ALIMENTATION: 200.0}
        
        with patch.object(service, 'get_depenses_mois', return_value=depenses):
            with patch.object(service, 'get_tous_budgets', return_value=budgets):
                resume = service.get_resume_mensuel(mois=1, annee=2024, db=mock_db)
        
        assert CategorieDepense.ALIMENTATION.value in resume.categories_a_risque


class TestGetTendances:
    """Tests pour get_tendances()."""
    
    def test_get_tendances_basic(self):
        """Test tendances basique."""
        service = BudgetService()
        mock_db = MagicMock()
        
        with patch.object(service, 'get_depenses_mois', return_value=[]):
            tendances = service.get_tendances(nb_mois=3, db=mock_db)
        
        # get_tendances retourne "mois" et les categories
        assert "mois" in tendances
        assert "total" in tendances
    
    def test_get_tendances_avec_depenses(self):
        """Test tendances avec depenses variees."""
        service = BudgetService()
        mock_db = MagicMock()
        
        def mock_depenses(mois, annee, db=None):
            return [
                Depense(
                    montant=100.0 + mois * 10,
                    description="Test",
                    categorie=CategorieDepense.ALIMENTATION,
                    date_depense=date(annee, mois, 15),
                )
            ]
        
        with patch.object(service, 'get_depenses_mois', side_effect=mock_depenses):
            tendances = service.get_tendances(nb_mois=6, db=mock_db)
        
        assert len(tendances["mois"]) == 6
        assert len(tendances["total"]) == 6


class TestPrevoirDepenses:
    """Tests pour prevoir_depenses()."""
    
    def test_prevoir_depenses_sans_historique(self):
        """Test previsions sans historique."""
        service = BudgetService()
        
        with patch('src.services.budget.obtenir_contexte_db') as mock_ctx:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.all.return_value = []
            mock_ctx.return_value.__enter__.return_value = mock_db
            
            previsions = service.prevoir_depenses(mois_cible=3, annee_cible=2024)
        
        assert isinstance(previsions, list)
    
    def test_prevoir_depenses_avec_historique(self):
        """Test previsions avec historique."""
        service = BudgetService()
        
        with patch('src.services.budget.obtenir_contexte_db') as mock_ctx:
            mock_db = MagicMock()
            mock_dep = MagicMock()
            mock_dep.categorie = "alimentation"
            mock_dep.montant = 100.0
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_dep]
            mock_ctx.return_value.__enter__.return_value = mock_db
            
            previsions = service.prevoir_depenses(mois_cible=3, annee_cible=2024)
        
        assert isinstance(previsions, list)


class TestVerifierAlertesBudget:
    """Tests pour _verifier_alertes_budget()."""
    
    def test_verifier_alertes_depasse(self):
        """Test alertes quand budget depasse."""
        service = BudgetService()
        mock_db = MagicMock()
        
        with patch.object(service, 'get_resume_mensuel') as mock_resume:
            mock_resume.return_value = MagicMock(
                categories_depassees=["alimentation"],
                categories_a_risque=[],
            )
            # Appeler la methode
            service._verifier_alertes_budget(mois=1, annee=2024, db=mock_db)
    
    def test_verifier_alertes_a_risque(self):
        """Test alertes quand budget a risque."""
        service = BudgetService()
        mock_db = MagicMock()
        
        with patch.object(service, 'get_resume_mensuel') as mock_resume:
            mock_resume.return_value = MagicMock(
                categories_depassees=[],
                categories_a_risque=["transport"],
            )
            service._verifier_alertes_budget(mois=1, annee=2024, db=mock_db)


class TestAjouterFactureMaison:
    """Tests pour ajouter_facture_maison()."""
    
    def test_ajouter_facture_nouvelle(self):
        """Test ajouter une nouvelle facture."""
        service = BudgetService()
        mock_db = MagicMock()
        
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=120.0,
            mois=1,
            annee=2024,
            consommation=450.0,
            unite_consommation="kWh",
            fournisseur="EDF",
        )
        
        result = service.ajouter_facture_maison(facture, db=mock_db)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_ajouter_facture_gaz(self):
        """Test ajouter facture gaz."""
        service = BudgetService()
        mock_db = MagicMock()
        
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=80.0,
            mois=1,
            annee=2024,
            consommation=150.0,
            unite_consommation="m3",
            fournisseur="Engie",
        )
        
        result = service.ajouter_facture_maison(facture, db=mock_db)
        
        mock_db.add.assert_called_once()


class TestGetFacturesMaison:
    """Tests pour get_factures_maison()."""
    
    def test_get_factures_maison_vide(self):
        """Test get factures sans donnees."""
        service = BudgetService()
        mock_db = MagicMock()
        
        # Pas de resultats
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        
        factures = service.get_factures_maison(db=mock_db)
        
        assert factures == []
    
    def test_get_factures_maison_avec_categorie(self):
        """Test get factures avec filtre categorie."""
        service = BudgetService()
        mock_db = MagicMock()
        
        mock_facture = MagicMock()
        mock_facture.id = 1
        mock_facture.categorie = "electricite"
        mock_facture.montant = 120.0
        mock_facture.mois = 1
        mock_facture.annee = 2024
        mock_facture.date_facture = date(2024, 1, 15)
        mock_facture.fournisseur = "EDF"
        mock_facture.consommation = 450.0
        mock_facture.numero_facture = ""
        mock_facture.note = ""
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_facture]
        
        factures = service.get_factures_maison(categorie=CategorieDepense.ELECTRICITE, db=mock_db)
        
        assert len(factures) == 1


class TestGetEvolutionConsommation:
    """Tests pour get_evolution_consommation()."""
    
    def test_get_evolution_vide(self):
        """Test evolution sans donnees."""
        service = BudgetService()
        
        with patch.object(service, 'get_factures_maison', return_value=[]):
            evolution = service.get_evolution_consommation(categorie=CategorieDepense.ELECTRICITE)
        
        # evolution est une liste
        assert isinstance(evolution, list)
    
    def test_get_evolution_avec_donnees(self):
        """Test evolution avec donnees."""
        service = BudgetService()
        
        mock_facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=120.0,
            mois=1,
            annee=2024,
            consommation=450.0,
            unite_consommation="kWh",
        )
        
        with patch.object(service, 'get_factures_maison', return_value=[mock_facture]):
            evolution = service.get_evolution_consommation(categorie=CategorieDepense.ELECTRICITE)
        
        assert len(evolution) == 1
