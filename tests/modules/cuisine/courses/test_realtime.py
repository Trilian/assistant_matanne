"""
Tests pour src/modules/cuisine/courses/realtime.py

Couverture complète des fonctions UI synchronisation temps réel courses.
"""

from unittest.mock import MagicMock, patch


class MockSessionState(dict):
    """Mock pour session_state qui supporte l'accès par attribut."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        self[name] = value

    def get(self, key, default=None):
        return super().get(key, default)


class TestInitRealtimeSync:
    """Tests pour _init_realtime_sync()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        assert _init_realtime_sync is not None

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_init_not_initialized(self, mock_st, mock_service):
        """Test initialisation première fois."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        session_state = MockSessionState({})
        mock_st.session_state = session_state

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.join_list.return_value = True
        mock_service.return_value = sync_svc

        _init_realtime_sync()

        assert session_state.get("realtime_initialized") is True
        sync_svc.join_list.assert_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_init_already_initialized(self, mock_st, mock_service):
        """Test déjà initialisé."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        mock_st.session_state = MockSessionState({"realtime_initialized": True})

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        mock_service.return_value = sync_svc

        _init_realtime_sync()

        sync_svc.join_list.assert_not_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_init_not_configured(self, mock_st, mock_service):
        """Test service non configuré."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        mock_st.session_state = MockSessionState({})

        sync_svc = MagicMock()
        sync_svc.is_configured = False
        mock_service.return_value = sync_svc

        _init_realtime_sync()

        sync_svc.join_list.assert_not_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    @patch("src.modules.cuisine.courses.realtime.logger")
    def test_init_exception(self, mock_logger, mock_st, mock_service):
        """Test gestion exception."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        mock_st.session_state = MockSessionState({})
        mock_service.side_effect = Exception("Service error")

        _init_realtime_sync()

        mock_logger.warning.assert_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_init_with_user_info(self, mock_st, mock_service):
        """Test avec info utilisateur."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        mock_st.session_state = MockSessionState(
            {
                "user_id": "user123",
                "user_name": "Alice",
                "liste_active_id": 5,
            }
        )

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.join_list.return_value = True
        mock_service.return_value = sync_svc

        _init_realtime_sync()

        sync_svc.join_list.assert_called_with(5, "user123", "Alice")

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_init_join_failed(self, mock_st, mock_service):
        """Test échec join_list."""
        from src.modules.cuisine.courses.realtime import _init_realtime_sync

        session_state = MockSessionState({})
        mock_st.session_state = session_state

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.join_list.return_value = False
        mock_service.return_value = sync_svc

        _init_realtime_sync()

        assert session_state.get("realtime_initialized") is not True


class TestRenderRealtimeStatus:
    """Tests pour afficher_realtime_status()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.realtime import afficher_realtime_status

        assert afficher_realtime_status is not None

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_render_not_configured(self, mock_st, mock_service):
        """Test service non configuré."""
        from src.modules.cuisine.courses.realtime import afficher_realtime_status

        sync_svc = MagicMock()
        sync_svc.is_configured = False
        mock_service.return_value = sync_svc

        afficher_realtime_status()

        # sidebar should not be used when not configured
        assert True  # Just check no exception

    @patch("src.ui.views.synchronisation.afficher_indicateur_presence")
    @patch("src.ui.views.synchronisation.afficher_statut_synchronisation")
    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_render_configured_no_typing(
        self, mock_st, mock_service, mock_render_sync, mock_render_presence
    ):
        """Test service configuré sans utilisateurs qui tapent."""
        from src.modules.cuisine.courses.realtime import afficher_realtime_status

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.users_present = {}
        mock_service.return_value = sync_svc

        sidebar_mock = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=sidebar_mock)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)

        afficher_realtime_status()

        # Just check no exception - functions are called internally
        assert True

    @patch("src.ui.views.synchronisation.afficher_indicateur_frappe")
    @patch("src.ui.views.synchronisation.afficher_indicateur_presence")
    @patch("src.ui.views.synchronisation.afficher_statut_synchronisation")
    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_render_with_typing_users(
        self, mock_st, mock_service, mock_render_sync, mock_render_presence, mock_render_typing
    ):
        """Test avec utilisateurs qui tapent."""
        from src.modules.cuisine.courses.realtime import afficher_realtime_status

        typing_user = MagicMock()
        typing_user.is_typing = True

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.users_present = {"user1": typing_user}
        mock_service.return_value = sync_svc

        sidebar_mock = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=sidebar_mock)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)

        afficher_realtime_status()

        # Just check no exception
        assert True

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    @patch("src.modules.cuisine.courses.realtime.logger")
    def test_render_exception(self, mock_logger, mock_st, mock_service):
        """Test gestion exception."""
        from src.modules.cuisine.courses.realtime import afficher_realtime_status

        mock_service.side_effect = Exception("Service error")

        afficher_realtime_status()

        mock_logger.debug.assert_called()


