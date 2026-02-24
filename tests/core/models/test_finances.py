"""
Tests unitaires pour finances.py

Module: src.core.models.finances
Contient: Depense, BudgetMensuelDB, DepenseMaison
"""

from datetime import date
from decimal import Decimal

from src.core.models.finances import (
    BudgetMensuelDB,
    CategorieDepense,
    CategorieDepenseDB,
    Depense,
    DepenseMaison,
    TypeRecurrence,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCategorieDepenseDB:
    """Tests pour l'énumération CategorieDepenseDB."""

    def test_valeurs_principales(self):
        """Vérifie les catégories principales."""
        assert CategorieDepenseDB.ALIMENTATION.value == "alimentation"
        assert CategorieDepenseDB.TRANSPORT.value == "transport"
        assert CategorieDepenseDB.LOGEMENT.value == "logement"
        assert CategorieDepenseDB.SANTE.value == "sante"
        assert CategorieDepenseDB.LOISIRS.value == "loisirs"

    def test_toutes_valeurs_existent(self):
        """Vérifie que toutes les catégories attendues existent."""
        valeurs = [v.value for v in CategorieDepenseDB]
        expected = [
            "alimentation",
            "transport",
            "logement",
            "sante",
            "loisirs",
            "vetements",
            "education",
            "cadeaux",
            "abonnements",
            "restaurant",
            "vacances",
            "bebe",
            "autre",
        ]
        for cat in expected:
            assert cat in valeurs


class TestRecurrenceType:
    """Tests pour l'énumération TypeRecurrence."""

    def test_valeurs_disponibles(self):
        """Vérifie les types de récurrence."""
        assert TypeRecurrence.PONCTUEL.value == "ponctuel"
        assert TypeRecurrence.HEBDOMADAIRE.value == "hebdomadaire"
        assert TypeRecurrence.MENSUEL.value == "mensuel"
        assert TypeRecurrence.TRIMESTRIEL.value == "trimestriel"
        assert TypeRecurrence.ANNUEL.value == "annuel"


class TestExpenseCategory:
    """Tests pour l'énumération CategorieDepense."""

    def test_categories_maison(self):
        """Vérifie les catégories de dépenses maison."""
        assert CategorieDepense.GAZ.value == "gaz"
        assert CategorieDepense.ELECTRICITE.value == "electricite"
        assert CategorieDepense.EAU.value == "eau"
        assert CategorieDepense.INTERNET.value == "internet"
        assert CategorieDepense.LOYER.value == "loyer"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestDepense:
    """Tests pour le modèle Depense."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert Depense.__tablename__ == "depenses"

    def test_creation_instance(self):
        """Test de création d'une dépense."""
        depense = Depense(
            montant=Decimal("50.00"),
            categorie="alimentation",
            description="Courses Leclerc",
            date=date(2026, 2, 10),
        )
        assert depense.montant == Decimal("50.00")
        assert depense.categorie == "alimentation"
        assert depense.description == "Courses Leclerc"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut définies."""
        # Vérifier la présence des colonnes avec default
        colonnes = Depense.__table__.columns
        assert colonnes["categorie"].default is not None
        assert colonnes["created_at"].default is not None

    def test_est_recurrente_property(self):
        """Test de la propriété est_recurrente."""
        # Dépense ponctuelle
        depense1 = Depense(montant=Decimal("10.00"), recurrence=None)
        assert depense1.est_recurrente is False

        depense2 = Depense(montant=Decimal("10.00"), recurrence="ponctuel")
        assert depense2.est_recurrente is False

        # Dépense récurrente
        depense3 = Depense(montant=Decimal("10.00"), recurrence="mensuel")
        assert depense3.est_recurrente is True

    def test_repr(self):
        """Test de la représentation string."""
        depense = Depense(id=1, montant=Decimal("25.50"), categorie="loisirs")
        result = repr(depense)
        assert "Depense" in result
        assert "25.50" in result or "25.5" in result
        assert "loisirs" in result


class TestBudgetMensuelDB:
    """Tests pour le modèle BudgetMensuelDB."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert BudgetMensuelDB.__tablename__ == "budgets_mensuels"

    def test_creation_instance(self):
        """Test de création d'un budget mensuel."""
        budget = BudgetMensuelDB(
            mois=date(2026, 2, 1),
            budget_total=Decimal("2500.00"),
            notes="Budget février",
        )
        assert budget.mois == date(2026, 2, 1)
        assert budget.budget_total == Decimal("2500.00")
        assert budget.notes == "Budget février"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = BudgetMensuelDB.__table__.columns
        assert colonnes["budget_total"].default is not None

    def test_budgets_par_categorie(self):
        """Test du champ JSONB budgets_par_categorie."""
        budget = BudgetMensuelDB(
            mois=date(2026, 2, 1),
            budget_total=Decimal("2000.00"),
            budgets_par_categorie={
                "alimentation": 600,
                "transport": 200,
                "loisirs": 150,
            },
        )
        assert budget.budgets_par_categorie["alimentation"] == 600
        assert len(budget.budgets_par_categorie) == 3

    def test_repr(self):
        """Test de la représentation string."""
        budget = BudgetMensuelDB(id=1, mois=date(2026, 2, 1), budget_total=Decimal("1500"))
        result = repr(budget)
        assert "BudgetMensuelDB" in result
        assert "1500" in result


class TestHouseExpense:
    """Tests pour le modèle DepenseMaison."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert DepenseMaison.__tablename__ == "depenses_maison"

    def test_creation_instance(self):
        """Test de création d'une dépense maison."""
        expense = DepenseMaison(
            categorie="electricite",
            mois=2,
            annee=2026,
            montant=Decimal("85.50"),
            consommation=350.0,
            unite_consommation="kWh",
        )
        assert expense.categorie == "electricite"
        assert expense.mois == 2
        assert expense.annee == 2026
        assert expense.montant == Decimal("85.50")
        assert expense.consommation == 350.0
        assert expense.unite_consommation == "kWh"

    def test_fournisseur(self):
        """Test des champs fournisseur."""
        expense = DepenseMaison(
            categorie="gaz",
            mois=1,
            annee=2026,
            montant=Decimal("120.00"),
            fournisseur="Engie",
            numero_contrat="123456789",
        )
        assert expense.fournisseur == "Engie"
        assert expense.numero_contrat == "123456789"

    def test_repr(self):
        """Test de la représentation string."""
        expense = DepenseMaison(id=1, categorie="eau", montant=Decimal("45.00"))
        result = repr(expense)
        assert "DepenseMaison" in result
        assert "eau" in result
        assert "45" in result
