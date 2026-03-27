#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to working directory
os.chdir('c:\\Users\\menar\\Documents\\Projet_perso\\assistant_matanne.worktrees\\copilot-worktree-2026-03-27T13-21-01')

print("=" * 60)
print("CHECK 1: Python Syntax Check")
print("=" * 60)
try:
    result = subprocess.run(
        [sys.executable, '-c', 
         'from src.services.core.events.subscribers import enregistrer_subscribers; n = enregistrer_subscribers(); print(f"OK: {n} subscribers")'],
        capture_output=True,
        text=True,
        timeout=30
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("CHECK 2: Backend Lint (Ruff)")
print("=" * 60)
try:
    result = subprocess.run(
        [sys.executable, '-m', 'ruff', 'check', 'src/services/core/events/subscribers.py', '--select', 'E,F', '--quiet'],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.stdout:
        print(result.stdout)
    else:
        print("No lint errors found")
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("CHECK 3: TypeScript Compile Check")
print("=" * 60)
try:
    result = subprocess.run(
        'cd frontend && npx tsc --noEmit',
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )
    lines = (result.stdout + result.stderr).split('\n')[:60]
    print('\n'.join(lines))
    if result.returncode != 0:
        print(f"\nReturn code: {result.returncode}")
except Exception as e:
    print(f"ERROR: {e}")
