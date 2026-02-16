"""Tests complets pour le module barcode.py UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de st.session_state."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock Streamlit."""
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.tabs.return_value = [MagicMock() for _ in range(5)]
    mock_st.session_state = SessionStateMock(session_data or {})
    for cm in ["container", "expander", "spinner", "form"]:
        getattr(mock_st, cm).return_value.__enter__ = MagicMock(return_value=MagicMock())
        getattr(mock_st, cm).return_value.__exit__ = MagicMock(return_value=False)


@pytest.mark.unit
class TestBarcodeUI:
    """Tests pour les fonctions UI du module barcode."""

    @patch("src.modules.outils.barcode.render_import_export")
    @patch("src.modules.outils.barcode.render_gestion_barcodes")
    @patch("src.modules.outils.barcode.render_verifier_stock")
    @patch("src.modules.outils.barcode.render_ajout_rapide")
    @patch("src.modules.outils.barcode.render_scanner")
    @patch("src.modules.outils.barcode.st")
    def test_app_basic(self, mock_st, *mocks) -> None:
        """Test du rendu basique de app()."""
        from src.modules.outils.barcode import app

        setup_mock_st(mock_st)
        app()
        mock_st.markdown.assert_called()
        mock_st.tabs.assert_called_once()

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_scanner_no_input(self, mock_st, mock_srv) -> None:
        """Test scanner sans input."""
        from src.modules.outils.barcode import render_scanner

        setup_mock_st(mock_st)
        mock_st.radio.return_value = "⌨️ Manuel"  # Mode manuel
        mock_st.text_input.return_value = ""
        mock_st.button.return_value = False
        render_scanner()
        mock_st.subheader.assert_called()

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_scanner_with_valid_code(self, mock_st, mock_srv) -> None:
        """Test scanner avec code valide."""
        from src.modules.outils.barcode import render_scanner

        setup_mock_st(mock_st)
        mock_st.radio.return_value = "⌨️ Manuel"  # Mode manuel
        mock_st.text_input.return_value = "3017620422003"
        mock_st.button.return_value = True
        mock_srv.return_value.valider_barcode.return_value = (True, "EAN13")
        mock_srv.return_value.rechercher_produit.return_value = {"nom": "Nutella"}
        render_scanner()
        mock_srv.return_value.valider_barcode.assert_called()

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_scanner_with_invalid_code(self, mock_st, mock_srv) -> None:
        """Test scanner avec code invalide."""
        from src.modules.outils.barcode import render_scanner

        setup_mock_st(mock_st)
        mock_st.radio.return_value = "⌨️ Manuel"  # Mode manuel
        mock_st.text_input.return_value = "invalid"
        mock_st.button.return_value = True
        mock_srv.return_value.valider_barcode.return_value = (False, "Invalid format")
        render_scanner()
        mock_st.error.assert_called()

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_scanner_demo_mode(self, mock_st, mock_srv) -> None:
        """Test scanner en mode démo."""
        from src.modules.outils.barcode import render_scanner

        setup_mock_st(mock_st)
        mock_st.radio.return_value = "🎮 Démo (codes test)"  # Mode démo
        mock_st.selectbox.return_value = "Lait demi-écrémé 1L"
        mock_st.button.return_value = True
        mock_srv.return_value.valider_barcode.return_value = (True, "EAN13")
        render_scanner()
        mock_st.info.assert_called()  # Mode démo affiche un info

    @patch("src.modules.outils.barcode.st")
    def test_render_ajout_rapide(self, mock_st) -> None:
        """Test ajout rapide."""
        from src.modules.outils.barcode import render_ajout_rapide

        setup_mock_st(mock_st)
        mock_st.text_input.return_value = ""
        mock_st.number_input.return_value = 1
        mock_st.selectbox.return_value = "Alimentaire"
        mock_st.form_submit_button.return_value = False
        render_ajout_rapide()
        assert True

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_verifier_stock_empty(self, mock_st, mock_srv) -> None:
        """Test verification stock vide."""
        from src.modules.outils.barcode import render_verifier_stock

        setup_mock_st(mock_st)
        mock_st.text_input.return_value = ""
        mock_st.button.return_value = False
        render_verifier_stock()
        assert True

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_gestion_barcodes(self, mock_st, mock_srv) -> None:
        """Test gestion barcodes."""
        from src.modules.outils.barcode import render_gestion_barcodes

        setup_mock_st(mock_st)
        mock_srv.return_value.get_tous_barcodes.return_value = []
        render_gestion_barcodes()
        assert True

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_gestion_barcodes_with_data(self, mock_st, mock_srv) -> None:
        """Test gestion barcodes avec donnees."""
        from src.modules.outils.barcode import render_gestion_barcodes

        setup_mock_st(mock_st)
        mock_srv.return_value.get_tous_barcodes.return_value = [
            {"code": "123", "nom": "Prod1"},
            {"code": "456", "nom": "Prod2"},
        ]
        render_gestion_barcodes()
        assert True

    @patch("src.modules.outils.barcode.get_barcode_service")
    @patch("src.modules.outils.barcode.st")
    def test_render_import_export(self, mock_st, mock_srv) -> None:
        """Test import/export."""
        from src.modules.outils.barcode import render_import_export

        setup_mock_st(mock_st)
        mock_st.file_uploader.return_value = None
        mock_srv.return_value.exporter_barcodes.return_value = "code,nom\n123,Test"
        render_import_export()
        mock_st.download_button.assert_called()  # Download button affiché directement


@pytest.mark.unit
class TestGetBarcodeService:
    """Tests pour get_barcode_service."""

    @patch("src.modules.outils.barcode.BarcodeService")
    @patch("src.modules.outils.barcode.st")
    def test_creates_service(self, mock_st, mock_cls) -> None:
        """Test creation service."""
        from src.modules.outils.barcode import get_barcode_service

        mock_st.session_state = SessionStateMock({})
        get_barcode_service()
        mock_cls.assert_called_once()

    @patch("src.modules.outils.barcode.BarcodeService")
    @patch("src.modules.outils.barcode.st")
    def test_returns_cached_service(self, mock_st, mock_cls) -> None:
        """Test retourne service cache."""
        from src.modules.outils.barcode import get_barcode_service

        cached = MagicMock()
        mock_st.session_state = SessionStateMock({"barcode_service": cached})
        result = get_barcode_service()
        assert result == cached


class TestImports:
    """Tests des imports."""

    def test_import_app(self) -> None:
        """Test import app."""
        from src.modules.outils.barcode import app

        assert callable(app)

    def test_import_get_barcode_service(self) -> None:
        """Test import get_barcode_service."""
        from src.modules.outils.barcode import get_barcode_service

        assert callable(get_barcode_service)

    def test_import_render_scanner(self) -> None:
        """Test import render_scanner."""
        from src.modules.outils.barcode import render_scanner

        assert callable(render_scanner)

    def test_import_render_ajout_rapide(self) -> None:
        """Test import render_ajout_rapide."""
        from src.modules.outils.barcode import render_ajout_rapide

        assert callable(render_ajout_rapide)

    def test_import_render_verifier_stock(self) -> None:
        """Test import render_verifier_stock."""
        from src.modules.outils.barcode import render_verifier_stock

        assert callable(render_verifier_stock)

    def test_import_render_gestion_barcodes(self) -> None:
        """Test import render_gestion_barcodes."""
        from src.modules.outils.barcode import render_gestion_barcodes

        assert callable(render_gestion_barcodes)

    def test_import_render_import_export(self) -> None:
        """Test import render_import_export."""
        from src.modules.outils.barcode import render_import_export

        assert callable(render_import_export)
