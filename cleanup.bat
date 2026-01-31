@echo off
REM Nettoyage complet du projet Assistant MaTanne
REM Supprime tous les fichiers temporaires, scripts de fix et rapports

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   🧹 NETTOYAGE DU PROJET
echo ========================================
echo.

set /a count=0

REM Scripts Python temporaires
for %%f in (
    "fix_*.py"
    "emoji*.py"
    "apply_migration_*.py"
    "check_migration_status.py"
    "cleanup*.py"
    "analyze*.py"
    "count_tests.py"
    "RUN_*.py"
    "run_tests_simple.py"
    "quick_fix_emoji.py"
    "binary*.py"
    "brute_force*.py"
    "detect_*.py"
    "extract_*.py"
    "find_*.py"
    "final_*.py"
    "FINAL_*.py"
    "simple_string_fix.py"
    "ultimate_cleanup.py"
    "QUICK_SUMMARY.py"
    "replace_with_clean_emojis.py"
    "test_encoding.py"
    "test_fix_session.py"
    "test_image_generation_fix.py"
    "test_migration_010.py"
    "test_modeles_debug.py"
    "test_phase4_fixes.py"
    "test_planning_generation.py"
    "test_recipe_update.py"
    "test_trigger_simple.py"
    "test_updated_at_trigger.py"
    "MIGRATION_010_INSTRUCTIONS.py"
) do (
    for /r . %%g in (%%f) do (
        if exist "%%g" (
            del /f /q "%%g" 2>nul
            set /a count+=1
            echo   ✓ %%~nxg
        )
    )
)

REM Fichiers de log et txt
for %%f in (*.log *.txt) do (
    if exist "%%f" (
        del /f /q "%%f" 2>nul
        set /a count+=1
        echo   ✓ %%f
    )
)

REM Fichiers de rapport et documentation
for %%f in (
    "*_REPORT.md"
    "*_SUMMARY.md"
    "*_GUIDE.md"
    "*_INDEX.md"
    "*_CHECKLIST.md"
    "*_PLAN.md"
    "*_README.md"
    "PHASE*.md"
    "DEPLOY_*.md"
    "ACTION_*.md"
    "*_COMPLETE*.md"
    "*_FIX*.md"
    "*_SESSION*.md"
    "COMPLETION_*.md"
    "DELIVERABLES.md"
    "STARTING_HERE.md"
    "MIGRATION_*.md"
    "TESTING_*.md"
    "TESTS_*.md"
    "TEST_*.md"
    "RESTRUCTURATION_*.md"
    "MODULES_*.md"
    "NETTOYAGE_*.md"
    "EXACT_CHANGES.md"
    "CORRECTION_*.md"
    "FIX_SESSION_*.md"
    "INDEX_FIX_*.md"
    "MARMITON_*.md"
    "MOJIBAKE_*.md"
    "ONE_PAGE_*.txt"
    "QUICK_START_*.md"
    "UI_UTILS_*.md"
    "COVERAGE_REPORT.*"
    "TEST_EXECUTION_*.html"
    "FINAL_SUMMARY.txt"
    "RESULTAT_*.md"
    "SCHEMA_FIX_*.md"
    "SESSION_*.md"
) do (
    for /f %%g in ('dir /b %%f 2^>nul') do (
        if exist "%%g" (
            del /f /q "%%g" 2>nul
            set /a count+=1
            echo   ✓ %%g
        )
    )
)

REM Fichiers spécifiques
for %%f in (
    "hex_patterns.txt"
    "hex_replacement_result.txt"
    "mojibake_patterns_found.txt"
    "mojibake_patterns_hex.txt"
    "all_files_cleanup_log.txt"
    "brute_force_log.txt"
    "byte_cleanup_log.txt"
    "emoji_cleanup_log.txt"
    "emoji_fix_log.txt"
    "emoji_replacement_log.txt"
    "final_cleanup_log.txt"
    "final_regex_log.txt"
    "safe_replacement_log.txt"
    "test_log.txt"
    "tests.log"
    "test_results.txt"
    "coverage.json"
    "verify_fix.ps1"
    "verify_fix.sh"
) do (
    if exist "%%f" (
        del /f /q "%%f" 2>nul
        set /a count+=1
        echo   ✓ %%f
    )
)

REM Répertoires
for /d %%d in (backups my_backups htmlcov) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
        set /a count+=1
        echo   ✓ %%d\ ^(répertoire^)
    )
)

echo.
echo ========================================
echo   ✅ Nettoyage terminé !
echo   Fichiers/dossiers supprimés: %count%
echo ========================================
echo.
echo 📊 État du répertoire:
echo.

REM Compter les fichiers restants
setlocal enabledelayedexpansion
set /a filecount=0
set /a dircount=0

for /f %%f in ('dir /b /a:-d 2^>nul ^| find /c /v ""') do set /a filecount=%%f
for /f %%d in ('dir /b /ad 2^>nul ^| find /c /v ""') do set /a dircount=%%d

echo   Fichiers: %filecount%
echo   Répertoires: %dircount%
echo.
echo Prêt pour la production! 🚀
echo.
pause
