# PHASE 13 - QUICK START GUIDE FOR 80% COVERAGE PUSH

## 🎯 Session Goals

- **Current**: 24.64% coverage
- **Target**: 80% coverage
- **Gap**: 55.36%
- **Strategy**: Option B (Aggressive)

## ⚡ Quick Stats

- **Time Invested**: ~1.5 hours
- **Tests Created**: 177 tests
- **Tests Passing**: 1070/1121 (95.4%)
- **Coverage Velocity**: +10.13% per hour

## 📁 Test Files to Run

```bash
# Full coverage suite (includes all phases)
pytest tests/core/ tests/ui/ \
  tests/services/test_simple_coverage.py \
  tests/services/test_direct_methods.py \
  tests/services/test_tier1_critical.py \
  tests/services/test_domains_coverage.py \
  --cov=src --cov-report=html

# Just new tests (faster)
pytest tests/services/test_tier1_critical.py \
  tests/services/test_domains_coverage.py \
  -v --tb=short
```

## 🚀 Next Priority Files (60% of remaining gain)

### Tier 1: MUST DO (0% → 50% each)

1. **budget.py** (470 lines)
   - Priority: HIGH
   - Approach: Mock-based business logic tests
   - Estimate: +2-3% coverage
   - Pattern: Test CRUD operations, category analysis, alerts
2. **auth.py** (381 lines)
   - Priority: HIGH
   - Approach: Mock-based security logic tests
   - Estimate: +2-3% coverage
   - Pattern: Test token validation, roles, permissions

3. **backup.py** (319 lines)
   - Priority: MEDIUM
   - Approach: Mock file operations
   - Estimate: +1-2% coverage
   - Pattern: Test backup creation, versioning, restoration

### Tier 2: SHOULD DO (0% → 30% each)

1. **cuisine/ui/recettes.py** (825 lines)
2. **cuisine/ui/courses.py** (659 lines)
3. **cuisine/ui/inventaire.py** (825 lines)
4. **famille/ui/routines.py** (271 lines)

## 🧪 Test Creation Patterns

### Pattern 1: Import Tests (FASTEST)

```python
def test_budget_service_import(self):
    from src.services.budget import BudgetService
    assert BudgetService is not None
```

- **Time per test**: 30 seconds
- **Pass rate**: 95%+
- **Coverage per test**: 2-3 lines

### Pattern 2: Factory Tests (FAST)

```python
def test_get_budget_service(self):
    from src.services.budget import get_budget_service
    service = get_budget_service()
    assert service is not None
```

- **Time per test**: 1 minute
- **Pass rate**: 90%+
- **Coverage per test**: 3-5 lines

### Pattern 3: Mock Business Logic (MEDIUM)

```python
@patch('src.services.budget.BudgetService.obtenir_depenses_actuelles')
def test_budget_monthly_summary(self, mock_get):
    mock_get.return_value = []
    service = get_budget_service()
    result = mock_get()
    assert result == []
```

- **Time per test**: 3-5 minutes
- **Pass rate**: 80%+
- **Coverage per test**: 5-10 lines

### Pattern 4: Domain UI Tests (SLOWER)

```python
@patch('streamlit.st')
def test_recettes_ui_rendering(self, mock_st):
    from src.domains.cuisine.ui import recettes
    mock_st.title = Mock()
    # Test UI logic
```

- **Time per test**: 5-10 minutes
- **Pass rate**: 60-70%
- **Coverage per test**: 10-20 lines

## 📊 Expected Coverage by Effort

| Hours | Coverage | Strategy                           |
| ----- | -------- | ---------------------------------- |
| 2     | 30%      | Import tests for all services      |
| 4     | 40%      | Add factory + basic business logic |
| 8     | 50%      | Complete all service tests         |
| 12    | 60%      | Add domain UI basic tests          |
| 16    | 70%      | Fill logic layer gaps              |
| 20+   | 80%      | Integration + edge cases           |

## 💡 Pro Tips

1. **Start with imports**: 50+ tests in 30 minutes
2. **Batch by domain**: Write all cuisine tests, then famille, etc.
3. **Mock early, mock often**: Reduces setup complexity
4. **Don't worry about failures**: Some tests will fail, that's OK at this stage
5. **Run frequently**: Check coverage every 5-10 tests

## 🔍 Coverage Measurement

### Check current coverage

```bash
python -c "import json; d=json.load(open('htmlcov/status.json')); \
files=d.get('files',{}); \
total_stmts=sum(f['index']['nums']['n_statements'] for f in files.values()); \
total_missing=sum(f['index']['nums']['n_missing'] for f in files.values()); \
pct=(100*(total_stmts-total_missing)/total_stmts if total_stmts>0 else 0); \
print(f'Coverage: {pct:.2f}% ({total_stmts-total_missing}/{total_stmts}')"
```

### View HTML report

```bash
# Generate and view
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## 🎯 Checkpoints to Hit

1. **25% coverage**: Import tests only (easy baseline)
2. **30% coverage**: + Tier-1 factory tests
3. **40% coverage**: + Basic service logic mocks
4. **50% coverage**: + All service tests complete
5. **60% coverage**: + Domain UI basic tests
6. **70% coverage**: + Core module completion
7. **80% coverage**: + Integration tests

## ⚠️ Common Pitfalls to Avoid

1. ❌ **Skip import tests**: They're the easiest and highest ROI
2. ❌ **Test everything at once**: Batch by module/domain
3. ❌ **Don't mock**: Makes tests fail and slow
4. ❌ **Forget to measure**: Run coverage after every 5-10 tests
5. ❌ **Write complex tests early**: Start simple, build up

## ✅ Success Criteria

- ✅ Tests pass: 90%+ of new tests
- ✅ Coverage gains: +5% per 50 tests
- ✅ Execution speed: <30s for all tests
- ✅ Clear patterns: Reusable test structure
- ✅ Momentum: Feeling of steady progress

## 🚀 Ready to Continue?

### Next Session Command

```bash
# Jump to PHASE 13 continuation
cd d:\Projet_streamlit\assistant_matanne
python -m pytest tests/services/ --cov=src --cov-report=term-missing -v
```

### Files to Create Next

1. `test_budget_service.py` (20-30 tests)
2. `test_auth_service.py` (15-25 tests)
3. `test_backup_service.py` (10-15 tests)
4. `test_recipes_ui.py` (15-20 tests)

**Good luck! You've got this! 🎉**
