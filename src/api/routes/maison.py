"""
Routes API pour la maison.

Agrégateur : inclut 4 sous-routeurs thématiques via include_router() :
- maison_projets   : Projets domestiques, estimation IA, priorisation IA
  → /projets, /projets/*
- maison_entretien : Routines, tâches d'entretien, entretien saisonnier, santé appareils
  → /routines, /entretien, /entretien-saisonnier
- maison_finances  : Artisans, alertes prédictives
  → /artisans
- maison_jardin    : Jardinage, stocks, nuisibles, calendrier semis
  → /jardin, /stocks, /nuisibles

Endpoints directs (ce fichier) :
- Briefing quotidien (/briefing)
- Alertes globales (/alertes)
- Meubles wishlist (/meubles)
- Cellier — cave & garde-manger (/cellier)
- Diagnostics immobiliers & estimations
- Éco-tips (actions écologiques)
- Dépenses maison
- Devis comparatifs
- Relevés compteurs
- Visualisation plan maison
- Hub data (stats dashboard)

Préfixe parent : /api/v1/maison
Pour routes/__init__.py, "maison_router": ".maison" reste inchangé.
"""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict
from src.services.maison.schemas import AlerteMaison, BriefingMaison, TacheJour

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/maison", tags=["Maison"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONTEXTE MAISON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/briefing", response_model=BriefingMaison, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_briefing_maison(
    date_cible: date | None = Query(None, description="Date du briefing (dÃ©faut: aujourd'hui)"),
    user: dict[str, Any] = Depends(require_auth),
) -> BriefingMaison:
    """
    Obtient le briefing quotidien maison.

    AgrÃ¨ge 6 sources de donnÃ©es:
    - Alertes (diagnostics, entretien)
    - TÃ¢ches du jour (mÃ©nage, entretien, projets, jardin)
    - MÃ©tÃ©o (impact jardin & mÃ©nage)
    - Projets actifs
    - Jardin contextuel
    - Cellier & Ã©nergie (anomalies)

    Returns:
        Briefing maison contextuel
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_briefing(date_cible=date_cible)

    return await executer_async(_query)


@router.get("/taches-jour", response_model=list[TacheJour], responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_taches_jour(
    user: dict[str, Any] = Depends(require_auth),
) -> list[TacheJour]:
    """Retourne les tâches du jour (extrait du briefing maison)."""
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query() -> list[TacheJour]:
        service = obtenir_service_contexte_maison()
        briefing = service.obtenir_briefing()
        return briefing.taches_jour_detail

    return await executer_async(_query)


@router.get("/alertes", response_model=list[AlerteMaison], responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_alertes_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> list[AlerteMaison]:
    """
    Obtient toutes les alertes maison.

    Retourne toutes les alertes (pas juste le top 8 du briefing):

    - Diagnostics immobiliers
    - Entretien saisonnier

    Returns:
        Liste complÃ¨te des alertes triÃ©es par urgence
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_toutes_alertes()

    return await executer_async(_query)


