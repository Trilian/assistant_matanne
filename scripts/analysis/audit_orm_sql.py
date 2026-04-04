#!/usr/bin/env python3
"""Audit rapide ORM ↔ SQL pour la consolidation Phase 3.

Vérifie :
- que chaque table ORM existe bien dans `sql/INIT_COMPLET.sql`
- qu'aucune nouvelle table SQL orpheline n'a été introduite
- que `sql/schema/13_views.sql` ne contient plus d'indexes dupliqués
- que `sql/schema/17_migrations_absorbees.sql` contient bien des instructions

Usage:
    python scripts/analysis/audit_orm_sql.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SQL_INIT = ROOT / "sql" / "INIT_COMPLET.sql"
VIEWS_FILE = ROOT / "sql" / "schema" / "13_views.sql"
MIGRATIONS_FILE = ROOT / "sql" / "schema" / "17_migrations_absorbees.sql"

TABLES_SQL_SANS_ORM: dict[str, str] = {
    "schema_migrations": "infrastructure — tracking des migrations appliquées",
    "budgets_home": "legacy — remplacé par budgets_maison (ORM BudgetMaison)",
    "depenses_home": "legacy — remplacé par depenses_maison (ORM DepenseMaison)",
    "job_executions": "infrastructure — journal d'exécution des jobs admin/cron",
    "objectifs_autonomie": "reference — objectifs autonomie Jules, accès direct via service",
    "plantes_catalogue": "reference — catalogue plantes jardin, pas d'ORM requis",
    "preferences_home": "legacy — remplacé par preferences_utilisateurs",
    "recoltes": "reference — récoltes jardin, accès direct via service",
}


def _lire_tables_sql() -> set[str]:
    """Retourne l'ensemble des tables déclarées dans INIT_COMPLET.sql."""
    sql = SQL_INIT.read_text(encoding="utf-8")
    sql_sans_commentaires = "\n".join(
        ligne for ligne in sql.splitlines() if not ligne.lstrip().startswith("--")
    )
    return set(
        re.findall(
            r"^\s*CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)",
            sql_sans_commentaires,
            re.IGNORECASE | re.MULTILINE,
        )
    )


def _lire_tables_orm() -> set[str]:
    """Retourne les `__tablename__` des modèles SQLAlchemy chargés."""
    from src.core.models import Base, charger_tous_modeles  # noqa: PLC0415

    charger_tous_modeles()
    return {mapper.class_.__tablename__ for mapper in Base.registry.mappers}



def _detecter_indexes_dupliques() -> list[str]:
    """Détecte toute création d'index résiduelle dans 13_views.sql."""
    contenu = VIEWS_FILE.read_text(encoding="utf-8")
    return re.findall(
        r"^\s*CREATE\s+(?:UNIQUE\s+)?INDEX\b.*$",
        contenu,
        re.IGNORECASE | re.MULTILINE,
    )



def _instructions_migrations() -> list[str]:
    """Retourne les lignes SQL utiles de 17_migrations_absorbees.sql."""
    contenu = MIGRATIONS_FILE.read_text(encoding="utf-8")
    return [
        ligne.strip()
        for ligne in contenu.splitlines()
        if ligne.strip() and not ligne.lstrip().startswith("--")
    ]



def main() -> int:
    """Exécute l'audit et retourne 0 si tout est cohérent."""
    if not SQL_INIT.exists():
        print(f"❌ Fichier manquant : {SQL_INIT}")
        return 1

    sql_tables = _lire_tables_sql()
    orm_tables = _lire_tables_orm()

    manquantes = sorted(orm_tables - sql_tables)
    orphelines = sorted(sql_tables - orm_tables - set(TABLES_SQL_SANS_ORM))
    indexes_dupliques = _detecter_indexes_dupliques()
    migrations = _instructions_migrations()

    print("=== Audit ORM ↔ SQL ===")
    print(f"Tables SQL : {len(sql_tables)}")
    print(f"Tables ORM : {len(orm_tables)}")
    print(f"Orphelines documentées : {len(TABLES_SQL_SANS_ORM)}")
    print()

    erreurs = False

    if manquantes:
        erreurs = True
        print("❌ Tables ORM absentes du SQL :")
        for table in manquantes:
            print(f"   - {table}")
    else:
        print("✅ Toutes les tables ORM sont présentes dans INIT_COMPLET.sql")

    if orphelines:
        erreurs = True
        print("❌ Nouvelles tables SQL orphelines détectées :")
        for table in orphelines:
            print(f"   - {table}")
    else:
        print("✅ Aucune nouvelle table SQL orpheline détectée")

    if indexes_dupliques:
        erreurs = True
        print("❌ CREATE INDEX détecté(s) dans 13_views.sql :")
        for index in indexes_dupliques:
            print(f"   - {index}")
    else:
        print("✅ 13_views.sql ne contient plus d'indexes dupliqués")

    if not migrations:
        erreurs = True
        print("❌ 17_migrations_absorbees.sql est encore vide côté instructions SQL")
    else:
        print(f"✅ 17_migrations_absorbees.sql contient {len(migrations)} instruction(s) SQL")

    return 1 if erreurs else 0


if __name__ == "__main__":
    raise SystemExit(main())
