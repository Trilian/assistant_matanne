"""
Tests unitaires pour utils.py

Module: src.services.budget.utils
Tests des fonctions utilitaires pures pour le service budget.
"""

import pytest
from datetime import date
from unittest.mock import MagicMock

from src.services.budget.utils import (
    # Conversion
    db_entry_to_depense,
    db_entries_to_depenses,
    # Calculs statistiques
    calculer_moyenne_ponderee,
    calculer_tendance,
    calculer_variance,
    calculer_confiance_prevision,
    generer_prevision_categorie,
    # Calculs budget
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
from src.services.budget.schemas import (
    CategorieDepense,
    FrequenceRecurrence,
    Depense,
    BudgetMensuel,
    ResumeFinancier,
    PrevisionDepense,
)


# ═══════════════════════════════════════════════════════════
# CONVERSION DB → PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestDbEntryToDepense:
    """Tests pour db_entry_to_depense."""

    def test_conversion_simple(self):
        """Conversion basique d'une entrée DB."""
        entry = MagicMock()
        entry.id = 1
        entry.date = date(2026, 2, 10)
        entry.montant = 45.50
        entry.categorie = "alimentation"
        entry.description = "Test"
        entry.magasin = "Carrefour"
        entry.est_recurrent = False
        entry.frequence_recurrence = None

        result = db_entry_to_depense(entry)

        assert result.id == 1
        assert result.date == date(2026, 2, 10)
        assert result.montant == 45.50
        assert result.categorie == CategorieDepense.ALIMENTATION
        assert result.description == "Test"
        assert result.magasin == "Carrefour"
        assert result.est_recurrente is False

    def test_conversion_categorie_inconnue(self):
        """Catégorie inconnue devient AUTRE."""
        entry = MagicMock()
        entry.id = 2
        entry.date = date.today()
        entry.montant = 10.0
        entry.categorie = "categorie_inconnue"
        entry.description = ""
        entry.magasin = ""
        entry.est_recurrent = False
        entry.frequence_recurrence = None

        result = db_entry_to_depense(entry)

        assert result.categorie == CategorieDepense.AUTRE

    def test_conversion_montant_none(self):
        """Montant None devient 0.0."""
        entry = MagicMock()
        entry.id = 3
        entry.date = date.today()
        entry.montant = None
        entry.categorie = "transport"
        entry.description = None
        entry.magasin = None
        entry.est_recurrent = None
        entry.frequence_recurrence = None

        result = db_entry_to_depense(entry)

        assert result.montant == 0.0
        assert result.description == ""
        assert result.magasin == ""
        assert result.est_recurrente is False

    def test_conversion_recurrence(self):
        """Conversion avec récurrence."""
        entry = MagicMock()
        entry.id = 4
        entry.date = date.today()
        entry.montant = 100.0
        entry.categorie = "loyer"
        entry.description = "Loyer"
        entry.magasin = ""
        entry.est_recurrent = True
        entry.frequence_recurrence = "mensuel"

        result = db_entry_to_depense(entry)

        assert result.est_recurrente is True
        assert result.frequence == FrequenceRecurrence.MENSUEL

    def test_conversion_frequence_inconnue(self):
        """Fréquence inconnue devient PONCTUEL."""
        entry = MagicMock()
        entry.id = 5
        entry.date = date.today()
        entry.montant = 50.0
        entry.categorie = "autre"
        entry.description = ""
        entry.magasin = ""
        entry.est_recurrent = True
        entry.frequence_recurrence = "frequence_invalide"

        result = db_entry_to_depense(entry)

        assert result.frequence == FrequenceRecurrence.PONCTUEL


class TestDbEntriesToDepenses:
    """Tests pour db_entries_to_depenses."""

    def test_conversion_liste_vide(self):
        """Liste vide retourne liste vide."""
        result = db_entries_to_depenses([])
        assert result == []

    def test_conversion_plusieurs_entrees(self):
        """Conversion de plusieurs entrées."""
        entries = []
        for i in range(3):
            entry = MagicMock()
            entry.id = i + 1
            entry.date = date.today()
            entry.montant = 10.0 * (i + 1)
            entry.categorie = "alimentation"
            entry.description = f"Test {i}"
            entry.magasin = ""
            entry.est_recurrent = False
            entry.frequence_recurrence = None
            entries.append(entry)

        result = db_entries_to_depenses(entries)

        assert len(result) == 3
        assert result[0].montant == 10.0
        assert result[1].montant == 20.0
        assert result[2].montant == 30.0


# ═══════════════════════════════════════════════════════════
# CALCULS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculerMoyennePonderee:
    """Tests pour calculer_moyenne_ponderee."""

    def test_liste_vide(self):
        """Liste vide retourne 0."""
        assert calculer_moyenne_ponderee([]) == 0.0

    def test_une_seule_valeur(self):
        """Une seule valeur retourne cette valeur."""
        result = calculer_moyenne_ponderee([100.0])
        assert result == 100.0

    def test_moyennes_egales_sans_poids(self):
        """Valeurs égales sans poids spécifiés."""
        result = calculer_moyenne_ponderee([50.0, 50.0, 50.0])
        assert 49 < result < 51  # Proche de 50

    def test_poids_personnalises(self):
        """Utilisation de poids personnalisés."""
        # Premier = 20, poids 1; Deuxième = 40, poids 2
        result = calculer_moyenne_ponderee([20.0, 40.0], [1.0, 2.0])
        expected = (20 * 1 + 40 * 2) / (1 + 2)  # 33.33
        assert abs(result - expected) < 0.01

    def test_poids_tous_zero(self):
        """Poids tous à zéro retourne 0."""
        result = calculer_moyenne_ponderee([100.0, 200.0], [0.0, 0.0])
        assert result == 0.0

    def test_poids_trop_longs(self):
        """Poids plus longs que valeurs sont tronqués."""
        result = calculer_moyenne_ponderee([10.0, 20.0], [1.0, 1.0, 1.0, 1.0])
        expected = (10 + 20) / 2.0
        assert result == expected


class TestCalculerTendance:
    """Tests pour calculer_tendance."""

    def test_moins_de_2_valeurs(self):
        """Moins de 2 valeurs retourne 0."""
        assert calculer_tendance([]) == 0.0
        assert calculer_tendance([100.0]) == 0.0

    def test_tendance_croissante(self):
        """Tendance vers le haut."""
        result = calculer_tendance([100.0, 150.0, 200.0])
        assert result > 0

    def test_tendance_decroissante(self):
        """Tendance vers le bas."""
        result = calculer_tendance([200.0, 150.0, 100.0])
        assert result < 0

    def test_tendance_stable(self):
        """Tendance stable (mêmes valeurs)."""
        result = calculer_tendance([100.0, 100.0, 100.0])
        assert result == 0.0


class TestCalculerVariance:
    """Tests pour calculer_variance."""

    def test_moins_de_2_valeurs(self):
        """Moins de 2 valeurs retourne 0."""
        assert calculer_variance([]) == 0.0
        assert calculer_variance([100.0]) == 0.0

    def test_variance_zero(self):
        """Valeurs identiques ont variance 0."""
        result = calculer_variance([50.0, 50.0, 50.0])
        assert result == 0.0

    def test_variance_positive(self):
        """Valeurs différentes ont variance > 0."""
        result = calculer_variance([10.0, 20.0, 30.0])
        assert result > 0

    def test_variance_avec_moyenne_fournie(self):
        """Calcul avec moyenne pré-calculée."""
        valeurs = [10.0, 20.0, 30.0]
        moyenne = 20.0
        result = calculer_variance(valeurs, moyenne)
        # Variance = ((10-20)² + (20-20)² + (30-20)²) / 3 = (100 + 0 + 100) / 3
        expected = 200 / 3
        assert abs(result - expected) < 0.01


class TestCalculerConfiancePrevision:
    """Tests pour calculer_confiance_prevision."""

    def test_moins_de_3_valeurs(self):
        """Moins de 3 valeurs retourne 0.5."""
        assert calculer_confiance_prevision([], 0) == 0.5
        assert calculer_confiance_prevision([100.0], 100.0) == 0.5
        assert calculer_confiance_prevision([100.0, 100.0], 100.0) == 0.5

    def test_confiance_elevee_variance_faible(self):
        """Variance faible = confiance élevée."""
        valeurs = [100.0, 100.0, 100.0]
        result = calculer_confiance_prevision(valeurs, 100.0)
        assert result >= 0.9

    def test_confiance_entre_0_et_1(self):
        """Confiance toujours entre 0 et 1."""
        valeurs = [10.0, 50.0, 100.0, 200.0]
        moyenne = sum(valeurs) / len(valeurs)
        result = calculer_confiance_prevision(valeurs, moyenne)
        assert 0 <= result <= 1


class TestGenererPrevisionCategorie:
    """Tests pour generer_prevision_categorie."""

    def test_liste_vide(self):
        """Liste vide retourne None."""
        result = generer_prevision_categorie(CategorieDepense.ALIMENTATION, [])
        assert result is None

    def test_valeurs_toutes_zero(self):
        """Toutes les valeurs à 0 retourne None."""
        result = generer_prevision_categorie(CategorieDepense.COURSES, [0, 0, 0])
        assert result is None

    def test_prevision_valide(self):
        """Génère une prévision valide."""
        valeurs = [100.0, 120.0, 150.0]
        result = generer_prevision_categorie(CategorieDepense.TRANSPORT, valeurs)

        assert result is not None
        assert isinstance(result, PrevisionDepense)
        assert result.categorie == CategorieDepense.TRANSPORT
        assert result.montant_prevu >= 0
        assert 0 <= result.confiance <= 1
        assert "3 mois" in result.base_calcul


# ═══════════════════════════════════════════════════════════
# CALCULS DE BUDGET
# ═══════════════════════════════════════════════════════════


class TestCalculerPourcentageBudget:
    """Tests pour calculer_pourcentage_budget."""

    def test_budget_zero(self):
        """Budget zéro retourne 0%."""
        assert calculer_pourcentage_budget(100.0, 0.0) == 0.0

    def test_budget_negatif(self):
        """Budget négatif retourne 0%."""
        assert calculer_pourcentage_budget(50.0, -100.0) == 0.0

    def test_50_pourcent(self):
        """Moitié du budget utilisé."""
        assert calculer_pourcentage_budget(250.0, 500.0) == 50.0

    def test_100_pourcent(self):
        """Budget entièrement utilisé."""
        assert calculer_pourcentage_budget(500.0, 500.0) == 100.0

    def test_plafond_999(self):
        """Pourcentage plafonné à 999%."""
        result = calculer_pourcentage_budget(10000.0, 100.0)
        assert result == 999.0


class TestCalculerResteDisponible:
    """Tests pour calculer_reste_disponible."""

    def test_reste_positif(self):
        """Reste calculé correctement."""
        assert calculer_reste_disponible(500.0, 200.0) == 300.0

    def test_reste_zero(self):
        """Budget épuisé = reste 0."""
        assert calculer_reste_disponible(500.0, 500.0) == 0.0

    def test_reste_negatif_devient_zero(self):
        """Dépenses > budget retourne 0 (pas négatif)."""
        assert calculer_reste_disponible(500.0, 600.0) == 0.0


class TestEstBudgetDepasse:
    """Tests pour est_budget_depasse."""

    def test_pas_depasse(self):
        """Dépense < budget = pas dépassé."""
        assert est_budget_depasse(400.0, 500.0) is False

    def test_egal_pas_depasse(self):
        """Dépense = budget = pas dépassé."""
        assert est_budget_depasse(500.0, 500.0) is False

    def test_depasse(self):
        """Dépense > budget = dépassé."""
        assert est_budget_depasse(600.0, 500.0) is True


class TestEstBudgetARisque:
    """Tests pour est_budget_a_risque."""

    def test_budget_zero(self):
        """Budget zéro = pas à risque."""
        assert est_budget_a_risque(50.0, 0.0) is False

    def test_pas_a_risque(self):
        """< 80% = pas à risque."""
        assert est_budget_a_risque(350.0, 500.0) is False  # 70%

    def test_a_risque_80_pourcent(self):
        """80% exactement = à risque."""
        assert est_budget_a_risque(400.0, 500.0) is True

    def test_a_risque_entre_80_et_100(self):
        """Entre 80% et 100% = à risque."""
        assert est_budget_a_risque(450.0, 500.0) is True  # 90%

    def test_100_pourcent_pas_a_risque(self):
        """100% n'est pas à risque (c'est dépassé)."""
        assert est_budget_a_risque(500.0, 500.0) is False

    def test_depasse_pas_a_risque(self):
        """Dépassé n'est pas 'à risque' (c'est dépassé!)."""
        assert est_budget_a_risque(600.0, 500.0) is False

    def test_seuil_personnalise(self):
        """Seuil personnalisé."""
        # 70% sur 500 = 350
        assert est_budget_a_risque(350.0, 500.0, seuil=70.0) is True
        assert est_budget_a_risque(300.0, 500.0, seuil=70.0) is False


# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES DÉPENSES
# ═══════════════════════════════════════════════════════════


class TestAgregerDepensesParCategorie:
    """Tests pour agreger_depenses_par_categorie."""

    def test_liste_vide(self):
        """Liste vide retourne dict vide."""
        result = agreger_depenses_par_categorie([])
        assert result == {}

    def test_une_categorie(self):
        """Une seule catégorie."""
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.ALIMENTATION),
            Depense(montant=50.0, categorie=CategorieDepense.ALIMENTATION),
        ]
        result = agreger_depenses_par_categorie(depenses)

        assert len(result) == 1
        assert result[CategorieDepense.ALIMENTATION] == 150.0

    def test_plusieurs_categories(self):
        """Plusieurs catégories."""
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.ALIMENTATION),
            Depense(montant=50.0, categorie=CategorieDepense.TRANSPORT),
            Depense(montant=75.0, categorie=CategorieDepense.ALIMENTATION),
        ]
        result = agreger_depenses_par_categorie(depenses)

        assert len(result) == 2
        assert result[CategorieDepense.ALIMENTATION] == 175.0
        assert result[CategorieDepense.TRANSPORT] == 50.0


