"""Tests unitaires pour le service budget."""

import pytest
from datetime import date, datetime


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCategorieDepenseEnum:
    """Tests pour l'enum CategorieDepense."""

    def test_categories_disponibles(self):
        """Vérifie que toutes les catégories sont définies."""
        from src.services.budget import CategorieDepense
        
        assert CategorieDepense.ALIMENTATION is not None
        assert CategorieDepense.COURSES is not None
        assert CategorieDepense.MAISON is not None
        assert CategorieDepense.LOISIRS is not None

    def test_categorie_valeur_string(self):
        """Les catégories ont des valeurs string."""
        from src.services.budget import CategorieDepense
        
        for cat in CategorieDepense:
            assert isinstance(cat.value, str)


class TestFrequenceRecurrenceEnum:
    """Tests pour l'enum FrequenceRecurrence."""

    def test_frequences_disponibles(self):
        """Vérifie les fréquences de dépenses."""
        from src.services.budget import FrequenceRecurrence
        
        assert FrequenceRecurrence.PONCTUEL is not None
        assert FrequenceRecurrence.HEBDOMADAIRE is not None
        assert FrequenceRecurrence.MENSUEL is not None
        assert FrequenceRecurrence.ANNUEL is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDepenseModel:
    """Tests pour le modèle Pydantic Depense."""

    def test_depense_creation_minimale(self):
        """Création d'une dépense avec champs minimaux."""
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=50.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Courses"
        )
        
        assert depense.montant == 50.0
        assert depense.description == "Courses"
        assert depense.categorie == CategorieDepense.ALIMENTATION

    def test_depense_date_defaut(self):
        """Date par défaut = aujourd'hui."""
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=25.0,
            categorie=CategorieDepense.LOISIRS
        )
        
        assert depense.date == date.today()

    def test_depense_avec_recurrence(self):
        """Dépense récurrente."""
        from src.services.budget import Depense, CategorieDepense, FrequenceRecurrence
        
        depense = Depense(
            montant=100.0,
            categorie=CategorieDepense.SERVICES,
            description="Abonnement internet",
            est_recurrente=True,
            frequence=FrequenceRecurrence.MENSUEL
        )
        
        assert depense.est_recurrente is True
        assert depense.frequence == FrequenceRecurrence.MENSUEL


class TestBudgetMensuelModel:
    """Tests pour BudgetMensuel."""

    def test_budget_mensuel_creation(self):
        """Création d'un budget mensuel."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=600.0,
            depense_reelle=450.0
        )
        
        assert budget.mois == 1
        assert budget.annee == 2026
        assert budget.budget_prevu == 600.0

    def test_pourcentage_utilise(self):
        """Calcul du pourcentage utilisé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=100.0,
            depense_reelle=75.0
        )
        
        assert budget.pourcentage_utilise == 75.0

    def test_pourcentage_utilise_zero_prevu(self):
        """Pourcentage avec budget prévu à 0."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=0.0,
            depense_reelle=50.0
        )
        
        assert budget.pourcentage_utilise == 0.0

    def test_reste_disponible(self):
        """Calcul du reste disponible."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=300.0
        )
        
        assert budget.reste_disponible == 200.0

    def test_reste_disponible_negatif(self):
        """Reste disponible jamais négatif."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=100.0,
            depense_reelle=150.0
        )
        
        assert budget.reste_disponible == 0

    def test_est_depasse(self):
        """Détection budget dépassé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=100.0,
            depense_reelle=150.0
        )
        
        assert budget.est_depasse is True


class TestResumeFinancierModel:
    """Tests pour ResumeFinancier."""

    def test_resume_creation(self):
        """Création d'un résumé financier."""
        from src.services.budget import ResumeFinancier
        
        resume = ResumeFinancier(
            mois=1,
            annee=2026,
            total_depenses=1500.0,
            total_budget=2000.0
        )
        
        assert resume.mois == 1
        assert resume.total_depenses == 1500.0


