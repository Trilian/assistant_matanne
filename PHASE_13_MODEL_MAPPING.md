# 🔧 PHASE 13: Model Mapping & Import Fixes

## Real Models Found

### Inventory Models

- **Location**: `src/core/models/inventaire.py`
- **Models**:
  - ✅ `ArticleInventaire` (replaces: `Article`)
  - ✅ `HistoriqueInventaire` (replaces: `HistoriqueConsommation`)

### Budget/Expense Models

- **Location**: `src/core/models/maison_extended.py`
- **Models**:
  - ✅ `HouseExpense` (replaces: `Depense`)
  - ❌ `Budget` - Not found, use `FamilyBudget` from users model OR create dates manually
  - ❌ `CategorieDepense` - Found in `budget.py` as Enum (replaces: `CategorieDepense`)

### Shopping/Courses Models

- **Location**: `src/core/models/courses.py`
- **Models**:
  - ✅ `ArticleCourses`
  - ✅ `ModeleCourses`
  - ✅ `ArticleModele`

### Planning Models

- **Location**: `src/core/models/planning.py`
- **Models**:
  - ✅ `Planning`
  - ✅ `Repas` (replaces: `PlanningJour`)

---

## Import Corrections Required

### File: test_phase10_planning_real.py

**Status**: ✅ FIXED

### File: test_phase10_inventory_real.py

**Current**:

```python
from src.core.models.inventaire import Article, StockAlerte, HistoriqueConsommation
```

**Fix To**:

```python
from src.core.models.inventaire import ArticleInventaire, HistoriqueInventaire
```

### File: test_phase10_budget_real.py

**Current**:

```python
from src.core.models.maison_extended import Depense, Budget, CategorieDepense
```

**Fix To**:

```python
from src.core.models.maison_extended import HouseExpense
from src.services.budget import CategorieDepense, BudgetService
# Note: Budget doesn't exist as a model - use HouseExpense + manual date tracking
```

### File: test_phase11_recipes_shopping.py

**Expected issues**:

```python
# May have wrong imports - verify:
# ArticleCourses, ModeleCourses - check these exist in courses.py
```

### File: test_phase12_edge_cases.py

**Expected issues**:

```python
# Likely has same Article + Depense + Budget issues
# Apply same fixes as test_phase10_budget/inventory
```

---

## Quick Action Items

1. **Fix test_phase10_inventory_real.py** (5 min)
   - Replace `Article` → `ArticleInventaire`
   - Replace `HistoriqueConsommation` → `HistoriqueInventaire`
   - Replace `StockAlerte` → check if exists or remove

2. **Fix test_phase10_budget_real.py** (10 min)
   - Replace `Depense` → `HouseExpense`
   - Replace `Budget` → Create manually in tests
   - Keep `CategorieDepense` from service

3. **Fix test_phase11_recipes_shopping.py** (5 min)
   - Verify `ArticleCourses` import
   - Verify `ModeleCourses` import

4. **Fix test_phase12_edge_cases.py** (10 min)
   - Apply same fixes as inventory + budget tests

5. **Run All Tests** (30 min)
   - Execute all PHASE 10-12 tests
   - Measure coverage

---

## Detailed Model Info

### ArticleInventaire

```python
# src/core/models/inventaire.py:36
class ArticleInventaire(Base):
    """Article d'inventaire"""
    # Fields: id, nom, categorie, quantite, unite, prix_unitaire, etc.
```

### HistoriqueInventaire

```python
# src/core/models/inventaire.py:99
class HistoriqueInventaire(Base):
    """Historique des modifications d'inventaire"""
    # Fields: id, article_id, type_operation, quantite, date, etc.
```

### HouseExpense

```python
# src/core/models/maison_extended.py:172
class HouseExpense(Base):
    """Dépense maison (gaz, eau, électricité, etc.)"""
    # Fields: id, categorie, montant, date, mois, annee, etc.
```

### CategorieDepense (from budget.py)

```python
# src/services/budget.py:36+
class CategorieDepense(str, Enum):
    ALIMENTATION = "alimentation"
    COURSES = "courses"
    MAISON = "maison"
    SANTE = "sante"
    TRANSPORT = "transport"
    LOISIRS = "loisirs"
    VETEMENTS = "vetements"
    ENFANT = "enfant"
    SERVICES = "services"
    AUTRE = "autre"
```

### ArticleCourses

```python
# src/core/models/courses.py:37
class ArticleCourses(Base):
    """Article de liste de courses"""
    # Fields: id, nom, quantite, unite, categorie, prix, etc.
```

---

## Timeline

- **Now**: Create mapping document ✅
- **Next**: Fix all 5 test files (25 min)
- **Then**: Run tests & measure coverage (30 min)
- **Result**: Unblock 440+ PHASE 10-12 tests
