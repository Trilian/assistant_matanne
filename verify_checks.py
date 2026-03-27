#!/usr/bin/env python3
"""Verification checks for the project."""
import subprocess
import sys
import os

# Change to working directory
os.chdir('c:\\Users\\menar\\Documents\\Projet_perso\\assistant_matanne.worktrees\\copilot-worktree-2026-03-27T13-21-01')

print("=" * 80)
print("CHECK 1: Python Tests for routes_famille")
print("=" * 80)
try:
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/api/test_routes_famille.py', '-v', '--tb=short', '-q'],
        capture_output=True,
        text=True,
        timeout=120
    )
    output = result.stdout + result.stderr
    lines = output.split('\n')
    # Print last 30 lines
    for line in lines[-30:]:
        print(line)
    print(f"\nReturn code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("CHECK 2: TypeScript Type Check")
print("=" * 80)
try:
    result = subprocess.run(
        'cd frontend && npx tsc --noEmit 2>&1 | head -50',
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )
    output = result.stdout + result.stderr
    lines = output.split('\n')[:50]
    print('\n'.join(lines))
    print(f"\nReturn code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("CHECK 3: Verify AchatFamille Import")
print("=" * 80)
try:
    result = subprocess.run(
        [sys.executable, '-c', 
         "from src.core.models import AchatFamille; print(f'AchatFamille OK: {AchatFamille.__tablename__}')"],
        capture_output=True,
        text=True,
        timeout=30
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
