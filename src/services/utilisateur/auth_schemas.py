"""
Enums et schémas Pydantic pour l'authentification.

Définit:
- Role, Permission: Enums pour les rôles et permissions utilisateur
- UserProfile: Modèle Pydantic du profil utilisateur
- AuthResult: Résultat d'une opération d'authentification
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

# -----------------------------------------------------------
# ENUMS
# -----------------------------------------------------------


class Role(StrEnum):
    """Rôles utilisateur."""

    ADMIN = "admin"
    MEMBRE = "membre"
    INVITE = "invite"


class Permission(StrEnum):
    """Permissions granulaires."""

    READ_RECIPES = "read_recipes"
    WRITE_RECIPES = "write_recipes"
    DELETE_RECIPES = "delete_recipes"
    READ_INVENTORY = "read_inventory"
    WRITE_INVENTORY = "write_inventory"
    READ_PLANNING = "read_planning"
    WRITE_PLANNING = "write_planning"
    MANAGE_USERS = "manage_users"
    ADMIN_ALL = "admin_all"


# -----------------------------------------------------------
# MODÈLES PYDANTIC
# -----------------------------------------------------------


class UserProfile(BaseModel):
    """Profil utilisateur."""

    id: str = ""
    email: str = ""
    nom: str = ""
    prenom: str = ""
    role: Role = Role.MEMBRE
    avatar_url: str | None = None
    preferences: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    last_login: datetime | None = None

    def has_permission(self, permission: Permission) -> bool:
        """Vérifie si l'utilisateur a une permission."""
        from .auth_permissions import ROLE_PERMISSIONS

        return permission in ROLE_PERMISSIONS.get(self.role, [])

    @property
    def display_name(self) -> str:
        """Nom d'affichage."""
        if self.prenom and self.nom:
            return f"{self.prenom} {self.nom}"
        return self.email.split("@")[0] if self.email else "Utilisateur"


class AuthResult(BaseModel):
    """Résultat d'une opération d'authentification."""

    success: bool = False
    user: UserProfile | None = None
    message: str = ""
    error_code: str | None = None


__all__ = [
    "AuthResult",
    "Permission",
    "Role",
    "UserProfile",
]
