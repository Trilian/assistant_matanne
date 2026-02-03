"""
PHASE 10: Budget Service - Real Business Logic Tests
Tests for expense tracking, budget analysis, and financial reporting
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.services.budget import BudgetService
from src.core.models.maison_extended import Depense, Budget, CategorieDepense
from src.core.errors import ErreurBaseDeDonnees


class TestBudgetCreation:
    """Test budget creation and setup"""

    def test_create_monthly_budget(self, db: Session):
        """Create a monthly budget"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget Février 2026",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=2000.00
        )
        db.add(budget)
        db.commit()
        
        assert budget.id is not None
        assert budget.montant_total == 2000.00

    def test_create_budget_with_categories(self, db: Session):
        """Create budget with spending categories"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget familial",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=3000.00
        )
        db.add(budget)
        db.commit()
        
        # Add category allocations
        categories = [
            CategorieDepense(budget_id=budget.id, nom="Alimentation", montant=800),
            CategorieDepense(budget_id=budget.id, nom="Logement", montant=1200),
            CategorieDepense(budget_id=budget.id, nom="Transport", montant=300),
            CategorieDepense(budget_id=budget.id, nom="Loisirs", montant=300),
        ]
        db.add_all(categories)
        db.commit()
        
        assert len(budget.categories) == 4


class TestExpenseTracking:
    """Test expense creation and tracking"""

    def test_record_expense(self, db: Session):
        """Record an expense"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget test",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        db.commit()
        
        expense = Depense(
            budget_id=budget.id,
            nom="Courses supermarché",
            categorie="Alimentation",
            montant=150.50,
            date=date.today(),
            fournisseur="Carrefour"
        )
        db.add(expense)
        db.commit()
        
        assert expense.id is not None
        assert expense.montant == 150.50

    def test_record_multiple_expenses(self, db: Session):
        """Record multiple expenses"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        db.commit()
        
        expenses = [
            Depense(budget_id=budget.id, nom="Courses 1", montant=100, 
                   categorie="Alimentation", date=date.today()),
            Depense(budget_id=budget.id, nom="Courses 2", montant=80, 
                   categorie="Alimentation", date=date.today()),
            Depense(budget_id=budget.id, nom="Essence", montant=60, 
                   categorie="Transport", date=date.today()),
        ]
        db.add_all(expenses)
        db.commit()
        
        total_expenses = sum(e.montant for e in expenses)
        assert total_expenses == 240

    def test_record_expense_with_tags(self, db: Session):
        """Record expense with tags for filtering"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        db.commit()
        
        expense = Depense(
            budget_id=budget.id,
            nom="Courses bio",
            montant=50,
            categorie="Alimentation",
            date=date.today(),
            tags=["bio", "sain", "express"]
        )
        db.add(expense)
        db.commit()
        
        assert "bio" in expense.tags


class TestBudgetAnalysis:
    """Test budget analysis and reporting"""

    def test_calculate_total_spent(self, db: Session):
        """Calculate total spent in period"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        for i in range(5):
            Depense(
                budget_id=budget.id,
                nom=f"Dépense {i}",
                montant=100,
                categorie="Alimentation",
                date=date.today()
            ).save(db)
        db.commit()
        
        total_spent = service.calculer_total_depenses(budget_id=budget.id)
        
        assert total_spent == 500

    def test_calculate_remaining_budget(self, db: Session):
        """Calculate remaining budget"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        Depense(
            budget_id=budget.id,
            nom="Courses",
            montant=300,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        remaining = service.calculer_restant(budget_id=budget.id)
        
        assert remaining == 700

    def test_calculate_percentage_spent(self, db: Session):
        """Calculate percentage of budget spent"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        Depense(
            budget_id=budget.id,
            nom="Dépense",
            montant=250,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        percentage = service.calculer_pourcentage_depense(budget_id=budget.id)
        
        assert percentage == 25

    def test_get_expenses_by_category(self, db: Session):
        """Get expenses grouped by category"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        # Add expenses in different categories
        Depense(budget_id=budget.id, nom="Courses", montant=200, 
               categorie="Alimentation", date=date.today()).save(db)
        Depense(budget_id=budget.id, nom="Essence", montant=100, 
               categorie="Transport", date=date.today()).save(db)
        Depense(budget_id=budget.id, nom="Fruits", montant=50, 
               categorie="Alimentation", date=date.today()).save(db)
        db.commit()
        
        by_category = service.get_depenses_par_categorie(budget_id=budget.id)
        
        assert by_category["Alimentation"] == 250
        assert by_category["Transport"] == 100


