#!/usr/bin/env python3
"""Apply Supabase migration 010 - Add updated_at columns"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def apply_migration_via_alembic():
    """Apply migration using Alembic"""
    import subprocess
    
    print("[INFO] Applying migrations via Alembic...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Migration applied successfully!")
            if result.stdout:
                print("Output:", result.stdout[:500])
            return True
        else:
            print("[ERROR] Alembic failed:")
            if result.stderr:
                print(result.stderr[:1000])
            return False
    except Exception as e:
        print(f"[ERROR] Failed to run Alembic: {e}")
        return False

def apply_migration_via_python():
    """Apply migration using Python database manager"""
    print("[INFO] Applying migrations via Python...")
    try:
        from src.core.database import GestionnaireMigrations
        
        print("[INFO] Connecting to database...")
        current_version = GestionnaireMigrations.obtenir_version_courante()
        print(f"[INFO] Current migration version: {current_version}")
        
        print("[INFO] Applying pending migrations...")
        GestionnaireMigrations.appliquer_migrations()
        
        new_version = GestionnaireMigrations.obtenir_version_courante()
        print(f"[OK] Migration applied! New version: {new_version}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to apply migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify that migration was applied"""
    print("\n[INFO] Verifying migration...")
    try:
        from src.core.database import get_db_context
        
        with get_db_context() as db:
            # Check if updated_at columns exist
            from sqlalchemy import text
            
            result = db.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name IN ('recettes', 'modeles_courses') 
                AND column_name = 'updated_at'
                ORDER BY table_name;
            """)).fetchall()
            
            if len(result) == 2:
                print("[OK] Columns verified!")
                for row in result:
                    print(f"  - {row[0]}")
                return True
            else:
                print(f"[WARNING] Expected 2 columns, found {len(result)}")
                return False
                
    except Exception as e:
        print(f"[WARNING] Could not verify: {e}")
        return False

def main():
    print("""
================================================================================
                   SUPABASE MIGRATION 010 - APPLY MIGRATION
================================================================================

Migration: Add updated_at columns to recettes and modeles_courses tables

""")
    
    # Try Alembic first
    print("=" * 80)
    if apply_migration_via_alembic():
        print("=" * 80)
        verify_migration()
        print("\n[OK] Migration 010 applied successfully!")
        return True
    
    # Fallback to Python
    print("\n[INFO] Trying alternative method (Python database manager)...")
    print("=" * 80)
    if apply_migration_via_python():
        print("=" * 80)
        verify_migration()
        print("\n[OK] Migration 010 applied successfully!")
        return True
    
    print("\n[ERROR] Failed to apply migration")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