class TestCalculerTotalDepenses:
    """Tests pour calculer_total_depenses."""

    def test_liste_vide(self):
        """Liste vide retourne 0."""
        assert calculer_total_depenses([]) == 0.0

    def test_une_depense(self):
        """Une seule dépense."""
        depenses = [Depense(montant=123.45, categorie=CategorieDepense.AUTRE)]
        assert calculer_total_depenses(depenses) == 123.45

    def test_plusieurs_depenses(self):
        """Somme de plusieurs dépenses."""
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.ALIMENTATION),
            Depense(montant=50.0, categorie=CategorieDepense.TRANSPORT),
            Depense(montant=25.0, categorie=CategorieDepense.LOISIRS),
        ]
        assert calculer_total_depenses(depenses) == 175.0


class TestFiltrerDepensesParCategorie:
    """Tests pour filtrer_depenses_par_categorie."""

    def test_liste_vide(self):
        """Liste vide retourne liste vide."""
        result = filtrer_depenses_par_categorie([], CategorieDepense.ALIMENTATION)
        assert result == []

    def test_aucun_match(self):
        """Aucune correspondance retourne liste vide."""
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.TRANSPORT),
        ]
        result = filtrer_depenses_par_categorie(depenses, CategorieDepense.ALIMENTATION)
        assert result == []

    def test_filtre_correct(self):
        """Filtre correctement par catégorie."""
        depenses = [
            Depense(montant=100.0, categorie=CategorieDepense.ALIMENTATION),
            Depense(montant=50.0, categorie=CategorieDepense.TRANSPORT),
            Depense(montant=75.0, categorie=CategorieDepense.ALIMENTATION),
        ]
        result = filtrer_depenses_par_categorie(depenses, CategorieDepense.ALIMENTATION)

        assert len(result) == 2
        assert all(d.categorie == CategorieDepense.ALIMENTATION for d in result)


