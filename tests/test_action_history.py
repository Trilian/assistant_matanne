"""Tests unitaires pour le service action_history."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestActionTypeEnum:
    """Tests pour l'enum ActionType."""

    def test_types_actions_disponibles(self):
        """Vérifie les types d'actions traçables."""
        from src.services.action_history import ActionType
        
        types_attendus = [
            "RECETTE_CREATED",
            "RECETTE_UPDATED",
            "RECETTE_DELETED",
            "INVENTAIRE_ADDED",
            "INVENTAIRE_UPDATED",
            "COURSES_ITEM_CHECKED",
            "PLANNING_REPAS_ADDED",
            "SYSTEM_LOGIN",
            "SYSTEM_LOGOUT"
        ]
        
        for type_action in types_attendus:
            assert hasattr(ActionType, type_action)


class TestActionEntryModel:
    """Tests pour le modèle ActionEntry."""

    def test_action_entry_creation(self):
        """Création d'une entrée d'action."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            entity_id=1,
            description="Création de la recette 'Tarte aux pommes'"
        )
        
        assert entry.action_type == ActionType.RECETTE_CREATED
        assert entry.entity_type == "recette"
        assert entry.entity_id == 1

    def test_action_entry_timestamp_auto(self):
        """Le timestamp est généré automatiquement."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            action_type=ActionType.INVENTAIRE_ADDED,
            entity_type="inventaire",
            entity_id=42,
            description="Ajout de lait"
        )
        
        assert entry.timestamp is not None
        assert isinstance(entry.timestamp, datetime)

    def test_action_entry_avec_details(self):
        """Entrée avec détails supplémentaires."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=5,
            description="Mise à jour des ingrédients",
            details={"ancien_nom": "Tarte", "nouveau_nom": "Tarte aux pommes"}
        )
        
        assert entry.details is not None
        assert "ancien_nom" in entry.details


class TestActionFilterModel:
    """Tests pour le modèle ActionFilter."""

    def test_filter_defaults(self):
        """Valeurs par défaut du filtre."""
        from src.services.action_history import ActionFilter
        
        filtre = ActionFilter()
        
        # Pas de filtre par défaut
        assert filtre.action_types is None or filtre.action_types == []
        assert filtre.entity_type is None
        assert filtre.date_debut is None
        assert filtre.date_fin is None

    def test_filter_par_type(self):
        """Filtre par type d'action."""
        from src.services.action_history import ActionFilter, ActionType
        
        filtre = ActionFilter(
            action_types=[ActionType.RECETTE_CREATED, ActionType.RECETTE_UPDATED]
        )
        
        assert len(filtre.action_types) == 2

    def test_filter_par_periode(self):
        """Filtre par période."""
        from src.services.action_history import ActionFilter
        
        filtre = ActionFilter(
            date_debut=datetime.now() - timedelta(days=7),
            date_fin=datetime.now()
        )
        
        assert filtre.date_debut < filtre.date_fin


class TestActionStatsModel:
    """Tests pour le modèle ActionStats."""

    def test_stats_defaults(self):
        """Valeurs par défaut des stats."""
        from src.services.action_history import ActionStats
        
        stats = ActionStats()
        
        assert stats.total_actions == 0
        assert stats.actions_par_type == {}


class TestActionHistoryServiceInit:
    """Tests d'initialisation du service."""

    def test_get_action_history_service(self):
        """La factory retourne une instance."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        assert service is not None

    def test_service_methodes_requises(self):
        """Le service expose les méthodes requises."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        assert hasattr(service, 'log_action')
        assert hasattr(service, 'log_recette_created')
        assert hasattr(service, 'log_recette_updated')
        assert hasattr(service, 'log_recette_deleted')
        assert hasattr(service, 'get_history')
        assert hasattr(service, 'get_stats')


class TestComputeChanges:
    """Tests pour _compute_changes (logique pure)."""

    def test_compute_changes_ajout(self):
        """Détection d'ajout de champs."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        ancien = {"nom": "Tarte"}
        nouveau = {"nom": "Tarte", "temps_preparation": 30}
        
        changes = service._compute_changes(ancien, nouveau)
        
        assert "temps_preparation" in changes or changes.get("ajouts", [])

    def test_compute_changes_modification(self):
        """Détection de modification."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        ancien = {"nom": "Tarte", "portions": 4}
        nouveau = {"nom": "Tarte aux pommes", "portions": 4}
        
        changes = service._compute_changes(ancien, nouveau)
        
        # Le nom a changé
        assert changes is not None
        assert "nom" in str(changes)

    def test_compute_changes_suppression(self):
        """Détection de suppression de champs."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        ancien = {"nom": "Tarte", "description": "Délicieuse"}
        nouveau = {"nom": "Tarte"}
        
        changes = service._compute_changes(ancien, nouveau)
        
        assert "description" in str(changes)

    def test_compute_changes_aucun(self):
        """Pas de changement."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        ancien = {"nom": "Tarte", "portions": 4}
        nouveau = {"nom": "Tarte", "portions": 4}
        
        changes = service._compute_changes(ancien, nouveau)
        
        # Pas de changement ou dict vide
        assert changes is None or changes == {}


