"""
Sprint 12 — A5: Audit tables orphelines ORM <-> SQL.

Compare:
- ORM tables: __tablename__ declarations in src/core/models/
- SQL tables: CREATE TABLE statements in sql/INIT_COMPLET.sql
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
MODELS_DIR = ROOT / "src" / "core" / "models"
SQL_FILE = ROOT / "sql" / "INIT_COMPLET.sql"


def extract_orm_tables() -> dict[str, str]:
    """Return {table_name: filename} from all ORM model files."""
    tables = {}
    for f in sorted(MODELS_DIR.glob("*.py")):
        text = f.read_text(encoding="utf-8")
        matches = re.findall(r'__tablename__\s*=\s*["\'](\w+)["\']', text)
        for name in matches:
            tables[name] = f.name
    return tables


def extract_sql_tables() -> set[str]:
    """Return set of table names from CREATE TABLE statements in SQL file."""
    text = SQL_FILE.read_text(encoding="utf-8")
    # Match CREATE TABLE [IF NOT EXISTS] "schema"."name" or just "name" or name
    matches = re.findall(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'(?:\w+\.)?["\'`]?(\w+)["\'`]?',
        text,
        re.IGNORECASE,
    )
    return set(matches)


def main() -> None:
    orm_tables = extract_orm_tables()
    sql_tables = extract_sql_tables()

    orm_set = set(orm_tables.keys())

    print("=" * 70)
    print("Sprint 12 A5 — Audit tables orphelines ORM <-> SQL")
    print("=" * 70)
    print(f"\nORM tables total : {len(orm_set)}")
    print(f"SQL tables total : {len(sql_tables)}")

    # ORM tables with no SQL CREATE TABLE
    orm_only = orm_set - sql_tables
    print(f"\n{'─'*70}")
    print(f"ORM sans CREATE TABLE SQL ({len(orm_only)}) :")
    print("  → Action requise : ajouter CREATE TABLE dans INIT_COMPLET.sql ou supprimer le modele")
    for name in sorted(orm_only):
        print(f"  [ORM only]  {name:40s}  ({orm_tables[name]})")

    # SQL tables with no ORM model
    sql_only = sql_tables - orm_set
    print(f"\n{'─'*70}")
    print(f"SQL sans modele ORM ({len(sql_only)}) :")
    print("  → Action requise : creer le modele SQLAlchemy ou supprimer le CREATE TABLE")
    for name in sorted(sql_only):
        print(f"  [SQL only]  {name}")

    # Matching tables
    matched = orm_set & sql_tables
    print(f"\n{'─'*70}")
    print(f"Tables presentes ORM + SQL ({len(matched)}) : OK")

    print("\n" + "=" * 70)
    print("Fin de l'audit.")


if __name__ == "__main__":
    main()
