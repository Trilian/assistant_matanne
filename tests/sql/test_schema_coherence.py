"""
CT-12 — Test de cohérence ORM ↔ INIT_COMPLET.sql

Vérifie que chaque modèle SQLAlchemy déclaré dans src/core/models/ possède
un CREATE TABLE correspondant dans sql/INIT_COMPLET.sql.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _sql_tables() -> set[str]:
    """Parse INIT_COMPLET.sql et retourne l'ensemble des noms de tables."""
    sql_path = Path(__file__).resolve().parents[2] / "sql" / "INIT_COMPLET.sql"
    assert sql_path.exists(), f"INIT_COMPLET.sql introuvable : {sql_path}"
    sql = sql_path.read_text(encoding="utf-8")
    return set(re.findall(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)", sql, re.IGNORECASE))


def _orm_tables() -> list[tuple[str, str]]:
    """Retourne (class_name, __tablename__) pour chaque modèle ORM enregistré."""
    from src.core.models import Base, charger_tous_modeles  # noqa: PLC0415

    charger_tous_modeles()
    return [(mapper.class_.__name__, mapper.class_.__tablename__) for mapper in Base.registry.mappers]


class TestSchemaCoherence:
    """Cohérence entre les modèles ORM et le schéma SQL."""

    def test_init_complet_sql_existe(self):
        """Le fichier INIT_COMPLET.sql doit exister."""
        sql_path = Path(__file__).resolve().parents[2] / "sql" / "INIT_COMPLET.sql"
        assert sql_path.exists(), "sql/INIT_COMPLET.sql introuvable"
        assert sql_path.stat().st_size > 0, "sql/INIT_COMPLET.sql est vide"

    def test_init_complet_contient_des_tables(self):
        """INIT_COMPLET.sql doit déclarer au moins 10 tables."""
        tables = _sql_tables()
        assert len(tables) >= 10, f"Seulement {len(tables)} tables trouvées dans INIT_COMPLET.sql"

    def test_orm_contient_des_modeles(self):
        """charger_tous_modeles() doit enregistrer au moins 10 modèles ORM."""
        mappers = _orm_tables()
        assert len(mappers) >= 10, f"Seulement {len(mappers)} modèles ORM trouvés"

    @pytest.mark.parametrize("class_name,table_name", _orm_tables())
    def test_chaque_orm_a_un_create_table(self, class_name: str, table_name: str):
        """Chaque __tablename__ ORM doit correspondre à un CREATE TABLE dans le SQL."""
        sql_tables = _sql_tables()
        assert table_name in sql_tables, (
            f"Table ORM '{table_name}' (classe {class_name}) "
            f"absente de sql/INIT_COMPLET.sql\n"
            f"Tables SQL disponibles : {sorted(sql_tables)}"
        )
