"""Routes API pour les automations simples type 'Si -> Alors'."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/automations", tags=["Automations"])


class GenerationAutomationIARequest(BaseModel):
    """Prompt libre pour generer une regle Si->Alors."""

    prompt: str = Field(..., min_length=5, max_length=1200)


class RegleAutomationIA(BaseModel):
    """Sortie structuree attendue de l'IA pour une automation."""

    condition: dict[str, Any] = Field(default_factory=dict)
    action: dict[str, Any] = Field(default_factory=dict)
    parametres: dict[str, Any] = Field(default_factory=dict)
    nom: str = Field(default="Automation IA")


def _charger_automations(session, user: dict[str, Any]):
    from src.core.models import AutomationRegle
    from src.core.models.users import ProfilUtilisateur

    profil = None
    if user.get("email"):
        profil = session.query(ProfilUtilisateur).filter(ProfilUtilisateur.email == user["email"]).first()
    if profil is None:
        profil = session.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id.asc()).first()
    if profil is None:
        raise HTTPException(status_code=404, detail="Profil utilisateur introuvable")

    automations = (
        session.query(AutomationRegle)
        .filter(AutomationRegle.user_id == profil.id)
        .order_by(AutomationRegle.id.asc())
        .all()
    )

    return profil, automations


def _automations_par_defaut() -> list[dict[str, Any]]:
    """Jeu de règles par défaut pour les automations IA."""
    return [
        {
            "nom": "A1 — Recette mal notée → exclure des suggestions",
            "declencheur": {"type": "feedback_recette_negatif", "jours": 30},
            "action": {"type": "ajuster_suggestions_recette", "seuil_note": 2},
            "active": True,
        },
        {
            "nom": "A2 — Planning validé → générer les courses",
            "declencheur": {"type": "planning_valide", "jours": 14},
            "action": {"type": "generer_courses_planning"},
            "active": True,
        },
        {
            "nom": "A3 — Batch terminé → pré-remplir le planning",
            "declencheur": {"type": "batch_termine", "jours": 14},
            "action": {"type": "pre_remplir_planning_batch"},
            "active": True,
        },
        {
            "nom": "A4 — Gel prévu → alerte protection plantes",
            "declencheur": {"type": "meteo_alerte", "mot_cle": "gel"},
            "action": {
                "type": "notifier",
                "titre": "Protection plantes jardin",
                "message": "Gel ou froid marqué détecté : protéger les plantes sensibles aujourd’hui.",
            },
            "active": True,
        },
        {
            "nom": "A5 — Entretien en retard → tâche + notification",
            "declencheur": {"type": "tache_en_retard"},
            "action": {
                "type": "creer_tache_maison",
                "nom": "Relance entretien en retard",
                "description": "Créée automatiquement car une opération d’entretien est échue.",
                "categorie": "maintenance",
                "priorite": "haute",
                "notifier": True,
                "titre_notification": "Entretien en retard détecté",
                "message_notification": "Une tâche d’entretien en retard a été recréée automatiquement.",
            },
            "active": True,
        },
    ]


def _migrer_automations_depuis_preferences(session, profil) -> list:
    """Migration douce préférences -> AutomationRegle (POST /init uniquement, pas dans GET)."""
    from src.core.models import AutomationRegle

    preferences_modules = profil.preferences_modules or {}
    automations_pref = list(preferences_modules.get("automations", []))
    if not automations_pref:
        automations_pref = _automations_par_defaut()

    for item in automations_pref:
        session.add(
            AutomationRegle(
                user_id=profil.id,
                nom=item.get("nom") or "Nouvelle automation",
                declencheur=item.get("declencheur") or {"type": "stock_bas", "seuil": 2},
                action=item.get("action") or {"type": "ajouter_courses", "quantite": 1},
                active=bool(item.get("active", True)),
            )
        )
    session.commit()
    return (
        session.query(AutomationRegle)
        .filter(AutomationRegle.user_id == profil.id)
        .order_by(AutomationRegle.id.asc())
        .all()
    )


