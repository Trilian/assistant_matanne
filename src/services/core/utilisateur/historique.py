"""
Service d'historique des actions utilisateur.

Trace toutes les actions importantes effectuées par les utilisateurs
pour audit, debugging et fonctionnalités de type "annuler".

Fonctionnalités:
- Logging des actions CRUD
- Historique consultable par utilisateur
- Timeline d'activité
- Restauration d'états précédents

Mixins extraits (Phase 3):
- historique_queries.py: Consultation, statistiques, undo
"""

import logging
from datetime import datetime

from .historique_queries import HistoriqueQueriesMixin, HistoriqueStatsMixin, HistoriqueUndoMixin
from .historique_types import ActionEntry, ActionFilter, ActionStats, ActionType

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# SERVICE D'HISTORIQUE
# -----------------------------------------------------------


class ActionHistoryService(HistoriqueQueriesMixin, HistoriqueStatsMixin, HistoriqueUndoMixin):
    """
    Service de traçabilité des actions utilisateur.

    Enregistre toutes les actions importantes pour:
    - Audit et conformité
    - Debugging
    - Fonctionnalité "annuler"
    - Timeline d'activité

    Mixins:
    - HistoriqueQueriesMixin → Consultation et filtrage
    - HistoriqueStatsMixin → Statistiques d'activité
    - HistoriqueUndoMixin → Annulation d'actions
    """

    # Cache en mémoire pour les actions récentes (performance)
    _recent_cache: list[ActionEntry] = []
    _cache_max_size: int = 100

    def __init__(self):
        """Initialise le service."""
        pass

    # -----------------------------------------------------------
    # ENREGISTREMENT D'ACTIONS
    # -----------------------------------------------------------

    def log_action(
        self,
        action_type: ActionType,
        entity_type: str,
        description: str,
        entity_id: int | None = None,
        entity_name: str | None = None,
        details: dict | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> ActionEntry:
        """
        Enregistre une action.

        Args:
            action_type: Type d'action
            entity_type: Type d'entité (recette, inventaire, etc.)
            description: Description lisible de l'action
            entity_id: ID de l'entité concernée
            entity_name: Nom de l'entité (pour affichage)
            details: Détails additionnels
            old_value: Valeur avant modification (pour undo)
            new_value: Valeur après modification

        Returns:
            Entrée d'historique créée
        """
        user_id, user_name = self._get_current_user()

        entry = ActionEntry(
            user_id=user_id,
            user_name=user_name,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            details=details or {},
            old_value=old_value,
            new_value=new_value,
        )

        # Sauvegarder en base
        self._save_to_database(entry)

        # Ajouter au cache
        self._add_to_cache(entry)

        logger.info(f"Action logged: {action_type.value} - {description}")

        return entry

    def log_recette_created(self, recette_id: int, nom: str, details: dict = None):
        """Log création de recette."""
        return self.log_action(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' créée",
            new_value=details,
        )

    def log_recette_updated(self, recette_id: int, nom: str, old_data: dict, new_data: dict):
        """Log modification de recette."""
        changes = self._compute_changes(old_data, new_data)
        return self.log_action(
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' modifiée",
            details={"changes": changes},
            old_value=old_data,
            new_value=new_data,
        )

    def log_recette_deleted(self, recette_id: int, nom: str, backup_data: dict):
        """Log suppression de recette."""
        return self.log_action(
            action_type=ActionType.RECETTE_DELETED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' supprimée",
            old_value=backup_data,
        )

    def log_inventaire_added(self, item_id: int, nom: str, quantite: float, unite: str):
        """Log ajout à l'inventaire."""
        return self.log_action(
            action_type=ActionType.INVENTAIRE_ADDED,
            entity_type="inventaire",
            entity_id=item_id,
            entity_name=nom,
            description=f"'{nom}' ajouté à l'inventaire ({quantite} {unite})",
            details={"quantite": quantite, "unite": unite},
        )

    def log_courses_item_checked(self, liste_id: int, item_name: str, checked: bool):
        """Log cochage d'article de courses."""
        status = "coché" if checked else "décoché"
        return self.log_action(
            action_type=ActionType.COURSES_ITEM_CHECKED,
            entity_type="courses",
            entity_id=liste_id,
            entity_name=item_name,
            description=f"'{item_name}' {status}",
            details={"checked": checked},
        )

    def log_planning_repas_added(
        self, planning_id: int, recette_nom: str, date: datetime, type_repas: str
    ):
        """Log ajout de repas au planning."""
        return self.log_action(
            action_type=ActionType.PLANNING_REPAS_ADDED,
            entity_type="planning",
            entity_id=planning_id,
            entity_name=recette_nom,
            description=f"'{recette_nom}' planifié pour le {type_repas} du {date.strftime('%d/%m')}",
            details={"date": date.isoformat(), "type_repas": type_repas},
        )

    def log_system_login(self):
        """Log connexion utilisateur."""
        return self.log_action(
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Connexion à l'application",
        )

    def log_system_logout(self):
        """Log déconnexion utilisateur."""
        return self.log_action(
            action_type=ActionType.SYSTEM_LOGOUT,
            entity_type="system",
            description="Déconnexion de l'application",
        )

    # -----------------------------------------------------------
    # CONSULTATION, STATS & UNDO
    # NOTE: get_history, get_user_history, get_entity_history,
    # get_recent_actions → HistoriqueQueriesMixin
    # get_stats → HistoriqueStatsMixin
    # can_undo, undo_action → HistoriqueUndoMixin
    # (voir historique_queries.py)
    # -----------------------------------------------------------

    # -----------------------------------------------------------
    # MÉTHODES PRIVÉES
    # -----------------------------------------------------------

    def _get_current_user(self) -> tuple[str, str]:
        """Retourne (user_id, user_name) de l'utilisateur courant."""
        try:
            from src.services.core.utilisateur.authentification import get_auth_service

            auth = get_auth_service()
            user = auth.get_current_user()
            if user:
                return user.id, user.display_name
        except Exception as e:
            logger.debug("Utilisateur courant indisponible: %s", e)
        return "anonymous", "Anonyme"

    def _save_to_database(self, entry: ActionEntry):
        """Sauvegarde l'entrée en base de données."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import HistoriqueAction

            with obtenir_contexte_db() as session:
                db_entry = HistoriqueAction(
                    user_id=entry.user_id,
                    user_name=entry.user_name,
                    action_type=entry.action_type.value,
                    entity_type=entry.entity_type,
                    entity_id=entry.entity_id,
                    entity_name=entry.entity_name,
                    description=entry.description,
                    details=entry.details,
                    old_value=entry.old_value,
                    new_value=entry.new_value,
                    cree_le=entry.created_at,
                )
                session.add(db_entry)
                session.commit()
                entry.id = db_entry.id

        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {e}")

    def _add_to_cache(self, entry: ActionEntry):
        """Ajoute une entrée au cache mémoire."""
        self._recent_cache.insert(0, entry)
        if len(self._recent_cache) > self._cache_max_size:
            self._recent_cache.pop()

    def _compute_changes(self, old: dict, new: dict) -> list[dict]:
        """Calcule les changements entre deux états."""
        changes = []
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)

            if old_val != new_val:
                changes.append(
                    {
                        "field": key,
                        "old": old_val,
                        "new": new_val,
                    }
                )

        return changes


# -----------------------------------------------------------
# FACTORY
# -----------------------------------------------------------


from src.services.core.registry import service_factory


@service_factory("historique_actions", tags={"utilisateur", "audit"})
def obtenir_service_historique_actions() -> ActionHistoryService:
    """Factory pour le service d'historique (thread-safe via registre)."""
    return ActionHistoryService()


def get_action_history_service() -> ActionHistoryService:
    """Factory pour le service d'historique (alias anglais)."""
    return obtenir_service_historique_actions()


# Ré-exports UI — fonctions view rétrocompatibles
from src.ui.views.historique import (
    afficher_activite_utilisateur as afficher_user_activity,
)
from src.ui.views.historique import (
    afficher_statistiques_activite as afficher_activity_stats,
)
from src.ui.views.historique import (
    afficher_timeline_activite as afficher_activity_timeline,
)

__all__ = [
    "ActionHistoryService",
    "obtenir_service_historique_actions",
    "get_action_history_service",
    "ActionType",
    "ActionEntry",
    "ActionFilter",
    "ActionStats",
    # UI rétrocompat — réexportées depuis src.ui.views.historique
    "afficher_activity_timeline",
    "afficher_user_activity",
    "afficher_activity_stats",
]
