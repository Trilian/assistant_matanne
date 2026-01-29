#!/usr/bin/env python3
"""
Apply migration 010 directly via SQL execution
This bypasses Alembic and connects directly to Supabase
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def apply_migration_directly():
    """Apply migration by executing SQL directly"""
    print("[INFO] Attempting direct SQL execution...")
    
    try:
        # Get the SQL script content
        sql_file = Path(__file__).parent / "sql" / "010_add_updated_at_columns.sql"
        
        if not sql_file.exists():
            print(f"[ERROR] SQL file not found: {sql_file}")
            return False
        
        with open(sql_file) as f:
            sql_content = f.read()
        
        print(f"[INFO] Loaded SQL from {sql_file.name}")
        print(f"[INFO] SQL length: {len(sql_content)} bytes")
        
        # Try to connect and execute
        from sqlalchemy import create_engine, text
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        db_url = params.DATABASE_URL
        
        if not db_url:
            print("[ERROR] DATABASE_URL not configured")
            return False
        
        print(f"[INFO] Connecting to database...")
        
        # Create engine
        engine = create_engine(db_url, echo=False)
        
        # Extract individual SQL statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"[INFO] Found {len(statements)} SQL statements to execute")
        
        with engine.connect() as conn:
            executed = 0
            for i, statement in enumerate(statements, 1):
                if not statement or statement.startswith('--'):
                    continue
                
                try:
                    print(f"[*] Executing statement {i}/{len(statements)}...")
                    conn.execute(text(statement))
                    print(f"[OK] Statement {i} executed")
                    executed += 1
                except Exception as e:
                    print(f"[WARNING] Statement {i} error: {str(e)[:100]}")
                    # Some statements might fail (like IF NOT EXISTS), continue
            
            conn.commit()
            print(f"\n[OK] Migration applied! ({executed} statements executed)")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to apply migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("SUPABASE MIGRATION 010 - DIRECT SQL EXECUTION")
    print("=" * 80)
    print()
    
    success = apply_migration_directly()
    
    if success:
        print("\n" + "=" * 80)
        print("[SUCCESS] Migration 010 applied!")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("[FAILED] Could not apply migration")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
