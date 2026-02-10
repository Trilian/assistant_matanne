"""
Tests unitaires pour systeme.py

Module: src.core.models.systeme
Contient: Backup
"""

import pytest
from datetime import datetime

from src.core.models.systeme import Backup


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestBackup:
    """Tests pour le modèle Backup."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert Backup.__tablename__ == "backups"

    def test_creation_instance(self):
        """Test de création d'un backup."""
        backup = Backup(
            filename="backup_2026-02-10.zip",
            size_bytes=1024000,
            storage_path="/backups/2026/02/",
        )
        assert backup.filename == "backup_2026-02-10.zip"
        assert backup.size_bytes == 1024000
        assert backup.storage_path == "/backups/2026/02/"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = Backup.__table__.columns
        assert colonnes['size_bytes'].default is not None
        assert colonnes['compressed'].default is not None
        assert colonnes['version'].default is not None

    def test_tables_included(self):
        """Test du champ tables_included."""
        backup = Backup(
            filename="full_backup.zip",
            tables_included=["recettes", "ingredients", "planning"],
        )
        assert "recettes" in backup.tables_included
        assert len(backup.tables_included) == 3

    def test_row_counts(self):
        """Test du champ row_counts."""
        backup = Backup(
            filename="backup.zip",
            row_counts={"recettes": 150, "ingredients": 500},
        )
        assert backup.row_counts["recettes"] == 150
        assert backup.row_counts["ingredients"] == 500

    def test_repr(self):
        """Test de la représentation string."""
        backup = Backup(id=1, filename="test.zip", size_bytes=2048)
        result = repr(backup)
        assert "Backup" in result
        assert "test.zip" in result
        assert "2048" in result
