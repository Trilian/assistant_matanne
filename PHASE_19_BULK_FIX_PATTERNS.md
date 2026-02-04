# Phase 19 Bulk Fix Patterns - Method Signature Mapping

## PATTERN 1: Service Creation Method

### Before (Incorrect - current test code)
```python
def test_add_basic_expense(self, budget_service):
    """Record basic household expense"""
    data = {
        "description": "Courses",
        "montant": 50.75,
        "categorie": "ALIMENTATION",
        "date": datetime.now().date()
    }
    result = budget_service.create(data)
    
    assert result is not None
    assert result.montant == 50.75
```

### After (Correct - actual service method)
```python
def test_add_basic_expense(self, budget_service, db):
    """Record basic household expense"""
    from src.core.models import Depense
    
    depense = Depense(
        description="Courses",
        montant=50.75,
        categorie="ALIMENTATION",
        date=datetime.now().date()
    )
    
    result = budget_service.ajouter_depense(depense, db)
    
    assert result is not None
    assert result.montant == 50.75
```

### Bulk Replacement Command
```python
# Step 1: Replace method call
old = 'result = budget_service.create(data)'
new = 'result = budget_service.ajouter_depense(depense, db)'

# Step 2: Replace data dict construction with ORM model
old = '''data = {
            "description": .+?,
            "montant": .+?,
            "categorie": .+?,
            "date": .+?
        }'''
new = '''depense = Depense(
            description=...,
            montant=...,
            categorie=...,
            date=...
        )'''

# Step 3: Add db parameter to test function
old = 'def test_add_.*\(self, budget_service\):'
new = 'def test_add_.*\(self, budget_service, db\):'

# Step 4: Add import at top of test class
old = 'class TestBudgetExpensesCreate:'
new = 'class TestBudgetExpensesCreate:\n    from src.core.models import Depense\n'
```

---

## PATTERN 2: Get/Read Methods

### Before
```python
def test_get_expense_by_id(self, budget_service):
    created = budget_service.create({
        "description": "Test",
        "montant": 50,
        "categorie": "AUTRE",
        "date": datetime.now().date()
    })
    
    result = budget_service.get_by_id(created.id)
    
    assert result.montant == 50
```

### After
```python
def test_get_expense_by_id(self, budget_service, db):
    from src.core.models import Depense
    
    depense = Depense(
        description="Test",
        montant=50,
        categorie="AUTRE",
        date=datetime.now().date()
    )
    depense_created = budget_service.ajouter_depense(depense, db)
    
    # Use get_depenses_mois to retrieve by filtering
    result = [d for d in budget_service.get_depenses_mois(
        depense_created.date.month, 
        depense_created.date.year, 
        db
    ) if d.id == depense_created.id]
    
    assert len(result) > 0
    assert result[0].montant == 50
```

### Service Method Reference
```python
# Available in BudgetService:
def get_depenses_mois(self, mois: int, annee: int, db: Session = None) -> list[Depense]
def get_resume_mensuel(self, mois: int, annee: int, db: Session = None) -> dict
```

---

## PATTERN 3: Update Methods

### Before
```python
def test_update_expense_amount(self, budget_service):
    created = budget_service.create({...})
    result = budget_service.update(created.id, {"montant": 75})
    assert result.montant == 75
```

### After
```python
def test_update_expense_amount(self, budget_service, db):
    # Create original
    depense = Depense(...)
    created = budget_service.ajouter_depense(depense, db)
    
    # Update
    success = budget_service.modifier_depense(
        created.id, 
        {"montant": 75}, 
        db
    )
    
    assert success is True
    
    # Verify by re-fetching
    updated = [d for d in budget_service.get_depenses_mois(
        created.date.month,
        created.date.year,
        db
    ) if d.id == created.id][0]
    
    assert updated.montant == 75
```

### Service Method Reference
```python
def modifier_depense(self, depense_id: int, updates: dict, db: Session = None) -> bool
```

---

## PATTERN 4: Delete Methods

### Before
```python
def test_delete_expense(self, budget_service):
    created = budget_service.create({...})
    result = budget_service.delete(created.id)
    assert result is True
```

### After
```python
def test_delete_expense(self, budget_service, db):
    # Create
    depense = Depense(...)
    created = budget_service.ajouter_depense(depense, db)
    
    # Delete
    success = budget_service.supprimer_depense(created.id, db)
    assert success is True
    
    # Verify deletion
    remaining = [d for d in budget_service.get_depenses_mois(
        created.date.month,
        created.date.year,
        db
    ) if d.id == created.id]
    
    assert len(remaining) == 0
```

### Service Method Reference
```python
def supprimer_depense(self, depense_id: int, db: Session = None) -> bool
```

---

## PATTERN 5: Fixture Parameter Fix

### Before (test_maison_extended.py - FIXED)
```python
@pytest.fixture
def budget_service(db: Session):
    """Create budget service instance"""
    return get_budget_service(db)  # ❌ get_budget_service() takes 0 args
```

### After (test_maison_extended.py - NOW CORRECT)
```python
@pytest.fixture
def budget_service():
    """Create budget service instance"""
    return get_budget_service()  # ✅ Correct
```