class TestFiltrerDepensesParPeriode:
    """Tests pour filtrer_depenses_par_periode."""

    def test_liste_vide(self):
        """Liste vide retourne liste vide."""
        result = filtrer_depenses_par_periode(
            [],
            date(2026, 1, 1),
            date(2026, 12, 31)
        )
        assert result == []

    def test_filtre_periode(self):
        """Filtre correctement par période."""
        depenses = [
            Depense(date=date(2026, 1, 15), montant=100.0, categorie=CategorieDepense.AUTRE),
            Depense(date=date(2026, 2, 10), montant=50.0, categorie=CategorieDepense.AUTRE),
            Depense(date=date(2026, 3, 5), montant=75.0, categorie=CategorieDepense.AUTRE),
        ]
        result = filtrer_depenses_par_periode(
            depenses,
            date(2026, 2, 1),
            date(2026, 2, 28)
        )

        assert len(result) == 1
        assert result[0].date == date(2026, 2, 10)

    def test_dates_incluses(self):
        """Les dates de début et fin sont incluses."""
        depenses = [
            Depense(date=date(2026, 2, 1), montant=100.0, categorie=CategorieDepense.AUTRE),
            Depense(date=date(2026, 2, 15), montant=50.0, categorie=CategorieDepense.AUTRE),
            Depense(date=date(2026, 2, 28), montant=75.0, categorie=CategorieDepense.AUTRE),
        ]
        result = filtrer_depenses_par_periode(
            depenses,
            date(2026, 2, 1),
            date(2026, 2, 28)
        )

        assert len(result) == 3


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DE RÉSUMÉS
# ═══════════════════════════════════════════════════════════


