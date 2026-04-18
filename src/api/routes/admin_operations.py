"""Routes admin — Opérations (Services Health, Schéma SQL, Données de test).

Les endpoints suivants ont été déplacés dans des modules dédiés :
- admin_notifications.py : Notifications (test, templates, simulation, historique, queue)
- admin_ia_console.py   : IA (métriques, console)
- admin_cache.py        : Cache (purge, clear, stats)
- admin_users.py        : Utilisateurs (liste, désactivation, impersonation)
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from fastapi import Depends, Query

from src.api.dependencies import require_role
from src.api.schemas.admin import (
    AdminSanteServicesResponse,
    AdminSchemaDiffResponse,
)
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

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


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST — PLANNING
# ═══════════════════════════════════════════════════════════


@router.delete(
    "/planning/semaine",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Vider les repas planifiés d'une semaine (test)",
    description=(
        "Supprime tous les repas planifiés pour la semaine commençant à date_debut. "
        "Utile pour réinitialiser un planning de test. Nécessite le rôle admin."
    ),
)
@gerer_exception_api
async def vider_planning_semaine_test(
    date_debut: str | None = Query(
        None,
        description="Lundi de la semaine à vider (YYYY-MM-DD). Défaut : semaine courante.",
    ),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Supprime tous les Repas dont date_repas tombe dans la semaine indiquée."""

    def _delete() -> dict:
        from src.core.models.planning import Repas

        if date_debut:
            lundi = date.fromisoformat(date_debut)
        else:
            today = date.today()
            lundi = today - timedelta(days=today.weekday())

        dimanche = lundi + timedelta(days=6)

        with executer_avec_session() as session:
            nb = (
                session.query(Repas)
                .filter(Repas.date_repas >= lundi, Repas.date_repas <= dimanche)
                .delete(synchronize_session=False)
            )
            session.commit()

        _journaliser_action_admin(
            action="admin.planning.vider_semaine",
            entite_type="repas",
            utilisateur_id=str(user.get("id", "admin")),
            details={
                "semaine_debut": str(lundi),
                "semaine_fin": str(dimanche),
                "nb_supprimes": nb,
            },
        )
        return MessageResponse(
            message=f"{nb} repas supprimé(s) pour la semaine du {lundi.strftime('%d/%m/%Y')}",
            id=nb,
        )

    return await executer_async(_delete)
