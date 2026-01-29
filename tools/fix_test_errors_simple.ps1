# Script PowerShell simplifié pour corriger les encodages et imports
# Fixes: encoding uniquement

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   Correction des erreurs d'encodage et imports" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$basePath = "d:\Projet_streamlit\assistant_matanne"
$testPath = Join-Path $basePath "tests"

# Étape 1: Corriger les encodages
Write-Host "`n[1/3] Correction des encodages UTF-8..." -ForegroundColor Yellow

$testFiles = @(Get-ChildItem -Path $testPath -Recurse -Filter "*.py" -ErrorAction SilentlyContinue)
$fixed = 0
$skipped = 0

foreach ($file in $testFiles) {
    if ($file.DirectoryName -like "*__pycache__*") {
        continue
    }
    
    try {
        # Lire le fichier
        $content = Get-Content -Path $file.FullName -Encoding UTF8 -ErrorAction SilentlyContinue
        
        # Si vide, essayer avec encodage par défaut
        if (-not $content) {
            $content = Get-Content -Path $file.FullName -Encoding Default -ErrorAction SilentlyContinue
        }
        
        if ($content) {
            # Réécrire en UTF-8
            [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
            $fixed++
        }
    } catch {
        $skipped++
    }
}

Write-Host "  ✓ $fixed fichiers corrigés" -ForegroundColor Green
Write-Host "  - $skipped fichiers ignorés" -ForegroundColor Gray

# Étape 2: Corriger sante.py
Write-Host "`n[2/3] Correction de src/domains/famille/ui/sante.py..." -ForegroundColor Yellow

$saneFile = Join-Path $basePath "src\domains\famille\ui\sante.py"
if (Test-Path $saneFile) {
    try {
        $content = Get-Content -Path $saneFile -Encoding UTF8 -ErrorAction SilentlyContinue
        if (-not $content) {
            $content = Get-Content -Path $saneFile -Encoding Default
        }
        [System.IO.File]::WriteAllText($saneFile, $content, [System.Text.Encoding]::UTF8)
        Write-Host "  ✓ sante.py corrigé" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Erreur: $_" -ForegroundColor Red
    }
}

# Étape 3: Vérifier les imports problématiques
Write-Host "`n[3/3] Vérification des imports..." -ForegroundColor Yellow

$planningTest = Join-Path $basePath "tests\integration\test_planning_module.py"
$coursesTest = Join-Path $basePath "tests\integration\test_courses_module.py"

Write-Host "`n  ⚠  test_planning_module.py:" -ForegroundColor Yellow
Write-Host "      Import: render_planning, render_generer, render_historique" -ForegroundColor Gray
Write-Host "      Status: À CORRIGER MANUELLEMENT" -ForegroundColor Red
Write-Host "      Fonction: render_* n'existe pas dans planning_logic.py" -ForegroundColor Red

Write-Host "`n  ⚠  test_courses_module.py:" -ForegroundColor Yellow
Write-Host "      Import: render_liste_active, render_rayon_articles, etc." -ForegroundColor Gray
Write-Host "      Status: À CORRIGER MANUELLEMENT" -ForegroundColor Red
Write-Host "      Fonction: render_* n'existe pas dans courses_logic.py" -ForegroundColor Red

# Résumé
Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   RÉSUMÉ" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Encodage: $fixed fichiers corrigés" -ForegroundColor Green
Write-Host "  ⚠ Imports: 2 fichiers à corriger manuellement" -ForegroundColor Yellow
Write-Host "`n  Prochaines étapes:" -ForegroundColor Cyan
Write-Host "    1. Ouvrir test_planning_module.py et vérifier l'import" -ForegroundColor Gray
Write-Host "    2. Ouvrir test_courses_module.py et vérifier l'import" -ForegroundColor Gray
Write-Host "    3. Exécuter: pytest tests/ -v pour valider" -ForegroundColor Gray
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
