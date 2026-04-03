"""
Tests pour les utilitaires API (src/api/utils/).

Couvre les helpers CRUD, pagination et gestion d'exceptions.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

# ═══════════════════════════════════════════════════════════════════════
# TESTS construire_reponse_paginee
# ═══════════════════════════════════════════════════════════════════════


class TestConstruireReponsePaginee:
    """Tests pour la construction de réponses paginées."""

    def test_reponse_basique(self):
        """Retourne la structure paginée correcte."""
        from src.api.utils import construire_reponse_paginee

        result = construire_reponse_paginee(
            items=[{"id": 1}, {"id": 2}],
            total=10,
            page=1,
            page_size=2,
        )

        assert result["items"] == [{"id": 1}, {"id": 2}]
        assert result["total"] == 10
        assert result["page"] == 1
        assert result["page_size"] == 2
        assert result["pages"] == 5

    def test_calcul_pages_arrondi(self):
        """Calcule correctement le nombre de pages avec arrondi supérieur."""
        from src.api.utils import construire_reponse_paginee

        result = construire_reponse_paginee(
            items=[],
            total=11,
            page=1,
            page_size=5,
        )

        assert result["pages"] == 3  # ceil(11/5) = 3

    def test_zero_items(self):
        """Gère correctement le cas sans éléments."""
        from src.api.utils import construire_reponse_paginee

        result = construire_reponse_paginee(
            items=[],
            total=0,
            page=1,
            page_size=20,
        )

        assert result["items"] == []
        assert result["total"] == 0
        assert result["pages"] == 0

    def test_une_seule_page(self):
        """Un seul élément donne 1 page."""
        from src.api.utils import construire_reponse_paginee

        result = construire_reponse_paginee(
            items=[{"id": 1}],
            total=1,
            page=1,
            page_size=20,
        )

        assert result["pages"] == 1

    def test_avec_schema_pydantic(self):
        """Sérialise les items avec un schéma Pydantic."""
        from pydantic import BaseModel

        from src.api.utils import construire_reponse_paginee

        class ItemSchema(BaseModel):
            id: int
            nom: str

            model_config = {"from_attributes": True}

        # Simuler des objets ORM avec attributs
        mock_obj = MagicMock()
        mock_obj.id = 1
        mock_obj.nom = "Test"

        result = construire_reponse_paginee(
            items=[mock_obj],
            total=1,
            page=1,
            page_size=20,
            schema=ItemSchema,
        )

        assert result["items"] == [{"id": 1, "nom": "Test"}]

    def test_page_size_exact(self):
        """Quand total est un multiple exact de page_size."""
        from src.api.utils import construire_reponse_paginee

        result = construire_reponse_paginee(
            items=[],
            total=40,
            page=2,
            page_size=20,
        )

        assert result["pages"] == 2


# ═══════════════════════════════════════════════════════════════════════
# TESTS executer_avec_session
# ═══════════════════════════════════════════════════════════════════════


class TestExecuterAvecSession:
    """Tests pour le context manager de session DB."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_yield_session(self, mock_db):
        """Fournit une session DB fonctionnelle."""
        from src.api.utils import executer_avec_session

        mock_session = MagicMock()
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        with executer_avec_session() as session:
            assert session is mock_session

    @patch("src.core.db.obtenir_contexte_db")
    def test_releve_http_exception(self, mock_db):
        """Re-lève les HTTPException sans les transformer."""
        from src.api.utils import executer_avec_session

        mock_session = MagicMock()
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            with executer_avec_session() as session:
                raise HTTPException(status_code=404, detail="Non trouvé")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Non trouvé"

    @patch("src.core.db.obtenir_contexte_db")
    def test_convertit_exception_en_500(self, mock_db):
        """Convertit les exceptions génériques en HTTPException 500."""
        from src.api.utils import executer_avec_session

        mock_session = MagicMock()
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            with executer_avec_session() as session:
                raise ValueError("Erreur inattendue")

        assert exc_info.value.status_code == 500
        assert "erreur interne" in exc_info.value.detail.lower()


# ═══════════════════════════════════════════════════════════════════════
# TESTS gerer_exception_api
# ═══════════════════════════════════════════════════════════════════════


class TestGererExceptionApi:
    """Tests pour le décorateur de gestion d'exceptions."""

    @pytest.mark.asyncio
    async def test_passe_resultat_normal(self):
        """Retourne le résultat si pas d'exception."""
        from src.api.utils import gerer_exception_api

        @gerer_exception_api
        async def ma_route():
            return {"ok": True}

        result = await ma_route()
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_releve_http_exception(self):
        """Re-lève les HTTPException sans transformation."""
        from src.api.utils import gerer_exception_api

        @gerer_exception_api
        async def ma_route():
            raise HTTPException(status_code=403, detail="Interdit")

        with pytest.raises(HTTPException) as exc_info:
            await ma_route()

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_convertit_exception_generique(self):
        """Convertit les exceptions en HTTPException 500."""
        from src.api.utils import gerer_exception_api

        @gerer_exception_api
        async def ma_route():
            raise RuntimeError("Boom")

        with pytest.raises(HTTPException) as exc_info:
            await ma_route()

        assert exc_info.value.status_code == 500
        assert "erreur interne" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_preserve_arguments(self):
        """Passe correctement les arguments à la fonction décorée."""
        from src.api.utils import gerer_exception_api

        @gerer_exception_api
        async def ma_route(nom: str, age: int = 25):
            return {"nom": nom, "age": age}

        result = await ma_route("Alice", age=30)
        assert result == {"nom": "Alice", "age": 30}


# ═══════════════════════════════════════════════════════════════════════
# TESTS creer_dependance_session
# ═══════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests des imports du package utils."""

    def test_import_package(self):
        """Le package utils s'importe sans erreur."""
        from src.api import utils

        assert hasattr(utils, "executer_avec_session")
        assert hasattr(utils, "construire_reponse_paginee")
        assert hasattr(utils, "gerer_exception_api")

    def test_import_crud(self):
        """Le module crud s'importe directement."""
        from src.api.utils.crud import (
            construire_reponse_paginee,
            executer_avec_session,
        )

        assert callable(executer_avec_session)
        assert callable(construire_reponse_paginee)

    def test_import_exceptions(self):
        """Le module exceptions s'importe directement."""
        from src.api.utils.exceptions import gerer_exception_api

        assert callable(gerer_exception_api)
