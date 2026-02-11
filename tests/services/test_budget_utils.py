"""
Tests pour les fonctions utilitaires pures de budget.

Ces tests ne nécessitent pas de base de données.
"""

import pytest
from datetime import date
from unittest.mock import MagicMock

from src.services.budget import (
    # Types
    CategorieDepense,
    Depense,
    FrequenceRecurrence,
    # Conversion
    db_entry_to_depense,
    db_entries_to_depenses,
    # Calculs statistiques
    calculer_moyenne_ponderee,
    calculer_tendance,
    calculer_variance,
    calculer_confiance_prevision,
    generer_prevision_categorie,
    # Calculs de budget
    calculer_pourcentage_budget,
    calculer_reste_disponible,
    est_budget_depasse,
    est_budget_a_risque,
    # Agrégation
    agreger_depenses_par_categorie,
    calculer_total_depenses,
    filtrer_depenses_par_categorie,
    filtrer_depenses_par_periode,
    # Résumés
    construire_resume_financier,
    # Validation
    valider_montant,
    valider_mois,
    valider_annee,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION DB → PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestDbEntryToDepense:
    """Tests pour db_entry_to_depense."""
    
    def test_conversion_basique(self):
        entry = MagicMock()
        entry.id = 1
        entry.date = date(2026, 2, 8)
        entry.montant = 50.0
        entry.categorie = "alimentation"
        entry.description = "Courses"
        entry.magasin = "Carrefour"
        entry.est_recurrent = False
        entry.frequence_recurrence = None
        
        result = db_entry_to_depense(entry)
        
        assert result.id == 1
        assert result.montant == 50.0
        assert result.categorie == CategorieDepense.ALIMENTATION
        assert result.description == "Courses"
    
    def test_conversion_categorie_inconnue(self):
        entry = MagicMock()
        entry.id = 1
        entry.date = date(2026, 2, 8)
        entry.montant = 50.0
        entry.categorie = "categorie_inexistante"
        entry.description = ""
        entry.magasin = ""
        entry.est_recurrent = False
        entry.frequence_recurrence = None
        
        result = db_entry_to_depense(entry)
        
        assert result.categorie == CategorieDepense.AUTRE
    
    def test_conversion_recurrente(self):
        entry = MagicMock()
        entry.id = 1
        entry.date = date(2026, 2, 8)
        entry.montant = 800.0
        entry.categorie = "maison"
        entry.description = "Loyer"
        entry.magasin = ""
        entry.est_recurrent = True
        entry.frequence_recurrence = "mensuel"
        
        result = db_entry_to_depense(entry)
        
        assert result.est_recurrente is True
        assert result.frequence == FrequenceRecurrence.MENSUEL
    
    def test_conversion_montant_none(self):
        entry = MagicMock()
        entry.id = 1
        entry.date = date(2026, 2, 8)
        entry.montant = None
        entry.categorie = "loisirs"
        entry.description = ""
        entry.magasin = ""
        entry.est_recurrent = False
        entry.frequence_recurrence = None
        
        result = db_entry_to_depense(entry)
        
        assert result.montant == 0.0


class TestDbEntriesToDepenses:
    """Tests pour db_entries_to_depenses."""
    
    def test_liste_vide(self):
        result = db_entries_to_depenses([])
        assert result == []
    
    def test_conversion_liste(self):
        entries = []
        for i in range(3):
            entry = MagicMock()
            entry.id = i + 1
            entry.date = date(2026, 2, i + 1)
            entry.montant = 50.0 * (i + 1)
            entry.categorie = "alimentation"
            entry.description = f"Dépense {i}"
            entry.magasin = ""
            entry.est_recurrent = False
            entry.frequence_recurrence = None
            entries.append(entry)
        
        result = db_entries_to_depenses(entries)
        
        assert len(result) == 3
        assert result[0].montant == 50.0
        assert result[2].montant == 150.0


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculerMoyennePonderee:
    """Tests pour calculer_moyenne_ponderee."""
    
    def test_liste_vide(self):
        assert calculer_moyenne_ponderee([]) == 0.0
    
    def test_valeur_unique(self):
        result = calculer_moyenne_ponderee([100.0])
        assert result == 100.0
    
    def test_valeurs_egales(self):
        result = calculer_moyenne_ponderee([100.0, 100.0, 100.0])
        # Avec poids croissants, moyenne devrait être 100
        assert result == 100.0
    
    def test_valeurs_croissantes(self):
        # Valeurs: [100, 200, 300] avec poids [1.0, 1.2, 1.4]
        result = calculer_moyenne_ponderee([100.0, 200.0, 300.0])
        # (100*1.0 + 200*1.2 + 300*1.4) / (1.0 + 1.2 + 1.4) = 760/3.6 ≈ 211.11
        assert 210 < result < 212
    
    def test_poids_personnalises(self):
        result = calculer_moyenne_ponderee([100.0, 200.0], poids=[1.0, 1.0])
        assert result == 150.0
    
    def test_poids_zero(self):
        result = calculer_moyenne_ponderee([100.0], poids=[0.0])
        assert result == 0.0


class TestCalculerTendance:
    """Tests pour calculer_tendance."""
    
    def test_liste_vide(self):
        assert calculer_tendance([]) == 0.0
    
    def test_valeur_unique(self):
        assert calculer_tendance([100.0]) == 0.0
    
    def test_tendance_croissante(self):
        result = calculer_tendance([100.0, 150.0, 200.0])
        # (200 - 100) / 3 = 33.33
        assert 33 < result < 34
    
    def test_tendance_decroissante(self):
        result = calculer_tendance([200.0, 150.0, 100.0])
        # (100 - 200) / 3 = -33.33
        assert -34 < result < -33
    
    def test_tendance_stable(self):
        result = calculer_tendance([100.0, 100.0, 100.0])
        assert result == 0.0


class TestCalculerVariance:
    """Tests pour calculer_variance."""
    
    def test_liste_vide(self):
        assert calculer_variance([]) == 0.0
    
    def test_valeur_unique(self):
        assert calculer_variance([100.0]) == 0.0
    
    def test_valeurs_identiques(self):
        result = calculer_variance([100.0, 100.0, 100.0])
        assert result == 0.0
    
    def test_variance_positive(self):
        result = calculer_variance([0.0, 100.0])
        # Moyenne = 50, Variance = ((0-50)² + (100-50)²) / 2 = 2500
        assert result == 2500.0
    
    def test_avec_moyenne_precalculee(self):
        result = calculer_variance([0.0, 100.0], moyenne=50.0)
        assert result == 2500.0


class TestCalculerConfiancePrevision:
    """Tests pour calculer_confiance_prevision."""
    
    def test_peu_de_donnees(self):
        result = calculer_confiance_prevision([100.0, 100.0], 100.0)
        assert result == 0.5
    
    def test_valeurs_stables(self):
        result = calculer_confiance_prevision([100.0, 100.0, 100.0], 100.0)
        assert result > 0.9  # Haute confiance si stable
    
    def test_valeurs_variables(self):
        result = calculer_confiance_prevision([50.0, 150.0, 50.0, 150.0], 100.0)
        assert result < 0.8  # Moins de confiance si variable


class TestGenererPrevisionCategorie:
    """Tests pour generer_prevision_categorie."""
    
    def test_liste_vide(self):
        result = generer_prevision_categorie(CategorieDepense.ALIMENTATION, [])
        assert result is None
    
    def test_valeurs_zero(self):
        result = generer_prevision_categorie(CategorieDepense.ALIMENTATION, [0.0, 0.0, 0.0])
        assert result is None
    
    def test_prevision_valide(self):
        result = generer_prevision_categorie(
            CategorieDepense.ALIMENTATION,
            [500.0, 520.0, 530.0, 540.0]
        )
        
        assert result is not None
        assert result.categorie == CategorieDepense.ALIMENTATION
        assert result.montant_prevu > 0
        assert 0 <= result.confiance <= 1


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS DE BUDGET
# ═══════════════════════════════════════════════════════════


class TestCalculerPourcentageBudget:
    """Tests pour calculer_pourcentage_budget."""
    
    def test_pourcentage_zero(self):
        result = calculer_pourcentage_budget(0.0, 100.0)
        assert result == 0.0
    
    def test_pourcentage_50(self):
        result = calculer_pourcentage_budget(50.0, 100.0)
        assert result == 50.0
    
    def test_pourcentage_100(self):
        result = calculer_pourcentage_budget(100.0, 100.0)
        assert result == 100.0
    
    def test_pourcentage_depasse(self):
        result = calculer_pourcentage_budget(150.0, 100.0)
        assert result == 150.0
    
    def test_pourcentage_plafonne(self):
        result = calculer_pourcentage_budget(10000.0, 100.0)
        assert result == 999.0
    
    def test_budget_zero(self):
        result = calculer_pourcentage_budget(100.0, 0.0)
        assert result == 0.0
    
    def test_budget_negatif(self):
        result = calculer_pourcentage_budget(50.0, -100.0)
        assert result == 0.0


class TestCalculerResteDisponible:
    """Tests pour calculer_reste_disponible."""
    
    def test_reste_positif(self):
        result = calculer_reste_disponible(100.0, 30.0)
        assert result == 70.0
    
    def test_reste_zero(self):
        result = calculer_reste_disponible(100.0, 100.0)
        assert result == 0.0
    
    def test_reste_depasse(self):
        result = calculer_reste_disponible(100.0, 150.0)
        assert result == 0.0  # Pas de valeur négative


class TestEstBudgetDepasse:
    """Tests pour est_budget_depasse."""
    
    def test_pas_depasse(self):
        assert est_budget_depasse(50.0, 100.0) is False
    
    def test_exact(self):
        assert est_budget_depasse(100.0, 100.0) is False
    
    def test_depasse(self):
        assert est_budget_depasse(101.0, 100.0) is True


class TestEstBudgetARisque:
    """Tests pour est_budget_a_risque."""
    
    def test_sous_seuil(self):
        assert est_budget_a_risque(70.0, 100.0) is False
    
    def test_au_seuil(self):
        assert est_budget_a_risque(80.0, 100.0) is True
    
    def test_au_dessus_seuil(self):
        assert est_budget_a_risque(90.0, 100.0) is True
    
    def test_depasse(self):
        # Si dépassé, n'est plus "à risque" mais "dépassé"
        assert est_budget_a_risque(110.0, 100.0) is False
    
    def test_seuil_custom(self):
        assert est_budget_a_risque(70.0, 100.0, seuil=70.0) is True
    
    def test_budget_zero(self):
        assert est_budget_a_risque(50.0, 0.0) is False


# ═══════════════════════════════════════════════════════════
# TESTS AGRÉGATION
# ═══════════════════════════════════════════════════════════


class TestAgregerDepensesParCategorie:
    """Tests pour agreger_depenses_par_categorie."""
    
    def test_liste_vide(self):
        result = agreger_depenses_par_categorie([])
        assert result == {}
    
    def test_une_categorie(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description=""),
            Depense(montant=30.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        
        result = agreger_depenses_par_categorie(depenses)
        
        assert result[CategorieDepense.ALIMENTATION] == 80.0
    
    def test_plusieurs_categories(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description=""),
            Depense(montant=30.0, categorie=CategorieDepense.TRANSPORT, description=""),
            Depense(montant=20.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        
        result = agreger_depenses_par_categorie(depenses)
        
        assert result[CategorieDepense.ALIMENTATION] == 70.0
        assert result[CategorieDepense.TRANSPORT] == 30.0


class TestCalculerTotalDepenses:
    """Tests pour calculer_total_depenses."""
    
    def test_liste_vide(self):
        assert calculer_total_depenses([]) == 0.0
    
    def test_total(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description=""),
            Depense(montant=30.0, categorie=CategorieDepense.TRANSPORT, description=""),
        ]
        
        result = calculer_total_depenses(depenses)
        
        assert result == 80.0


class TestFiltrerDepensesParCategorie:
    """Tests pour filtrer_depenses_par_categorie."""
    
    def test_liste_vide(self):
        result = filtrer_depenses_par_categorie([], CategorieDepense.ALIMENTATION)
        assert result == []
    
    def test_filtre(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description=""),
            Depense(montant=30.0, categorie=CategorieDepense.TRANSPORT, description=""),
            Depense(montant=20.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        
        result = filtrer_depenses_par_categorie(depenses, CategorieDepense.ALIMENTATION)
        
        assert len(result) == 2
        assert all(d.categorie == CategorieDepense.ALIMENTATION for d in result)


class TestFiltrerDepensesParPeriode:
    """Tests pour filtrer_depenses_par_periode."""
    
    def test_liste_vide(self):
        result = filtrer_depenses_par_periode([], date(2026, 1, 1), date(2026, 12, 31))
        assert result == []
    
    def test_filtre_periode(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description="", date=date(2026, 2, 1)),
            Depense(montant=30.0, categorie=CategorieDepense.TRANSPORT, description="", date=date(2026, 2, 15)),
            Depense(montant=20.0, categorie=CategorieDepense.ALIMENTATION, description="", date=date(2026, 3, 1)),
        ]
        
        result = filtrer_depenses_par_periode(depenses, date(2026, 2, 1), date(2026, 2, 28))
        
        assert len(result) == 2
    
    def test_bornes_incluses(self):
        depenses = [
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION, description="", date=date(2026, 2, 1)),
            Depense(montant=30.0, categorie=CategorieDepense.TRANSPORT, description="", date=date(2026, 2, 28)),
        ]
        
        result = filtrer_depenses_par_periode(depenses, date(2026, 2, 1), date(2026, 2, 28))
        
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS RÉSUMÉ FINANCIER
# ═══════════════════════════════════════════════════════════


class TestConstruireResumeFinancier:
    """Tests pour construire_resume_financier."""
    
    def test_resume_vide(self):
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=[],
            budgets={},
        )
        
        assert result.mois == 2
        assert result.annee == 2026
        assert result.total_depenses == 0.0
        assert result.total_budget == 0.0
    
    def test_resume_avec_depenses(self):
        depenses = [
            Depense(montant=200.0, categorie=CategorieDepense.ALIMENTATION, description=""),
            Depense(montant=50.0, categorie=CategorieDepense.TRANSPORT, description=""),
        ]
        budgets = {
            CategorieDepense.ALIMENTATION: 500.0,
            CategorieDepense.TRANSPORT: 100.0,
        }
        
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets,
        )
        
        assert result.total_depenses == 250.0
        assert result.total_budget == 600.0
        assert result.depenses_par_categorie["alimentation"] == 200.0
    
    def test_resume_budget_depasse(self):
        depenses = [
            Depense(montant=600.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        budgets = {
            CategorieDepense.ALIMENTATION: 500.0,
        }
        
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets,
        )
        
        assert "alimentation" in result.categories_depassees
    
    def test_resume_budget_a_risque(self):
        depenses = [
            Depense(montant=450.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        budgets = {
            CategorieDepense.ALIMENTATION: 500.0,
        }
        
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets,
        )
        
        assert "alimentation" in result.categories_a_risque
    
    def test_resume_variation_mois_precedent(self):
        depenses = [
            Depense(montant=1000.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        depenses_prec = [
            Depense(montant=800.0, categorie=CategorieDepense.ALIMENTATION, description=""),
        ]
        
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets={},
            depenses_mois_precedent=depenses_prec,
        )
        
        # (1000 - 800) / 800 * 100 = 25%
        assert result.variation_vs_mois_precedent == 25.0


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderMontant:
    """Tests pour valider_montant."""
    
    def test_float(self):
        assert valider_montant(50.0) == 50.0
    
    def test_int(self):
        assert valider_montant(50) == 50.0
    
    def test_string_numerique(self):
        assert valider_montant("50.5") == 50.5
    
    def test_invalide(self):
        with pytest.raises(ValueError):
            valider_montant("invalid")


class TestValiderMois:
    """Tests pour valider_mois."""
    
    def test_mois_valides(self):
        for m in range(1, 13):
            assert valider_mois(m) == m
    
    def test_mois_zero(self):
        with pytest.raises(ValueError):
            valider_mois(0)
    
    def test_mois_13(self):
        with pytest.raises(ValueError):
            valider_mois(13)


class TestValiderAnnee:
    """Tests pour valider_annee."""
    
    def test_annee_valide(self):
        assert valider_annee(2026) == 2026
    
    def test_annee_trop_ancienne(self):
        with pytest.raises(ValueError):
            valider_annee(1800)
    
    def test_annee_future_lointaine(self):
        with pytest.raises(ValueError):
            valider_annee(2200)