class TestAddToCache:
    """Tests pour _add_to_cache."""

    def test_add_to_cache_limite_taille(self):
        """Le cache a une taille limitée."""
        from src.services.action_history import get_action_history_service, ActionEntry, ActionType
        
        service = get_action_history_service()
        
        # Vider le cache
        service._cache = []
        
        # Ajouter plus que la limite
        for i in range(150):
            entry = ActionEntry(
                action_type=ActionType.RECETTE_CREATED,
                entity_type="recette",
                entity_id=i,
                description=f"Test {i}"
            )
            service._add_to_cache(entry)
        
        # Le cache ne devrait pas dépasser 100 (ou la limite configurée)
        assert len(service._cache) <= 100


class TestCanUndo:
    """Tests pour can_undo."""

    def test_can_undo_avec_cache(self):
        """Vérification si undo possible."""
        from src.services.action_history import get_action_history_service, ActionEntry, ActionType
        
        service = get_action_history_service()
        
        # Ajouter une action
        entry = ActionEntry(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            entity_id=1,
            description="Test"
        )
        service._add_to_cache(entry)
        
        # Devrait pouvoir annuler
        assert service.can_undo() == True

    def test_can_undo_cache_vide(self):
        """Pas d'undo avec cache vide."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        service._cache = []
        
        # Pas d'action à annuler
        assert service.can_undo() == False


class TestLogHelpers:
    """Tests pour les helpers de logging."""

    def test_log_recette_created(self):
        """Log de création de recette."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        recette = MagicMock()
        recette.id = 1
        recette.nom = "Tarte aux pommes"
        
        # Ne devrait pas lever d'exception
        with patch.object(service, '_save_to_database'):
            service.log_recette_created(recette)

    def test_log_recette_updated(self):
        """Log de mise à jour de recette."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        recette = MagicMock()
        recette.id = 1
        recette.nom = "Tarte aux pommes"
        
        ancien = {"nom": "Tarte"}
        
        with patch.object(service, '_save_to_database'):
            service.log_recette_updated(recette, ancien)

    def test_log_inventaire_added(self):
        """Log d'ajout à l'inventaire."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        article = MagicMock()
        article.id = 1
        article.nom = "Lait"
        article.quantite = 2
        
        with patch.object(service, '_save_to_database'):
            service.log_inventaire_added(article)

    def test_log_courses_item_checked(self):
        """Log d'article coché dans les courses."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        item = MagicMock()
        item.id = 1
        item.nom = "Pain"
        
        with patch.object(service, '_save_to_database'):
            service.log_courses_item_checked(item)

    def test_log_planning_repas_added(self):
        """Log d'ajout de repas au planning."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        repas = MagicMock()
        repas.id = 1
        repas.recette_id = 5
        repas.date_repas = datetime.now().date()
        
        with patch.object(service, '_save_to_database'):
            service.log_planning_repas_added(repas)


class TestGetHistory:
    """Tests pour get_history avec mocks."""

    @patch('src.services.action_history.get_db_context')
    def test_get_history_sans_filtre(self, mock_db):
        """Récupération de l'historique sans filtre."""
        from src.services.action_history import get_action_history_service
        
        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        
        service = get_action_history_service()
        history = service.get_history()
        
        assert isinstance(history, list)

    @patch('src.services.action_history.get_db_context')
    def test_get_history_avec_limite(self, mock_db):
        """Récupération avec limite."""
        from src.services.action_history import get_action_history_service
        
        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        
        service = get_action_history_service()
        history = service.get_history(limit=10)
        
        assert isinstance(history, list)


class TestGetStats:
    """Tests pour get_stats."""

    @patch('src.services.action_history.get_db_context')
    def test_get_stats_structure(self, mock_db):
        """Structure des statistiques."""
        from src.services.action_history import get_action_history_service
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        
        service = get_action_history_service()
        stats = service.get_stats()
        
        assert isinstance(stats, dict) or hasattr(stats, 'total_actions')
