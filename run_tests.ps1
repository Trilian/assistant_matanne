$testDir = "d:\Projet_streamlit\assistant_matanne"
Set-Location $testDir

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ETAPE 1: EXECUTION DES TESTS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$testFiles = @(
    "tests/services/test_services_basic.py",
    "tests/services/test_services_integration.py",
    "tests/models/test_models_basic.py",
    "tests/core/test_decorators_basic.py",
    "tests/utils/test_utils_basic.py",
    "tests/integration/test_domains_integration.py",
    "tests/integration/test_business_logic.py",
    "tests/integration/test_phase16_extended.py"
)

$startTime = Get-Date

# Etape 1: Tests
$testOutput = & python -m pytest $testFiles --tb=short -q 2>&1
Write-Host $testOutput

$testDuration = (Get-Date) - $startTime
Write-Host "`nDuree tests: $($testDuration.TotalSeconds.ToString('F2')) s"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ETAPE 2: MESURE COUVERTURE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$coverageStart = Get-Date

$coverageOutput = & python -m pytest $testFiles --cov=src --cov-report=json --cov-report=term-missing -q --tb=short 2>&1
Write-Host $coverageOutput

$coverageDuration = (Get-Date) - $coverageStart
Write-Host "`nDuree couverture: $($coverageDuration.TotalSeconds.ToString('F2')) s"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ETAPE 3: EXTRACTION METRIQUES COUVERTURE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path "coverage.json") {
    $jsonContent = Get-Content "coverage.json" -Raw | ConvertFrom-Json
    $totalPct = $jsonContent.totals.percent_covered
    $baseline = 9.74
    $gain = $totalPct - $baseline
    
    Write-Host "`nPHASE 16 FIXED - RESULTATS" -ForegroundColor Green
    Write-Host "Couverture globale: $($totalPct.ToString('F2'))%" -ForegroundColor Green
    Write-Host "Target etait: 14-16%" -ForegroundColor Yellow
    Write-Host "Baseline etait: $baseline%" -ForegroundColor Yellow
    Write-Host "Gain: $($gain.ToString('F2'))%" -ForegroundColor Green
    
    if ($totalPct -ge 14) {
        Write-Host "`nSUCCESS: Couverture >= 14% (realise: $($totalPct.ToString('F2'))%)" -ForegroundColor Green
    } elseif ($totalPct -ge 9.74) {
        Write-Host "`nPARTIEL: Couverture > baseline mais < 14% (realise: $($totalPct.ToString('F2'))%)" -ForegroundColor Yellow
    } else {
        Write-Host "`nFAIL: Couverture < baseline (realise: $($totalPct.ToString('F2'))%)" -ForegroundColor Red
    }
} else {
    Write-Host "ERREUR: Fichier coverage.json non trouve" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTE COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
