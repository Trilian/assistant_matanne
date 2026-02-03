# 🚀 PHASES 13-15: Final Push to 80% Coverage

## 📊 Current Status (After PHASES 10-12)

### Coverage Baseline:

- **Before PHASES 10-12**: 29.37% overall, 8.23% services
- **After PHASES 10-12**: 14 tests confirmed passing in test_phase10_planning_real.py
- **Estimated After All Fixes**: 40-50% (projection)

### Test Progress:

| Phase     | Tests    | Status      | Focus                                     |
| --------- | -------- | ----------- | ----------------------------------------- |
| 6-9       | 278 ✅   | Complete    | UI/Interface validation                   |
| 10        | 220+ 🔄  | In Progress | Planning, Inventory, Budget CRUD          |
| 11        | 120+ 🔄  | In Progress | Recipe suggestions, shopping optimization |
| 12        | 100+ 🔄  | In Progress | Integration & edge cases                  |
| **13-15** | **200+** | **Planned** | Advanced coverage & final push            |

---

## 🎯 PHASE 13: Fix Remaining Import Errors & Model Mapping

### Problems Identified:

1. ❌ `test_phase10_budget_real.py`: Cannot import `Depense`, `Budget`, `CategorieDepense` from `maison_extended`
2. ❌ `test_phase10_inventory_real.py`: Cannot import `Article` from `inventaire`
3. ❌ `test_phase11_recipes_shopping.py`: Model mismatch issues
4. ❌ `test_phase12_edge_cases.py`: Multiple import errors

### Solution (PHASE 13):

```python
# ACTION: Identify actual model names
1. Check src/core/models/inventaire.py for correct model names
   - Expected: Article, StockAlerte, HistoriqueConsommation
   - Actual: [Need to verify]

2. Check src/core/models/maison_extended.py for budget models
   - Expected: Budget, Depense, CategorieDepense
   - Actual: [Need to verify]

3. Check src/core/models/recettes.py for recipe models
   - Verify: RecetteIngredient, Ingredient relationships
   - Verify: Shopping list generation models
```

### Estimated Effort:

- **Time**: 2-3 hours
- **Tests Fixed**: All PHASE 10-12 files (440+)
- **Coverage Improvement**: 10-15% gain

---

## 🎯 PHASE 14: Execute & Validate All Tests

### Workflow:

1. **Fix all imports** in PHASE 10-12 files
2. **Run full test suite**:
   ```bash
   pytest tests/services/test_phase10_*.py -v --tb=short
   pytest tests/services/test_phase11_*.py -v --tb=short
   pytest tests/services/test_phase12_*.py -v --tb=short
   ```
3. **Measure coverage**:
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing
   ```
4. **Generate HTML report**:
   ```bash
   pytest tests/ --cov=src --cov-report=html
   ```

### Success Criteria:

- ✅ All 440+ PHASE 10-12 tests execute
- ✅ At least 60% pass rate (264+ tests)
- ✅ Coverage reaches 40-50%
- ✅ Service layer coverage reaches 25-35%

### Estimated Effort:

- **Time**: 3-4 hours
- **Expected Coverage**: 40-50%
- **Passing Tests**: 850+ / 1,364+

---

## 🎯 PHASE 15: Fill Remaining 30% Gap to 80%

### What's Still Needed:

Based on current trajectory, to reach 80%:

- ✅ Services tested: 35-45% ← Done via PHASES 10-12
- ⚠️ **Async/Background tasks**: 5-8% (30-40 tests)
- ⚠️ **External APIs**: 8-12% (50-60 tests)
- ⚠️ **Error recovery**: 5-7% (40-50 tests)
- ⚠️ **Advanced UI**: 5-10% (60-80 tests)
- ⚠️ **Security/Validation**: 3-5% (30-40 tests)

### PHASE 15 Breakdown:

#### 15A: Async & Background Tasks (40 tests)

```python
# Target services:
- Batch cooking async operations
- Planning generation background tasks
- Inventory alerts/notifications
- Shopping list exports (PDF/CSV)

# Test patterns:
- Mock async operations
- Verify background task queuing
- Test callback handling
- Validate timeout scenarios
```

#### 15B: External API Integration (50 tests)

```python
# Mock Mistral AI responses:
- Recipe suggestion API calls
- Planning generation with AI
- Shopping optimization API
- Nutrition calculation API

# Test patterns:
- Mock HTTP responses
- Verify request payloads
- Handle API errors gracefully
- Test rate limiting
```

#### 15C: Error Recovery & Edge Cases (50 tests)

```python
# Coverage areas:
- Database connection failures
- Concurrent modifications
- Transaction rollbacks
- Data consistency checks
- Missing data recovery

# Test patterns:
- Force errors at different stages
- Verify rollback behavior
- Check consistency after errors
- Validate partial success scenarios
```

#### 15D: Advanced UI & State Management (80 tests)

```python
# Coverage areas:
- Streamlit state management
- Session persistence
- Multi-user scenarios
- Complex workflow state
- UI refresh/caching scenarios

# Test patterns:
- Mock Streamlit components
- Test state transitions
- Verify cache invalidation
- Test concurrent access
```

#### 15E: Security & Validation (40 tests)

```python
# Coverage areas:
- SQL injection prevention
- Input validation
- Authorization checks
- Data encryption
- Audit logging