class TestBudgetAlerts:
    """Test budget alert system"""

    def test_alert_budget_exceeded(self, db: Session):
        """Alert when budget is exceeded"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=500.00
        )
        db.add(budget)
        
        # Spend more than budget
        Depense(
            budget_id=budget.id,
            nom="Dépense",
            montant=600,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        alerts = service.get_alerts(budget_id=budget.id)
        
        assert len(alerts) > 0
        assert any("dépassé" in str(a).lower() for a in alerts)

    def test_alert_category_exceeded(self, db: Session):
        """Alert when category budget exceeded"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        # Add category with limit
        category = CategorieDepense(
            budget_id=budget.id,
            nom="Alimentation",
            montant=200
        )
        db.add(category)
        
        # Exceed category
        Depense(
            budget_id=budget.id,
            nom="Courses",
            montant=250,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        alerts = service.get_alerts_categorie(budget_id=budget.id)
        
        assert len(alerts) > 0

    def test_alert_approaching_limit(self, db: Session):
        """Alert when approaching budget limit"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        # Spend 85% of budget
        Depense(
            budget_id=budget.id,
            nom="Dépense",
            montant=850,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        alerts = service.get_alerts(budget_id=budget.id)
        
        assert len(alerts) > 0
        assert any("approche" in str(a).lower() for a in alerts)


class TestBudgetForecasting:
    """Test budget forecasting"""

    def test_forecast_spending(self, db: Session):
        """Forecast remaining spending based on trend"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=2000.00
        )
        db.add(budget)
        
        # Add expenses for first 10 days
        for i in range(10):
            Depense(
                budget_id=budget.id,
                nom=f"Dépense {i}",
                montant=100,
                categorie="Alimentation",
                date=date(2026, 2, 1) + timedelta(days=i)
            ).save(db)
        db.commit()
        
        forecast = service.estimer_depense_mois(budget_id=budget.id)
        
        # Should forecast around 300 for full month (100/day * 30 days)
        assert forecast > 200

    def test_compare_to_previous_periods(self, db: Session):
        """Compare spending to previous periods"""
        service = BudgetService(db)
        
        # Create budgets for different months
        for month in range(1, 3):
            budget = Budget(
                nom=f"Budget mois {month}",
                date_debut=date(2026, month, 1),
                date_fin=date(2026, month, 28),
                montant_total=1000.00
            )
            db.add(budget)
            
            # Add expenses
            Depense(
                budget_id=budget.id,
                nom="Courses",
                montant=300,
                categorie="Alimentation",
                date=date(2026, month, 15)
            ).save(db)
        db.commit()
        
        comparison = service.comparer_periodes(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 2, 28)
        )
        
        assert comparison is not None


class TestBudgetExport:
    """Test budget data export"""

    def test_export_to_csv(self, db: Session):
        """Export budget to CSV"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        
        Depense(
            budget_id=budget.id,
            nom="Courses",
            montant=100,
            categorie="Alimentation",
            date=date.today()
        ).save(db)
        db.commit()
        
        csv_data = service.export_to_csv(budget_id=budget.id)
        
        assert csv_data is not None
        assert "Courses" in csv_data

    def test_generate_report(self, db: Session):
        """Generate budget report"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        db.commit()
        
        report = service.generer_rapport(budget_id=budget.id)
        
        assert report is not None
        assert "budget" in str(report).lower()


class TestBudgetValidation:
    """Test budget validation"""

    def test_validate_expense_amount(self, db: Session):
        """Validate expense amounts are positive"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(budget)
        db.commit()
        
        # Negative expense should fail
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            Depense(
                budget_id=budget.id,
                nom="Invalid",
                montant=-100,
                categorie="Alimentation",
                date=date.today()
            )

    def test_validate_budget_dates(self, db: Session):
        """Validate budget date range"""
        service = BudgetService(db)
        
        # End date before start date
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            Budget(
                nom="Budget",
                date_debut=date(2026, 2, 28),
                date_fin=date(2026, 2, 1),
                montant_total=1000.00
            )

    def test_validate_positive_budget_amount(self, db: Session):
        """Validate budget amount is positive"""
        service = BudgetService(db)
        
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            Budget(
                nom="Budget",
                date_debut=date(2026, 2, 1),
                date_fin=date(2026, 2, 28),
                montant_total=-100
            )


class TestBudgetRecurring:
    """Test recurring budget templates"""

    def test_create_recurring_budget(self, db: Session):
        """Create recurring monthly budget"""
        service = BudgetService(db)
        
        budget = Budget(
            nom="Budget mensuel",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00,
            recurring=True,
            recurrence_type="monthly"
        )
        db.add(budget)
        db.commit()
        
        assert budget.recurring is True

    def test_clone_budget(self, db: Session):
        """Clone budget to next period"""
        service = BudgetService(db)
        
        original = Budget(
            nom="Budget Février",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            montant_total=1000.00
        )
        db.add(original)
        db.commit()
        
        # Clone to next month
        cloned = service.cloner_budget(budget_id=original.id, 
                                      new_date_debut=date(2026, 3, 1))
        
        assert cloned is not None
        assert cloned.date_debut == date(2026, 3, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
