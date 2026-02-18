"""
Mixin de logging des actions utilisateur.

Fournit des méthodes pratiques pour enregistrer les actions courantes
(recettes, inventaire, courses, planning, système).

Note:
    Ce mixin dépend de ``self.log_action(...)`` qui DOIT être fourni
    par la classe hôte (typiquement ``ActionHistoryService``).
    Il dépend aussi de ``self._compute_changes(old, new)`` pour le diff.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from .historique_types import ActionEntry, ActionType

if TYPE_CHECKING:

    class _HistoryHost(Protocol):
        """Protocole décrivant les méthodes requises par la classe hôte."""

        def log_action(
            self,
            action_type: ActionType,
            entity_type: str,
            description: str,
            entity_id: int | None = ...,
            entity_name: str | None = ...,
            details: dict[str, Any] | None = ...,
            old_value: dict[str, Any] | None = ...,
            new_value: dict[str, Any] | None = ...,
        ) -> ActionEntry: ...

        def _compute_changes(
            self, old: dict[str, Any], new: dict[str, Any]
        ) -> list[dict[str, Any]]: ...


class ActionLoggerMixin:
    """
    Mixin de raccourcis de logging d'actions.

    Requiert que la classe hôte implémente:
    - ``log_action(action_type, entity_type, description, ...)`` → ActionEntry
    - ``_compute_changes(old: dict, new: dict)`` → list[dict]
    """

    if TYPE_CHECKING:
        # Aide le type-checker à résoudre les méthodes de la classe hôte
        log_action: _HistoryHost.log_action  # type: ignore[assignment]
        _compute_changes: _HistoryHost._compute_changes  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Recettes
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Inventaire
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Système
    # ------------------------------------------------------------------

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
