"""
Tests pour les schémas Pydantic de l'API (src/api/schemas/).

Couvre la validation, sérialisation et les cas limites.
"""

import pytest
from pydantic import ValidationError

# ═══════════════════════════════════════════════════════════════════════
# TESTS PaginationParams
# ═══════════════════════════════════════════════════════════════════════


class TestPaginationParams:
    """Tests pour les paramètres de pagination."""

    def test_valeurs_par_defaut(self):
        """Les valeurs par défaut sont page=1, page_size=20."""
        from src.api.schemas import PaginationParams

        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_valeurs_personnalisees(self):
        """Accepte des valeurs personnalisées."""
        from src.api.schemas import PaginationParams

        params = PaginationParams(page=3, page_size=50)
        assert params.page == 3
        assert params.page_size == 50

    def test_page_minimum(self):
        """Page ne peut pas être < 1."""
        from src.api.schemas import PaginationParams

        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_page_negative(self):
        """Page ne peut pas être négative."""
        from src.api.schemas import PaginationParams

        with pytest.raises(ValidationError):
            PaginationParams(page=-1)

    def test_page_size_minimum(self):
        """page_size ne peut pas être < 1."""
        from src.api.schemas import PaginationParams

        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)

    def test_page_size_maximum(self):
        """page_size ne peut pas dépasser 100."""
        from src.api.schemas import PaginationParams

        with pytest.raises(ValidationError):
            PaginationParams(page_size=101)

    def test_page_size_limite(self):
        """page_size=100 est accepté."""
        from src.api.schemas import PaginationParams

        params = PaginationParams(page_size=100)
        assert params.page_size == 100


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
# TESTS ErreurResponse
# ═══════════════════════════════════════════════════════════════════════


class TestErreurResponse:
    """Tests pour les réponses d'erreur."""

    def test_erreur_simple(self):
        """Crée une erreur avec détail uniquement."""
        from src.api.schemas import ErreurResponse

        err = ErreurResponse(detail="Non trouvé")
        assert err.detail == "Non trouvé"
        assert err.code is None
        assert err.errors is None

    def test_erreur_avec_code(self):
        """Crée une erreur avec code d'erreur."""
        from src.api.schemas import ErreurResponse

        err = ErreurResponse(detail="Accès refusé", code="FORBIDDEN")
        assert err.code == "FORBIDDEN"

    def test_erreur_avec_liste_erreurs(self):
        """Crée une erreur avec sous-erreurs de validation."""
        from src.api.schemas import ErreurResponse

        err = ErreurResponse(
            detail="Validation échouée",
            code="VALIDATION_ERROR",
            errors=[
                {"field": "nom", "message": "Champ requis"},
                {"field": "email", "message": "Format invalide"},
            ],
        )

        assert len(err.errors) == 2
        assert err.errors[0]["field"] == "nom"

    def test_serialisation_json(self):
        """Se sérialise correctement en JSON."""
        from src.api.schemas import ErreurResponse

        err = ErreurResponse(detail="Erreur serveur", code="INTERNAL")
        data = err.model_dump()

        assert data["detail"] == "Erreur serveur"
        assert data["code"] == "INTERNAL"
        assert data["errors"] is None


# ═══════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests des imports du package schemas."""

    def test_import_package(self):
        """Le package schemas s'importe sans erreur."""
        from src.api import schemas

        assert hasattr(schemas, "PaginationParams")
        assert hasattr(schemas, "ReponsePaginee")
        assert hasattr(schemas, "MessageResponse")
        assert hasattr(schemas, "ErreurResponse")

    def test_import_direct(self):
        """Imports directs depuis common.py."""
        from src.api.schemas.common import (
            ErreurResponse,
            MessageResponse,
            PaginationParams,
            ReponsePaginee,
        )

        assert PaginationParams is not None
        assert ReponsePaginee is not None
        assert MessageResponse is not None
        assert ErreurResponse is not None