### Apply to test_planning_extended.py
```python
# BEFORE
@pytest.fixture
def planning_service(db: Session):
    return get_planning_service(db)

# AFTER
@pytest.fixture
def planning_service():
    return get_planning_service()

# Also update test methods to include db parameter where needed
# BEFORE
def test_create_planning(self, planning_service):
    result = planning_service.create(...)

# AFTER
def test_create_planning(self, planning_service, db):
    result = planning_service.ajouter_planning(..., db)
```

---

## PATTERN 6: Multi-Replace Implementation

### Using multi_replace_string_in_file Tool

```python
# Example for test_maison_extended.py
replacements = [
    {
        "filePath": "tests/services/test_maison_extended.py",
        "oldString": """    def test_add_basic_expense(self, budget_service):
        \"\"\"Record basic household expense\"\"\"
        data = {
            "description": "Courses",
            "montant": 50.75,
            "categorie": "ALIMENTATION",
            "date": datetime.now().date()
        }
        result = budget_service.create(data)
        
        assert result is not None
        assert result.montant == 50.75""",
        "newString": """    def test_add_basic_expense(self, budget_service, db):
        \"\"\"Record basic household expense\"\"\"
        from src.core.models import Depense
        
        depense = Depense(
            description="Courses",
            montant=50.75,
            categorie="ALIMENTATION",
            date=datetime.now().date()
        )
        result = budget_service.ajouter_depense(depense, db)
        
        assert result is not None
        assert result.montant == 50.75""",
        "explanation": "Fix test_add_basic_expense to use correct service method"
    },
    # ... more replacements
]
```

---

## Implementation Priority

### Phase 19 - Day 1 (2-3 hours)

1. **Fix Fixtures** (15 min)
   - test_planning_extended.py: Remove db parameter from fixtures
   - test_tier1_critical.py: Check for same pattern

2. **Fix test_maison_extended CRUD** (45 min)
   - ~30 tests use generic create/get_by_id/update/delete pattern
   - Apply patterns 1-4 above
   - Use multi_replace for bulk application

3. **Validate** (15 min)
   - Run: `pytest tests/services/test_maison_extended.py -q`
   - Expected: 30+ tests should go from XFAIL to PASS

4. **Fix test_tier1_critical CRUD** (60 min)
   - ~39 auto-generated tests
   - Apply same patterns 1-4
   - May need individual adjustments for some tests

---

## Testing the Patterns

### Quick Validation Script
```python
# Save as test_pattern_validation.py
import pytest
from datetime import datetime
from src.services.budget import get_budget_service
from src.core.models import Depense

def test_pattern_1_create(db):
    """Validate Pattern 1: Create method works"""
    service = get_budget_service()
    
    depense = Depense(
        description="Test",
        montant=50.0,
        categorie="ALIMENTATION",
        date=datetime.now().date()
    )
    
    result = service.ajouter_depense(depense, db)
    
    assert result is not None
    assert result.montant == 50.0
    assert result.description == "Test"

def test_pattern_2_read(db):
    """Validate Pattern 2: Read method works"""
    service = get_budget_service()
    
    # Create
    depense = Depense(
        description="Test",
        montant=75.0,
        categorie="ENERGIE",
        date=datetime.now().date()
    )
    created = service.ajouter_depense(depense, db)
    
    # Read
    results = service.get_depenses_mois(
        created.date.month,
        created.date.year,
        db
    )
    
    assert len(results) > 0
    found = [r for r in results if r.id == created.id]
    assert len(found) == 1
    assert found[0].montant == 75.0

# Run validation
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Success Criteria

After applying these patterns:

1. ✅ test_maison_extended.py: 30+ XFAIL → PASS (currently 6 XPASS)
2. ✅ test_planning_extended.py: Fixtures fixed, 2+ XPASS
3. ✅ test_tier1_critical.py: 20+ XFAIL → PASS
4. ✅ Week 1 endpoints: Still 78/78 PASS (no regression)
5. ✅ Overall pass rate: **91.2% → 94%+**

---

## Common Pitfalls to Avoid

1. **Don't forget to import Depense in test files**
   - Pattern shows this, but easy to miss

2. **Service methods take db parameter**
   - `ajouter_depense(depense, db=None)` - db is keyword arg
   - Can be passed positionally or by name

3. **Some tests might need different service methods**
   - Test `get_all_expenses` won't use `get_depenses_mois` directly
   - May need query-based verification instead

4. **Date filtering can be tricky**
   - Tests that check "this month" need to match actual dates
   - Use `datetime.now()` consistently to avoid date mismatches

5. **Transaction scope matters**
   - Some operations might need `db.flush()` before assertions
   - If tests fail with "not found", try adding flush

---

## Questions for Phase 19

If new patterns emerge that don't match these, document them in a PHASE_19_PATTERNS.md file for Phase 20 reference.

Common questions likely to arise:
- Q: What if service method returns different type than test expects?
  A: Check service method signature, adjust assertion
  
- Q: What if test needs multiple services?
  A: Add more fixtures, follow same pattern
  
- Q: How to handle cascade deletes?
  A: Use `db.flush()` and refresh objects before checking state

---

## Final Checklist

Before starting Phase 19:
- [ ] Save this file to project root
- [ ] Confirm Week 1 endpoints at 100%
- [ ] Review PHASE_18_SUMMARY.md
- [ ] Review PHASE_19_QUICK_WINS.md
- [ ] Copy test_pattern_validation.py logic into tests
- [ ] Run `python strategic_test_sampling.py` to confirm baseline
- [ ] Ready to apply patterns!

Good luck! 🚀
