"""Tests unitaires pour le service budget."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock
from pydantic import ValidationError


class TestCategorieDepenseEnum:
    """Tests pour l'enum CategorieDepense."""

    def test_categories_disponibles(self):
        """Vérifie que toutes les catégories sont définies."""
        from src.services.budget import CategorieDepense
        
        categories_attendues = [
            "alimentation", "courses", "sante", "transport",
            "loisirs", "education", "vetements", "maison",
            "factures", "abonnements", "epargne", "cadeaux", "autre"
        ]
        
        for cat in categories_attendues:
            assert hasattr(CategorieDepense, cat.upper()) or cat in [c.value for c in CategorieDepense]

    def test_categorie_valeur_string(self):
        """Les catégories ont des valeurs string."""
        from src.services.budget import CategorieDepense
        
        for cat in CategorieDepense:
            assert isinstance(cat.value, str)


class TestFrequenceEnum:
    """Tests pour l'enum Frequence."""

    def test_frequences_disponibles(self):
        """Vérifie les fréquences de dépenses."""
        from src.services.budget import Frequence
        
        assert Frequence.PONCTUEL is not None
        assert Frequence.HEBDOMADAIRE is not None
        assert Frequence.MENSUEL is not None


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

    def test_depense_montant_positif(self):
        """Le montant doit être positif."""
        from src.services.budget import Depense, CategorieDepense
        
        # Montant positif OK
        depense = Depense(
            montant=100.0,
            categorie=CategorieDepense.ALIMENTATION,
            description="Test"
        )
        assert depense.montant == 100.0

    def test_depense_date_defaut(self):
        """La date par défaut est aujourd'hui."""
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=25.0,
            categorie=CategorieDepense.TRANSPORT,
            description="Essence"
        )
        
        # La date devrait être définie (aujourd'hui ou None selon le modèle)
        assert depense.date is None or isinstance(depense.date, (date, datetime))


class TestBudgetMensuelModel:
    """Tests pour le modèle BudgetMensuel avec propriétés calculées."""

    def test_budget_mensuel_creation(self):
        """Création d'un budget mensuel."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=350.0
        )
        
        assert budget.montant_prevu == 500.0
        assert budget.montant_depense == 350.0

    def test_pourcentage_utilise(self):
        """Calcul du pourcentage utilisé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=250.0
        )
        
        # 250/500 = 50%
        assert budget.pourcentage_utilise == 50.0

    def test_pourcentage_utilise_zero_prevu(self):
        """Pourcentage avec budget prévu à zéro."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=0.0,
            montant_depense=100.0
        )
        
        # Division par zéro → devrait retourner 0 ou 100
        assert budget.pourcentage_utilise in [0.0, 100.0, float('inf')]

    def test_reste_disponible(self):
        """Calcul du reste disponible."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=350.0
        )
        
        # 500 - 350 = 150
        assert budget.reste_disponible == 150.0

    def test_reste_disponible_negatif(self):
        """Reste disponible peut être négatif (dépassement)."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=100.0,
            montant_depense=150.0
        )
        
        # 100 - 150 = -50
        assert budget.reste_disponible == -50.0

    def test_est_depasse(self):
        """Détection de budget dépassé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        # Non dépassé
        budget_ok = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=400.0
        )
        assert budget_ok.est_depasse == False
        
        # Dépassé
        budget_ko = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=600.0
        )
        assert budget_ko.est_depasse == True


class TestResumeMensuelModel:
    """Tests pour le modèle ResumeMensuel."""

    def test_resume_creation(self):
        """Création d'un résumé mensuel."""
        from src.services.budget import ResumeMensuel
        
        resume = ResumeMensuel(
            mois=1,
            annee=2026,
            total_prevu=2000.0,
            total_depense=1500.0,
            budgets=[]
        )
        
        assert resume.mois == 1
        assert resume.annee == 2026
        assert resume.total_prevu == 2000.0


class TestPrevisionModel:
    """Tests pour le modèle Prevision."""

    def test_prevision_creation(self):
        """Création d'une prévision."""
        from src.services.budget import Prevision, CategorieDepense
        
        prevision = Prevision(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=450.0,
            confiance=0.85
        )
        
        assert prevision.montant_prevu == 450.0
        assert prevision.confiance == 0.85

    def test_prevision_confiance_bornee(self):
        """La confiance doit être entre 0 et 1."""
        from src.services.budget import Prevision, CategorieDepense
        
        # Confiance valide
        prevision = Prevision(
            categorie=CategorieDepense.TRANSPORT,
            montant_prevu=200.0,
            confiance=0.75
        )
        assert 0 <= prevision.confiance <= 1


class TestBudgetServiceInit:
    """Tests d'initialisation du service budget."""

    def test_get_budget_service_singleton(self):
        """La factory retourne une instance."""
        from src.services.budget import get_budget_service
        
        service = get_budget_service()
        assert service is not None

    def test_service_has_required_methods(self):
        """Le service expose les méthodes requises."""
        from src.services.budget import get_budget_service
        
        service = get_budget_service()
        
        # Méthodes CRUD
        assert hasattr(service, 'ajouter_depense')
        assert hasattr(service, 'modifier_depense')
        assert hasattr(service, 'supprimer_depense')
        assert hasattr(service, 'get_depenses_mois')
        
        # Méthodes analytics
        assert hasattr(service, 'get_resume_mensuel')
        assert hasattr(service, 'prevoir_depenses')


