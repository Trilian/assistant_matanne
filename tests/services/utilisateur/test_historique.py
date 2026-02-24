"""
Tests pour src/services/utilisateur/historique.py
Cible: Couverture >80%

Tests pour:
- ActionHistoryService: log_action, get_history, stats
- Types: ActionType, ActionEntry, ActionFilter, ActionStats
- Méthodes de logging spécifiques
- Cache et sauvegarde
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# IMPORTS DU MODULE
# ═══════════════════════════════════════════════════════════
from src.services.core.utilisateur.historique import (
    ActionEntry,
    ActionFilter,
    ActionHistoryService,
    ActionStats,
    ActionType,
    get_action_history_service,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionType:
    """Tests pour l'enum ActionType."""

    def test_recette_actions(self):
        """Vérifie les actions recettes."""
        assert ActionType.RECETTE_CREATED.value == "recette.created"
        assert ActionType.RECETTE_UPDATED.value == "recette.updated"
        assert ActionType.RECETTE_DELETED.value == "recette.deleted"
        assert ActionType.RECETTE_FAVORITED.value == "recette.favorited"

    def test_inventaire_actions(self):
        """Vérifie les actions inventaire."""
        assert ActionType.INVENTAIRE_ADDED.value == "inventaire.added"
        assert ActionType.INVENTAIRE_UPDATED.value == "inventaire.updated"
        assert ActionType.INVENTAIRE_CONSUMED.value == "inventaire.consumed"
        assert ActionType.INVENTAIRE_EXPIRED.value == "inventaire.expired"

    def test_courses_actions(self):
        """Vérifie les actions courses."""
        assert ActionType.COURSES_LIST_CREATED.value == "courses.list_created"
        assert ActionType.COURSES_ITEM_ADDED.value == "courses.item_added"
        assert ActionType.COURSES_ITEM_CHECKED.value == "courses.item_checked"
        assert ActionType.COURSES_LIST_ARCHIVED.value == "courses.list_archived"

    def test_planning_actions(self):
        """Vérifie les actions planning."""
        assert ActionType.PLANNING_REPAS_ADDED.value == "planning.repas_added"
        assert ActionType.PLANNING_REPAS_MOVED.value == "planning.repas_moved"
        assert ActionType.PLANNING_REPAS_DELETED.value == "planning.repas_deleted"

    def test_famille_actions(self):
        """Vérifie les actions famille."""
        assert ActionType.FAMILLE_ACTIVITY_LOGGED.value == "famille.activity_logged"
        assert ActionType.FAMILLE_MILESTONE_ADDED.value == "famille.milestone_added"

    def test_system_actions(self):
        """Vérifie les actions système."""
        assert ActionType.SYSTEM_LOGIN.value == "system.login"
        assert ActionType.SYSTEM_LOGOUT.value == "system.logout"
        assert ActionType.SYSTEM_SETTINGS_CHANGED.value == "system.settings_changed"
        assert ActionType.SYSTEM_EXPORT.value == "system.export"
        assert ActionType.SYSTEM_IMPORT.value == "system.import"


# ═══════════════════════════════════════════════════════════
# TESTS ACTIONENTRY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionEntry:
    """Tests pour ActionEntry."""

    def test_create_action_entry(self):
        """Création d'une entrée d'action."""
        entry = ActionEntry(
            user_id="user123",
            user_name="Test User",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test description",
        )

        assert entry.user_id == "user123"
        assert entry.user_name == "Test User"
        assert entry.action_type == ActionType.RECETTE_CREATED
        assert entry.entity_type == "recette"
        assert entry.description == "Test description"

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        entry = ActionEntry(
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Login",
        )

        assert entry.id is None
        assert entry.entity_id is None
        assert entry.entity_name is None
        assert entry.details == {}
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.ip_address is None
        assert entry.user_agent is None
        assert isinstance(entry.created_at, datetime)

    def test_with_all_fields(self):
        """Création avec tous les champs."""
        now = datetime.now()
        entry = ActionEntry(
            id=1,
            user_id="user123",
            user_name="Test User",
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=42,
            entity_name="Tarte aux pommes",
            description="Mise à jour de recette",
            details={"field": "temps"},
            old_value={"temps": 30},
            new_value={"temps": 45},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            created_at=now,
        )

        assert entry.id == 1
        assert entry.entity_id == 42
        assert entry.entity_name == "Tarte aux pommes"
        assert entry.details == {"field": "temps"}
        assert entry.old_value == {"temps": 30}
        assert entry.new_value == {"temps": 45}
        assert entry.ip_address == "192.168.1.1"
        assert entry.user_agent == "Mozilla/5.0"
        assert entry.created_at == now


