# Script de correction des erreurs de tests
# Fixes: encoding, imports manquants

function Fix-FileEncoding {
    <#
    .SYNOPSIS
    Convertit un fichier d'un encodage à UTF-8
    #>
    param(
        [string]$FilePath
    )
    
    try {
        # Essayer de lire comme UTF-8 d'abord
        $content = Get-Content -Path $FilePath -Encoding UTF8 -ErrorAction SilentlyContinue
        
        # Si échec, lire avec encodage par défaut (potentiellement Latin-1)
        if (-not $content) {
            $content = Get-Content -Path $FilePath -Encoding Default -ErrorAction SilentlyContinue
        }
        
        # Réécrire en UTF-8
        if ($content) {
            [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.Encoding]::UTF8)
            return $true
        }
        return $false
    }
    catch {
        Write-Error "Erreur lors du traitement $FilePath : $_"
        return $false
    }
}

function Fix-TestEncodings {
    <#
    .SYNOPSIS
    Corrige l'encodage de tous les fichiers de test
    #>
    Write-Host "🔄 Correction des encodages en cours..." -ForegroundColor Cyan
    
    $basePath = "d:\Projet_streamlit\assistant_matanne"
    $testPath = Join-Path $basePath "tests"
    $srcPath = Join-Path $basePath "src"
    
    # Fichiers de test
    $testFiles = Get-ChildItem -Path $testPath -Recurse -Filter "*.py" | Where-Object { $_.DirectoryName -notmatch "__pycache__" }
    
    $fixed = 0
    $failed = 0
    
    foreach ($file in $testFiles) {
        if (Fix-FileEncoding -FilePath $file.FullName) {
            $fixed++
            Write-Host "✅ $($file.Name)" -ForegroundColor Green
        }
        else {
            $failed++
            Write-Host "❌ $($file.Name)" -ForegroundColor Red
        }
    }
    
    # Fichier source avec erreur d'encodage
    $saneFile = Join-Path $srcPath "domains\famille\ui\sante.py"
    if (Test-Path $saneFile) {
        if (Fix-FileEncoding -FilePath $saneFile) {
            $fixed++
            Write-Host "✅ sante.py" -ForegroundColor Green
        }
        else {
            $failed++
            Write-Host "❌ sante.py" -ForegroundColor Red
        }
    }
    
    Write-Host "`n📊 Résumé: $fixed fichiers corrigés, $failed erreurs" -ForegroundColor Cyan
}

function Fix-ImportErrors {
    <#
    .SYNOPSIS
    Corrige les erreurs d'import manquants
    #>
    Write-Host "`n🔧 Correction des imports en cours..." -ForegroundColor Cyan
    
    $basePath = "d:\Projet_streamlit\assistant_matanne"
    
    # ERREUR 1: test_planning_module.py
    $planningTestPath = Join-Path $basePath "tests\integration\test_planning_module.py"
    if (Test-Path $planningTestPath) {
        Write-Host "`n📋 Traitement: test_planning_module.py" -ForegroundColor Yellow
        
        $content = Get-Content -Path $planningTestPath -Raw -Encoding UTF8
        
        # Remplacer l'import incorrect
        $oldImport = @"
from src.domains.cuisine.logic.planning_logic import (
    render_planning,
    render_generer,
    render_historique
)
"@
        
        $newImport = @"
# FIXME: render_* functions not found in planning_logic.py
# Available functions: get_debut_semaine, get_fin_semaine, get_dates_semaine, etc.
# Import moved to src/domains/cuisine/ui/planning.py or removed
# from src.domains.cuisine.logic.planning_logic import (
#     render_planning,
#     render_generer,
#     render_historique
# )

# Utilisez plutôt:
# from src.domains.cuisine.ui.planning import ...
# OU
# from src.domains.cuisine.logic.planning_logic import (
#     get_debut_semaine,
#     get_fin_semaine,
#     get_dates_semaine,
#     organiser_repas_par_jour,
#     organiser_repas_par_type,
#     calculer_statistiques_planning
# )
"@
        
        if ($content -like "*render_planning*") {
            $content = $content -replace [regex]::Escape($oldImport), $newImport
            $content | Set-Content -Path $planningTestPath -Encoding UTF8
            Write-Host "✅ Import corrigé (mis en commentaire, vérifier manuellement)" -ForegroundColor Green
        }
    }
    
    # ERREUR 2: test_courses_module.py
    $coursesTestPath = Join-Path $basePath "tests\integration\test_courses_module.py"
    if (Test-Path $coursesTestPath) {
        Write-Host "`n📋 Traitement: test_courses_module.py" -ForegroundColor Yellow
        
        $content = Get-Content -Path $coursesTestPath -Raw -Encoding UTF8
        
        # Remplacer l'import incorrect
        $oldImport = @"
from src.domains.cuisine.logic.courses import (
    render_liste_active,
    render_rayon_articles,
    render_ajouter_article,
    render_suggestions_ia,
    render_historique,
    render_modeles,
)
"@
        
        $newImport = @"
# FIXME: render_* functions not found in courses_logic.py
# Available functions: filtrer_par_priorite, grouper_par_rayon, calculer_statistiques, etc.
# from src.domains.cuisine.logic.courses import (
#     render_liste_active,
#     render_rayon_articles,
#     render_ajouter_article,
#     render_suggestions_ia,
#     render_historique,
#     render_modeles,
# )

# Utilisez plutôt:
# from src.domains.cuisine.ui.courses import ...
# OU
# from src.domains.cuisine.logic.courses_logic import (
#     filtrer_par_priorite,
#     filtrer_par_rayon,
#     grouper_par_rayon,
#     trier_par_priorite,
#     calculer_statistiques
# )
"@
        
        if ($content -like "*render_liste_active*") {
            $content = $content -replace [regex]::Escape($oldImport), $newImport
            $content | Set-Content -Path $coursesTestPath -Encoding UTF8
            Write-Host "✅ Import corrigé (mis en commentaire, vérifier manuellement)" -ForegroundColor Green
        }
    }
}

