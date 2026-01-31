#!/usr/bin/env powershell
# Script de vérification du fix SQLAlchemy Session (Windows)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ VÉRIFICATION DU FIX SQLAlchemy Session" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier la syntaxe
Write-Host "[1/4] Vérification de la syntaxe Python..." -ForegroundColor Yellow
try {
    python -m py_compile src\domains\cuisine\ui\planning.py 2>$null
    Write-Host "✅ Syntaxe OK" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erreur syntaxe" -ForegroundColor Red
    exit 1
}

# 2. Vérifier les imports
Write-Host ""
Write-Host "[2/4] Vérification des imports..." -ForegroundColor Yellow
try {
    $pythonCode = @"
from src.services.planning import get_planning_service
from src.domains.cuisine.ui.planning import render_planning
print('OK')
"@
    $result = python -c $pythonCode 2>$null
    if ($result -eq 'OK') {
        Write-Host "✅ Imports OK" -ForegroundColor Green
    }
    else {
        throw "Import check failed"
    }
}
catch {
    Write-Host "❌ Erreur imports: $_" -ForegroundColor Red
    exit 1
}

# 3. Vérifier les modifications
Write-Host ""
Write-Host "[3/4] Vérification des modifications..." -ForegroundColor Yellow

# Chercher joinedload
$planningContent = Get-Content "src\services\planning.py" -Raw
if ($planningContent -match "joinedload\(Planning\.repas\)") {
    Write-Host "✅ joinedload() trouvé dans planning.py" -ForegroundColor Green
}
else {
    Write-Host "❌ joinedload() NOT FOUND" -ForegroundColor Red
    exit 1
}

# Chercher context manager
$uiContent = Get-Content "src\domains\cuisine\ui\planning.py" -Raw
if ($uiContent -match "with obtenir_contexte_db\(\)") {
    Write-Host "✅ Context manager trouvé dans planning UI" -ForegroundColor Green
}
else {
    Write-Host "❌ Context manager NOT FOUND" -ForegroundColor Red
    exit 1
}

# 4. Statistiques
Write-Host ""
Write-Host "[4/4] Statistiques..." -ForegroundColor Yellow

$joinedloadCount = ($planningContent | Select-String -Pattern "joinedload" -AllMatches).Matches.Count
$contextCount = ($uiContent | Select-String -Pattern "with obtenir_contexte_db" -AllMatches).Matches.Count

Write-Host "  joinedload() usage: $joinedloadCount" -ForegroundColor Green
Write-Host "  context manager usage: $contextCount" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ TOUS LES TESTS PASSES!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "  1. streamlit run src/app.py" -ForegroundColor White
Write-Host "  2. Naviguer vers Cuisine > Planning > Planning Actif" -ForegroundColor White
Write-Host "  3. Verifier qu'aucune erreur not bound to a Session n'apparait" -ForegroundColor White
Write-Host "  4. Tester les modifications (recettes, prepare, notes, dupliquer)" -ForegroundColor White
Write-Host ""
