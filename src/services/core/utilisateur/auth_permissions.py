"""
Permissions et gestion des rôles pour l'authentification.

Définit:
- ROLE_PERMISSIONS: Mapping rôles → permissions autorisées
- PermissionsMixin: Mixin avec méthodes de vérification des permissions
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .auth_schemas import Permission, Role

if TYPE_CHECKING:
    from .auth_schemas import ProfilUtilisateur

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# MAPPING RÔLES → PERMISSIONS
# -----------------------------------------------------------

ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.ADMIN: list(Permission),  # Toutes les permissions
    Role.MEMBRE: [
        Permission.READ_RECIPES,
        Permission.WRITE_RECIPES,
        Permission.READ_INVENTORY,
        Permission.WRITE_INVENTORY,
        Permission.READ_PLANNING,
        Permission.WRITE_PLANNING,
    ],
    Role.INVITE: [
        Permission.READ_RECIPES,
        Permission.READ_INVENTORY,
        Permission.READ_PLANNING,
    ],
}

# Hiérarchie des rôles (du plus élevé au plus bas)
_ROLE_HIERARCHY: list[Role] = [Role.ADMIN, Role.MEMBRE, Role.INVITE]


# -----------------------------------------------------------
# FONCTIONS UTILITAIRES
# -----------------------------------------------------------


def obtenir_permissions_role(role: Role) -> list[Permission]:
    """Retourne la liste des permissions pour un rôle donné.

    Args:
        role: Rôle à interroger.

    Returns:
        Liste des permissions associées au rôle.
    """
    return ROLE_PERMISSIONS.get(role, [])


def verifier_permission(role: Role, permission: Permission) -> bool:
    """Vérifie si un rôle possède une permission donnée.

    Args:
        role: Rôle à vérifier.
        permission: Permission requise.

    Returns:
        True si le rôle possède la permission.
    """
    return permission in ROLE_PERMISSIONS.get(role, [])


def a_role_minimum(role_utilisateur: Role, role_requis: Role) -> bool:
    """Vérifie si un rôle est au moins aussi élevé qu'un rôle requis.

    Args:
        role_utilisateur: Rôle de l'utilisateur.
        role_requis: Rôle minimum requis.

    Returns:
        True si le rôle est suffisant.
    """
    try:
        idx_user = _ROLE_HIERARCHY.index(role_utilisateur)
        idx_requis = _ROLE_HIERARCHY.index(role_requis)
        return idx_user <= idx_requis  # Plus l'index est bas, plus le rôle est élevé
    except ValueError:
        return False


# -----------------------------------------------------------
# MIXIN PERMISSIONS POUR AuthService
# -----------------------------------------------------------


class PermissionsMixin:
    """Mixin ajoutant les méthodes de vérification des permissions à AuthService.

    Attend que la classe hôte implémente ``get_current_user() -> ProfilUtilisateur | None``.
    """

    def require_permission(self, permission: Permission) -> bool:
        """Vérifie si l'utilisateur courant a une permission.

        Args:
            permission: Permission requise.

        Returns:
            True si autorisé.
        """
        user: ProfilUtilisateur | None = self.get_current_user()  # type: ignore[attr-defined]

        if not user:
            return False

        return user.has_permission(permission)

    def get_user_permissions(self) -> list[Permission]:
        """Retourne les permissions de l'utilisateur connecté.

        Returns:
            Liste des permissions, vide si non connecté.
        """
        user: ProfilUtilisateur | None = self.get_current_user()  # type: ignore[attr-defined]

        if not user:
            return []

        return obtenir_permissions_role(user.role)

    def has_role_or_higher(self, required_role: Role) -> bool:
        """Vérifie si l'utilisateur a un rôle au moins aussi élevé que requis.

        Args:
            required_role: Rôle minimum requis.

        Returns:
            True si le rôle est suffisant.
        """
        user: ProfilUtilisateur | None = self.get_current_user()  # type: ignore[attr-defined]

        if not user:
            return False

        return a_role_minimum(user.role, required_role)


__all__ = [
    "ROLE_PERMISSIONS",
    "PermissionsMixin",
    "a_role_minimum",
    "obtenir_permissions_role",
    "verifier_permission",
]
