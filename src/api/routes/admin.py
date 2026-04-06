"""
Routes d'administration — point d'entrée & rétro-compatibilité.

Le code a été réparti dans :
- admin_shared.py        : Schémas, constantes, helpers partagés
- admin_audit.py         : Audit logs & Events
- admin_jobs.py          : Jobs & Bridges
- admin_operations.py    : Services Health, Schéma SQL
- admin_notifications.py : Notifications (test, templates, simulation, historique, queue)
- admin_ia_console.py    : IA (métriques, console)
- admin_cache.py         : Cache (purge, clear, stats)
- admin_users.py         : Utilisateurs (liste, désactivation, impersonation)
- admin_infra.py         : DB, Config, Console, DevTools, Seed, Reset

Ce fichier conserve les re-exports utilisés par d'autres modules.
"""

# Re-exports consommés par d'autres modules
from src.api.routes.admin_shared import (  # noqa: F401
    est_mode_test_actif,
    router,
    _resumer_api_metrics,
)

# Importer les sous-modules pour enregistrer les endpoints sur le router partagé
from src.api.routes import admin_audit as _audit  # noqa: F401
from src.api.routes import admin_jobs as _jobs  # noqa: F401
from src.api.routes import admin_operations as _ops  # noqa: F401
from src.api.routes import admin_notifications as _notif  # noqa: F401
from src.api.routes import admin_ia_console as _ia  # noqa: F401
from src.api.routes import admin_cache as _cache_mod  # noqa: F401
from src.api.routes import admin_users as _users  # noqa: F401
from src.api.routes import admin_infra as _infra  # noqa: F401

__all__ = ["router", "est_mode_test_actif", "_resumer_api_metrics"]
