@echo off
REM Script batch pour executer les tests et couverture Phase 16

cd /d "d:\Projet_streamlit\assistant_matanne"

echo.
echo ========================================
echo ETAPE 1: EXECUTION DES TESTS
echo ========================================

python -m pytest ^
  tests/services/test_services_basic.py ^
  tests/services/test_services_integration.py ^
  tests/models/test_models_basic.py ^
  tests/core/test_decorators_basic.py ^
  tests/utils/test_utils_basic.py ^
  tests/integration/test_domains_integration.py ^
  tests/integration/test_business_logic.py ^
  tests/integration/test_phase16_extended.py ^
  --tb=short -q

echo.
echo Code retour tests: %ERRORLEVEL%

echo.
echo ========================================
echo ETAPE 2: MESURE COUVERTURE
echo ========================================

python -m pytest ^
  tests/services/test_services_basic.py ^
  tests/services/test_services_integration.py ^
  tests/models/test_models_basic.py ^
  tests/core/test_decorators_basic.py ^
  tests/utils/test_utils_basic.py ^
  tests/integration/test_domains_integration.py ^
  tests/integration/test_business_logic.py ^
  tests/integration/test_phase16_extended.py ^
  --cov=src ^
  --cov-report=json ^
  --cov-report=term-missing ^
  -q --tb=short

echo.
echo ========================================
echo ETAPE 3: EXTRACTION COUVERTURE
echo ========================================

python -c "
import json
try:
    with open('coverage.json') as f:
        d = json.load(f)
    total_pct = d['totals']['percent_covered']
    baseline = 9.74
    gain = total_pct - baseline
    
    print(f'')
    print(f'PHASE 16 FIXED - RESULTATS')
    print(f'Couverture globale: {total_pct:.2f}%%')
    print(f'Target etait: 14-16%%')
    print(f'Baseline etait: {baseline}%%')
    print(f'Gain: {gain:.2f}%%')
    
    if total_pct >= 14:
        print(f'')
        print(f'SUCCESS: Couverture >= 14%% (realise: {total_pct:.2f}%%)')
    elif total_pct >= 9.74:
        print(f'')
        print(f'PARTIEL: Couverture > baseline mais < 14%% (realise: {total_pct:.2f}%%)')
    else:
        print(f'')
        print(f'FAIL: Couverture < baseline (realise: {total_pct:.2f}%%)')
except Exception as e:
    print(f'ERREUR: {e}')
"

echo.
echo ========================================
echo TERMINE
echo ========================================
pause