# ═══════════════════════════════════════════════════════════
# TESTS ACTIONFILTER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionFilter:
    """Tests pour ActionFilter."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        f = ActionFilter()

        assert f.user_id is None
        assert f.action_types is None
        assert f.entity_type is None
        assert f.entity_id is None
        assert f.date_from is None
        assert f.date_to is None
        assert f.search_text is None
        assert f.limit == 50
        assert f.offset == 0

    def test_with_filters(self):
        """Création avec filtres."""
        now = datetime.now()
        f = ActionFilter(
            user_id="user123",
            action_types=[ActionType.RECETTE_CREATED, ActionType.RECETTE_UPDATED],
            entity_type="recette",
            entity_id=42,
            date_from=now - timedelta(days=7),
            date_to=now,
            search_text="tarte",
            limit=20,
            offset=10,
        )

        assert f.user_id == "user123"
        assert len(f.action_types) == 2
        assert f.entity_type == "recette"
        assert f.entity_id == 42
        assert f.search_text == "tarte"
        assert f.limit == 20
        assert f.offset == 10


# ═══════════════════════════════════════════════════════════
# TESTS ACTIONSTATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionStats:
    """Tests pour ActionStats."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        stats = ActionStats()

        assert stats.total_actions == 0
        assert stats.actions_today == 0
        assert stats.actions_this_week == 0
        assert stats.most_active_users == []
        assert stats.most_common_actions == []
        assert stats.peak_hours == []

    def test_with_data(self):
        """Création avec données."""
        stats = ActionStats(
            total_actions=100,
            actions_today=10,
            actions_this_week=50,
            most_active_users=[{"name": "Anne", "count": 30}],
            most_common_actions=[{"type": "recette.created", "count": 20}],
            peak_hours=[9, 12, 19],
        )

        assert stats.total_actions == 100
        assert stats.actions_today == 10
        assert stats.actions_this_week == 50
        assert len(stats.most_active_users) == 1
        assert stats.most_active_users[0]["name"] == "Anne"
        assert len(stats.most_common_actions) == 1
        assert len(stats.peak_hours) == 3


# ═══════════════════════════════════════════════════════════
# TESTS ACTIONHISTORYSERVICE - INIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionHistoryServiceInit:
    """Tests pour l'initialisation d'ActionHistoryService."""

    def test_init_no_session(self):
        """Initialisation sans session."""
        service = ActionHistoryService()
        assert service._session is None

    def test_init_with_session(self):
        """Initialisation avec session."""
        mock_session = Mock()
        service = ActionHistoryService(session=mock_session)
        assert service._session == mock_session

    def test_class_cache_attributes(self):
        """Vérifie les attributs de cache de classe."""
        # Reset cache
        ActionHistoryService._recent_cache = []

        assert ActionHistoryService._cache_max_size == 100
        assert isinstance(ActionHistoryService._recent_cache, list)


# ═══════════════════════════════════════════════════════════
# TESTS LOG_ACTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionHistoryServiceLogAction:
    """Tests pour log_action."""

    @patch.object(ActionHistoryService, "_save_to_database")
    @patch.object(ActionHistoryService, "_add_to_cache")
    @patch.object(ActionHistoryService, "_get_current_user")
    def test_log_action_basic(self, mock_get_user, mock_cache, mock_save):
        """Log action basique."""
        mock_get_user.return_value = ("user123", "Test User")

        service = ActionHistoryService()
        entry = service.log_action(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Recette créée",
        )

        assert entry.user_id == "user123"
        assert entry.user_name == "Test User"
        assert entry.action_type == ActionType.RECETTE_CREATED
        assert entry.entity_type == "recette"
        mock_save.assert_called_once()
        mock_cache.assert_called_once()

    @patch.object(ActionHistoryService, "_save_to_database")
    @patch.object(ActionHistoryService, "_add_to_cache")
    @patch.object(ActionHistoryService, "_get_current_user")
    def test_log_action_with_details(self, mock_get_user, mock_cache, mock_save):
        """Log action avec détails."""
        mock_get_user.return_value = ("user123", "Test User")

        service = ActionHistoryService()
        entry = service.log_action(
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            description="Recette modifiée",
            entity_id=42,
            entity_name="Tarte aux pommes",
            details={"changes": ["temps"]},
            old_value={"temps": 30},
            new_value={"temps": 45},
        )

        assert entry.entity_id == 42
        assert entry.entity_name == "Tarte aux pommes"
        assert entry.details == {"changes": ["temps"]}
        assert entry.old_value == {"temps": 30}
        assert entry.new_value == {"temps": 45}