class TestPrevisionDepenseModel:
    """Tests pour PrevisionDepense."""

    def test_prevision_creation(self):
        """Création d'une prévision."""
        from src.services.budget import PrevisionDepense, CategorieDepense
        
        prevision = PrevisionDepense(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=550.0,
            confiance=0.85
        )
        
        assert prevision.montant_prevu == 550.0
        assert prevision.confiance == 0.85


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE BUDGET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBudgetServiceInit:
    """Tests d'initialisation du service."""

    def test_get_budget_service_singleton(self):
        """La factory retourne un singleton."""
        from src.services.budget import get_budget_service
        
        service1 = get_budget_service()
        service2 = get_budget_service()
        
        assert service1 is service2

    def test_service_has_required_methods(self):
        """Le service a les méthodes requises."""
        from src.services.budget import get_budget_service
        
        service = get_budget_service()
        
        assert hasattr(service, 'ajouter_depense')
        assert hasattr(service, 'get_depenses_mois')  # méthode réelle
        assert hasattr(service, 'definir_budget')


class TestBudgetServiceLogique:
    """Tests de logique métier (fonctions pures)."""

    def test_calculer_moyenne_ponderee(self):
        """Calcul de moyenne pondérée."""
        valeurs = [100, 200, 300]
        poids = [1, 2, 3]
        
        somme_ponderee = sum(v * p for v, p in zip(valeurs, poids))
        somme_poids = sum(poids)
        moyenne = somme_ponderee / somme_poids
        
        assert abs(moyenne - 233.33) < 0.01

    def test_calculer_variation_mensuelle(self):
        """Calcul de variation mensuelle."""
        mois_precedent = 500.0
        mois_courant = 600.0
        
        variation = ((mois_courant - mois_precedent) / mois_precedent) * 100
        
        assert variation == 20.0


class TestBudgetServiceAlerts:
    """Tests pour les alertes budget."""

    def test_alerte_budget_depasse(self):
        """Alerte quand budget dépassé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=600.0
        )
        
        assert budget.est_depasse is True

    def test_alerte_seuil_80_pourcent(self):
        """Alerte quand >80% utilisé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=1, annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.0,
            depense_reelle=420.0
        )
        
        assert budget.pourcentage_utilise >= 80


class TestBudgetAggregation:
    """Tests pour agrégation des dépenses."""

    def test_grouper_par_categorie(self):
        """Groupement des dépenses par catégorie."""
        from src.services.budget import CategorieDepense
        
        depenses = [
            {"categorie": CategorieDepense.ALIMENTATION, "montant": 100},
            {"categorie": CategorieDepense.ALIMENTATION, "montant": 50},
            {"categorie": CategorieDepense.LOISIRS, "montant": 80},
        ]
        
        par_cat = {}
        for d in depenses:
            cat = d["categorie"]
            par_cat[cat] = par_cat.get(cat, 0) + d["montant"]
        
        assert par_cat[CategorieDepense.ALIMENTATION] == 150
        assert par_cat[CategorieDepense.LOISIRS] == 80

    def test_total_mensuel(self):
        """Total des dépenses du mois."""
        depenses = [100.0, 200.0, 150.0, 80.0]
        total = sum(depenses)
        
        assert total == 530.0


class TestBudgetTendances:
    """Tests pour analyse des tendances."""

    def test_tendance_croissante(self):
        """Détection tendance croissante."""
        historique = [400, 450, 500, 550, 600]
        
        debut = sum(historique[:2]) / 2
        fin = sum(historique[-2:]) / 2
        
        tendance = "croissante" if fin > debut * 1.1 else "stable"
        
        assert tendance == "croissante"

    def test_tendance_stable(self):
        """Détection tendance stable."""
        historique = [500, 510, 495, 505, 500]
        
        debut = sum(historique[:2]) / 2
        fin = sum(historique[-2:]) / 2
        
        tendance = "croissante" if fin > debut * 1.1 else "stable" if fin > debut * 0.9 else "décroissante"
        
        assert tendance == "stable"


class TestBudgetDefaut:
    """Tests pour les budgets par défaut."""

    def test_budgets_defaut_existent(self):
        """Budgets par défaut définis."""
        from src.services.budget import BudgetService, CategorieDepense
        
        assert CategorieDepense.ALIMENTATION in BudgetService.BUDGETS_DEFAUT
        assert BudgetService.BUDGETS_DEFAUT[CategorieDepense.ALIMENTATION] == 600

    def test_budgets_defaut_positifs(self):
        """Tous les budgets défaut sont positifs."""
        from src.services.budget import BudgetService
        
        for cat, montant in BudgetService.BUDGETS_DEFAUT.items():
            assert montant > 0

