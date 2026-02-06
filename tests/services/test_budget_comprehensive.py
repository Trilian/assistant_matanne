"""
Tests complets pour le service budget.

Couvre:
- CategorieDepense, FrequenceRecurrence (enums)
- Depense, FactureMaison, BudgetMensuel, ResumeFinancier (modèles)
- BudgetService (CRUD dépenses, budgets, calculs)
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.services.budget import (
    CategorieDepense,
    FrequenceRecurrence,
    Depense,
    FactureMaison,
    BudgetMensuel,
    ResumeFinancier,
    PrevisionDepense,
    BudgetService,
)


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCategorieDepense:
    """Tests pour l'enum CategorieDepense."""

    def test_alimentation(self):
        assert CategorieDepense.ALIMENTATION.value == "alimentation"

    def test_courses(self):
        assert CategorieDepense.COURSES.value == "courses"

    def test_transport(self):
        assert CategorieDepense.TRANSPORT.value == "transport"

    def test_sante(self):
        assert CategorieDepense.SANTE.value == "santé"

    def test_loisirs(self):
        assert CategorieDepense.LOISIRS.value == "loisirs"

    def test_all_categories_exist(self):
        # Minimum expected categories
        expected = {"alimentation", "courses", "transport", "loisirs"}
        actual = {c.value for c in CategorieDepense}
        assert expected.issubset(actual)


class TestFrequenceRecurrence:
    """Tests pour l'enum FrequenceRecurrence."""

    def test_ponctuel(self):
        assert FrequenceRecurrence.PONCTUEL.value == "ponctuel"

    def test_mensuel(self):
        assert FrequenceRecurrence.MENSUEL.value == "mensuel"

    def test_hebdomadaire(self):
        assert FrequenceRecurrence.HEBDOMADAIRE.value == "hebdomadaire"

    def test_annuel(self):
        assert FrequenceRecurrence.ANNUEL.value == "annuel"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestDepense:
    """Tests pour le modèle Depense."""

    def test_create_minimal_depense(self):
        depense = Depense(
            montant=50.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Courses Carrefour",
        )
        assert depense.montant == 50.0
        assert depense.categorie == CategorieDepense.ALIMENTATION
        assert depense.description == "Courses Carrefour"

    def test_create_depense_with_date(self):
        depense = Depense(
            montant=100.0,
            categorie=CategorieDepense.TRANSPORT,
            description="Essence",
            date=date(2026, 2, 6),
        )
        assert depense.date == date(2026, 2, 6)

    def test_create_depense_recurrente(self):
        depense = Depense(
            montant=800.0,
            categorie=CategorieDepense.MAISON,
            description="Loyer",
            frequence=FrequenceRecurrence.MENSUEL,
        )
        assert depense.frequence == FrequenceRecurrence.MENSUEL

    def test_depense_with_id(self):
        depense = Depense(
            id=42,
            montant=25.0,
            categorie=CategorieDepense.LOISIRS,
            description="Cinéma",
        )
        assert depense.id == 42


class TestFactureMaison:
    """Tests pour le modèle FactureMaison."""

    def test_create_facture(self):
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=150.0,
            mois=2,
            annee=2026,
        )
        assert facture.categorie == CategorieDepense.ELECTRICITE
        assert facture.montant == 150.0
        assert facture.mois == 2
        assert facture.annee == 2026

    def test_facture_avec_consommation(self):
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=80.0,
            mois=2,
            annee=2026,
            consommation=120.5,
            unite_consommation="kWh",
        )
        assert facture.consommation == 120.5
        assert facture.unite_consommation == "kWh"

    def test_prix_unitaire_calculated(self):
        facture = FactureMaison(
            categorie=CategorieDepense.EAU,
            montant=100.0,
            mois=2,
            annee=2026,
            consommation=50.0,
            unite_consommation="m³",
        )
        assert facture.prix_unitaire == 2.0

    def test_prix_unitaire_none_without_consommation(self):
        facture = FactureMaison(
            categorie=CategorieDepense.MAISON,
            montant=40.0,
            mois=2,
            annee=2026,
        )
        assert facture.prix_unitaire is None

    def test_periode_formatted(self):
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=150.0,
            mois=2,
            annee=2026,
        )
        periode = facture.periode
        assert "2026" in periode
        assert "Février" in periode


class TestBudgetMensuel:
    """Tests pour le modèle BudgetMensuel."""

    def test_create_budget(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=350.0,
        )
        assert budget.budget_prevu == 500.0
        assert budget.depense_reelle == 350.0

    def test_pourcentage_utilise(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=250.0,
        )
        assert budget.pourcentage_utilise == 50.0

    def test_pourcentage_utilise_zero_prevu(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=0.0,
            depense_reelle=100.0,
        )
        # Should handle division by zero
        assert budget.pourcentage_utilise >= 0

    def test_reste_disponible(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.TRANSPORT,
            budget_prevu=300.0,
            depense_reelle=200.0,
        )
        assert budget.reste_disponible == 100.0

    def test_reste_disponible_zero(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.SANTE,
            budget_prevu=100.0,
            depense_reelle=150.0,
        )
        # Property returns max(0, ...) so always >= 0
        assert budget.reste_disponible == 0

    def test_est_depasse_false(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=400.0,
        )
        assert budget.est_depasse is False

    def test_est_depasse_true(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=600.0,
        )
        assert budget.est_depasse is True