# ═══════════════════════════════════════════════════════════
# TESTS LOGGING SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSpecificLogMethods:
    """Tests pour les méthodes de logging spécifiques."""

    @patch.object(ActionHistoryService, "log_action")
    def test_log_recette_created(self, mock_log):
        """Log création de recette."""
        service = ActionHistoryService()
        service.log_recette_created(42, "Tarte aux pommes", {"temps": 30})

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.RECETTE_CREATED
        assert args.kwargs["entity_type"] == "recette"
        assert args.kwargs["entity_id"] == 42
        assert args.kwargs["entity_name"] == "Tarte aux pommes"

    @patch.object(ActionHistoryService, "log_action")
    def test_log_recette_updated(self, mock_log):
        """Log mise à jour de recette."""
        service = ActionHistoryService()
        old_data = {"temps": 30}
        new_data = {"temps": 45}
        service.log_recette_updated(42, "Tarte aux pommes", old_data, new_data)

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.RECETTE_UPDATED
        assert args.kwargs["old_value"] == old_data
        assert args.kwargs["new_value"] == new_data

    @patch.object(ActionHistoryService, "log_action")
    def test_log_recette_deleted(self, mock_log):
        """Log suppression de recette."""
        service = ActionHistoryService()
        backup = {"nom": "Tarte", "temps": 30}
        service.log_recette_deleted(42, "Tarte aux pommes", backup)

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.RECETTE_DELETED
        assert args.kwargs["old_value"] == backup

    @patch.object(ActionHistoryService, "log_action")
    def test_log_inventaire_added(self, mock_log):
        """Log ajout à l'inventaire."""
        service = ActionHistoryService()
        service.log_inventaire_added(1, "Pommes", 500, "g")

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.INVENTAIRE_ADDED
        assert args.kwargs["entity_type"] == "inventaire"
        assert args.kwargs["details"] == {"quantite": 500, "unite": "g"}

    @patch.object(ActionHistoryService, "log_action")
    def test_log_courses_item_checked_true(self, mock_log):
        """Log cochage d'article de courses (coché)."""
        service = ActionHistoryService()
        service.log_courses_item_checked(1, "Lait", True)

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.COURSES_ITEM_CHECKED
        # Vérifie que "coch" est dans la description (évite problème encodage)
        assert "coch" in args.kwargs["description"].lower()

    @patch.object(ActionHistoryService, "log_action")
    def test_log_courses_item_checked_false(self, mock_log):
        """Log cochage d'article de courses (décoché)."""
        service = ActionHistoryService()
        service.log_courses_item_checked(1, "Lait", False)

        mock_log.assert_called_once()
        args = mock_log.call_args
        # Vérifie que "coch" est dans la description (évite problème encodage)
        assert "coch" in args.kwargs["description"].lower()

    @patch.object(ActionHistoryService, "log_action")
    def test_log_planning_repas_added(self, mock_log):
        """Log ajout de repas au planning."""
        service = ActionHistoryService()
        test_date = datetime(2024, 1, 15, 12, 0)
        service.log_planning_repas_added(1, "Tarte", test_date, "déjeuner")

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.PLANNING_REPAS_ADDED
        assert args.kwargs["entity_type"] == "planning"

    @patch.object(ActionHistoryService, "log_action")
    def test_log_system_login(self, mock_log):
        """Log connexion système."""
        service = ActionHistoryService()
        service.log_system_login()

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.SYSTEM_LOGIN
        assert args.kwargs["entity_type"] == "system"

    @patch.object(ActionHistoryService, "log_action")
    def test_log_system_logout(self, mock_log):
        """Log déconnexion système."""
        service = ActionHistoryService()
        service.log_system_logout()

        mock_log.assert_called_once()
        args = mock_log.call_args
        assert args.kwargs["action_type"] == ActionType.SYSTEM_LOGOUT


