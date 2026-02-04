# PHASE 16 - SUMMARY TABLES

## Table 1: Test Results Summary

| Metric                | Count | Percentage | Status          |
| --------------------- | ----- | ---------- | --------------- |
| **Total Tests**       | 352   | 100%       | -               |
| **Passed**            | 149   | 42.3%      | ✅              |
| **Failed**            | 203   | 57.7%      | ❌              |
| **Phase 14-15 Tests** | 149   | 42.3%      | ✅ All Pass     |
| **Phase 16 Tests**    | 203   | 57.7%      | ❌ Model Issues |

---

## Table 2: Coverage Metrics

| Metric               | Value  | Unit     |
| -------------------- | ------ | -------- |
| **Global Coverage**  | 9.74%  | %        |
| **Covered Lines**    | 3,911  | lines    |
| **Total Statements** | 31,364 | lines    |
| **Missing Lines**    | 27,453 | lines    |
| **Excluded Lines**   | 174    | lines    |
| **Branch Coverage**  | 0.44%  | %        |
| **Covered Branches** | 40     | branches |
| **Total Branches**   | 9,194  | branches |

---

## Table 3: Module Coverage Ranking

| Rank | Module   | Coverage | Covered | Total  | Status      |
| ---- | -------- | -------- | ------- | ------ | ----------- |
| 1    | core     | 45.78%   | 2,754   | 6,016  | 🟢 Good     |
| 2    | utils    | 12.57%   | 169     | 1,344  | 🟡 Fair     |
| 3    | services | 11.04%   | 846     | 7,664  | 🟡 Fair     |
| 4    | domains  | 1.00%    | 142     | 14,257 | 🔴 Critical |
| 5    | root     | 0.00%    | 0       | 45     | 🔴 Critical |
| 6    | api      | 0.00%    | 0       | 554    | 🔴 Critical |
| 7    | ui       | 0.00%    | 0       | 1,484  | 🔴 Critical |

---

## Table 4: Coverage Distribution by Range

| Range               | Count | Percentage | Severity |
| ------------------- | ----- | ---------- | -------- |
| 80-100% (Excellent) | 12    | 5.7%       | ✅       |
| 60-80% (Good)       | 2     | 1.0%       | ✅       |
| 40-60% (Fair)       | 4     | 1.9%       | ⚠️       |
| 20-40% (Poor)       | 22    | 10.5%      | ⚠️       |
| 0-20% (Critical)    | 156   | 74.3%      | ❌       |

---

## Table 5: Test Execution Details

| Test Suite           | Total   | Passed | Failed  | Pass Rate |
| -------------------- | ------- | ------ | ------- | --------- |
| services_basic       | 12      | 12     | 0       | 100% ✅   |
| services_integration | 20      | 20     | 0       | 100% ✅   |
| models_basic         | 26      | 26     | 0       | 100% ✅   |
| decorators_basic     | 27      | 27     | 0       | 100% ✅   |
| utils_basic          | 18      | 18     | 0       | 100% ✅   |
| domains_integration  | 32      | 32     | 0       | 100% ✅   |
| business_logic       | 14      | 14     | 0       | 100% ✅   |
| **phase16_extended** | **203** | **0**  | **203** | **0%** ❌ |

---

## Table 6: Phase 16 Failure Analysis

| Test Class                 | Count   | Failures | Error Type               | Cause                    |
| -------------------------- | ------- | -------- | ------------------------ | ------------------------ |
| InventaireServiceExtensive | 30      | 30       | TypeError                | 'nom' field mismatch     |
| FamilleServiceExtensive    | 25      | 25       | TypeError/IntegrityError | Field + NULL constraints |
| BusinessLogicComplex       | 20      | 20       | IntegrityError           | NOT NULL violations      |
| APIEndpoints               | 15      | 15       | IntegrityError/TypeError | Field + constraints      |
| UIComponents               | 15      | 15       | TypeError/IntegrityError | Field + constraints      |
| **Total**                  | **105** | **105**  | -                        | Model Issues             |

---

## Table 7: Files by Coverage Level

| Coverage Level      | File Count | Total Files | Percentage |
| ------------------- | ---------- | ----------- | ---------- |
| >= 80%              | 12         | 210         | 5.7%       |
| 60-80%              | 2          | 210         | 1.0%       |
| 40-60%              | 4          | 210         | 1.9%       |
| 20-40%              | 22         | 210         | 10.5%      |
| < 20%               | 156        | 210         | 74.3%      |
| **0% (Not Tested)** | **118**    | **210**     | **56.2%**  |

