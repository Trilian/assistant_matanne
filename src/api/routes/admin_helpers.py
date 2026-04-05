"""Fonctions helpers pour les routes admin."""

from __future__ import annotations

import io
import logging
import re
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .admin_constants import (
    _FEATURE_FLAGS_PAR_DEFAUT,
    _LABELS_JOBS,
    _NAMESPACE_FEATURE_FLAGS,
    _NAMESPACE_RUNTIME_CONFIG,
    _RUNTIME_CONFIG_PAR_DEFAUT,
)
from .admin_schemas import ConfigImportRequest, FlowSimulationRequest

logger = logging.getLogger(__name__)


def _extraire_jobs_matin() -> list[str]:
    """Retourne les IDs de jobs planifiés entre 06:00 et 09:00 inclus, selon les labels connus."""
    jobs_matin: list[str] = []
    for job_id, label in _LABELS_JOBS.items():
        match = re.search(r"\((\d{2})h(\d{2})\)", label)
        if not match:
            continue
        heure = int(match.group(1))
        if 6 <= heure <= 9:
            jobs_matin.append(job_id)
    return sorted(set(jobs_matin))


def _construire_pdf_audit(entrees: list[Any], filtres: dict[str, Any]) -> bytes:
    """Construit un PDF simple des logs d'audit filtrés."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    elements: list[Any] = []

    elements.append(Paragraph("Audit Logs - Export PDF", styles["Title"]))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(f"Genere le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Paragraph(f"Nombre d'entrees : {len(entrees)}", styles["Normal"]))

    filtres_actifs = [f"{k}={v}" for k, v in filtres.items() if v not in {None, ""}]
    if filtres_actifs:
        elements.append(Paragraph(f"Filtres : {' | '.join(filtres_actifs)}", styles["Normal"]))
    elements.append(Spacer(1, 0.35 * cm))

    lignes = [["Timestamp", "Action", "Source", "Entite", "Utilisateur"]]
    for entry in entrees:
        lignes.append([
            entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "",
            str(entry.action or "")[:45],
            str(entry.source or "")[:25],
            str(entry.entite_type or "")[:30],
            str(entry.utilisateur_id or "")[:28],
        ])

    table = Table(lignes, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def _lire_namespace_persistant(
    namespace: str,
    fallback: dict[str, Any],
    *,
    user_id: str = "global",
) -> dict[str, Any]:
    """Lit une configuration persistante dans ``etats_persistants`` (best-effort)."""
    from src.api.utils import executer_avec_session

    try:
        from src.core.models import EtatPersistantDB

        with executer_avec_session() as session:
            row = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == namespace,
                    EtatPersistantDB.user_id == user_id,
                )
                .first()
            )
            if row and isinstance(row.data, dict):
                return {**fallback, **row.data}
    except Exception:
        logger.debug("Namespace persistant indisponible: %s", namespace, exc_info=True)
    return dict(fallback)


def _ecrire_namespace_persistant(
    namespace: str,
    values: dict[str, Any],
    *,
    user_id: str = "global",
) -> dict[str, Any]:
    """Écrit une configuration persistante dans ``etats_persistants`` (best-effort)."""
    from src.api.utils import executer_avec_session

    from src.core.models import EtatPersistantDB

    with executer_avec_session() as session:
        row = (
            session.query(EtatPersistantDB)
            .filter(
                EtatPersistantDB.namespace == namespace,
                EtatPersistantDB.user_id == user_id,
            )
            .first()
        )
        if row is None:
            row = EtatPersistantDB(namespace=namespace, user_id=user_id, data={})
            session.add(row)

        current_data = row.data if isinstance(row.data, dict) else {}
        row.data = {**current_data, **values}
        session.commit()
        return dict(row.data)


def est_mode_test_actif() -> bool:
    """Vérifie si le Mode Test admin est activé (best-effort, False par défaut)."""
    try:
        flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
        return bool(flags.get("admin.mode_test", False))
    except Exception:
        return False


def _catalogue_actions_services() -> list[dict[str, Any]]:
    """Retourne le catalogue d'actions de services exécutables manuellement."""
    return [
        {
            "id": "dashboard.score_bien_etre.recalculer",
            "service": "score_bien_etre",
            "description": "Recalculer immédiatement le score bien-être.",
            "dry_run": False,
        },
        {
            "id": "dashboard.points_famille.recalculer",
            "service": "points_famille",
            "description": "Recalculer les points famille.",
            "dry_run": False,
        },
        {
            "id": "automations.executer",
            "service": "moteur_automations",
            "description": "Exécuter le moteur d'automations actif.",
            "dry_run": True,
        },
        {
            "id": "ia.suggestions.regenerer",
            "service": "ia",
            "description": "Forcer le recalcul des suggestions recettes, activités et weekend.",
            "dry_run": True,
        },
        {
            "id": "cache.clear_all",
            "service": "cache",
            "description": "Vider le cache multi-niveaux.",
            "dry_run": True,
        },
    ]