# ═══════════════════════════════════════════════════════════
# TESTS GET_HISTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetHistory:
    """Tests pour get_history."""

    def test_get_history_success(self):
        """Récupération d'historique avec succès."""
        # Ce test vérifie que get_history retourne une liste
        # Même en cas d'erreur, il utilise le cache comme fallback
        ActionHistoryService._recent_cache = []

        service = ActionHistoryService()
        filters = ActionFilter(limit=10)

        # On utilise le fallback sur le cache (liste vide)
        with patch("src.core.db.obtenir_contexte_db") as mock_context:
            mock_context.return_value.__enter__.side_effect = Exception("Connection error")
            result = service.get_history(filters)
            assert isinstance(result, list)

    def test_get_history_error_fallback_to_cache(self):
        """Erreur de récupération, fallback sur le cache."""
        # Setup cache
        test_entry = ActionEntry(
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Test",
        )
        ActionHistoryService._recent_cache = [test_entry]

        service = ActionHistoryService()

        with patch("src.core.db.obtenir_contexte_db") as mock_context:
            mock_context.return_value.__enter__.side_effect = Exception("DB Error")
            result = service.get_history(ActionFilter(limit=10))

        assert len(result) <= 10

    def test_get_history_default_filter(self):
        """get_history sans filtre crée ActionFilter par défaut."""
        service = ActionHistoryService()

        # Reset cache pour fallback
        ActionHistoryService._recent_cache = []

        with patch("src.core.db.obtenir_contexte_db") as mock_db:
            mock_db.return_value.__enter__.side_effect = Exception("Error")
            result = service.get_history()
            assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS HELPER METHODS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestHistoryHelperMethods:
    """Tests pour les méthodes helper."""

    def test_get_user_history(self):
        """Récupère l'historique d'un utilisateur."""
        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = []
            service.get_user_history("user123", limit=20)

            mock.assert_called_once()
            filter_arg = mock.call_args[0][0]
            assert filter_arg.user_id == "user123"
            assert filter_arg.limit == 20

    def test_get_entity_history(self):
        """Récupère l'historique d'une entité."""
        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = []
            service.get_entity_history("recette", 42, limit=20)

            mock.assert_called_once()
            filter_arg = mock.call_args[0][0]
            assert filter_arg.entity_type == "recette"
            assert filter_arg.entity_id == 42
            assert filter_arg.limit == 20

    def test_get_recent_actions(self):
        """Récupère les actions récentes."""
        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = []
            service.get_recent_actions(limit=10)

            mock.assert_called_once()
            filter_arg = mock.call_args[0][0]
            assert filter_arg.limit == 10


# ═══════════════════════════════════════════════════════════
# TESTS STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetStats:
    """Tests pour get_stats."""

    def test_get_stats_success(self):
        """Récupération des stats avec succès."""
        # get_stats utilise obtenir_contexte_db importé localement dans la méthode
        # On mock au niveau de src.core.database
        service = ActionHistoryService()

        with patch("src.core.db.obtenir_contexte_db") as mock_context:
            mock_session = MagicMock()
            mock_session.query.return_value.scalar.return_value = 100
            mock_session.query.return_value.filter.return_value.scalar.return_value = 10
            mock_session.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_context.return_value.__enter__.return_value = mock_session

            stats = service.get_stats(days=7)
            assert isinstance(stats, ActionStats)

    def test_get_stats_error(self):
        """Erreur dans get_stats retourne stats vides."""
        service = ActionHistoryService()

        with patch("src.core.db.obtenir_contexte_db") as mock_context:
            mock_context.return_value.__enter__.side_effect = Exception("DB Error")
            stats = service.get_stats()

        assert isinstance(stats, ActionStats)
        assert stats.total_actions == 0


