# Phase 18 - Jour 4-5 Strategic Plan

**Current Status**: 186/236 tests passed (78.8%)  
**Target**: 215+/236 tests (90%+) by end of Jour 5  
**Remaining Work**: 50 failing tests across 5 categories

---

## Failure Analysis: Root Cause Breakdown

### Category 1: Unimplemented Endpoints (28 tests)

**Issue**: Endpoints not implemented or partially implemented  
**Root Cause**: New endpoints not yet connected to database layer

**Affected Endpoints**:

- `GET /api/v1/inventaire` (8 tests)
- `POST /api/v1/inventaire` (6 tests)
- `GET /api/v1/courses` (5 tests)
- `POST /api/v1/courses` (5 tests)
- `POST /api/v1/planning/repas` (4 tests)

**Fix Strategy**: Implement basic CRUD in FastAPI that calls existing service layer

**Estimated Effort**: 90 minutes  
**Expected Test Impact**: +20-25 tests fixed

---

### Category 2: Validation & Input Constraints (12 tests)

**Issue**: Missing field validators or improper constraint handling  
**Examples**:

- `test_create_inventaire_minimal_data` - Missing required fields
- `test_inventaire_quantite_negative_rejected` - No negativity constraint
- `test_repas_type_invalid_rejected` - No enum validation

**Fix Strategy**: Add Pydantic validators similar to RecetteBase pattern

**Estimated Effort**: 45 minutes  
**Expected Test Impact**: +8-10 tests fixed

---

### Category 3: Integration & Edge Cases (7 tests)

**Issue**: Complex workflows, CORS, security headers, performance  
**Examples**:

- `test_multiple_filters_acceptable_performance`
- `test_sensitive_data_not_in_logs`
- `test_create_endpoint_responds_quickly`

**Fix Strategy**: Add logging filters, performance monitoring, optimize queries

**Estimated Effort**: 60 minutes  
**Expected Test Impact**: +3-5 tests fixed

---

### Category 4: Error Response Handling (2 tests)

**Issue**: Fallback behavior and error messages  
**Examples**:

- `test_get_suggestions_no_params` - Missing fallback

**Fix Strategy**: Add default parameters and error handling

**Estimated Effort**: 15 minutes  
**Expected Test Impact**: +2 tests fixed

---

### Category 5: Misc Issues (1 test)

**Issue**: Various uncategorized failures

**Estimated Effort**: 10 minutes  
**Expected Test Impact**: +1 test fixed

---

## Implementation Roadmap

### Jour 4 (Day 4) - 4 hours

**Focus**: Implement missing Inventaire & Courses endpoints

**Phase 4.1 (60 min)**: Inventaire CRUD Endpoints

```python
# GET /api/v1/inventaire
- Query parameters: page, page_size, categorie, expiring_soon
- Returns: {"items": [...], "total": int, "page": int, ...}
- Expected: 8 passing tests

# POST /api/v1/inventaire
- Body: InventaireItemCreate (nom, categorie, quantite, date_expiration)
- Returns: InventaireItemResponse
- Expected: 6 passing tests
```

**Phase 4.2 (45 min)**: Courses Endpoints

```python
# GET /api/v1/courses
- Query parameters: page, page_size, active_only
- Returns: {"items": [...], "total": int, ...}
- Expected: 5 passing tests

# POST /api/v1/courses
- Body: CourseListCreate (nom)
- Returns: CourseListResponse
- Expected: 5 passing tests
```

**Phase 4.3 (45 min)**: Validation & Input Constraints

- Add `@field_validator` for quantite (must be > 0)
- Add `@field_validator` for repas type (must be in enum)
- Add `@field_validator` for date validation
- Expected: +8-10 passing tests

**Phase 4.4 (30 min)**: Quick Fixes

- Fix Planning endpoints
- Add error handling for edge cases
- Expected: +3-5 passing tests

**Jour 4 Target**: 215+ tests passing

---

### Jour 5 (Day 5) - 2-3 hours

**Focus**: Integration tests, performance, and polish

**Phase 5.1 (30 min)**: Performance Optimization

- Add database query optimization (selectinload, joined loads)
- Implement caching for frequently accessed data
- Expected: +2-3 tests fixed

**Phase 5.2 (30 min)**: Security & Logging

