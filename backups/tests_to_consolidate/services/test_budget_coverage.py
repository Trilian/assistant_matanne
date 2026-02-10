"""
Tests supplémentaires pour améliorer la couverture de budget.py

Couvre les edge cases des propriétés Pydantic et les constantes.
"""

import pytest
from datetime import date

from src.services.budget import (
    CategorieDepense,
    FrequenceRecurrence,
    Depense,
    FactureMaison,
    BudgetMensuel,
    ResumeFinancier,
    PrevisionDepense,
    BudgetService,
    get_budget_service,
    DEFAULT_USER_ID,
)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes du module."""
    
    def test_default_user_id(self):
        assert DEFAULT_USER_ID == "matanne"
    
    def test_budgets_defaut_exists(self):
        assert hasattr(BudgetService, 'BUDGETS_DEFAUT')
        assert isinstance(BudgetService.BUDGETS_DEFAUT, dict)
    
    def test_budgets_defaut_alimentation(self):
        assert BudgetService.BUDGETS_DEFAUT[CategorieDepense.ALIMENTATION] == 600
    
    def test_budgets_defaut_courses(self):
        assert BudgetService.BUDGETS_DEFAUT[CategorieDepense.COURSES] == 200
    
    def test_budgets_defaut_sante(self):
        assert BudgetService.BUDGETS_DEFAUT[CategorieDepense.SANTE] == 100


# ═══════════════════════════════════════════════════════════
# CATÉGORIES ENUM COMPLÈTEMENT TESTÉES
# ═══════════════════════════════════════════════════════════


class TestCategorieDepenseComplete:
    """Tests complets pour toutes les catégories."""
    
    def test_maison(self):
        assert CategorieDepense.MAISON.value == "maison"
    
    def test_vetements(self):
        assert CategorieDepense.VETEMENTS.value == "vêtements"
    
    def test_enfant(self):
        assert CategorieDepense.ENFANT.value == "enfant"
    
    def test_education(self):
        assert CategorieDepense.EDUCATION.value == "éducation"
    
    def test_services(self):
        assert CategorieDepense.SERVICES.value == "services"
    
    def test_impots(self):
        assert CategorieDepense.IMPOTS.value == "impôts"
    
    def test_epargne(self):
        assert CategorieDepense.EPARGNE.value == "épargne"
    
    def test_gaz(self):
        assert CategorieDepense.GAZ.value == "gaz"
    
    def test_electricite(self):
        assert CategorieDepense.ELECTRICITE.value == "electricite"
    
    def test_eau(self):
        assert CategorieDepense.EAU.value == "eau"
    
    def test_internet(self):
        assert CategorieDepense.INTERNET.value == "internet"
    
    def test_loyer(self):
        assert CategorieDepense.LOYER.value == "loyer"
    
    def test_assurance(self):
        assert CategorieDepense.ASSURANCE.value == "assurance"
    
    def test_taxe_fonciere(self):
        assert CategorieDepense.TAXE_FONCIERE.value == "taxe_fonciere"
    
    def test_creche(self):
        assert CategorieDepense.CRECHE.value == "creche"
    
    def test_autre(self):
        assert CategorieDepense.AUTRE.value == "autre"


class TestFrequenceRecurrenceComplete:
    """Tests complets pour les fréquences."""
    
    def test_trimestriel(self):
        assert FrequenceRecurrence.TRIMESTRIEL.value == "trimestriel"


# ═══════════════════════════════════════════════════════════
# FACTURE MAISON - EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestFactureMaisonEdgeCases:
    """Tests edge cases pour FactureMaison."""
    
    def test_prix_unitaire_consommation_zero(self):
        """Consommation à 0 devrait retourner None."""
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=100.0,
            mois=1,
            annee=2026,
            consommation=0.0,
        )
        assert facture.prix_unitaire is None
    
    def test_prix_unitaire_consommation_negative(self):
        """Consommation négative devrait retourner None."""
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=50.0,
            mois=3,
            annee=2026,
            consommation=-10.0,
        )
        assert facture.prix_unitaire is None
    
    def test_periode_tous_mois(self):
        """Test de tous les mois formatés."""
        mois_attendus = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        for i, nom in enumerate(mois_attendus, 1):
            facture = FactureMaison(
                categorie=CategorieDepense.EAU,
                montant=40.0,
                mois=i,
                annee=2025,
            )
            assert nom in facture.periode
            assert "2025" in facture.periode
    
    def test_facture_avec_tous_champs(self):
        """Facture complète avec tous les champs."""
        facture = FactureMaison(
            id=1,
            categorie=CategorieDepense.ELECTRICITE,
            montant=150.0,
            consommation=250.0,
            unite_consommation="kWh",
            mois=6,
            annee=2026,
            date_facture=date(2026, 6, 15),
            fournisseur="EDF",
            numero_facture="EDF-2026-001",
            note="Facture été",
        )
        assert facture.fournisseur == "EDF"
        assert facture.numero_facture == "EDF-2026-001"
        assert facture.note == "Facture été"
        assert facture.date_facture == date(2026, 6, 15)


# ═══════════════════════════════════════════════════════════
# BUDGET MENSUEL - EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestBudgetMensuelEdgeCases:
    """Tests edge cases pour BudgetMensuel."""
    
    def test_pourcentage_utilise_negatif_prevu(self):
        """Budget prévu négatif retourne 0%."""
        budget = BudgetMensuel(
            mois=1,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=-100.0,
            depense_reelle=50.0,
        )
        assert budget.pourcentage_utilise == 0.0
    
    def test_pourcentage_utilise_max_capped(self):
        """Pourcentage plafonné à 999%."""
        budget = BudgetMensuel(
            mois=1,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=10.0,
            depense_reelle=10000.0,  # 100000%
        )
        assert budget.pourcentage_utilise == 999
    
    def test_reste_disponible_deficitaire(self):
        """Reste disponible avec dépassement."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.TRANSPORT,
            budget_prevu=100.0,
            depense_reelle=500.0,
        )
        assert budget.reste_disponible == 0
    
    def test_est_depasse_egal(self):
        """Budget égal n'est pas dépassé."""
        budget = BudgetMensuel(
            mois=3,
            annee=2026,
            categorie=CategorieDepense.SANTE,
            budget_prevu=200.0,
            depense_reelle=200.0,
        )
        assert budget.est_depasse is False


