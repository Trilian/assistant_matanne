"""
Routes API pour la maison.

Endpoints pour la gestion de la maison:
- Projets domestiques
- Routines
- Tâches d'entretien
- Jardin
- Stocks maison
- Meubles wishlist
- Cellier (cave & garde-manger)
- Artisans (carnet d'adresses)
- Contrats (assurances, énergie, etc.)
- Garanties (appareils & SAV)
- Diagnostics immobiliers & estimations
- Éco-tips (actions écologiques)
- Dépenses maison
- Nuisibles (traitements)
- Devis comparatifs
- Entretien saisonnier
- Relevés compteurs
- Visualisation plan maison
- Hub data (stats dashboard)
"""

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

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/maison", tags=["Maison"])


# ═══════════════════════════════════════════════════════════
# CONTEXTE MAISON (Phase X)
# ═══════════════════════════════════════════════════════════


@router.get("/briefing", response_model=BriefingMaison, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_briefing_maison(
    date_cible: date | None = Query(None, description="Date du briefing (défaut: aujourd'hui)"),
    user: dict[str, Any] = Depends(require_auth),
) -> BriefingMaison:
    """
    Obtient le briefing quotidien maison.
    
    Agrège 6 sources de données:
    - Alertes (garanties, contrats, diagnostics, entretien)
    - Tâches du jour (ménage, entretien, projets, jardin)
    - Météo (impact jardin & ménage)
    - Projets actifs
    - Jardin contextuel
    - Cellier & énergie (anomalies)
    
    Returns:
        Briefing maison contextuel
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_briefing(date_cible=date_cible)

    return await executer_async(_query)


@router.get("/alertes", response_model=list[AlerteMaison], responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_alertes_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> list[AlerteMaison]:
    """
    Obtient toutes les alertes maison.
    
    Retourne toutes les alertes (pas juste le top 8 du briefing):
    - Garanties expirant
    - Contrats (assurance, énergie, internet)
    - Diagnostics immobiliers
    - Entretien saisonnier
    
    Returns:
        Liste complète des alertes triées par urgence
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_toutes_alertes()

    return await executer_async(_query)


# MEUBLES WISHLIST
# ═══════════════════════════════════════════════════════════


@router.get("/meubles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_meubles(
    piece: str | None = Query(None, description="Filtrer par pièce"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    priorite: str | None = Query(None, description="Filtrer par priorité"),
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


# MEUBLES — CRUD complémentaire (GET existe déjà ci-dessus)
# ═══════════════════════════════════════════════════════════


@router.post("/meubles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_meuble(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un meuble dans la wishlist."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return model_to_dict(service.create_meuble(payload))

    return await executer_async(_query)


@router.patch("/meubles/{meuble_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_meuble(
    meuble_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un meuble."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return model_to_dict(service.update_meuble(meuble_id, payload))

    return await executer_async(_query)


@router.delete("/meubles/{meuble_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_meuble(
    meuble_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un meuble de la wishlist."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        service.delete_meuble(meuble_id)
        return MessageResponse(message="Meuble supprimé")

    return await executer_async(_query)


@router.get("/meubles/budget", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_budget_meubles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Résumé budget meubles (total estimé, max, par pièce)."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return service.get_budget_resume()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CELLIER (cave & garde-manger)
# ═══════════════════════════════════════════════════════════


@router.get("/cellier", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_articles_cellier(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    emplacement: str | None = Query(None, description="Filtrer par emplacement"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les articles du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
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
    """Articles dont la date de péremption approche."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return {"items": service.get_alertes_peremption(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/cellier/alertes/stock", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_stock_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Articles dont le stock est en dessous du seuil d'alerte."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return {"items": service.get_alertes_stock()}

    return await executer_async(_query)


@router.get("/cellier/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques du cellier (total, par catégorie, valeur)."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return service.get_stats_cellier()

    return await executer_async(_query)


@router.get("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        result = service.get_article_by_id(article_id)
        if not result:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/cellier", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_article_cellier(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un article au cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return model_to_dict(service.create_article(payload))

    return await executer_async(_query)


@router.patch("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_article_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return model_to_dict(service.update_article(article_id, payload))

    return await executer_async(_query)


@router.delete("/cellier/{article_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        service.delete_article(article_id)
        return MessageResponse(message="Article supprimé")

    return await executer_async(_query)


@router.patch("/cellier/{article_id}/quantite", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def ajuster_quantite_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajuste la quantité d'un article (+/- delta)."""
    from src.services.maison import get_cellier_crud_service

    delta = payload.get("delta", 0)

    def _query():
        service = get_cellier_crud_service()
        return service.ajuster_quantite(article_id, delta)

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════


@router.get("/visualisation/pieces", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_pieces(
    etage: int | None = Query(None, description="Filtrer par étage"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les pièces avec détails (objets, travaux, état visuel)."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"items": service.obtenir_pieces_avec_details(etage=etage)}

    return await executer_async(_query)


@router.get("/visualisation/etages", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_etages(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les étages disponibles."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"etages": service.obtenir_etages_disponibles()}

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/historique", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des travaux dans une pièce."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return service.obtenir_historique_piece(piece_id)

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/objets", responses=REPONSES_LISTE)
@gerer_exception_api
async def objets_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Objets/meubles dans une pièce."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"items": service.obtenir_objets_piece(piece_id)}

    return await executer_async(_query)


@router.get("/pieces/{piece_id}/detail", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def detail_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'une pièce avec ses objets et stats entretien."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            from src.core.models.temps_entretien import ObjetMaison, PieceMaison

            piece = session.get(PieceMaison, piece_id)
            if piece is None:
                raise HTTPException(status_code=404, detail="Pièce introuvable")
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
    """Sauvegarde le layout drag-and-drop des pièces."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        service.sauvegarder_positions(payload.get("pieces", []))
        return {"message": "Positions sauvegardées"}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# HUB DATA (stats dashboard)
# ═══════════════════════════════════════════════════════════


@router.get("/hub/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_hub_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques agrégées pour le dashboard maison."""
    from src.services.maison import get_hub_data_service

    def _query():
        service = get_hub_data_service()
        return service.obtenir_stats_db()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# DOMOTIQUE
# ═══════════════════════════════════════════════════════════


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
            data["categories"] = [
                c for c in data.get("categories", []) if c.get("id") == categorie
            ]
        return data

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# LIENS ACHAT
# ═══════════════════════════════════════════════════════════


@router.get("/liens-achat", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def liens_achat(
    produit: str = Query(..., description="Nom du produit"),
    categorie: str = Query("default", description="Catégorie (bricolage, meubles, etc.)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère des liens d'achat vers les marchands spécialisés par catégorie."""
    from src.core.liens_achat import generer_liens_achat, categories_disponibles

    def _query():
        liens = generer_liens_achat(produit, categorie)
        return {"produit": produit, "categorie": categorie, "liens": liens, "categories_disponibles": categories_disponibles()}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# PIÈCES AVEC OBJETS (inventaire équipements)
# ═══════════════════════════════════════════════════════════


@router.get("/pieces-avec-objets", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def pieces_avec_objets(
    piece: str | None = Query(None, description="Filtrer par pièce"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les pièces de la maison avec leurs objets/équipements inventoriés."""
    from src.core.models.temps_entretien import ObjetMaison
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            query = session.query(ObjetMaison)
            if piece:
                query = query.filter(ObjetMaison.piece_id == piece)
            objets = query.order_by(ObjetMaison.nom).all()
            # Grouper par pièce
            par_piece: dict[str, list[dict[str, Any]]] = {}
            for o in objets:
                p = str(o.piece_id or "Non classé")
                if p not in par_piece:
                    par_piece[p] = []
                par_piece[p].append({
                    "id": o.id,
                    "nom": o.nom,
                    "categorie": o.categorie,
                    "statut": o.statut,
                    "marque": o.marque,
                    "modele": o.modele,
                    "date_achat": str(o.date_achat) if o.date_achat else None,
                    "prix_achat": float(o.prix_achat) if o.prix_achat else None,
                    "prix_remplacement_estime": float(o.prix_remplacement_estime) if o.prix_remplacement_estime else None,
                    "notes": o.notes,
                })
            return {"pieces": [{"piece": k, "objets": v} for k, v in par_piece.items()], "total": len(objets)}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS RENOUVELLEMENT
# ═══════════════════════════════════════════════════════════


@router.get("/suggestions-renouvellement", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suggestions_renouvellement(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les objets en fin de vie ou à remplacer."""
    from src.core.models.temps_entretien import ObjetMaison
    from src.api.utils import executer_avec_session

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
                        "prix_remplacement_estime": float(o.prix_remplacement_estime) if o.prix_remplacement_estime else None,
                        "marque": o.marque,
                        "modele": o.modele,
                    }
                    for o in objets
                ],
                "total": len(objets),
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# FIN DE VIE GARANTIE
# ═══════════════════════════════════════════════════════════


@router.get("/garanties/{garantie_id}/fin-vie", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def fin_vie_garantie(
    garantie_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Calcule le ratio de fin de vie d'une garantie (0.0 → 1.0)."""
    from src.core.models.temps_entretien import Garantie
    from src.api.utils import executer_avec_session
    from datetime import datetime

    def _query():
        with executer_avec_session() as session:
            g = session.get(Garantie, garantie_id)
            if not g:
                raise HTTPException(status_code=404, detail="Garantie introuvable")
            now = date.today()
            if not g.date_debut or not g.date_fin:
                return {"garantie_id": garantie_id, "ratio": 0.0, "jours_restants": None}
            total = (g.date_fin - g.date_debut).days
            if total <= 0:
                return {"garantie_id": garantie_id, "ratio": 1.0, "jours_restants": 0}
            ecoule = (now - g.date_debut).days
            ratio = min(1.0, max(0.0, ecoule / total))
            jours_restants = max(0, (g.date_fin - now).days)
            return {
                "garantie_id": garantie_id,
                "nom": g.nom,
                "ratio": round(ratio, 3),
                "jours_restants": jours_restants,
                "date_fin": str(g.date_fin),
                "alerte": ratio > 0.85,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SOUS-ROUTEURS (Sprint 12 — A1 split)
# ═══════════════════════════════════════════════════════════
from src.api.routes.maison_projets import router as _projets_router
from src.api.routes.maison_entretien import router as _entretien_router
from src.api.routes.maison_finances import router as _finances_router
from src.api.routes.maison_jardin import router as _jardin_router

router.include_router(_projets_router)
router.include_router(_entretien_router)
router.include_router(_finances_router)
router.include_router(_jardin_router)