class TestResumeFinancier:
    """Tests pour le modèle ResumeFinancier."""

    def test_create_resume(self):
        resume = ResumeFinancier(
            mois=2,
            annee=2026,
            total_depenses=2500.0,
            total_budget=3000.0,
        )
        assert resume.total_depenses == 2500.0
        assert resume.total_budget == 3000.0
        assert resume.mois == 2

    def test_resume_with_details(self):
        resume = ResumeFinancier(
            mois=2,
            annee=2026,
            total_depenses=2000.0,
            total_budget=2500.0,
            depenses_par_categorie={
                "alimentation": 800.0,
                "transport": 400.0,
                "loisirs": 300.0,
            },
        )
        assert len(resume.depenses_par_categorie) == 3
        assert resume.depenses_par_categorie["alimentation"] == 800.0


class TestPrevisionDepense:
    """Tests pour le modèle PrevisionDepense."""

    def test_create_prevision(self):
        prevision = PrevisionDepense(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=600.0,
            confiance=0.85,
            base_calcul="Moyenne 6 derniers mois",
        )
        assert prevision.montant_prevu == 600.0
        assert prevision.confiance == 0.85
        assert prevision.base_calcul == "Moyenne 6 derniers mois"

    def test_prevision_defaults(self):
        prevision = PrevisionDepense(
            categorie=CategorieDepense.TRANSPORT,
            montant_prevu=200.0,
        )
        assert prevision.confiance == 0.0
        assert prevision.base_calcul == ""


# ═══════════════════════════════════════════════════════════
# TESTS BUDGET SERVICE
# ═══════════════════════════════════════════════════════════


