<#
Run pre-commit hooks and pytest in a single command (PowerShell).

Usage:
  .\scripts\run_checks.ps1

Requires: pre-commit installed in the environment and pytest available.
#>

Write-Host "Running pre-commit on all files..."
pre-commit run --all-files
$LASTEXITCODE | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "pre-commit failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "pre-commit passed. Running pytest..."
pytest -q
$LASTEXITCODE | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "pytest failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "All checks passed."
