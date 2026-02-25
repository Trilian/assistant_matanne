"""
Tests pour les schémas Pydantic de l'API (src/api/schemas/).

Couvre la validation, sérialisation et les cas limites.
"""

import pytest
from pydantic import ValidationError

# ═══════════════════════════════════════════════════════════════════════
# TESTS ReponsePaginee
# ═══════════════════════════════════════════════════════════════════════


class TestReponsePaginee:
    """Tests pour la réponse paginée générique."""

    def test_creation_basique(self):
        """Crée une réponse paginée avec des données simples."""
        from src.api.schemas import ReponsePaginee

        resp = ReponsePaginee(
            items=[1, 2, 3],
            total=10,
            page=1,
            page_size=3,
            pages=4,
        )

        assert len(resp.items) == 3
        assert resp.total == 10
        assert resp.pages == 4

    def test_items_vides(self):
        """Accepte une liste vide d'items."""
        from src.api.schemas import ReponsePaginee

        resp = ReponsePaginee(
            items=[],
            total=0,
            page=1,
            page_size=20,
            pages=0,
        )

        assert resp.items == []
        assert resp.total == 0

    def test_serialisation_dict(self):
        """Se sérialise correctement en dict."""
        from src.api.schemas import ReponsePaginee

        resp = ReponsePaginee(
            items=["a", "b"],
            total=2,
            page=1,
            page_size=20,
            pages=1,
        )

        data = resp.model_dump()
        assert data["items"] == ["a", "b"]
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["pages"] == 1

    def test_items_dicts(self):
        """Fonctionne avec des items complexes (dicts)."""
        from src.api.schemas import ReponsePaginee

        resp = ReponsePaginee(
            items=[{"id": 1, "nom": "Tarte"}, {"id": 2, "nom": "Salade"}],
            total=2,
            page=1,
            page_size=20,
            pages=1,
        )

        assert resp.items[0]["nom"] == "Tarte"


# ═══════════════════════════════════════════════════════════════════════
# TESTS MessageResponse
# ═══════════════════════════════════════════════════════════════════════


class TestMessageResponse:
    """Tests pour les réponses avec message."""

    def test_message_seul(self):
        """Crée une réponse avec message uniquement."""
        from src.api.schemas import MessageResponse

        resp = MessageResponse(message="Opération réussie")
        assert resp.message == "Opération réussie"
        assert resp.id is None
        assert resp.details is None

    def test_message_avec_id(self):
        """Crée une réponse avec message et id."""
        from src.api.schemas import MessageResponse

        resp = MessageResponse(message="Créé", id=42)
        assert resp.message == "Créé"
        assert resp.id == 42

    def test_message_avec_details(self):
        """Crée une réponse avec message et détails."""
        from src.api.schemas import MessageResponse

        resp = MessageResponse(
            message="OK",
            details={"count": 5, "status": "done"},
        )

        assert resp.details["count"] == 5
        assert resp.details["status"] == "done"

    def test_serialisation_complete(self):
        """Sérialise tous les champs."""
        from src.api.schemas import MessageResponse

        resp = MessageResponse(message="Test", id=1, details={"key": "val"})
        data = resp.model_dump()

        assert data["message"] == "Test"
        assert data["id"] == 1
        assert data["details"] == {"key": "val"}


# ═══════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests des imports du package schemas."""

    def test_import_package(self):
        """Le package schemas s'importe sans erreur."""
        from src.api import schemas

        assert hasattr(schemas, "ReponsePaginee")
        assert hasattr(schemas, "MessageResponse")

    def test_import_direct(self):
        """Imports directs depuis common.py."""
        from src.api.schemas.common import (
            MessageResponse,
            ReponsePaginee,
        )

        assert ReponsePaginee is not None
        assert MessageResponse is not None