def _executer_action_service(
    action_id: str,
    *,
    dry_run: bool,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Exécute une action de service autorisée."""
    if action_id == "dashboard.score_bien_etre.recalculer":
        from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

        result = obtenir_score_bien_etre_service().calculer_score()
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": False}

    if action_id == "dashboard.points_famille.recalculer":
        from src.services.dashboard.points_famille import get_points_famille_service

        result = get_points_famille_service().calculer_points()
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": False}

    if action_id == "automations.executer":
        from src.services.utilitaires.automations_engine import obtenir_moteur_automations_service

        service = obtenir_moteur_automations_service()
        result = (
            service.executer_automations_actives_dry_run()
            if dry_run
            else service.executer_automations_actives()
        )
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": dry_run}

    if action_id == "ia.suggestions.regenerer":
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            cache.invalidate(pattern="suggestions")
            cache.invalidate(pattern="weekend")
        except Exception:
            logger.debug("Invalidation cache IA indisponible", exc_info=True)

        if dry_run:
            return {
                "status": "dry_run",
                "action_id": action_id,
                "dry_run": True,
                "result": {
                    "message": "Simulation de régénération IA uniquement.",
                    "cibles": ["recettes", "activites", "weekend"],
                },
            }

        from src.api.utils import executer_avec_session

        with executer_avec_session() as session:
            from src.services.cuisine.inter_module_inventaire_planning import (
                obtenir_service_inventaire_planning_interaction,
            )
            from src.services.famille.inter_module_meteo_activites import (
                obtenir_service_meteo_activites_interaction,
            )
            from src.services.famille.inter_module_weekend_courses import (
                obtenir_service_weekend_courses_interaction,
            )

            recettes = obtenir_service_inventaire_planning_interaction().suggerer_recettes_selon_stock(db=session)
            activites = obtenir_service_meteo_activites_interaction().suggerer_activites_selon_meteo(db=session)
            weekend = obtenir_service_weekend_courses_interaction().suggerer_fournitures_weekend(db=session)

        return {
            "status": "ok",
            "action_id": action_id,
            "dry_run": False,
            "result": {
                "recettes": recettes,
                "activites": activites,
                "weekend": weekend,
            },
        }

    if action_id == "cache.clear_all":
        if dry_run:
            return {
                "status": "dry_run",
                "action_id": action_id,
                "dry_run": True,
                "result": {"message": "Simulation uniquement - cache non vidé."},
            }

        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache.clear(levels="all")
        return {
            "status": "ok",
            "action_id": action_id,
            "dry_run": False,
            "result": {"message": "Cache vidé (L1 + L3)."},
        }

    raise HTTPException(status_code=404, detail=f"Action de service inconnue: {action_id}")


def _cibles_resync() -> list[dict[str, str]]:
    """Catalogue des cibles de re-synchronisation externe."""
    return [
        {
            "id": "garmin",
            "job_id": "garmin_sync_matinal",
            "description": "Forcer la synchronisation Garmin.",
        },
        {
            "id": "google_calendar",
            "job_id": "sync_google_calendar",
            "description": "Forcer la synchronisation Google Calendar.",
        },
        {
            "id": "openfoodfacts",
            "job_id": "sync_openfoodfacts",
            "description": "Rafraîchir le cache OpenFoodFacts.",
        },
    ]


def _resumer_api_metrics() -> dict[str, Any]:
    """Construit un résumé compact des métriques HTTP pour le cockpit admin."""
    from src.api.utils import get_metrics

    metrics = get_metrics()
    requests_total = metrics.get("requests", {}).get("total", {}) or {}
    latency = metrics.get("latency", {}) or {}

    total_requetes = sum(int(v) for v in requests_total.values())
    endpoints_tries = sorted(
        requests_total.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    latences_moyennes = [
        float(values.get("avg_ms", 0.0))
        for values in latency.values()
        if values.get("avg_ms") is not None
    ]
    p95_values = [
        float(values.get("p95_ms", 0.0))
        for values in latency.values()
        if values.get("p95_ms") is not None
    ]

    return {
        "uptime_seconds": metrics.get("uptime_seconds", 0),
        "requests_total": total_requetes,
        "top_endpoints": [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in endpoints_tries
        ],
        "latency": {
            "avg_ms": round(sum(latences_moyennes) / len(latences_moyennes), 2)
            if latences_moyennes
            else 0.0,
            "p95_ms": round(max(p95_values), 2) if p95_values else 0.0,
            "tracked_endpoints": len(latency),
        },
        "rate_limiting": metrics.get("rate_limiting", {}),
        "ai": metrics.get("ai", {}),
    }


def _serialiser_valeur_export_db(value: Any) -> Any:
    """Sérialise une valeur SQLAlchemy vers un format JSON-safe."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="ignore")
    return value


def _normaliser_nom_table(table_name: str) -> str:
    """Vérifie qu'un nom de table est sûr avant interpolation SQL."""
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
        raise HTTPException(status_code=422, detail=f"Nom de table invalide: {table_name}")
    return table_name


def _exporter_config_admin() -> dict[str, Any]:
    """Exporte la configuration runtime persistée côté admin."""
    return {
        "exported_at": datetime.now().isoformat(),
        "feature_flags": _lire_namespace_persistant(
            _NAMESPACE_FEATURE_FLAGS,
            _FEATURE_FLAGS_PAR_DEFAUT,
        ),
        "runtime_config": _lire_namespace_persistant(
            _NAMESPACE_RUNTIME_CONFIG,
            _RUNTIME_CONFIG_PAR_DEFAUT,
        ),
    }


def _importer_config_admin(body: ConfigImportRequest) -> dict[str, Any]:
    """Importe la configuration runtime persistée côté admin."""
    feature_flags = body.feature_flags or {}
    runtime_config = body.runtime_config or {}

    if not body.merge:
        feature_flags = {**_FEATURE_FLAGS_PAR_DEFAUT, **feature_flags}
        runtime_config = {**_RUNTIME_CONFIG_PAR_DEFAUT, **runtime_config}

    flags = _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, feature_flags)
    runtime = _ecrire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, runtime_config)
    return {
        "feature_flags": flags,
        "runtime_config": runtime,
    }