class TestBroadcastArticleChange:
    """Tests pour _broadcast_article_change()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        assert _broadcast_article_change is not None

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_not_configured(self, mock_st, mock_service):
        """Test service non configuré."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        sync_svc = MagicMock()
        sync_svc.is_configured = False
        mock_service.return_value = sync_svc

        _broadcast_article_change("added", {"id": 1, "nom": "Test"})

        sync_svc.broadcast_item_added.assert_not_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_not_connected(self, mock_st, mock_service):
        """Test non connecté."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = False
        mock_service.return_value = sync_svc

        _broadcast_article_change("added", {"id": 1})

        sync_svc.broadcast_item_added.assert_not_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_added(self, mock_st, mock_service):
        """Test broadcast ajout."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({"liste_active_id": 2})

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = True
        mock_service.return_value = sync_svc

        article_data = {"id": 5, "nom": "Lait"}
        _broadcast_article_change("added", article_data)

        sync_svc.broadcast_item_added.assert_called_with(2, article_data)

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_checked(self, mock_st, mock_service):
        """Test broadcast coché."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({"liste_active_id": 3})

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = True
        mock_service.return_value = sync_svc

        article_data = {"id": 10, "achete": True}
        _broadcast_article_change("checked", article_data)

        sync_svc.broadcast_item_checked.assert_called_with(3, 10, True)

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_deleted(self, mock_st, mock_service):
        """Test broadcast supprimé."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({"liste_active_id": 4})

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = True
        mock_service.return_value = sync_svc

        article_data = {"id": 15}
        _broadcast_article_change("deleted", article_data)

        sync_svc.broadcast_item_deleted.assert_called_with(4, 15)

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    @patch("src.modules.cuisine.courses.realtime.logger")
    def test_broadcast_exception(self, mock_logger, mock_st, mock_service):
        """Test gestion exception."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({"liste_active_id": 1})
        mock_service.side_effect = Exception("Broadcast error")

        _broadcast_article_change("added", {"id": 1})

        mock_logger.debug.assert_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_unknown_event(self, mock_st, mock_service):
        """Test événement inconnu."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({"liste_active_id": 1})

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = True
        mock_service.return_value = sync_svc

        _broadcast_article_change("unknown", {"id": 1})

        # None of the broadcast methods should be called
        sync_svc.broadcast_item_added.assert_not_called()
        sync_svc.broadcast_item_checked.assert_not_called()
        sync_svc.broadcast_item_deleted.assert_not_called()

    @patch("src.modules.cuisine.courses.realtime.get_realtime_sync_service")
    @patch("src.modules.cuisine.courses.realtime.st")
    def test_broadcast_default_liste_id(self, mock_st, mock_service):
        """Test liste_id par défaut."""
        from src.modules.cuisine.courses.realtime import _broadcast_article_change

        mock_st.session_state = MockSessionState({})  # No liste_active_id

        sync_svc = MagicMock()
        sync_svc.is_configured = True
        sync_svc.state.connected = True
        mock_service.return_value = sync_svc

        _broadcast_article_change("added", {"id": 1})

        sync_svc.broadcast_item_added.assert_called_with(1, {"id": 1})  # Default liste_id=1


class TestRealtimeModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import realtime

        assert "_init_realtime_sync" in realtime.__all__
        assert "afficher_realtime_status" in realtime.__all__
        assert "_broadcast_article_change" in realtime.__all__
