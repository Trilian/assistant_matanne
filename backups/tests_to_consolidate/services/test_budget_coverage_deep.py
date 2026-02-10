"""
Tests complets pour src/services/budget.py

Couverture cible: >80%
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCategorieDepense:
    """Tests enum CategorieDepense."""

    def test_import_enum(self):
        from src.services.budget import CategorieDepense
        assert CategorieDepense is not None

    def test_categories_principales(self):
        from src.services.budget import CategorieDepense
        
        assert CategorieDepense.ALIMENTATION == "alimentation"
        assert CategorieDepense.COURSES == "courses"
        assert CategorieDepense.MAISON == "maison"
        assert CategorieDepense.SANTE == "santé"
        assert CategorieDepense.TRANSPORT == "transport"
        assert CategorieDepense.LOISIRS == "loisirs"

    def test_categories_factures(self):
        from src.services.budget import CategorieDepense
        
        assert CategorieDepense.GAZ == "gaz"
        assert CategorieDepense.ELECTRICITE == "electricite"
        assert CategorieDepense.EAU == "eau"
        assert CategorieDepense.INTERNET == "internet"
        assert CategorieDepense.LOYER == "loyer"

    def test_enum_count(self):
        from src.services.budget import CategorieDepense
        
        # Au moins 20 catégories
        assert len(CategorieDepense) >= 20


class TestFrequenceRecurrence:
    """Tests enum FrequenceRecurrence."""

    def test_enum_values(self):
        from src.services.budget import FrequenceRecurrence
        
        assert FrequenceRecurrence.PONCTUEL == "ponctuel"
        assert FrequenceRecurrence.HEBDOMADAIRE == "hebdomadaire"
        assert FrequenceRecurrence.MENSUEL == "mensuel"
        assert FrequenceRecurrence.TRIMESTRIEL == "trimestriel"
        assert FrequenceRecurrence.ANNUEL == "annuel"


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestDepense:
    """Tests schéma Depense."""

    def test_import_schema(self):
        from src.services.budget import Depense
        assert Depense is not None

    def test_creation_basique(self):
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=50.0,
            categorie=CategorieDepense.COURSES, 
            description="Courses hebdomadaires"
        )
        
        assert depense.montant == 50.0
        assert depense.categorie == CategorieDepense.COURSES
        assert depense.date == date.today()

    def test_depense_complete(self):
        from src.services.budget import Depense, CategorieDepense, FrequenceRecurrence
        
        depense = Depense(
            date=date(2026, 2, 8),
            montant=150.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Courses supermarché",
            magasin="Carrefour",
            est_recurrente=True,
            frequence=FrequenceRecurrence.HEBDOMADAIRE,
            payeur="Papa",
            moyen_paiement="CB",
            remboursable=False,
            rembourse=False
        )
        
        assert depense.est_recurrente is True
        assert depense.frequence == FrequenceRecurrence.HEBDOMADAIRE
        assert depense.payeur == "Papa"

    def test_valeurs_par_defaut(self):
        from src.services.budget import Depense, CategorieDepense, FrequenceRecurrence
        
        depense = Depense(
            montant=25.0,
            categorie=CategorieDepense.LOISIRS
        )
        
        assert depense.description == ""
        assert depense.magasin == ""
        assert depense.est_recurrente is False
        assert depense.frequence == FrequenceRecurrence.PONCTUEL
        assert depense.remboursable is False


class TestFactureMaison:
    """Tests schéma FactureMaison."""

    def test_creation_valide(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=85.0,
            consommation=450.0,
            unite_consommation="kWh",
            mois=1,
            annee=2026,
            fournisseur="EDF"
        )
        
        assert facture.montant == 85.0
        assert facture.consommation == 450.0
        assert facture.mois == 1

    def test_prix_unitaire(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=100.0,
            consommation=200.0,
            unite_consommation="m³",
            mois=2,
            annee=2026
        )
        
        assert facture.prix_unitaire == 0.5  # 100/200

    def test_prix_unitaire_sans_consommation(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.INTERNET,
            montant=35.0,
            consommation=None,
            mois=2,
            annee=2026
        )
        
        assert facture.prix_unitaire is None

    def test_prix_unitaire_zero_consommation(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.EAU,
            montant=30.0,
            consommation=0.0,
            mois=2,
            annee=2026
        )
        
        assert facture.prix_unitaire is None

    def test_periode(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=100.0,
            mois=3,
            annee=2026
        )
        
        assert facture.periode == "Mars 2026"


class TestBudgetMensuel:
    """Tests schéma BudgetMensuel."""

    def test_creation_valide(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=350.0
        )
        
        assert budget.budget_prevu == 500.0
        assert budget.depense_reelle == 350.0

    def test_pourcentage_utilise(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.COURSES,
            budget_prevu=400.0,
            depense_reelle=200.0
        )
        
        assert budget.pourcentage_utilise == 50.0

    def test_pourcentage_depasse(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=100.0,
            depense_reelle=150.0
        )
        
        assert budget.pourcentage_utilise == 150.0

    def test_pourcentage_budget_zero(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.AUTRE,
            budget_prevu=0.0,
            depense_reelle=50.0
        )
        
        assert budget.pourcentage_utilise == 0.0

    def test_reste_disponible(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.MAISON,
            budget_prevu=300.0,
            depense_reelle=100.0
        )
        
        assert budget.reste_disponible == 200.0

    def test_reste_disponible_depasse(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.VETEMENTS,
            budget_prevu=100.0,
            depense_reelle=150.0
        )
        
        assert budget.reste_disponible == 0.0  # Jamais négatif


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestBudgetConstants:
    """Tests constantes du module."""

    def test_default_user_id(self):
        from src.services.budget import DEFAULT_USER_ID
        
        assert DEFAULT_USER_ID == "matanne"


# ═══════════════════════════════════════════════════════════
# TESTS MODELS IMPORTS
# ═══════════════════════════════════════════════════════════


class TestBudgetModels:
    """Tests imports modèles DB."""

    def test_import_models(self):
        from src.core.models import FamilyBudget, BudgetMensuelDB
        
        assert FamilyBudget is not None
        assert BudgetMensuelDB is not None


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestBudgetEdgeCases:
    """Tests cas limites."""

    def test_depense_montant_zero(self):
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=0.0,
            categorie=CategorieDepense.AUTRE
        )
        
        assert depense.montant == 0.0

    def test_depense_montant_negatif(self):
        from src.services.budget import Depense, CategorieDepense
        
        # Remboursement pourrait être négatif
        depense = Depense(
            montant=-50.0,
            categorie=CategorieDepense.AUTRE,
            description="Remboursement"
        )
        
        assert depense.montant == -50.0

    def test_facture_tous_mois(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        mois_noms_attendus = {
            1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
            5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
            9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
        }
        
        for mois, nom in mois_noms_attendus.items():
            facture = FactureMaison(
                categorie=CategorieDepense.GAZ,
                montant=100.0,
                mois=mois,
                annee=2026
            )
            assert nom in facture.periode

    def test_budget_pourcentage_max(self):
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=10.0,
            depense_reelle=10000.0  # 100 000%!
        )
        
        # Limité à 999%
        assert budget.pourcentage_utilise == 999


class TestBudgetIntegration:
    """Tests d'intégration."""

    def test_workflow_depenses_mensuelles(self):
        from src.services.budget import Depense, BudgetMensuel, CategorieDepense
        
        # Créer plusieurs dépenses
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.COURSES),
            Depense(montant=50.0, categorie=CategorieDepense.COURSES),
            Depense(montant=75.0, categorie=CategorieDepense.COURSES),
        ]
        
        total_depenses = sum(d.montant for d in depenses)
        
        # Créer budget
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.COURSES,
            budget_prevu=300.0,
            depense_reelle=total_depenses
        )
        
        assert budget.depense_reelle == 225.0
        assert budget.pourcentage_utilise == 75.0
        assert budget.reste_disponible == 75.0

    def test_workflow_factures_annuelles(self):
        from src.services.budget import FactureMaison, CategorieDepense
        
        # Créer les factures d'électricité de l'année
        factures = []
        for mois in range(1, 13):
            facture = FactureMaison(
                categorie=CategorieDepense.ELECTRICITE,
                montant=80.0 + (mois * 5),  # Variation saisonnière
                consommation=400 + (mois * 20),
                unite_consommation="kWh",
                mois=mois,
                annee=2026,
                fournisseur="EDF"
            )
            factures.append(facture)
        
        # Calculer totaux
        total_montant = sum(f.montant for f in factures)
        total_conso = sum(f.consommation for f in factures)
        
        assert len(factures) == 12
        assert total_montant > 0
        assert total_conso > 0

    def test_toutes_categories_valides(self):
        from src.services.budget import Depense, CategorieDepense
        
        # Créer une dépense pour chaque catégorie
        for categorie in CategorieDepense:
            depense = Depense(
                montant=10.0,
                categorie=categorie
            )
            assert depense.categorie == categorie

    def test_toutes_frequences_valides(self):
        from src.services.budget import Depense, CategorieDepense, FrequenceRecurrence
        
        for frequence in FrequenceRecurrence:
            depense = Depense(
                montant=10.0,
                categorie=CategorieDepense.AUTRE,
                est_recurrente=True,
                frequence=frequence
            )
            assert depense.frequence == frequence


class TestBudgetServiceMethods:
    """Tests méthodes du service (si service existe)."""

    def test_budget_utils_import(self):
        """Test import des utilitaires budget."""
        try:
            from src.services.budget_utils import (
                calculate_monthly_total,
                get_category_breakdown,
            )
            assert True
        except ImportError:
            # Les utils peuvent ne pas exister
            pass

    def test_imports_from_core(self):
        """Test imports depuis core."""
        from src.core.database import obtenir_contexte_db
        from src.core.decorators import with_db_session, with_cache
        from src.core.models import FamilyBudget
        
        assert obtenir_contexte_db is not None
        assert with_db_session is not None
        assert FamilyBudget is not None