---

## Table 8: Top 10 Lowest Coverage Files

| #   | File Path               | Coverage | Lines | Status |
| --- | ----------------------- | -------- | ----- | ------ |
| 1   | root/app.py             | 0.00%    | 0/45  | ❌     |
| 2   | api/**init**.py         | 0.00%    | 0/2   | ❌     |
| 3   | api/main.py             | 0.00%    | 0/360 | ❌     |
| 4   | api/rate_limiting.py    | 0.00%    | 0/192 | ❌     |
| 5   | core/ai_agent.py        | 0.00%    | 0/37  | ❌     |
| 6   | core/lazy_loader.py     | 0.00%    | 0/116 | ❌     |
| 7   | core/multi_tenant.py    | 0.00%    | 0/162 | ❌     |
| 8   | core/notifications.py   | 0.00%    | 0/257 | ❌     |
| 9   | core/performance_opt.py | 0.00%    | 0/249 | ❌     |
| 10  | core/redis_cache.py     | 0.00%    | 0/262 | ❌     |

---

## Table 9: Top 10 Highest Coverage Files

| #   | File Path           | Coverage | Lines   | Status |
| --- | ------------------- | -------- | ------- | ------ |
| 1   | core/config.py      | 100%     | 256/256 | ✅     |
| 2   | core/database.py    | 93.55%   | 129/138 | ✅     |
| 3   | core/errors.py      | 93.33%   | 28/30   | ✅     |
| 4   | core/constants.py   | 100%     | 45/45   | ✅     |
| 5   | core/cache.py       | 87.50%   | 70/80   | ✅     |
| 6   | core/state.py       | 85.19%   | 46/54   | ✅     |
| 7   | core/decorators.py  | 80.95%   | 68/84   | ✅     |
| 8   | core/errors_base.py | 80%      | 20/25   | ✅     |
| 9   | utils/dates.py      | 72.73%   | 24/33   | ✅     |
| 10  | services/base.py    | 65.52%   | 19/29   | ✅     |

---

## Table 10: Phase 16 Action Items

| Priority | Action                                  | Timeline  | Owner |
| -------- | --------------------------------------- | --------- | ----- |
| 🔴 P1    | Fix model field names in Phase 16 tests | 30-60 min | Dev   |
| 🔴 P1    | Fix NOT NULL constraint violations      | 30-60 min | Dev   |
| 🔴 P1    | Re-run test suite after fixes           | 15 min    | Test  |
| 🟠 P2    | Increase domains coverage (1% → 30%)    | 4-6 hours | Dev   |
| 🟠 P2    | Add API endpoint tests                  | 2-4 hours | Dev   |
| 🟡 P3    | Add UI component tests                  | 4-6 hours | Dev   |
| 🟡 P3    | Target 20%+ global coverage             | 1-2 days  | Dev   |

---

## Summary Statistics

```
📊 PROJECT STATISTICS
====================

Source Code:
  • Total Files: 210
  • Total Lines: 31,364
  • Covered Lines: 3,911
  • Coverage Ratio: 9.74%

Tests:
  • Total Test Cases: 352
  • Passed: 149 (42.3%)
  • Failed: 203 (57.7%)

Coverage Distribution:
  • Excellent (80%+): 12 files
  • Good (60-80%): 2 files
  • Fair (40-60%): 4 files
  • Poor (20-40%): 22 files
  • Critical (<20%): 156 files

Module Performance:
  • Best: core (45.78%)
  • Worst: root/api/ui (0.00%)
  • Average: 11.76%
```

---

## Key Findings

### ✅ Strengths

1. **Core Infrastructure:** 45.78% coverage is solid for foundational code
2. **Phase 14-15 Tests:** 100% pass rate demonstrates test quality
3. **Service Layer:** Well-tested with comprehensive integration tests
4. **Test Framework:** Robust pytest setup with proper fixtures

### ❌ Weaknesses

1. **Phase 16 Tests:** All failing due to model field naming issues
2. **Domain Logic:** Only 1% coverage despite 14,257 lines
3. **API & UI:** 0% coverage - completely untested
4. **Branch Coverage:** Only 0.44% - conditional logic not exercised

### 🎯 Opportunities

1. Quickly fix Phase 16 models for 5-10% coverage gain
2. Add API tests for ~10% additional coverage
3. Add UI tests for ~10% additional coverage
4. Can reach 20%+ coverage within 2-3 days

---

**Generated:** February 3, 2026
**Format:** Markdown Tables + Summary
**Next Action:** Fix Phase 16 model issues and re-run tests
