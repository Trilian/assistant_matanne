#!/usr/bin/env python3
"""
Génère le schéma SQL complet pour Supabase à partir des modèles SQLAlchemy
"""
from sqlalchemy import MetaData, create_engine, text
from src.core.models import Base
import sys

def generate_schema():
    """Génère et affiche le SQL complet"""
    # Créer un moteur temporaire SQLite pour générer le schéma
    engine = create_engine("sqlite:///:memory:")
    
    # Créer toutes les tables
    Base.metadata.create_all(engine)
    
    # Récupérer les instructions SQL
    from sqlalchemy.schema import CreateTable
    
    print("-- ════════════════════════════════════════════════════════════════════════════")
    print("-- SCHÉMA COMPLET - Assistant Matanne")
    print("-- Généré automatiquement depuis les modèles SQLAlchemy")
    print("-- ════════════════════════════════════════════════════════════════════════════\n")
    
    for table in sorted(Base.metadata.tables.values(), key=lambda t: t.name):
        print(f"-- Table: {table.name}")
        print(f"CREATE TABLE IF NOT EXISTS {table.name} (")
        
        columns = []
        for col in table.columns:
            col_def = f"    {col.name} "
            
            # Type
            if col.type.__class__.__name__ == 'Integer':
                col_def += "INTEGER"
            elif col.type.__class__.__name__ == 'String':
                length = getattr(col.type, 'length', None)
                col_def += f"VARCHAR({length})" if length else "VARCHAR(255)"
            elif col.type.__class__.__name__ == 'Text':
                col_def += "TEXT"
            elif col.type.__class__.__name__ == 'Boolean':
                col_def += "BOOLEAN"
            elif col.type.__class__.__name__ == 'Date':
                col_def += "DATE"
            elif col.type.__class__.__name__ == 'DateTime':
                col_def += "TIMESTAMP"
            elif col.type.__class__.__name__ == 'Float':
                col_def += "FLOAT"
            else:
                col_def += str(col.type)
            
            # Constraints
            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.nullable is False:
                col_def += " NOT NULL"
            if col.default is not None:
                default_val = col.default.arg if hasattr(col.default, 'arg') else col.default
                if callable(default_val):
                    col_def += " DEFAULT CURRENT_TIMESTAMP"
                else:
                    col_def += f" DEFAULT '{default_val}'"
            if col.index:
                col_def += " -- INDEX"
            
            columns.append(col_def)
        
        # Ajouter les foreign keys
        for fk in table.foreign_keys:
            columns.append(f"    FOREIGN KEY ({fk.parent.name}) REFERENCES {fk.column.table.name}({fk.column.name})")
        
        print(",\n".join(columns))
        print(");\n")
        
        # Indices
        if any(col.index for col in table.columns):
            for col in table.columns:
                if col.index:
                    print(f"CREATE INDEX IF NOT EXISTS idx_{table.name}_{col.name} ON {table.name}({col.name});")

if __name__ == "__main__":
    generate_schema()
