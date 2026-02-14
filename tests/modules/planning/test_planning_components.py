# Tests planning components
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestImports:
    def test_imports(self):
        with patch("streamlit.session_state", {}):
            from src.modules.planning.components import (
                afficher_badge_charge,
            )

            assert callable(afficher_badge_charge)


class TestBadgeCharge:
    @patch("streamlit.write")
    @patch("streamlit.markdown")
    def test_faible(self, mock_md, mock_w):
        from src.modules.planning.components import afficher_badge_charge

        afficher_badge_charge(20)
        mock_md.assert_called_once()

    @patch("streamlit.write")
    @patch("streamlit.markdown")
    def test_normal(self, mock_md, mock_w):
        from src.modules.planning.components import afficher_badge_charge

        afficher_badge_charge(50)
        mock_md.assert_called_once()

    @patch("streamlit.write")
    @patch("streamlit.markdown")
    def test_intense(self, mock_md, mock_w):
        from src.modules.planning.components import afficher_badge_charge

        afficher_badge_charge(80)
        mock_md.assert_called_once()

    @patch("streamlit.write")
    @patch("streamlit.markdown")
    def test_petit(self, mock_md, mock_w):
        from src.modules.planning.components import afficher_badge_charge

        afficher_badge_charge(50, taille="petit")
        mock_w.assert_called_once()


class TestBadgePriorite:
    @patch("streamlit.write")
    def test_basse(self, m):
        from src.modules.planning.components import afficher_badge_priorite

        afficher_badge_priorite("basse")
        m.assert_called_once()

    @patch("streamlit.write")
    def test_haute(self, m):
        from src.modules.planning.components import afficher_badge_priorite

        afficher_badge_priorite("haute")
        m.assert_called_once()


class TestBadgeJules:
    @patch("streamlit.write")
    def test_adapte(self, m):
        from src.modules.planning.components import afficher_badge_activite_jules

        afficher_badge_activite_jules(True)
        m.assert_called_once()

    @patch("streamlit.write")
    def test_non_adapte(self, m):
        from src.modules.planning.components import afficher_badge_activite_jules

        afficher_badge_activite_jules(False)
        m.assert_called_once()


class TestSelecteur:
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.session_state", {})
    def test_init(self, m_btn, m_cols, m_md):
        from src.modules.planning.components import selecteur_semaine

        m_btn.return_value = False
        m_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        r = selecteur_semaine()
        assert r is not None


class TestCarteRepas:
    @patch("streamlit.caption")
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    def test_simple(self, m_cont, m_cols, m_w, m_cap):
        from src.modules.planning.components import carte_repas

        m_cont.return_value.__enter__ = MagicMock()
        m_cont.return_value.__exit__ = MagicMock()
        m_cols.return_value = [MagicMock(), MagicMock()]
        carte_repas({"type": "dej", "recette": "P", "portions": 4})
        m_cont.assert_called()


class TestCarteActivite:
    @patch("streamlit.metric")
    @patch("streamlit.caption")
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    def test_simple(self, m_cont, m_cols, m_w, m_cap, m_met):
        from src.modules.planning.components import carte_activite

        m_cont.return_value.__enter__ = MagicMock()
        m_cont.return_value.__exit__ = MagicMock()
        m_cols.return_value = [MagicMock(), MagicMock()]
        carte_activite({"titre": "Sport"})
        m_cont.assert_called()


class TestCarteProjet:
    @patch("streamlit.caption")
    @patch("streamlit.write")
    @patch("streamlit.container")
    def test_simple(self, m_cont, m_w, m_cap):
        from src.modules.planning.components import carte_projet

        m_cont.return_value.__enter__ = MagicMock()
        m_cont.return_value.__exit__ = MagicMock()
        carte_projet({"nom": "Reno", "statut": "ok"})
        m_cont.assert_called()


class TestCarteEvent:
    @patch("streamlit.caption")
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.container")
    def test_simple(self, m_cont, m_cols, m_w, m_cap):
        from src.modules.planning.components import carte_event

        m_cont.return_value.__enter__ = MagicMock()
        m_cont.return_value.__exit__ = MagicMock()
        m_cols.return_value = [MagicMock(), MagicMock()]
        carte_event({"titre": "RDV", "debut": datetime(2024, 1, 15, 10)})
        m_cont.assert_called()


class TestAlertes:
    @patch("streamlit.warning")
    def test_warning(self, m):
        from src.modules.planning.components import afficher_alerte

        afficher_alerte("Test", "warning")
        m.assert_called_once()

    @patch("streamlit.error")
    def test_error(self, m):
        from src.modules.planning.components import afficher_alerte

        afficher_alerte("Test", "error")
        m.assert_called_once()

    @patch("streamlit.success")
    def test_success(self, m):
        from src.modules.planning.components import afficher_alerte

        afficher_alerte("Test", "success")
        m.assert_called_once()

    @patch("streamlit.info")
    def test_info(self, m):
        from src.modules.planning.components import afficher_alerte

        afficher_alerte("Test", "info")
        m.assert_called_once()


class TestListeAlertes:
    @patch("streamlit.warning")
    @patch("streamlit.markdown")
    def test_vide(self, m_md, m_w):
        from src.modules.planning.components import afficher_liste_alertes

        afficher_liste_alertes([])
        m_md.assert_not_called()

    @patch("streamlit.warning")
    @patch("streamlit.markdown")
    def test_avec(self, m_md, m_w):
        from src.modules.planning.components import afficher_liste_alertes

        afficher_liste_alertes(["A1", "A2"])
        m_md.assert_called_once()


class TestStats:
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    def test_stats(self, m_cols, m_met):
        from src.modules.planning.components import afficher_stats_semaine

        m_cols.return_value = [MagicMock() for _ in range(5)]
        afficher_stats_semaine({"total_repas": 14})
        assert m_met.call_count == 5