def _simuler_flux_admin(body: FlowSimulationRequest, user_id: str) -> dict[str, Any]:
    """Simule un flux inter-modules/notifications sans effet de bord."""
    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    event_message = body.message or {
        "peremption_j2": "3 produits expirent sous 48h.",
        "document_expirant": "1 passeport expire sous 30 jours.",
        "echec_cron_job": "Le job sync_google_calendar a échoué.",
        "rappel_courses": "Pense à terminer la liste de courses ce soir.",
        "resume_hebdo": "Résumé hebdomadaire prêt à être envoyé.",
    }[body.scenario]

    canaux = dispatcher._resoudre_canaux(  # type: ignore[attr-defined]
        user_id=user_id,
        canaux=None,
        type_evenement=body.scenario,
        categorie=None,
    )
    sequence_failover = dispatcher._construire_sequence_failover(canaux)  # type: ignore[attr-defined]

    actions = [
        {
            "type": "notification.preparee",
            "message": event_message,
            "canaux": canaux,
            "failover": sequence_failover,
        }
    ]

    if body.scenario == "peremption_j2":
        actions.append(
            {
                "type": "suggestion_recettes",
                "details": "Déclencher des suggestions de recettes anti-gaspi à partir des produits expirants.",
            }
        )
    elif body.scenario == "document_expirant":
        actions.append(
            {
                "type": "rappel_administratif",
                "details": "Créer une alerte documentaire prioritaire avec échéance visible sur le dashboard.",
            }
        )
    elif body.scenario == "echec_cron_job":
        actions.append(
            {
                "type": "audit_admin",
                "details": "Journaliser l'échec et exposer l'entrée dans le cockpit admin temps réel.",
            }
        )
    elif body.scenario == "rappel_courses":
        actions.append(
            {
                "type": "budget_sync",
                "details": "Prévoir une synchronisation budget si une liste est finalisée après le rappel.",
            }
        )
    elif body.scenario == "resume_hebdo":
        actions.append(
            {
                "type": "digest",
                "details": "Consolider les sections famille, maison et cuisine avant l'envoi.",
            }
        )

    return {
        "scenario": body.scenario,
        "user_id": user_id,
        "dry_run": body.dry_run,
        "actions": actions,
        "payload": body.payload,
    }


def _simuler_test_e2e_one_click(user_id: str) -> dict[str, Any]:
    """Construit un scénario E2E admin en une seule action."""
    etapes = [
        {
            "etape": "recette",
            "action": "Sélectionner/générer une recette candidate",
            "status": "ok",
        },
        {
            "etape": "planning",
            "action": "Planifier la recette sur la semaine en cours",
            "status": "ok",
        },
        {
            "etape": "courses",
            "action": "Générer la liste de courses à partir du planning",
            "status": "ok",
        },
        {
            "etape": "checkout",
            "action": "Marquer la liste courses comme finalisée (checkout)",
            "status": "ok",
        },
        {
            "etape": "inventaire",
            "action": "Propager les écritures inventaire post-checkout",
            "status": "ok",
        },
    ]
    return {
        "status": "ok",
        "workflow": "recette->planning->courses->checkout->inventaire",
        "user_id": user_id,
        "mode": "simulation",
        "etapes": etapes,
        "total_etapes": len(etapes),
    }