def _serialiser_automation(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "nom": item.nom,
        "declencheur": item.declencheur or {},
        "action": item.action or {},
        "active": bool(item.active),
        "derniere_execution": item.derniere_execution.isoformat() if item.derniere_execution else None,
        "execution_count": int(item.execution_count or 0),
    }


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_automations(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            _, automations = _charger_automations(session, user)
            items = [_serialiser_automation(item) for item in automations]
            return {"items": items, "total": len(items)}

    return await executer_async(_query)


@router.post("/init", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def initialiser_automations(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Initialise les automations depuis les préférences legacy (migration unique, idempotent)."""
    def _query():
        with executer_avec_session() as session:
            profil, automations = _charger_automations(session, user)
            if automations:
                return {"message": "Automations déjà initialisées", "total": len(automations)}
            migrees = _migrer_automations_depuis_preferences(session, profil)
            return {"message": f"{len(migrees)} automation(s) importée(s)", "total": len(migrees)}

    return await executer_async(_query)


@router.post("", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_automation(payload: dict[str, Any], user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = AutomationRegle(
                user_id=profil.id,
                nom=payload.get("nom") or "Nouvelle automation",
                declencheur=payload.get("declencheur") or {"type": "stock_bas", "seuil": 2},
                action=payload.get("action") or {"type": "ajouter_courses", "quantite": 1},
                active=bool(payload.get("active", True)),
            )
            session.add(automation)
            session.commit()
            session.refresh(automation)
            return {"message": "Automation créée", "item": _serialiser_automation(automation)}

    return await executer_async(_query)


@router.put("/{automation_id}", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def modifier_automation(
    automation_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = (
                session.query(AutomationRegle)
                .filter(
                    AutomationRegle.id == automation_id,
                    AutomationRegle.user_id == profil.id,
                )
                .first()
            )
            if automation is None:
                raise HTTPException(status_code=404, detail="Automation introuvable")

            if "nom" in payload:
                automation.nom = payload["nom"]
            if "declencheur" in payload:
                automation.declencheur = payload["declencheur"]
            if "action" in payload:
                automation.action = payload["action"]
            if "active" in payload:
                automation.active = bool(payload["active"])

            session.commit()
            return {"message": "Automation mise à jour", "item": _serialiser_automation(automation)}

    return await executer_async(_query)


@router.post("/{automation_id}/simuler", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def simuler_automation(
    automation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = (
                session.query(AutomationRegle)
                .filter(
                    AutomationRegle.id == automation_id,
                    AutomationRegle.user_id == profil.id,
                )
                .first()
            )
            if not automation:
                raise HTTPException(status_code=404, detail="Automation introuvable")
            declencheur = automation.declencheur or {}
            action = automation.action or {}
            return {
                "success": True,
                "resume": f"Si {declencheur.get('type', 'événement')} alors {action.get('type', 'action')}",
                "item": _serialiser_automation(automation),
            }

    return await executer_async(_query)


@router.post("/{automation_id}/executer-maintenant", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def executer_automation_maintenant(
    automation_id: int,
    dry_run: bool = Query(False, description="Simuler l'exécution sans persistance"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Déclenche manuellement une automation (LT-04)."""
    from src.services.utilitaires.automations_engine import obtenir_moteur_automations_service

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            service = obtenir_moteur_automations_service()
            result = service.executer_automation_par_id(
                automation_id,
                user_id=profil.id,
                dry_run=dry_run,
                db=session,
            )
            if not result.get("success"):
                raise HTTPException(status_code=404, detail=result.get("message", "Automation introuvable"))
            message = "Automation simulée" if dry_run else "Automation exécutée"
            return {"message": message, "resultat": result, "user_id": profil.id, "dry_run": dry_run}

    return await executer_async(_query)


@router.post("/generer-ia", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def generer_automation_ia(
    payload: GenerationAutomationIARequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """IA6 - Genere une regle d'automation Si->Alors depuis un prompt libre."""
    from src.services.core.base.ai_service import create_base_ai_service

    def _query() -> dict[str, Any]:
        ai_service = create_base_ai_service(
            cache_prefix="automations_ia",
            service_name="automations_ia",
            default_ttl=900,
            default_temperature=0.2,
        )

        prompt = (
            "Transforme la demande utilisateur en regle d'automation.\n"
            f"Demande: {payload.prompt}\n\n"
            "Retourne uniquement un JSON strict avec les cles:\n"
            "- nom\n"
            "- condition (dict)\n"
            "- action (dict)\n"
            "- parametres (dict)\n"
            "Exemple condition: {\"type\": \"stock_bas\", \"seuil\": 2}\n"
            "Exemple action: {\"type\": \"ajouter_courses\"}"
        )

        regle = ai_service.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=RegleAutomationIA,
            system_prompt=(
                "Tu es un moteur d'automations domestiques. "
                "Reponds en JSON valide uniquement, sans markdown."
            ),
            max_tokens=450,
            use_cache=False,
        )

        if regle is None:
            # Fallback deterministe minimal
            regle = RegleAutomationIA(
                nom="Automation IA",
                condition={"type": "evenement", "source": "manuel"},
                action={"type": "notification"},
                parametres={"message": payload.prompt[:200]},
            )

        return {
            "message": "Regle generee, previsualisez puis confirmez avant creation.",
            "regle": regle.model_dump(),
        }

    return await executer_async(_query)