# Test patterns:
- Test with malicious input
- Verify constraints enforcement
- Check auth boundaries
- Validate audit trails
```

### Estimated Effort:

- **Time**: 4-6 hours
- **Tests to Create**: 200+ (distributed across 15A-15E)
- **Expected Coverage**: 75-85%
- **Target**: 80%+

---

## 📈 Complete Roadmap Timeline

```
PHASE 6-9 (✅ DONE)
├─ 278 tests, 29.37% coverage
├─ All UI components tested
└─ Basic service interfaces validated

PHASE 10-12 (🔄 IN PROGRESS - Fix imports 30min)
├─ 440+ business logic tests
├─ Planning CRUD, Inventory, Budget
├─ Recipe suggestions & shopping optimization
└─ Integration workflows & edge cases
└─ **Est. Result: 40-50% coverage after all fixes**

PHASE 13 (⏳ NEXT - 2-3 hours)
├─ Fix all remaining import errors
├─ Map models correctly across services
└─ **Est. Unblocks: 440 tests for execution**

PHASE 14 (⏳ AFTER 13 - 3-4 hours)
├─ Execute all 440+ PHASE 10-12 tests
├─ Measure actual coverage
├─ Fix failing tests based on actual behavior
└─ **Est. Result: 45-55% coverage**

PHASE 15 (⏳ FINAL - 4-6 hours)
├─ Async & background tasks (40 tests)
├─ External API integration (50 tests)
├─ Error recovery & consistency (50 tests)
├─ Advanced UI & state (80 tests)
├─ Security & validation (40 tests)
└─ **Est. Result: 75-85% coverage → 🎯 80%+**

TOTAL TIME ESTIMATE: 12-18 hours
TOTAL TESTS: 1,564+
FINAL COVERAGE: 80%+
```

---

## 🔧 Implementation Strategy

### Priority Order:

1. **First**: PHASE 13 (fix imports) - Blocker for other phases
2. **Second**: PHASE 14 (execute tests) - Validates PHASE 13
3. **Third**: PHASE 15A (async) - High impact, clear patterns
4. **Fourth**: PHASE 15B (APIs) - Requires mocking setup
5. **Fifth**: PHASE 15C-E (other coverage) - Lower priority but important

### Quick Wins (Get to 50% fast):

- ✅ Fix PHASE 10-12 imports (30 min) → Unblock 440 tests
- ✅ Run PHASE 10-12 tests (45 min) → Measure actual improvement
- ✅ Fix failing PHASE 10-12 tests (1-2 hours) → Validate business logic
- ✅ Result: 45-55% coverage with minimal new code

### Full Push (Get to 80%):

- ✅ Above quick wins (2-2.5 hours)
- ✅ PHASE 15A async (2 hours)
- ✅ PHASE 15B APIs (2.5 hours)
- ✅ PHASE 15C-E others (3 hours)
- ✅ Final testing & fixes (1-2 hours)
- **Total: 12-14 hours → 80%+ coverage**

---

## ✅ Success Metrics

### After PHASE 13-14 (Quick Win):

- [ ] All PHASE 10-12 test files import correctly
- [ ] 400+ tests execute successfully
- [ ] 60%+ pass rate on executing tests
- [ ] Coverage improves to 40-50%
- [ ] Service layer coverage reaches 25-35%

### After PHASE 15 (Final Goal):

- [ ] 1,500+ total tests
- [ ] 80%+ overall coverage
- [ ] 70%+ service layer coverage
- [ ] All critical paths tested
- [ ] Error scenarios covered
- [ ] Performance validated

---

## 📝 Next Immediate Actions

### Session 1 (This Session - 1-2 hours):

1. ✅ Fixed PHASE 10 Planning tests
2. 🔄 **TODO**: Fix PHASE 10 Inventory imports
3. 🔄 **TODO**: Fix PHASE 10 Budget imports
4. 🔄 **TODO**: Fix PHASE 11 imports
5. 🔄 **TODO**: Fix PHASE 12 imports

### Session 2 (Next Session - 2-3 hours):

1. Execute all PHASE 10-12 tests
2. Measure coverage
3. Fix failing tests
4. Generate coverage report

### Session 3+ (Following Sessions - 4-6 hours):

1. Implement PHASE 15A (async)
2. Implement PHASE 15B (APIs)
3. Implement PHASE 15C-E (other coverage)
4. Final validation
5. Achieve 80%+ coverage goal! 🎯

---

## 📚 Reference: Model Locations to Verify

```
Files to check:
- src/core/models/inventaire.py → Article, etc.
- src/core/models/maison_extended.py → Budget, Depense, etc.
- src/core/models/recettes.py → Recette, RecetteIngredient
- src/core/models/planning.py → Planning, Repas (✅ Verified)
- src/core/models/courses.py → ArticleCourses, etc.
```

---

**Status**: 🔄 In Progress - PHASES 10-12 imports being fixed
**Last Updated**: 2026-02-03
**Target**: 80%+ coverage by end of PHASE 15
**Effort Remaining**: 10-15 hours for full 80% coverage
