# Nettoyage complet du projet
$patterns = @(
    "fix_*.py",
    "emoji*.py",
    "apply_migration_*.py",
    "check_migration_status.py",
    "cleanup*.py",
    "analyze*.py",
    "count_tests.py",
    "RUN_*.py",
    "run_tests_simple.py",
    "quick_fix_emoji.py",
    "binary*.py",
    "brute_force*.py",
    "detect_*.py",
    "extract_*.py",
    "find_*.py",
    "final_*.py",
    "FINAL_*.py",
    "simple_string_fix.py",
    "ultimate_cleanup.py",
    "verify_fix.ps1",
    "verify_fix.sh",
    "QUICK_SUMMARY.py",
    "replace_with_clean_emojis.py",
    "test_encoding.py",
    "test_fix_session.py",
    "test_image_generation_fix.py",
    "test_migration_010.py",
    "test_modeles_debug.py",
    "test_phase4_fixes.py",
    "test_planning_generation.py",
    "test_recipe_update.py",
    "test_trigger_simple.py",
    "test_updated_at_trigger.py",
    "MIGRATION_010_INSTRUCTIONS.py",
    "*.log",
    "*_REPORT.md",
    "*_SUMMARY.md",
    "*_GUIDE.md",
    "*_INDEX.md",
    "*_CHECKLIST.md",
    "*_PLAN.md",
    "*_README.md",
    "PHASE*.md",
    "PHASE*.txt",
    "DEPLOY_*.md",
    "ACTION_*.md",
    "*_COMPLETE*.md",
    "*_FIX*.md",
    "*_SESSION*.md",
    "COMPLETION_*.md",
    "DELIVERABLES.md",
    "STARTING_HERE.md",
    "MIGRATION_*.md",
    "TESTING_*.md",
    "TESTS_*.md",
    "TEST_*.md",
    "RESTRUCTURATION_*.md",
    "MODULES_*.md",
    "NETTOYAGE_*.md",
    "EXACT_CHANGES.md",
    "CORRECTION_*.md",
    "FIX_SESSION_*.md",
    "INDEX_FIX_*.md",
    "MARMITON_*.md",
    "MOJIBAKE_*.md",
    "ONE_PAGE_*.txt",
    "QUICK_START_*.md",
    "UI_UTILS_*.md",
    "COVERAGE_REPORT.*",
    "TEST_EXECUTION_*.html",
    "FINAL_SUMMARY.txt",
    "RESULTAT_*.md",
    "SCHEMA_FIX_*.md",
    "SESSION_*.md",
    "hex_*.txt",
    "mojibake_*.txt",
    "*.json",
    "all_files_cleanup_log.txt",
    "brute_force_log.txt",
    "byte_cleanup_log.txt",
    "emoji_cleanup_log.txt",
    "emoji_fix_log.txt",
    "emoji_replacement_log.txt",
    "final_cleanup_log.txt",
    "final_regex_log.txt",
    "safe_replacement_log.txt",
    "test_log.txt",
    "tests.log"
)

$deleted = 0
Write-Host "🧹 Nettoyage du projet en cours..."

foreach ($pattern in $patterns) {
    Get-Item -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction SilentlyContinue
        $deleted++
    }
}

# Supprimer les répertoires
Remove-Item -Path "backups", "my_backups", "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Nettoyage terminé! $deleted fichiers supprimés"
Write-Host "`n📊 État final du répertoire:"
Get-ChildItem -File | Measure-Object | ForEach-Object { Write-Host "   Fichiers: $($_.Count)" }
Get-ChildItem -Directory | Measure-Object | ForEach-Object { Write-Host "   Répertoires: $($_.Count)" }
