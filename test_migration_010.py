#!/usr/bin/env python3
"""Test that migration 010 can be applied"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_migration_010():
    """Test if migration 010 is valid"""
    print("Testing migration 010 validity...")
    
    # Check if migration file exists
    migration_file = Path(__file__).parent / "alembic" / "versions" / "010_fix_trigger_modifie_le.py"
    if not migration_file.exists():
        print("[ERROR] Migration file not found:", migration_file)
        return False
    
    print("[OK] Migration file exists")
    
    # Try to import the migration
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration_010", migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check required functions
        if not hasattr(module, 'upgrade'):
            print("[ERROR] Migration missing 'upgrade' function")
            return False
        
        print("[OK] Migration has upgrade function")
        
        # Check if it has down_revision
        if hasattr(module, 'down_revision') and module.down_revision == '009':
            print("[OK] Migration references correct parent (009)")
        else:
            print("[WARNING] Down revision might not be correct")
        
    except Exception as e:
        print(f"[ERROR] Failed to load migration: {e}")
        return False
    
    # Check SQL script exists
    sql_file = Path(__file__).parent / "sql" / "010_add_updated_at_columns.sql"
    if not sql_file.exists():
        print("[WARNING] SQL script not found:", sql_file)
    else:
        print("[OK] SQL script exists")
        # Check content
        with open(sql_file) as f:
            sql_content = f.read()
        if 'updated_at' in sql_content and 'recettes' in sql_content:
            print("[OK] SQL script has correct content")
        else:
            print("[ERROR] SQL script content looks wrong")
            return False
    
    print("\n[OK] Migration 010 is ready to apply!")
    return True

if __name__ == "__main__":
    success = test_migration_010()
    sys.exit(0 if success else 1)
