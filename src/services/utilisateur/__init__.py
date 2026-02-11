"""
Package Utilisateur - Services liés à l'utilisateur.

Regroupe:
- auth: Authentification Supabase
- historique: Historique des actions utilisateur
- preferences: Préférences utilisateur persistantes

Usage:
    from src.services.utilisateur import (
        # Auth
        AuthService, get_auth_service, UserProfile, AuthResult, Role, Permission,
        render_login_form, render_user_menu, render_profile_settings,
        require_authenticated, require_role,
        # Historique
        ActionHistoryService, get_action_history_service,
        ActionType, ActionEntry, ActionFilter, ActionStats,
        render_activity_timeline, render_user_activity, render_activity_stats,
        # Préférences
        UserPreferenceService, get_user_preference_service,
    )
"""

# ═══════════════════════════════════════════════════════════
# AUTH - Authentification Supabase
# ═══════════════════════════════════════════════════════════
from .authentification import (
    AuthService,
    get_auth_service,
    UserProfile,
    AuthResult,
    Role,
    Permission,
    render_login_form,
    render_user_menu,
    render_profile_settings,
    require_authenticated,
    require_role,
)

# ═══════════════════════════════════════════════════════════
# HISTORIQUE - Historique des actions utilisateur
# ═══════════════════════════════════════════════════════════
from .historique import (
    ActionHistoryService,
    get_action_history_service,
    ActionType,
    ActionEntry,
    ActionFilter,
    ActionStats,
    render_activity_timeline,
    render_user_activity,
    render_activity_stats,
)

# ═══════════════════════════════════════════════════════════
# PRÉFÉRENCES - Préférences utilisateur persistantes
# ═══════════════════════════════════════════════════════════
from .preferences import (
    UserPreferenceService,
    get_user_preference_service,
)


__all__ = [
    # Auth
    "AuthService",
    "get_auth_service",
    "UserProfile",
    "AuthResult",
    "Role",
    "Permission",
    "render_login_form",
    "render_user_menu",
    "render_profile_settings",
    "require_authenticated",
    "require_role",
    # Historique
    "ActionHistoryService",
    "get_action_history_service",
    "ActionType",
    "ActionEntry",
    "ActionFilter",
    "ActionStats",
    "render_activity_timeline",
    "render_user_activity",
    "render_activity_stats",
    # Préférences
    "UserPreferenceService",
    "get_user_preference_service",
]
