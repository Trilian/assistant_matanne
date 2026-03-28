"""Routes API pour le mode Voyage."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/famille/voyages", tags=["Voyages"])


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_voyages(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.services.famille.voyage import obtenir_service_voyage

    def _query():
        service = obtenir_service_voyage()
        items = service.obtenir_resumes_voyages()
        return {"items": items, "total": len(items)}

    return await executer_async(_query)


@router.get("/templates", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_templates_voyage(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.services.famille.voyage import obtenir_service_voyage

    def _query():
        service = obtenir_service_voyage()
        service.importer_templates_defaut()
        templates = service.obtenir_templates()
        return {
            "items": [
                {
                    "id": t.id,
                    "nom": t.nom,
                    "type_voyage": t.type_voyage,
                    "membre": t.membre,
                    "description": t.description,
                    "articles": t.articles or [],
                }
                for t in templates
            ],
            "total": len(templates),
        }

    return await executer_async(_query)


@router.post("", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_voyage(payload: dict[str, Any], user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.services.famille.voyage import obtenir_service_voyage

    def _query():
        service = obtenir_service_voyage()
        voyage = service.ajouter_voyage(payload)
        if voyage is None:
            raise HTTPException(status_code=422, detail="Impossible de créer le voyage")
        return {"id": voyage.id, "message": "Voyage créé"}

    return await executer_async(_query)


@router.get("/{voyage_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def detail_voyage(voyage_id: int, user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.services.famille.voyage import obtenir_service_voyage

    def _query():
        service = obtenir_service_voyage()
        voyage = service.obtenir_voyage(voyage_id)
        if voyage is None:
            raise HTTPException(status_code=404, detail="Voyage introuvable")
        checklists = service.obtenir_checklists(voyage_id)
        return {
            "id": voyage.id,
            "titre": voyage.titre,
            "destination": voyage.destination,
            "date_depart": voyage.date_depart.isoformat(),
            "date_retour": voyage.date_retour.isoformat(),
            "type_voyage": voyage.type_voyage,
            "statut": voyage.statut,
            "budget_prevu": voyage.budget_prevu,
            "budget_reel": voyage.budget_reel,
            "participants": voyage.participants or [],
            "notes": voyage.notes,
            "checklists": [
                {
                    "id": c.id,
                    "nom": c.nom,
                    "membre": c.membre,
                    "articles": c.articles or [],
                    "pourcentage_preparation": c.pourcentage_preparation,
                }
                for c in checklists
            ],
        }

    return await executer_async(_query)


@router.post("/planifier-ia", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def planifier_voyage_ia(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un voyage + checklists par templates selon le contexte de séjour."""
    from src.services.famille.voyage import obtenir_service_voyage

    destination = (payload.get("destination") or "").strip()
    if not destination:
        raise HTTPException(status_code=422, detail="La destination est requise")

    nb_jours = int(payload.get("nb_jours") or 5)
    type_sejour = (payload.get("type_sejour") or "mer_ete").strip().lower()
    budget = payload.get("budget_prevu")
    participants = payload.get("participants") or ["Jules", "Anne", "Mathieu"]

    mapping_type = {
        "mer_ete": "mer",
        "mer_hiver": "mer",
        "montagne_hiver": "montagne",
        "montagne_ete": "montagne",
    }
    type_voyage = mapping_type.get(type_sejour, "weekend")

    debut = date.today() + (date.today() - date.today()) + (date.resolution * 30)
    retour = debut.fromordinal(debut.toordinal() + max(nb_jours - 1, 0))

    suggestions = {
        "mer_ete": [
            "Prévoir protections solaires et tenues légères",
            "Ajouter une mini-liste courses sur place pour les petits-déjeuners",
            "Alléger le planning cuisine pendant le séjour",
        ],
        "mer_hiver": [
            "Prévoir coupe-vent, plaid et activités intérieures",
            "Vérifier les horaires hors saison",
            "Privilégier des repas simples et rapides",
        ],
        "montagne_hiver": [
            "Ajouter vêtements chauds, gants et trousse secours",
            "Prévoir collations énergétiques",
            "Anticiper les temps de trajet et pauses Jules",
        ],
        "montagne_ete": [
            "Prévoir chaussures marche, gourdes et chapeaux",
            "Organiser des sorties courtes adaptées à Jules",
            "Prévoir courses fraîches à l'arrivée",
        ],
    }.get(type_sejour, ["Prévoir une checklist commune", "Adapter les repas au séjour"])

    def _query():
        service = obtenir_service_voyage()
        imported = service.importer_templates_defaut()
        voyage = service.ajouter_voyage(
            {
                "titre": f"Séjour {destination}",
                "destination": destination,
                "date_depart": debut,
                "date_retour": retour,
                "type_voyage": type_voyage,
                "budget_prevu": budget,
                "statut": "planifie",
                "participants": participants,
                "notes": "Planifié via assistant voyage IA",
            }
        )
        if voyage is None:
            raise HTTPException(status_code=422, detail="Impossible de planifier le voyage")

        templates = service.obtenir_templates()
        templates_eligibles = [
            t for t in templates
            if not t.type_voyage or type_voyage in (t.type_voyage or "")
        ]

        checklists_creees = []
        for template in templates_eligibles[:4]:
            checklist = service.creer_checklist_depuis_template(voyage.id, template.id)
            if checklist is not None:
                checklists_creees.append({"id": checklist.id, "nom": checklist.nom})

        return {
            "message": "Voyage planifié",
            "voyage_id": voyage.id,
            "destination": destination,
            "type_sejour": type_sejour,
            "imported_templates": imported,
            "checklists": checklists_creees,
            "suggestions": suggestions,
        }

    return await executer_async(_query)


@router.post("/{voyage_id}/checklists/{checklist_id}/toggle", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def cocher_article_checklist(
    voyage_id: int,
    checklist_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.services.famille.voyage import obtenir_service_voyage

    index_article = int(payload.get("index_article", -1))
    fait = bool(payload.get("fait", True))

    def _query():
        service = obtenir_service_voyage()
        succes = service.cocher_article(checklist_id, index_article, fait)
        if not succes:
            raise HTTPException(status_code=404, detail="Article ou checklist introuvable")
        return {"success": True, "voyage_id": voyage_id, "checklist_id": checklist_id}

    return await executer_async(_query)