class TestConstruireResumeFinancier:
    """Tests pour construire_resume_financier."""

    def test_resume_vide(self):
        """Résumé sans dépenses."""
        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=[],
            budgets={}
        )

        assert result.mois == 2
        assert result.annee == 2026
        assert result.total_depenses == 0.0
        assert result.total_budget == 0.0

    def test_resume_complet(self):
        """Résumé avec dépenses et budgets."""
        depenses = [
            Depense(montant=400.0, categorie=CategorieDepense.ALIMENTATION),
            Depense(montant=100.0, categorie=CategorieDepense.TRANSPORT),
        ]
        budgets = {
            CategorieDepense.ALIMENTATION: 500.0,
            CategorieDepense.TRANSPORT: 200.0,
        }

        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets
        )

        assert result.total_depenses == 500.0
        assert result.total_budget == 700.0
        assert "alimentation" in result.depenses_par_categorie
        assert result.depenses_par_categorie["alimentation"] == 400.0

    def test_categories_depassees(self):
        """Détection des catégories dépassées."""
        depenses = [
            Depense(montant=600.0, categorie=CategorieDepense.ALIMENTATION),
        ]
        budgets = {
            CategorieDepense.ALIMENTATION: 500.0,
        }

        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets
        )

        assert "alimentation" in result.categories_depassees

    def test_categories_a_risque(self):
        """Détection des catégories à risque."""
        depenses = [
            Depense(montant=450.0, categorie=CategorieDepense.TRANSPORT),  # 90%
        ]
        budgets = {
            CategorieDepense.TRANSPORT: 500.0,
        }

        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets=budgets
        )

        assert "transport" in result.categories_a_risque
        assert "transport" not in result.categories_depassees

    def test_variation_vs_mois_precedent(self):
        """Calcul de la variation vs mois précédent."""
        depenses = [
            Depense(montant=600.0, categorie=CategorieDepense.ALIMENTATION),
        ]
        depenses_precedentes = [
            Depense(montant=500.0, categorie=CategorieDepense.ALIMENTATION),
        ]

        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets={},
            depenses_mois_precedent=depenses_precedentes
        )

        # (600 - 500) / 500 * 100 = 20%
        assert result.variation_vs_mois_precedent == 20.0

    def test_variation_mois_precedent_zero(self):
        """Variation quand mois précédent est vide."""
        depenses = [
            Depense(montant=500.0, categorie=CategorieDepense.ALIMENTATION),
        ]

        result = construire_resume_financier(
            mois=2,
            annee=2026,
            depenses=depenses,
            budgets={},
            depenses_mois_precedent=[]
        )

        assert result.variation_vs_mois_precedent == 0.0


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderMontant:
    """Tests pour valider_montant."""

    def test_float_valide(self):
        """Float valide accepté."""
        assert valider_montant(123.45) == 123.45

    def test_int_valide(self):
        """Int converti en float."""
        assert valider_montant(100) == 100.0

    def test_string_valide(self):
        """String numérique converti."""
        assert valider_montant("50.5") == 50.5

    def test_string_invalide(self):
        """String non numérique lève ValueError."""
        with pytest.raises(ValueError) as exc:
            valider_montant("abc")
        assert "invalide" in str(exc.value).lower()

    def test_none_invalide(self):
        """None lève ValueError."""
        with pytest.raises(ValueError):
            valider_montant(None)