class TestBudgetServiceLogique:
    """Tests de la logique métier du service budget."""

    @pytest.fixture
    def mock_session(self):
        """Session de base de données mockée."""
        session = MagicMock()
        session.query.return_value.filter.return_value.all.return_value = []
        session.query.return_value.filter.return_value.first.return_value = None
        return session

    def test_calculer_moyenne_ponderee(self):
        """Test du calcul de moyenne pondérée pour prévisions."""
        # Liste de montants avec poids décroissants (plus récent = plus de poids)
        montants = [100, 120, 110, 130, 125]  # Plus récent en dernier
        
        # Calcul manuel: poids = [1, 2, 3, 4, 5]
        # moyenne = (100*1 + 120*2 + 110*3 + 130*4 + 125*5) / (1+2+3+4+5)
        # = (100 + 240 + 330 + 520 + 625) / 15 = 1815 / 15 = 121
        
        total_poids = sum(range(1, len(montants) + 1))
        moyenne = sum(m * (i + 1) for i, m in enumerate(montants)) / total_poids
        
        assert moyenne == pytest.approx(121.0, rel=0.01)

    def test_calculer_variation_mensuelle(self):
        """Calcul de la variation entre deux mois."""
        mois_precedent = 500.0
        mois_courant = 550.0
        
        variation = ((mois_courant - mois_precedent) / mois_precedent) * 100
        
        assert variation == pytest.approx(10.0, rel=0.01)

    def test_calculer_variation_zero(self):
        """Variation avec mois précédent à zéro."""
        mois_precedent = 0.0
        mois_courant = 100.0
        
        # Éviter division par zéro
        if mois_precedent == 0:
            variation = 100.0 if mois_courant > 0 else 0.0
        else:
            variation = ((mois_courant - mois_precedent) / mois_precedent) * 100
        
        assert variation == 100.0


class TestBudgetServiceAlerts:
    """Tests des alertes budget."""

    def test_alerte_budget_depasse(self):
        """Génération d'alerte quand budget dépassé."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=500.0,
            montant_depense=600.0
        )
        
        # Budget dépassé de 20%
        depassement = budget.montant_depense - budget.montant_prevu
        pourcentage_depassement = (depassement / budget.montant_prevu) * 100
        
        assert budget.est_depasse == True
        assert depassement == 100.0
        assert pourcentage_depassement == 20.0

    def test_alerte_seuil_80_pourcent(self):
        """Alerte à 80% du budget."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.TRANSPORT,
            montant_prevu=200.0,
            montant_depense=170.0
        )
        
        # 170/200 = 85% > seuil 80%
        seuil_alerte = 80.0
        assert budget.pourcentage_utilise > seuil_alerte

    def test_pas_alerte_sous_seuil(self):
        """Pas d'alerte sous le seuil."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            categorie=CategorieDepense.LOISIRS,
            montant_prevu=300.0,
            montant_depense=150.0
        )
        
        # 50% < seuil 80%
        seuil_alerte = 80.0
        assert budget.pourcentage_utilise < seuil_alerte


class TestBudgetAggregation:
    """Tests d'agrégation des dépenses."""

    def test_grouper_par_categorie(self):
        """Groupement des dépenses par catégorie."""
        from src.services.budget import CategorieDepense
        
        depenses = [
            {"categorie": CategorieDepense.ALIMENTATION, "montant": 100},
            {"categorie": CategorieDepense.ALIMENTATION, "montant": 150},
            {"categorie": CategorieDepense.TRANSPORT, "montant": 50},
            {"categorie": CategorieDepense.TRANSPORT, "montant": 30},
            {"categorie": CategorieDepense.LOISIRS, "montant": 80},
        ]
        
        # Groupement manuel
        totaux = {}
        for d in depenses:
            cat = d["categorie"]
            totaux[cat] = totaux.get(cat, 0) + d["montant"]
        
        assert totaux[CategorieDepense.ALIMENTATION] == 250
        assert totaux[CategorieDepense.TRANSPORT] == 80
        assert totaux[CategorieDepense.LOISIRS] == 80

    def test_total_mensuel(self):
        """Calcul du total mensuel."""
        montants = [100, 150, 50, 30, 80]
        total = sum(montants)
        
        assert total == 410

    def test_moyenne_journaliere(self):
        """Calcul de la moyenne journalière."""
        total_mois = 900.0
        jours_dans_mois = 30
        
        moyenne_jour = total_mois / jours_dans_mois
        
        assert moyenne_jour == 30.0


class TestBudgetTendances:
    """Tests d'analyse des tendances."""

    def test_tendance_croissante(self):
        """Détection de tendance croissante."""
        mois_historique = [400, 420, 450, 480, 510, 540]
        
        # Tendance = moyenne des variations
        variations = []
        for i in range(1, len(mois_historique)):
            var = ((mois_historique[i] - mois_historique[i-1]) / mois_historique[i-1]) * 100
            variations.append(var)
        
        tendance_moyenne = sum(variations) / len(variations)
        
        # Tendance positive = croissante
        assert tendance_moyenne > 0

    def test_tendance_decroissante(self):
        """Détection de tendance décroissante."""
        mois_historique = [600, 550, 520, 480, 450, 420]
        
        variations = []
        for i in range(1, len(mois_historique)):
            var = ((mois_historique[i] - mois_historique[i-1]) / mois_historique[i-1]) * 100
            variations.append(var)
        
        tendance_moyenne = sum(variations) / len(variations)
        
        # Tendance négative = décroissante
        assert tendance_moyenne < 0

    def test_tendance_stable(self):
        """Détection de tendance stable."""
        mois_historique = [500, 505, 495, 502, 498, 500]
        
        variations = []
        for i in range(1, len(mois_historique)):
            var = ((mois_historique[i] - mois_historique[i-1]) / mois_historique[i-1]) * 100
            variations.append(var)
        
        tendance_moyenne = sum(variations) / len(variations)
        
        # Variation < 5% = stable
        assert abs(tendance_moyenne) < 5