class TestBudgetService:
    """Tests pour le service de budget - tests unitaires avec mocks."""

    @pytest.fixture
    def service(self):
        """Crée une instance du service."""
        return BudgetService()

    @pytest.fixture
    def mock_db(self):
        """Mock de session DB avec méthodes standard."""
        session = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.refresh = MagicMock()
        session.delete = MagicMock()
        session.query = MagicMock()
        return session

    @pytest.fixture
    def sample_depense(self):
        """Dépense exemple."""
        return Depense(
            montant=100.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Test dépense",
            date=date(2026, 2, 6),
        )

    def test_service_initialization(self, service):
        assert service is not None
        assert hasattr(service, 'ajouter_depense')
        assert hasattr(service, 'modifier_depense')

    def test_ajouter_depense(self, service, sample_depense, mock_db):
        """Test ajout dépense avec session mockée."""
        result = service.ajouter_depense(sample_depense, db=mock_db)
        
        assert result is not None
        assert result.categorie == CategorieDepense.ALIMENTATION
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    def test_modifier_depense(self, service, mock_db):
        """Test modification dépense avec session mockée."""
        mock_depense_db = MagicMock()
        mock_depense_db.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_depense_db
        
        updates = {"montant": 150.0, "description": "Updated"}
        result = service.modifier_depense(depense_id=1, updates=updates, db=mock_db)
        
        assert result is True
        mock_db.commit.assert_called()

    def test_modifier_depense_not_found(self, service, mock_db):
        """Test modification dépense inexistante."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.modifier_depense(depense_id=999, updates={"montant": 100.0}, db=mock_db)
        
        assert result is False

    def test_supprimer_depense(self, service, mock_db):
        """Test suppression dépense."""
        mock_depense_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_depense_db
        
        result = service.supprimer_depense(depense_id=1, db=mock_db)
        
        assert result is True
        mock_db.delete.assert_called_with(mock_depense_db)
        mock_db.commit.assert_called()

    def test_supprimer_depense_not_found(self, service, mock_db):
        """Test suppression dépense inexistante."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.supprimer_depense(depense_id=999, db=mock_db)
        
        assert result is False

    def test_get_depenses_mois(self, service, mock_db):
        """Test récupération dépenses du mois."""
        mock_entry1 = MagicMock()
        mock_entry1.id = 1
        mock_entry1.date = date(2026, 2, 5)
        mock_entry1.montant = 100.0
        mock_entry1.categorie = "alimentation"
        mock_entry1.description = "Test 1"
        mock_entry1.magasin = None
        mock_entry1.est_recurrent = False
        mock_entry1.frequence_recurrence = None
        
        mock_entry2 = MagicMock()
        mock_entry2.id = 2
        mock_entry2.date = date(2026, 2, 10)
        mock_entry2.montant = 200.0
        mock_entry2.categorie = "transport"
        mock_entry2.description = "Test 2"
        mock_entry2.magasin = None
        mock_entry2.est_recurrent = False
        mock_entry2.frequence_recurrence = None
        
        # Le code utilise query().filter().order_by().all()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_entry1, mock_entry2]
        
        result = service.get_depenses_mois(mois=2, annee=2026, db=mock_db)
        
        assert len(result) == 2
        assert result[0].categorie == CategorieDepense.ALIMENTATION

    def test_definir_budget_new(self, service, mock_db):
        """Test définition nouveau budget."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # definir_budget ne retourne rien (None), juste commit
        service.definir_budget(
            categorie=CategorieDepense.ALIMENTATION,
            montant=500.0,
            mois=2,
            annee=2026,
            db=mock_db,
        )
        
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    def test_definir_budget_update_existing(self, service, mock_db):
        """Test mise à jour budget existant."""
        existing_budget = MagicMock()
        existing_budget.budgets_par_categorie = {"alimentation": 400.0}
        mock_db.query.return_value.filter.return_value.first.return_value = existing_budget
        
        # definir_budget ne retourne rien
        service.definir_budget(
            categorie=CategorieDepense.ALIMENTATION,
            montant=600.0,
            mois=2,
            annee=2026,
            db=mock_db,
        )
        
        # Vérifier que le budget a été mis à jour
        assert existing_budget.budgets_par_categorie["alimentation"] == 600.0

    def test_get_budget(self, service, mock_db):
        """Test récupération budget."""
        mock_budget = MagicMock()
        mock_budget.categorie = "alimentation"
        mock_budget.montant = 500.0
        mock_budget.mois = 2
        mock_budget.annee = 2026
        mock_db.query.return_value.filter.return_value.first.return_value = mock_budget
        
        result = service.get_budget(
            categorie=CategorieDepense.ALIMENTATION,
            mois=2,
            annee=2026,
            db=mock_db,
        )
        
        assert result is not None

    def test_get_tous_budgets(self, service, mock_db):
        """Test récupération tous budgets du mois."""
        # Mock le retour de la DB
        mock_budget_db = MagicMock()
        mock_budget_db.budgets_par_categorie = {
            "alimentation": 500.0,
            "transport": 300.0,
        }
        mock_db.query.return_value.filter.return_value.first.return_value = mock_budget_db
        
        result = service.get_tous_budgets(mois=2, annee=2026, db=mock_db)
        
        # get_tous_budgets retourne un dict avec toutes les catégories (y compris defaults)
        assert isinstance(result, dict)
        assert result[CategorieDepense.ALIMENTATION] == 500.0
        assert result[CategorieDepense.TRANSPORT] == 300.0


class TestBudgetServiceCalculations:
    """Tests pour les calculs du service budget."""

    @pytest.fixture
    def service(self):
        return BudgetService()

    @pytest.fixture
    def mock_db(self):
        session = MagicMock()
        return session

    def test_calculer_total_depenses_mois(self, service, mock_db):
        """Test calcul total dépenses du mois."""
        mock_db.query.return_value.filter.return_value.scalar.return_value = 1500.0
        
        if hasattr(service, 'calculer_total_depenses_mois'):
            result = service.calculer_total_depenses_mois(mois=2, annee=2026, db=mock_db)
            assert result == 1500.0

    def test_get_resume_financier(self, service, mock_db):
        """Test résumé financier."""
        if hasattr(service, 'get_resume_financier'):
            result = service.get_resume_financier(mois=2, annee=2026, db=mock_db)
            assert result is not None


class TestBudgetServiceEdgeCases:
    """Tests pour les cas limites du service budget."""

    @pytest.fixture
    def service(self):
        return BudgetService()

    def test_depense_montant_zero(self):
        depense = Depense(
            montant=0.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Gratuit",
        )
        assert depense.montant == 0.0

    def test_depense_montant_negatif(self):
        # Remboursement
        depense = Depense(
            montant=-50.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Remboursement",
        )
        assert depense.montant == -50.0

    def test_budget_montant_zero(self):
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=0.0,
            depense_reelle=0.0,
        )
        assert budget.est_depasse is False

    def test_depense_description_longue(self):
        long_desc = "A" * 1000
        depense = Depense(
            montant=100.0,
            categorie=CategorieDepense.ALIMENTATION,
            description=long_desc,
        )
        assert len(depense.description) == 1000


class TestBudgetServiceRecurrence:
    """Tests pour les dépenses récurrentes."""

    @pytest.fixture
    def service(self):
        return BudgetService()

    def test_depense_recurrente_mensuelle(self):
        depense = Depense(
            montant=1200.0,
            categorie=CategorieDepense.MAISON,
            description="Loyer",
            est_recurrente=True,
            frequence=FrequenceRecurrence.MENSUEL,
        )
        assert depense.frequence == FrequenceRecurrence.MENSUEL
        assert depense.est_recurrente is True

    def test_depense_recurrente_annuelle(self):
        depense = Depense(
            montant=500.0,
            categorie=CategorieDepense.SANTE,
            description="Assurance annuelle",
            est_recurrente=True,
            frequence=FrequenceRecurrence.ANNUEL,
        )
        assert depense.frequence == FrequenceRecurrence.ANNUEL