# MEUBLES WISHLIST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/meubles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_meubles(
    piece: str | None = Query(None, description="Filtrer par piÃ¨ce"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    priorite: str | None = Query(None, description="Filtrer par prioritÃ©"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les meubles de la wishlist."""
    from src.core.models import Meuble

    def _query():
        with executer_avec_session() as session:
            query = session.query(Meuble)

            if piece:
                query = query.filter(Meuble.piece == piece)
            if statut:
                query = query.filter(Meuble.statut == statut)
            if priorite:
                query = query.filter(Meuble.priorite == priorite)

            meubles = query.order_by(Meuble.priorite, Meuble.nom).all()

            return {
                "items": [
                    {
                        "id": m.id,
                        "nom": m.nom,
                        "description": m.description,
                        "piece": m.piece,
                        "categorie": m.categorie,
                        "prix_estime": float(m.prix_estime) if m.prix_estime else None,
                        "prix_max": float(m.prix_max) if m.prix_max else None,
                        "prix_reel": float(m.prix_reel) if m.prix_reel else None,
                        "statut": m.statut,
                        "priorite": m.priorite,
                        "magasin": m.magasin,
                        "url": m.url,
                    }
                    for m in meubles
                ],
            }

    return await executer_async(_query)


# MEUBLES â€” CRUD complÃ©mentaire (GET existe dÃ©jÃ  ci-dessus)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/meubles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_meuble(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e un meuble dans la wishlist."""
    from src.services.maison import obtenir_meubles_crud_service

    def _query():
        service = obtenir_meubles_crud_service()
        return model_to_dict(service.create_meuble(payload))

    return await executer_async(_query)


@router.patch("/meubles/{meuble_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_meuble(
    meuble_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un meuble."""
    from src.services.maison import obtenir_meubles_crud_service

    def _query():
        service = obtenir_meubles_crud_service()
        return model_to_dict(service.update_meuble(meuble_id, payload))

    return await executer_async(_query)


@router.delete("/meubles/{meuble_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_meuble(
    meuble_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un meuble de la wishlist."""
    from src.services.maison import obtenir_meubles_crud_service

    def _query():
        service = obtenir_meubles_crud_service()
        service.delete_meuble(meuble_id)
        return MessageResponse(message="Meuble supprimÃ©")

    return await executer_async(_query)


@router.get("/meubles/budget", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_budget_meubles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©sumÃ© budget meubles (total estimÃ©, max, par piÃ¨ce)."""
    from src.services.maison import obtenir_meubles_crud_service

    def _query():
        service = obtenir_meubles_crud_service()
        return service.get_budget_resume()

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CELLIER (cave & garde-manger)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/cellier", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_articles_cellier(
    categorie: str | None = Query(None, description="Filtrer par catÃ©gorie"),
    emplacement: str | None = Query(None, description="Filtrer par emplacement"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les articles du cellier."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        articles = service.get_all_articles(
            filtre_categorie=categorie,
            filtre_emplacement=emplacement,
        )
        return {"items": articles}

    return await executer_async(_query)


@router.get("/cellier/alertes/peremption", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_peremption_cellier(
    jours: int = Query(14, ge=1, le=90, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Articles dont la date de pÃ©remption approche."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        return {"items": service.get_alertes_peremption(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/cellier/alertes/stock", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_stock_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Articles dont le stock est en dessous du seuil d'alerte."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        return {"items": service.get_alertes_stock()}

    return await executer_async(_query)


@router.get("/cellier/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques du cellier (total, par catÃ©gorie, valeur)."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        return service.get_stats_cellier()

    return await executer_async(_query)


@router.get("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tail d'un article du cellier."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        result = service.get_article_by_id(article_id)
        if not result:
            raise HTTPException(status_code=404, detail="Article non trouvÃ©")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/cellier", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_article_cellier(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un article au cellier."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        return model_to_dict(service.create_article(payload))

    return await executer_async(_query)


@router.patch("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_article_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un article du cellier."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        return model_to_dict(service.update_article(article_id, payload))

    return await executer_async(_query)


@router.delete("/cellier/{article_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un article du cellier."""
    from src.services.maison import obtenir_cellier_crud_service

    def _query():
        service = obtenir_cellier_crud_service()
        service.delete_article(article_id)
        return MessageResponse(message="Article supprimÃ©")

    return await executer_async(_query)


@router.patch("/cellier/{article_id}/quantite", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def ajuster_quantite_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajuste la quantitÃ© d'un article (+/- delta)."""
    from src.services.maison import obtenir_cellier_crud_service

    delta = payload.get("delta", 0)

    def _query():
        service = obtenir_cellier_crud_service()
        return service.ajuster_quantite(article_id, delta)

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/visualisation/pieces", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_pieces(
    etage: int | None = Query(None, description="Filtrer par Ã©tage"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les piÃ¨ces avec dÃ©tails (objets, travaux, Ã©tat visuel)."""
    from src.services.maison import obtenir_visualisation_service

    def _query():
        service = obtenir_visualisation_service()
        return {"items": service.obtenir_pieces_avec_details(etage=etage)}

    return await executer_async(_query)


@router.get("/visualisation/etages", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_etages(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les Ã©tages disponibles."""
    from src.services.maison import obtenir_visualisation_service

    def _query():
        service = obtenir_visualisation_service()
        return {"etages": service.obtenir_etages_disponibles()}

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/historique", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des travaux dans une piÃ¨ce."""
    from src.services.maison import obtenir_visualisation_service

    def _query():
        service = obtenir_visualisation_service()
        return service.obtenir_historique_piece(piece_id)

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/objets", responses=REPONSES_LISTE)
@gerer_exception_api
async def objets_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Objets/meubles dans une piÃ¨ce."""
    from src.services.maison import obtenir_visualisation_service

    def _query():
        service = obtenir_visualisation_service()
        return {"items": service.obtenir_objets_piece(piece_id)}

    return await executer_async(_query)


@router.get("/pieces/{piece_id}/detail", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def detail_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tail d'une piÃ¨ce avec ses objets et stats entretien."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            from src.core.models.temps_entretien import ObjetMaison, PieceMaison

            piece = session.get(PieceMaison, piece_id)
            if piece is None:
                raise HTTPException(status_code=404, detail="PiÃ¨ce introuvable")
            objets = (
                session.query(ObjetMaison)
                .filter(ObjetMaison.piece_id == piece_id)
                .order_by(ObjetMaison.nom)
                .all()
            )
            return {
                "piece": {
                    "id": piece.id,
                    "nom": piece.nom,
                    "etage": piece.etage,
                    "surface_m2": float(piece.superficie_m2) if piece.superficie_m2 else None,
                    "type_piece": piece.type_piece,
                },
                "objets": [
                    {
                        "id": o.id,
                        "nom": o.nom,
                        "statut": o.statut,
                        "categorie": o.categorie,
                    }
                    for o in objets
                ],
                "nb_taches_retard": 0,
            }

    return await executer_async(_query)


@router.post("/visualisation/positions", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def sauvegarder_positions(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde le layout drag-and-drop des piÃ¨ces."""
    from src.services.maison import obtenir_visualisation_service

    def _query():
        service = obtenir_visualisation_service()
        service.sauvegarder_positions(payload.get("pieces", []))
        return {"message": "Positions sauvegardÃ©es"}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HUB DATA (stats dashboard)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/hub/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_hub_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques agrÃ©gÃ©es pour le dashboard maison."""
    from src.services.maison import obtenir_hub_data_service

    def _query():
        service = obtenir_hub_data_service()
        return service.obtenir_stats_db()

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DOMOTIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/domotique/astuces", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def astuces_domotique(
    categorie: str | None = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les astuces et appareils domotique du catalogue."""
    import json
    from pathlib import Path

    def _query():
        chemin = Path("data/reference/astuces_domotique.json")
        if not chemin.exists():
            return {"categories": [], "conseils_generaux": []}
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        if categorie:
            data["categories"] = [c for c in data.get("categories", []) if c.get("id") == categorie]
        return data

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LIENS ACHAT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/liens-achat", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def liens_achat(
    produit: str = Query(..., description="Nom du produit"),
    categorie: str = Query("default", description="CatÃ©gorie (bricolage, meubles, etc.)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re des liens d'achat vers les marchands spÃ©cialisÃ©s par catÃ©gorie."""
    from src.core.liens_achat import categories_disponibles, generer_liens_achat

    def _query():
        liens = generer_liens_achat(produit, categorie)
        return {
            "produit": produit,
            "categorie": categorie,
            "liens": liens,
            "categories_disponibles": categories_disponibles(),
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PIÃˆCES AVEC OBJETS (inventaire Ã©quipements)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/pieces-avec-objets", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def pieces_avec_objets(
    piece: str | None = Query(None, description="Filtrer par piÃ¨ce"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les piÃ¨ces de la maison avec leurs objets/Ã©quipements inventoriÃ©s."""
    from src.api.utils import executer_avec_session
    from src.core.models.temps_entretien import ObjetMaison

    def _query():
        with executer_avec_session() as session:
            query = session.query(ObjetMaison)
            if piece:
                query = query.filter(ObjetMaison.piece_id == piece)
            objets = query.order_by(ObjetMaison.nom).all()
            # Grouper par piÃ¨ce
            par_piece: dict[str, list[dict[str, Any]]] = {}
            for o in objets:
                p = str(o.piece_id or "Non classÃ©")
                if p not in par_piece:
                    par_piece[p] = []
                par_piece[p].append(
                    {
                        "id": o.id,
                        "nom": o.nom,
                        "categorie": o.categorie,
                        "statut": o.statut,
                        "marque": o.marque,
                        "modele": o.modele,
                        "date_achat": str(o.date_achat) if o.date_achat else None,
                        "prix_achat": float(o.prix_achat) if o.prix_achat else None,
                        "prix_remplacement_estime": float(o.prix_remplacement_estime)
                        if o.prix_remplacement_estime
                        else None,
                        "notes": o.notes,
                        "duree_garantie_mois": o.duree_garantie_mois,
                        "sous_garantie": o.sous_garantie,
                    }
                )
            return {
                "pieces": [{"piece": k, "objets": v} for k, v in par_piece.items()],
                "total": len(objets),
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS RENOUVELLEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/suggestions-renouvellement", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suggestions_renouvellement(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les objets en fin de vie ou Ã  remplacer."""
    from src.api.utils import executer_avec_session
    from src.core.models.temps_entretien import ObjetMaison

    def _query():
        with executer_avec_session() as session:
            objets = (
                session.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_remplacer", "hors_service", "a_surveiller"]))
                .order_by(ObjetMaison.statut)
                .all()
            )
            return {
                "suggestions": [
                    {
                        "id": o.id,
                        "nom": o.nom,
                        "statut": o.statut,
                        "categorie": o.categorie,
                        "piece_id": o.piece_id,
                        "prix_remplacement_estime": float(o.prix_remplacement_estime)
                        if o.prix_remplacement_estime
                        else None,
                        "marque": o.marque,
                        "modele": o.modele,
                        "duree_garantie_mois": o.duree_garantie_mois,
                        "sous_garantie": o.sous_garantie,
                    }
                    for o in objets
                ],
                "total": len(objets),
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SOUS-ROUTEURS
# Chaque sous-routeur hérite du préfixe /api/v1/maison
# et définit ses propres paths relatifs.
# ═══════════════════════════════════════════════════════════
from src.api.routes.maison_entretien import router as _entretien_router
from src.api.routes.maison_finances import router as _finances_router
from src.api.routes.maison_jardin import router as _jardin_router
from src.api.routes.maison_projets import router as _projets_router

router.include_router(_projets_router, tags=["Maison — Projets"])
router.include_router(_entretien_router, tags=["Maison — Entretien"])
router.include_router(_finances_router, tags=["Maison — Finances"])
router.include_router(_jardin_router, tags=["Maison — Jardin"])