class TestValiderMois:
    """Tests pour valider_mois."""

    def test_mois_valide(self):
        """Mois 1-12 acceptés."""
        for mois in range(1, 13):
            assert valider_mois(mois) == mois

    def test_mois_zero_invalide(self):
        """Mois 0 lève ValueError."""
        with pytest.raises(ValueError) as exc:
            valider_mois(0)
        assert "invalide" in str(exc.value).lower()

    def test_mois_13_invalide(self):
        """Mois 13 lève ValueError."""
        with pytest.raises(ValueError) as exc:
            valider_mois(13)
        assert "invalide" in str(exc.value).lower()

    def test_mois_negatif_invalide(self):
        """Mois négatif lève ValueError."""
        with pytest.raises(ValueError):
            valider_mois(-1)


class TestValiderAnnee:
    """Tests pour valider_annee."""

    def test_annee_valide(self):
        """Années 1900-2100 acceptées."""
        assert valider_annee(2026) == 2026
        assert valider_annee(1900) == 1900
        assert valider_annee(2100) == 2100

    def test_annee_avant_1900_invalide(self):
        """Année < 1900 lève ValueError."""
        with pytest.raises(ValueError) as exc:
            valider_annee(1899)
        assert "invalide" in str(exc.value).lower()

    def test_annee_apres_2100_invalide(self):
        """Année > 2100 lève ValueError."""
        with pytest.raises(ValueError) as exc:
            valider_annee(2101)
        assert "invalide" in str(exc.value).lower()
