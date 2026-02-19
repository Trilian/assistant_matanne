"""
Package Utilisateur - Services liés à l'utilisateur.

Regroupe:
- auth: Authentification Supabase
- historique: Historique des actions utilisateur
- preferences: Préférences utilisateur persistantes

Usage:
    from src.services.core.utilisateur import (
        # Auth
        AuthService, get_auth_service, UserProfile, AuthResult, Role, Permission,
        afficher_login_form, afficher_user_menu, afficher_profile_settings,
        require_authenticated, require_role,
        # Historique
        ActionHistoryService, get_action_history_service,
        ActionType, ActionEntry, ActionFilter, ActionStats,
        afficher_activity_timeline, afficher_user_activity, afficher_activity_stats,
        # Préférences
        UserPreferenceService, get_user_preference_service,
    )
"""

# ═══════════════════════════════════════════════════════════
# AUTH - Authentification Supabase
# ═══════════════════════════════════════════════════════════
from .authentification import (
    AuthResult,
    AuthService,
    Permission,
    Role,
    UserProfile,
    get_auth_service,
    obtenir_service_authentification,
)

# ═══════════════════════════════════════════════════════════
# HISTORIQUE - Historique des actions utilisateur
# ═══════════════════════════════════════════════════════════
from .historique import (
    ActionEntry,
    ActionFilter,
    ActionHistoryService,
    ActionStats,
    ActionType,
    get_action_history_service,
    obtenir_service_historique_actions,
)

# ═══════════════════════════════════════════════════════════
# PRÉFÉRENCES - Préférences utilisateur persistantes
# ═══════════════════════════════════════════════════════════
from .preferences import (
    UserPreferenceService,
    get_user_preference_service,
    obtenir_service_preferences_utilisateur,
)

__all__ = [
    # Auth
    "AuthService",
    "get_auth_service",
    "obtenir_service_authentification",
    "UserProfile",
    "AuthResult",
    "Role",
    "Permission",
    # Historique
    "ActionHistoryService",
    "get_action_history_service",
    "obtenir_service_historique_actions",
    "ActionType",
    "ActionEntry",
    "ActionFilter",
    "ActionStats",
    # Préférences
    "UserPreferenceService",
    "get_user_preference_service",
    "obtenir_service_preferences_utilisateur",
]
