"""
Tests unitaires pour CSSManager (src/ui/css.py).

Couvre : register, inject_all, invalidate, get_stats, reset, déduplication MD5.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestCSSManager:
    """Tests pour la classe CSSManager."""

    def _reset(self):
        """Réinitialise le singleton CSSManager entre les tests."""
        from src.ui.engine import CSSManager

        CSSManager.reset()

    def test_register_stores_block(self):
        """Register stocke un bloc CSS sous un nom."""
        from src.ui.engine import CSSManager

        self._reset()
        CSSManager.register("test-block", ".foo { color: red; }")
        stats = CSSManager.get_stats()
        assert stats["blocks"] >= 1

    def test_register_overwrites_same_name(self):
        """Register écrase un bloc existant avec le même nom."""
        from src.ui.engine import CSSManager

        self._reset()
        CSSManager.register("dup", ".a { }")
        CSSManager.register("dup", ".b { }")
        stats = CSSManager.get_stats()
        # Un seul bloc nommé "dup" â†’ count == 1
        assert stats["blocks"] == 1

    @patch("streamlit.markdown")
    def test_inject_all_calls_markdown_once(self, mock_md):
        """inject_all produit un seul appel st.markdown."""
        from src.ui.engine import CSSManager

        self._reset()
        # Simuler session_state vide
        with patch("streamlit.session_state", {}):
            CSSManager.register("a", ".a { color: red; }")
            CSSManager.register("b", ".b { color: blue; }")
            CSSManager.inject_all()

        assert mock_md.call_count == 1
        call_args = mock_md.call_args
        html = call_args[0][0]
        assert "<style>" in html
        assert ".a { color: red; }" in html
        assert ".b { color: blue; }" in html
        assert call_args[1]["unsafe_allow_html"] is True

    @patch("streamlit.markdown")
    def test_inject_all_dedup_same_hash(self, mock_md):
        """inject_all ne réinjecte pas si le hash MD5 n'a pas changé."""
        from src.ui.engine import CSSManager

        self._reset()
        session = {}
        with patch("streamlit.session_state", session):
            CSSManager.register("x", ".x { }")
            CSSManager.inject_all()
            assert mock_md.call_count == 1

            # Deuxième appel — même contenu â†’ pas d'injection
            CSSManager.inject_all()
            assert mock_md.call_count == 1

    @patch("streamlit.markdown")
    def test_inject_all_reinjects_after_invalidate(self, mock_md):
        """Après invalidate(), inject_all réinjecte le CSS."""
        from src.ui.engine import CSSManager

        self._reset()
        session = {}
        with patch("streamlit.session_state", session):
            CSSManager.register("y", ".y { }")
            CSSManager.inject_all()
            assert mock_md.call_count == 1

            CSSManager.invalidate()
            CSSManager.inject_all()
            assert mock_md.call_count == 2

    def test_reset_clears_all(self):
        """reset() vide le registre."""
        from src.ui.engine import CSSManager

        self._reset()
        CSSManager.register("z", ".z { }")
        CSSManager.reset()
        stats = CSSManager.get_stats()
        assert stats["blocks"] == 0

    def test_get_stats_structure(self):
        """get_stats retourne les clés attendues."""
        from src.ui.engine import CSSManager

        self._reset()
        stats = CSSManager.get_stats()
        assert "blocks" in stats
        assert "total_bytes" in stats


class TestLazyBarrel:
    """Tests pour le barrel PEP 562 lazy de src/ui/__init__.py."""

    def test_lazy_import_tokens(self):
        """Les tokens sont importables via le barrel."""
        from src.ui import Couleur, Espacement, Variante

        assert Couleur.PRIMARY is not None
        assert Espacement.MD is not None
        assert Variante.SUCCESS is not None

    def test_lazy_import_system(self):
        """Le système StyleSheet est importable via le barrel."""
        from src.ui import StyleSheet

        assert StyleSheet is not None

    def test_all_exports_match_lazy_imports(self):
        """__all__ correspond exactement aux clés de _LAZY_IMPORTS."""
        import src.ui as ui_module

        assert set(ui_module.__all__) == set(ui_module._LAZY_IMPORTS.keys())

    def test_unknown_attribute_raises(self):
        """Un attribut inconnu lève AttributeError."""
        import src.ui

        with pytest.raises(AttributeError, match="has no attribute"):
            _ = src.ui.something_that_does_not_exist

    def test_cached_after_first_access(self):
        """Après le premier accès, le symbole est mis en cache dans globals()."""
        import src.ui

        # Force la résolution
        _ = src.ui.Couleur
        # Vérifie qu'il est dans le module dict maintenant
        assert "Couleur" in vars(src.ui)