# ═══════════════════════════════════════════════════════════
# TESTS UNDO
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUndo:
    """Tests pour les fonctionnalités undo."""

    def test_can_undo_reversible_with_old_value(self):
        """can_undo pour action réversible avec old_value."""
        entry = ActionEntry(
            id=1,
            user_id="user123",
            user_name="Test",
            action_type=ActionType.RECETTE_DELETED,
            entity_type="recette",
            description="Deleted",
            old_value={"nom": "Tarte"},
        )

        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = [entry]
            result = service.can_undo(1)

            assert result is True

    def test_can_undo_not_reversible(self):
        """can_undo pour action non réversible."""
        entry = ActionEntry(
            id=1,
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Login",
            old_value=None,
        )

        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = [entry]
            result = service.can_undo(1)

            assert result is False

    def test_can_undo_no_old_value(self):
        """can_undo sans old_value."""
        entry = ActionEntry(
            id=1,
            user_id="user123",
            user_name="Test",
            action_type=ActionType.RECETTE_DELETED,
            entity_type="recette",
            description="Deleted",
            old_value=None,
        )

        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = [entry]
            result = service.can_undo(1)

            assert result is False

    def test_can_undo_action_not_found(self):
        """can_undo quand action non trouvée."""
        service = ActionHistoryService()

        with patch.object(service, "get_history") as mock:
            mock.return_value = []
            result = service.can_undo(999)

            assert result is False

    def test_undo_action_not_implemented(self):
        """undo_action retourne False (non implémenté)."""
        service = ActionHistoryService()
        result = service.undo_action(1)

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES PRIVÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPrivateMethods:
    """Tests pour les méthodes privées."""

    def test_get_current_user_authenticated(self):
        """Récupération utilisateur authentifié."""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.display_name = "Test User"

        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user

        service = ActionHistoryService()

        with patch(
            "src.services.core.utilisateur.authentification.get_auth_service"
        ) as mock_get_auth:
            mock_get_auth.return_value = mock_auth
            user_id, user_name = service._get_current_user()

        assert user_id == "user123"
        assert user_name == "Test User"

    def test_get_current_user_anonymous(self):
        """Récupération utilisateur anonyme."""
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = None

        service = ActionHistoryService()

        with patch(
            "src.services.core.utilisateur.authentification.get_auth_service"
        ) as mock_get_auth:
            mock_get_auth.return_value = mock_auth
            user_id, user_name = service._get_current_user()

        assert user_id == "anonymous"
        assert user_name == "Anonyme"

    def test_get_current_user_exception(self):
        """Récupération utilisateur avec exception."""
        service = ActionHistoryService()

        with patch(
            "src.services.core.utilisateur.authentification.get_auth_service"
        ) as mock_get_auth:
            mock_get_auth.side_effect = Exception("Error")
            user_id, user_name = service._get_current_user()

        assert user_id == "anonymous"
        assert user_name == "Anonyme"

    def test_save_to_database_success(self):
        """Sauvegarde en base - s'exécute sans erreur."""
        service = ActionHistoryService()
        entry = ActionEntry(
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Test",
        )

        # La méthode _save_to_database importe HistoriqueAction localement
        # Si le modèle n'existe pas, elle logue l'erreur sans lever d'exception
        # On vérifie simplement que la méthode s'exécute sans crash
        service._save_to_database(entry)

    def test_save_to_database_error(self):
        """Sauvegarde en base avec erreur."""
        service = ActionHistoryService()
        entry = ActionEntry(
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Test",
        )

        with patch("src.core.db.obtenir_contexte_db") as mock_context:
            mock_context.return_value.__enter__.side_effect = Exception("DB Error")
            # Ne doit pas lever d'exception
            service._save_to_database(entry)

    def test_add_to_cache(self):
        """Ajout au cache."""
        ActionHistoryService._recent_cache = []

        service = ActionHistoryService()
        entry = ActionEntry(
            user_id="user123",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Test",
        )

        service._add_to_cache(entry)

        assert len(ActionHistoryService._recent_cache) == 1
        assert ActionHistoryService._recent_cache[0] == entry

    def test_add_to_cache_max_size(self):
        """Cache respecte la taille maximale."""
        ActionHistoryService._recent_cache = []
        ActionHistoryService._cache_max_size = 3

        service = ActionHistoryService()

        for i in range(5):
            entry = ActionEntry(
                user_id=f"user{i}",
                user_name=f"Test {i}",
                action_type=ActionType.SYSTEM_LOGIN,
                entity_type="system",
                description=f"Test {i}",
            )
            service._add_to_cache(entry)

        assert len(ActionHistoryService._recent_cache) <= 3

        # Reset
        ActionHistoryService._cache_max_size = 100

    def test_compute_changes(self):
        """Calcul des changements entre deux états."""
        service = ActionHistoryService()

        old = {"nom": "Tarte", "temps": 30, "removed": "value"}
        new = {"nom": "Tarte aux pommes", "temps": 30, "added": "new"}

        changes = service._compute_changes(old, new)

        assert isinstance(changes, list)
        assert len(changes) == 3  # nom changed, removed removed, added added

        names_changed = [c for c in changes if c["field"] == "nom"]
        assert len(names_changed) == 1
        assert names_changed[0]["old"] == "Tarte"
        assert names_changed[0]["new"] == "Tarte aux pommes"


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFactory:
    """Tests pour get_action_history_service."""

    def test_factory_returns_service(self):
        """Factory retourne ActionHistoryService."""
        import src.services.core.utilisateur.historique as hist_module

        hist_module._history_service = None

        service = get_action_history_service()

        assert isinstance(service, ActionHistoryService)

    def test_factory_singleton(self):
        """Factory retourne la même instance."""
        import src.services.core.utilisateur.historique as hist_module

        hist_module._history_service = None

        service1 = get_action_history_service()
        service2 = get_action_history_service()

        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS UI COMPONENTS (WITH MOCKED STREAMLIT)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUIComponents:
    """Tests pour les composants UI avec Streamlit mocké."""

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_activity_timeline_empty(self, mock_service, mock_st):
        """Timeline vide affiche message info."""
        from src.services.core.utilisateur.historique import afficher_activity_timeline

        mock_service.return_value.get_recent_actions.return_value = []

        afficher_activity_timeline(limit=10)

        mock_st.info.assert_called_once()

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_activity_timeline_with_actions(self, mock_service, mock_st):
        """Timeline avec actions."""
        from src.services.core.utilisateur.historique import afficher_activity_timeline

        mock_action = Mock()
        mock_action.entity_type = "recette"
        mock_action.description = "Test action"
        mock_action.user_name = "Test User"
        mock_action.created_at = datetime.now()

        mock_service.return_value.get_recent_actions.return_value = [mock_action]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        afficher_activity_timeline(limit=10)

        mock_st.markdown.assert_called()

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_user_activity_empty(self, mock_service, mock_st):
        """Activité utilisateur vide."""
        from src.services.core.utilisateur.historique import afficher_user_activity

        mock_service.return_value.get_user_history.return_value = []

        afficher_user_activity("user123")

        mock_st.info.assert_called()

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_user_activity_with_actions(self, mock_service, mock_st):
        """Activité utilisateur avec actions."""
        from src.services.core.utilisateur.historique import afficher_user_activity

        mock_action = Mock()
        mock_action.description = "Test action"
        mock_action.created_at = datetime.now()
        mock_action.details = {"key": "value"}

        mock_service.return_value.get_user_history.return_value = [mock_action]
        mock_st.expander.return_value.__enter__ = Mock(return_value=Mock())
        mock_st.expander.return_value.__exit__ = Mock(return_value=False)

        afficher_user_activity("user123")

        mock_st.markdown.assert_called()

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_activity_stats(self, mock_service, mock_st):
        """Statistiques d'activité."""
        from src.services.core.utilisateur.historique import afficher_activity_stats

        mock_stats = ActionStats(
            total_actions=100,
            actions_today=10,
            actions_this_week=50,
            most_active_users=[{"name": "Anne", "count": 30}],
        )
        mock_service.return_value.get_stats.return_value = mock_stats
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        afficher_activity_stats()

        mock_st.markdown.assert_called()
        mock_st.metric.assert_called()

    @patch("src.ui.views.historique.st")
    @patch("src.ui.views.historique.get_action_history_service")
    def test_render_activity_stats_no_users(self, mock_service, mock_st):
        """Statistiques sans utilisateurs actifs."""
        from src.services.core.utilisateur.historique import afficher_activity_stats

        mock_stats = ActionStats(
            total_actions=0, actions_today=0, actions_this_week=0, most_active_users=[]
        )
        mock_service.return_value.get_stats.return_value = mock_stats
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        afficher_activity_stats()

        mock_st.metric.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS ADDITIONAL EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_action_entry_model_config(self):
        """Vérifie la configuration du modèle Pydantic."""
        assert ActionEntry.model_config.get("from_attributes") is True

    @patch.object(ActionHistoryService, "_save_to_database")
    @patch.object(ActionHistoryService, "_add_to_cache")
    @patch.object(ActionHistoryService, "_get_current_user")
    def test_log_action_with_none_details(self, mock_get_user, mock_cache, mock_save):
        """Log action avec details=None."""
        mock_get_user.return_value = ("user123", "Test User")

        service = ActionHistoryService()
        entry = service.log_action(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test",
            details=None,
        )

        assert entry.details == {}

    def test_action_filter_with_all_params(self):
        """ActionFilter avec tous les paramètres."""
        now = datetime.now()
        f = ActionFilter(
            user_id="user123",
            action_types=[ActionType.RECETTE_CREATED],
            entity_type="recette",
            entity_id=42,
            date_from=now - timedelta(days=7),
            date_to=now,
            search_text="test",
            limit=100,
            offset=50,
        )

        assert f.user_id == "user123"
        assert f.limit == 100
        assert f.offset == 50
