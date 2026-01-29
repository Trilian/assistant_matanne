#!/usr/bin/env python3
"""
Migration 010 status check and fallback options
Checks Supabase connectivity and suggests fallback strategies
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_supabase_connection():
    """Check if Supabase connection is available"""
    print("[*] Checking Supabase connection status...")
    
    try:
        from sqlalchemy import create_engine, text
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        db_url = params.DATABASE_URL
        
        print(f"[INFO] DATABASE_URL configured: {db_url[:50]}...")
        
        # Try to create engine
        engine = create_engine(db_url, echo=False, connect_args={"timeout": 5})
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as status"))
            print("[OK] Supabase connection successful!")
            engine.dispose()
            return True
            
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Supabase connection failed")
        print(f"        {error_msg[:100]}")
        
        if "Tenant or user not found" in error_msg:
            print("[INFO] This is a Supabase authentication error")
            print("       Likely causes:")
            print("       1. Invalid or expired credentials")
            print("       2. User not found in Supabase tenant")
            print("       3. Connection pooler misconfiguration")
        
        return False

def check_migration_readiness():
    """Check if migration 010 is ready to apply"""
    print("\n[*] Checking migration 010 readiness...")
    
    migration_file = Path(__file__).parent / "alembic" / "versions" / "010_fix_trigger_modifie_le.py"
    sql_file = Path(__file__).parent / "sql" / "010_add_updated_at_columns.sql"
    
    print(f"[{'OK' if migration_file.exists() else 'MISSING'}] Migration file: {migration_file.name}")
    print(f"[{'OK' if sql_file.exists() else 'MISSING'}] SQL file: {sql_file.name}")
    
    if migration_file.exists():
        with open(migration_file) as f:
            content = f.read()
            ops_count = content.count("op.add_column")
            print(f"     Contains {ops_count} column additions")
    
    return migration_file.exists() and sql_file.exists()

def suggest_solutions():
    """Suggest solutions based on current state"""
    print("\n" + "=" * 80)
    print("SUGGESTED SOLUTIONS")
    print("=" * 80)
    
    print("""
[OPTION 1] Fix Supabase Credentials (RECOMMENDED)
   1. Go to: https://supabase.com/dashboard/
   2. Open your project 'assistant-matanne'
   3. Navigate to: Settings > Database > Connection pooling
   4. Copy the connection string from the "Pooler" tab
   5. Update DATABASE_URL in .env.local
   6. Try migration again: python apply_migration_010_direct.py

[OPTION 2] Use Direct Connection (Port 5432)
   1. Update DATABASE_URL in .env.local to use port 5432:
      postgresql://postgres.haieczwixbkeuwcgdzvn:Famille2Geek@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
   2. Note: This may not work if the pooler is disabled
   3. Try migration: python apply_migration_010_direct.py

[OPTION 3] Manual Application via Supabase Dashboard
   1. Go to: https://supabase.com/dashboard/project/_/sql/new
   2. Create a new SQL query
   3. Copy the contents of: sql/010_add_updated_at_columns.sql
   4. Paste and execute in the SQL Editor
   5. Verify: check if columns updated_at were added

[OPTION 4] Apply via Alembic CLI
   1. First, ensure DATABASE_URL is correct
   2. Run: alembic upgrade head
   3. Check status: alembic current

[OPTION 5] Postpone Production Migration
   If you're in development:
   1. The app will still run (models expect the columns)
   2. Work with local SQLite database for testing
   3. Apply migration to Supabase when credentials are fixed
    """)

def main():
    print("=" * 80)
    print("MIGRATION 010 - STATUS CHECK AND DIAGNOSTICS")
    print("=" * 80)
    print()
    
    # Check migration readiness
    migration_ready = check_migration_readiness()
    
    # Check Supabase connection
    supabase_ok = check_supabase_connection()
    
    # Suggest solutions
    suggest_solutions()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Migration 010 ready to apply:  [{'YES' if migration_ready else 'NO'}]")
    print(f"Supabase connection available: [{'YES' if supabase_ok else 'NO'}]")
    print()
    
    if migration_ready and supabase_ok:
        print("[OK] You can proceed with migration!")
        return 0
    elif migration_ready and not supabase_ok:
        print("[INFO] Fix Supabase credentials first, then retry")
        return 1
    else:
        print("[ERROR] Migration files are missing!")
        return 2

if __name__ == "__main__":
    sys.exit(main())