# ═══════════════════════════════════════════════════════════
# DEPENSE - CHAMPS SUPPLEMENTAIRES
# ═══════════════════════════════════════════════════════════


class TestDepenseComplete:
    """Tests complets pour Depense."""
    
    def test_depense_avec_payeur(self):
        depense = Depense(
            montant=75.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Courses",
            payeur="Maman",
        )
        assert depense.payeur == "Maman"
    
    def test_depense_avec_moyen_paiement(self):
        depense = Depense(
            montant=150.0,
            categorie=CategorieDepense.VETEMENTS,
            description="Vêtements enfant",
            moyen_paiement="CB",
        )
        assert depense.moyen_paiement == "CB"
    
    def test_depense_remboursable(self):
        depense = Depense(
            montant=50.0,
            categorie=CategorieDepense.SANTE,
            description="Médecin",
            remboursable=True,
            rembourse=False,
        )
        assert depense.remboursable is True
        assert depense.rembourse is False
    
    def test_depense_rembourse(self):
        depense = Depense(
            montant=50.0,
            categorie=CategorieDepense.SANTE,
            description="Médecin",
            remboursable=True,
            rembourse=True,
        )
        assert depense.rembourse is True
    
    def test_depense_avec_magasin(self):
        depense = Depense(
            montant=120.0,
            categorie=CategorieDepense.COURSES,
            description="Courses hebdo",
            magasin="Carrefour",
        )
        assert depense.magasin == "Carrefour"
    
    def test_depense_cree_le_defaut(self):
        depense = Depense(
            montant=10.0,
            categorie=CategorieDepense.AUTRE,
            description="Test",
        )
        assert depense.cree_le is not None


# ═══════════════════════════════════════════════════════════
# RESUME FINANCIER - EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestResumeFinancierComplete:
    """Tests complets pour ResumeFinancier."""
    
    def test_resume_avec_epargne(self):
        resume = ResumeFinancier(
            mois=4,
            annee=2026,
            total_epargne=500.0,
        )
        assert resume.total_epargne == 500.0
    
    def test_resume_avec_variation(self):
        resume = ResumeFinancier(
            mois=5,
            annee=2026,
            variation_vs_mois_precedent=-15.5,
        )
        assert resume.variation_vs_mois_precedent == -15.5
    
    def test_resume_avec_moyenne(self):
        resume = ResumeFinancier(
            mois=6,
            annee=2026,
            moyenne_6_mois=2500.0,
        )
        assert resume.moyenne_6_mois == 2500.0
    
    def test_resume_avec_alertes(self):
        resume = ResumeFinancier(
            mois=7,
            annee=2026,
            categories_depassees=["alimentation", "loisirs"],
            categories_a_risque=["transport"],
        )
        assert len(resume.categories_depassees) == 2
        assert "loisirs" in resume.categories_depassees
        assert len(resume.categories_a_risque) == 1


# ═══════════════════════════════════════════════════════════
# PREVISION DEPENSE - EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestPrevisionDepenseComplete:
    """Tests complets pour PrevisionDepense."""
    
    def test_prevision_confiance_minimum(self):
        prev = PrevisionDepense(
            categorie=CategorieDepense.LOISIRS,
            montant_prevu=100.0,
            confiance=0.0,
        )
        assert prev.confiance == 0.0
    
    def test_prevision_confiance_maximum(self):
        prev = PrevisionDepense(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=600.0,
            confiance=1.0,
        )
        assert prev.confiance == 1.0
    
    def test_prevision_toutes_categories(self):
        """Test qu'on peut créer une prévision pour chaque catégorie."""
        for cat in CategorieDepense:
            prev = PrevisionDepense(
                categorie=cat,
                montant_prevu=100.0,
            )
            assert prev.categorie == cat


# ═══════════════════════════════════════════════════════════
# FACTORY TESTS
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests pour la factory function."""
    
    def test_get_budget_service_singleton(self):
        """Factory retourne un singleton."""
        import src.services.budget as budget_module
        
        # Reset singleton
        budget_module._budget_service = None
        
        service1 = get_budget_service()
        service2 = get_budget_service()
        
        assert service1 is service2
    
    def test_get_budget_service_type(self):
        service = get_budget_service()
        assert isinstance(service, BudgetService)


# ═══════════════════════════════════════════════════════════
# SERVICE INITIALIZATION
# ═══════════════════════════════════════════════════════════


class TestBudgetServiceInit:
    """Tests pour l'initialisation du service."""
    
    def test_init_cache_empty(self):
        service = BudgetService()
        assert hasattr(service, '_depenses_cache')
        assert isinstance(service._depenses_cache, dict)
    
    def test_service_has_all_methods(self):
        """Vérifie que le service a toutes les méthodes attendues."""
        service = BudgetService()
        
        methods = [
            'ajouter_depense',
            'modifier_depense',
            'supprimer_depense',
            'get_depenses_mois',
            'definir_budget',
            'get_budget',
            'get_tous_budgets',
            'get_resume_mensuel',
            'get_tendances',
            'prevoir_depenses',
        ]
        
        for method in methods:
            assert hasattr(service, method), f"Méthode {method} manquante"