function Verify-Fixes {
    <#
    .SYNOPSIS
    Vérifie que les corrections ont été appliquées
    #>
    Write-Host "`n✅ Vérification en cours..." -ForegroundColor Cyan
    
    $basePath = "d:\Projet_streamlit\assistant_matanne"
    $testPath = Join-Path $basePath "tests"
    
    # Vérifier les encodages
    $testFiles = Get-ChildItem -Path $testPath -Recurse -Filter "*.py" | Where-Object { $_.DirectoryName -notmatch "__pycache__" }
    
    $stillBroken = 0
    foreach ($file in $testFiles) {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content -match '[Ã©Ã]') {
            $stillBroken++
        }
    }
    
    if ($stillBroken -eq 0) {
        Write-Host "✅ Tous les encodages corrigés!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Encore $stillBroken fichiers avec erreurs d'encodage" -ForegroundColor Yellow
    }
    
    # Vérifier les imports
    $planningTest = Join-Path $basePath "tests\integration\test_planning_module.py"
    $coursesTest = Join-Path $basePath "tests\integration\test_courses_module.py"
    
    $planning = Get-Content -Path $planningTest -Raw -Encoding UTF8 2>$null
    $courses = Get-Content -Path $coursesTest -Raw -Encoding UTF8 2>$null
    
    if ($planning -notmatch "from src\.domains\.cuisine\.logic\.planning_logic import.*render_planning") {
        Write-Host "✅ test_planning_module.py: Import corrigé" -ForegroundColor Green
    }
    
    if ($courses -notmatch "from src\.domains\.cuisine\.logic\.courses import.*render_liste_active") {
        Write-Host "✅ test_courses_module.py: Import corrigé" -ForegroundColor Green
    }
}

# Main execution
Write-Host "
╔════════════════════════════════════════════════════════════════╗
║     Script de Correction des Erreurs de Tests                 ║
║     Application Streamlit - Assistant Matanne                 ║
╚════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

Fix-TestEncodings
Fix-ImportErrors
Verify-Fixes

Write-Host "`n✨ Corrections terminées!" -ForegroundColor Green
Write-Host "`n📝 NOTES IMPORTANTES:" -ForegroundColor Yellow
Write-Host "  1. Les imports ont été mis en commentaire pour révision manuelle"
Write-Host "  2. Vérifier que les bonnes fonctions sont importées"
Write-Host "  3. Exécuter: pytest tests/ -v pour valider" -ForegroundColor Yellow