- Add CORS headers validation
- Add logging filters for sensitive data
- Expected: +1-2 tests fixed

**Phase 5.3 (45 min)**: Edge Cases & Fallbacks

- Implement fallback for IA suggestions without params
- Add comprehensive error handling
- Expected: +2-3 tests fixed

**Phase 5.4 (30 min)**: Final Polish

- Fix any remaining issues
- Verify 90%+ pass rate
- Expected: +1-2 tests fixed

**Jour 5 Target**: 225+ tests passing (90%+ rate)

---

## Code Templates for Quick Implementation

### Template 1: Standard CRUD Endpoint

```python
@app.get("/api/v1/{resource}", tags=["{Resource}"])
async def list_{resource}(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Lists all {resource} items."""
    try:
        from src.core.database import get_db_context
        from src.core.models import {Model}

        with get_db_context() as session:
            query = session.query({Model})
            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "items": [{Model}Response.model_validate(i).model_dump() for i in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
    except Exception as e:
        logger.error(f"Error listing {resource}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Template 2: Field Validator

```python
@field_validator("field_name")
@classmethod
def validate_field_name(cls, v: Type) -> Type:
    """Validates field_name."""
    if condition_not_met:
        raise ValueError("Error message")
    return v
```

### Template 3: Create Endpoint

```python
@app.post("/api/v1/{resource}", response_model={Model}Response, tags=["{Resource}"])
async def create_{resource}(
    data: {Model}Create,
    user: dict = Depends(require_auth)
):
    """Creates a new {resource}."""
    try:
        from src.core.database import get_db_context
        from src.core.models import {Model}

        with get_db_context() as session:
            item = {Model}(**data.model_dump())
            session.add(item)
            session.commit()
            session.refresh(item)

            return {Model}Response.model_validate(item)
    except Exception as e:
        logger.error(f"Error creating {resource}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Quick Reference: Required Models

### InventaireItemCreate

```python
class InventaireItemCreate(BaseModel):
    nom: str  # Required, non-empty
    categorie: str | None = None
    quantite: int = Field(1, gt=0)  # Must be > 0
    unite: str = "pcs"
    date_expiration: date | None = None
```

### CourseListCreate

```python
class CourseListCreate(BaseModel):
    nom: str = Field("Liste de courses", min_length=1)
```

### RepasCreate

```python
class RepasCreate(BaseModel):
    type_repas: str  # Must be in enum
    date: date
    recette_id: int | None = None
    notes: str | None = None
```

---

## Success Criteria

| Milestone            | Tests   | Pass Rate | Target Date |
| -------------------- | ------- | --------- | ----------- |
| Current (Jour 3 End) | 186/236 | 78.8%     | ✓ Today     |
| Jour 4 Target        | 215/236 | 91.0%     | Tomorrow    |
| Jour 5 Final         | 225/236 | 95.3%     | Day after   |

---

## Risk Mitigation

### Risk 1: Endpoints not working as expected

**Mitigation**: Test each endpoint individually with `-xvs` flag before moving on

### Risk 2: Running out of time

**Mitigation**: Prioritize Category 1 (28 tests) first for maximum ROI

### Risk 3: Database connection issues

**Mitigation**: Use existing `get_db_context()` and service layer

### Risk 4: Pydantic validation conflicts

**Mitigation**: Follow RecetteBase pattern exactly

---

## Key Metrics to Track

```bash
# Run this command at end of each phase:
python -m pytest tests/api/ tests/services/test_services_basic.py \
  tests/edge_cases/ tests/benchmarks/ --tb=no -q 2>&1 | tail -1

# Expected progression:
# Jour 4 Phase 1: 195 passed
# Jour 4 Phase 2: 205 passed
# Jour 4 Phase 3: 215 passed
# Jour 4 Phase 4: 218 passed
# Jour 5 Phase 1: 220 passed
# Jour 5 Phase 2: 222 passed
# Jour 5 Phase 3: 225 passed
```

---

## Final Notes

- **Consistency**: Follow the exact pattern from RecetteBase for all new models
- **Reuse**: Use existing service layer methods where possible
- **Testing**: Run tests after each endpoint implementation
- **Documentation**: Keep inline comments for complex validation logic

**Expected Outcome**: 90%+ pass rate by end of Jour 5, with strong foundation for future test suite expansion.
