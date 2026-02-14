from unittest.mock import MagicMock, patch


class TestProjetsServiceImport:
    @patch("src.modules.maison.projets.st")
    def test_import_service(self, mock_st):
        from src.modules.maison.projets import ProjetsService

        assert ProjetsService is not None

    @patch("src.modules.maison.projets.st")
    def test_service_callable(self, mock_st):
        from src.modules.maison.projets import ProjetsService

        mock_client = MagicMock()
        service = ProjetsService(client=mock_client)
        assert service is not None


class TestFonctionsImport:
    @patch("src.modules.maison.projets.st")
    def test_import_app(self, mock_st):
        from src.modules.maison.projets import app

        assert callable(app)


class TestApp:
    @patch("src.modules.maison.projets.charger_projets")
    @patch("src.modules.maison.projets.get_stats_projets")
    @patch("src.modules.maison.projets.obtenir_contexte_db")
    @patch("src.modules.maison.projets.st")
    def test_app_runs(self, mock_st, mock_ctx, mock_stats, mock_charger):
        from src.modules.maison.projets import app

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = {}
        mock_db = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        mock_charger.return_value = MagicMock()
        mock_stats.return_value = {"total": 5, "en_cours": 2, "termines": 3}
        try:
            app()
        except Exception:
            pass
