"""Outils de comparaison du schéma SQL.

Compare le schéma attendu (SQL + metadata SQLAlchemy) avec le schéma réellement
visible depuis la base configurée.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import Any

from sqlalchemy import inspect

from src.core.db.engine import obtenir_moteur
from src.core.models.base import Base

_RACINE_PROJET = Path(__file__).resolve().parents[3]
_REGEX_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(?:public\.)?\"?([a-zA-Z0-9_]+)\"?",
    flags=re.IGNORECASE,
)


def _extraire_tables_depuis_fichiers_sql() -> set[str]:
    tables: set[str] = set()
    candidats = [
        _RACINE_PROJET / "sql" / "INIT_COMPLET.sql",
        *sorted((_RACINE_PROJET / "sql" / "schema").glob("*.sql")),
    ]

    for fichier in candidats:
        if not fichier.exists():
            continue
        contenu = fichier.read_text(encoding="utf-8", errors="ignore")
        tables.update(match.group(1) for match in _REGEX_CREATE_TABLE.finditer(contenu))

    return tables


def _extraire_tables_metadata() -> set[str]:
    import_module("src.core.models")
    return {nom.split(".")[-1] for nom in Base.metadata.tables.keys()}


def generer_schema_diff() -> dict[str, Any]:
    """Retourne un diff synthétique du schéma."""
    tables_sql = _extraire_tables_depuis_fichiers_sql()
    tables_metadata = _extraire_tables_metadata()

    resultat: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "ok",
        "sources": {
            "sql_init": str(
                (_RACINE_PROJET / "sql" / "INIT_COMPLET.sql").relative_to(_RACINE_PROJET)
            ),
            "sql_schema_dir": str((_RACINE_PROJET / "sql" / "schema").relative_to(_RACINE_PROJET)),
        },
        "summary": {
            "sql_tables": len(tables_sql),
            "metadata_tables": len(tables_metadata),
            "db_tables": 0,
            "column_differences": 0,
        },
        "sql_only": sorted(tables_sql - tables_metadata),
        "metadata_only": sorted(tables_metadata - tables_sql),
        "missing_in_db": [],
        "extra_in_db": [],
        "column_differences": [],
    }

    if resultat["sql_only"] or resultat["metadata_only"]:
        resultat["status"] = "warning"

    try:
        moteur = obtenir_moteur()
        inspecteur = inspect(moteur)
        tables_db = set(inspecteur.get_table_names())
        tables_db_filtrees = {t for t in tables_db if t != "alembic_version"}
        tables_attendues = tables_metadata or tables_sql

        resultat["summary"]["db_tables"] = len(tables_db_filtrees)
        resultat["missing_in_db"] = sorted(tables_attendues - tables_db_filtrees)
        resultat["extra_in_db"] = sorted(tables_db_filtrees - tables_attendues)

        tables_communes = sorted(tables_db_filtrees & tables_metadata)
        for table_name in tables_communes:
            colonnes_db = {str(col.get("name")) for col in inspecteur.get_columns(table_name)}
            table = Base.metadata.tables.get(table_name)
            if table is None:
                continue
            colonnes_metadata = {col.name for col in table.columns}
            manquantes = sorted(colonnes_metadata - colonnes_db)
            extras = sorted(colonnes_db - colonnes_metadata)
            if manquantes or extras:
                resultat["column_differences"].append(
                    {
                        "table": table_name,
                        "missing_columns": manquantes,
                        "extra_columns": extras,
                    }
                )

        resultat["summary"]["column_differences"] = len(resultat["column_differences"])
        if resultat["missing_in_db"] or resultat["extra_in_db"] or resultat["column_differences"]:
            resultat["status"] = "warning"
    except Exception as exc:  # pragma: no cover - dépend de la configuration DB
        resultat["status"] = "error"
        resultat["db_error"] = str(exc)

    return resultat


def formater_schema_diff_console(diff: dict[str, Any]) -> str:
    """Formate le diff pour une sortie console lisible."""
    lignes = [
        f"Statut: {diff.get('status', 'unknown')}",
        (
            "Tables — SQL: "
            f"{diff.get('summary', {}).get('sql_tables', 0)} | "
            f"Metadata: {diff.get('summary', {}).get('metadata_tables', 0)} | "
            f"DB: {diff.get('summary', {}).get('db_tables', 0)}"
        ),
    ]

    for cle, libelle in (
        ("sql_only", "Présentes dans SQL uniquement"),
        ("metadata_only", "Présentes dans metadata uniquement"),
        ("missing_in_db", "Manquantes en DB"),
        ("extra_in_db", "Supplémentaires en DB"),
    ):
        valeurs: list[str] = list(diff.get(cle) or [])
        lignes.append(f"- {libelle}: {', '.join(valeurs) if valeurs else 'aucune'}")

    if diff.get("column_differences"):
        lignes.append("- Différences de colonnes:")
        for item in diff["column_differences"]:
            lignes.append(
                f"  • {item['table']} | manquantes: {item['missing_columns'] or '[]'} | extras: {item['extra_columns'] or '[]'}"
            )

    if diff.get("db_error"):
        lignes.append(f"- Erreur DB: {diff['db_error']}")

    return "\n".join(lignes)


__all__ = ["generer_schema_diff", "formater_schema_diff_console"]
