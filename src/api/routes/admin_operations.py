"""Routes admin — Opérations (Services Health, Schéma SQL).

Les endpoints suivants ont été déplacés dans des modules dédiés :
- admin_notifications.py : Notifications (test, templates, simulation, historique, queue)
- admin_ia_console.py   : IA (métriques, console)
- admin_cache.py        : Cache (purge, clear, stats)
- admin_users.py        : Utilisateurs (liste, désactivation, impersonation)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends

from src.api.dependencies import require_role
from src.api.schemas.admin import (
    AdminSanteServicesResponse,
    AdminSchemaDiffResponse,
)
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SERVICES HEALTH
# ═══════════════════════════════════════════════════════════


@router.get(
    "/services/health",
    response_model=AdminSanteServicesResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Health check registre services",
    description="Vérifie l'état de santé de tous les services instanciés. Nécessite le rôle admin.",
)
@gerer_exception_api
async def sante_services(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Retourne le health check global du registre de services."""
    from src.api.utils import executer_async

    def _check():
        try:
            from src.services.core.registry import registre

            sante = registre.health_check_global()
            metriques = registre.obtenir_metriques()
            return {
                **sante,
                "metriques": metriques,
            }
        except Exception as exc:
            logger.warning("Impossible de vérifier l'état des services : %s", exc)
            return {
                "global_status": "error",
                "total_services": 0,
                "instantiated": 0,
                "healthy": 0,
                "erreurs": [str(exc)],
                "services": {},
            }

    return await executer_async(_check)


# ═══════════════════════════════════════════════════════════
# SCHÉMA SQL / DIFF
# ═══════════════════════════════════════════════════════════


@router.get(
    "/schema-diff",
    response_model=AdminSchemaDiffResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Comparer le schéma SQL attendu et la base active",
    description="Retourne un diff synthétique entre les fichiers SQL, la metadata ORM et la base configurée.",
)
@gerer_exception_api
async def obtenir_schema_diff_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Expose un diff lisible du schéma pour l'admin."""
    from src.api.utils import executer_async

    def _diff() -> dict[str, Any]:
        from src.core.db.schema_diff import generer_schema_diff

        diff = generer_schema_diff()
        _journaliser_action_admin(
            action="admin.schema.diff",
            entite_type="schema_sql",
            utilisateur_id=str(user.get("id", "admin")),
            details={
                "status": diff.get("status"),
                "missing_in_db": len(diff.get("missing_in_db") or []),
                "extra_in_db": len(diff.get("extra_in_db") or []),
                "column_differences": len(diff.get("column_differences") or []),
            },
        )
        return diff

    return await executer_async(_diff)


