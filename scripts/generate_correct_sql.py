#!/usr/bin/env python3
"""
Génère le SQL correct depuis les modèles SQLAlchemy
et l'exporte pour utilisation sur Supabase
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from src.core.models import Base

def generer_sql():
    """Génère le SQL pour toutes les tables"""
    sql_statements = []
    
    for table in Base.metadata.sorted_tables:
        # Générer CREATE TABLE
        create_stmt = CreateTable(table)
        compiled = create_stmt.compile(dialect=postgresql.dialect())
        sql_statements.append(f"{compiled};\n")
    
    return "\n".join(sql_statements)

if __name__ == "__main__":
    sql = generer_sql()
    print(sql)
