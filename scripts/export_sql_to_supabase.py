#!/usr/bin/env python3
"""
Génère le SQL correct pour Supabase à partir des modèles SQLAlchemy
N'a PAS besoin de DATABASE_URL - génère juste le SQL
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from src.core.models import Base

print("-- ════════════════════════════════════════════════════════════════════════════")
print("-- CRÉATION DE TOUTES LES TABLES - Assistant MaTanne v2.0")
print("-- SQL généré depuis les modèles SQLAlchemy")
print("-- Date: 25 Janvier 2026")
print("-- À copier-coller dans Supabase SQL Editor")
print("-- ════════════════════════════════════════════════════════════════════════════")
print()

for table in sorted(Base.metadata.sorted_tables, key=lambda t: t.name):
    # Générer CREATE TABLE
    create_stmt = CreateTable(table).compile(dialect=postgresql.dialect())
    sql = str(create_stmt).replace("\\n", "\n")
    print(sql)
    print(";")
    print()
