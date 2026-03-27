#!/usr/bin/env python3
"""Quick verification checks - simplified version."""
import sys
import os

os.chdir('c:\\Users\\menar\\Documents\\Projet_perso\\assistant_matanne.worktrees\\copilot-worktree-2026-03-27T13-21-01')
sys.path.insert(0, os.getcwd())

print("=" * 80)
print("CHECK 3: Verify AchatFamille Import")
print("=" * 80)
try:
    from src.core.models import AchatFamille
    print(f"✓ AchatFamille import successful")
    print(f"✓ AchatFamille tablename: {AchatFamille.__tablename__}")
    print("Return code: 0")
except Exception as e:
    print(f"✗ Import failed: {e}")
    print("Return code: 1")

print("=" * 80)
