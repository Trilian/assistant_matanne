"""
Routes API Maison â€” Jardin, stocks et nuisibles.

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

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

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

# JARDIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/jardin", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_elements_jardin(
    type_element: str | None = Query(None, description="Filtrer par type (plante, lÃ©gume, etc.)"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les Ã©lÃ©ments du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            query = session.query(ElementJardin)

            if type_element:
                query = query.filter(ElementJardin.type == type_element)
            if statut:
                query = query.filter(ElementJardin.statut == statut)

            elements = query.order_by(ElementJardin.nom).all()

            return {
                "items": [
                    {
                        "id": e.id,
                        "nom": e.nom,
                        "type": e.type,
                        "location": e.location,
                        "statut": e.statut,
                        "date_plantation": e.date_plantation.isoformat()
                        if e.date_plantation
                        else None,
                        "date_recolte_prevue": e.date_recolte_prevue.isoformat()
                        if e.date_recolte_prevue
                        else None,
                    }
                    for e in elements
                ],
            }

    return await executer_async(_query)


@router.get("/jardin/{element_id}/journal", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_journal_jardin(
    element_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©cupÃ¨re le journal d'entretien d'un Ã©lÃ©ment du jardin."""
    from src.core.models import JournalJardin

    def _query():
        with executer_avec_session() as session:
            logs = (
                session.query(JournalJardin)
                .filter(JournalJardin.garden_item_id == element_id)
                .order_by(JournalJardin.date.desc())
                .all()
            )

            return {
                "element_id": element_id,
                "logs": [
                    {
                        "id": log.id,
                        "date": log.date.isoformat(),
                        "action": log.action,
                        "notes": log.notes,
                    }
                    for log in logs
                ],
            }

    return await executer_async(_query)


@router.post("/jardin", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_element_jardin(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un Ã©lÃ©ment au jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = ElementJardin(
                nom=payload["nom"],
                type=payload.get("type", "plante"),
                location=payload.get("location"),
                statut=payload.get("statut", "actif"),
                date_plantation=payload.get("date_plantation"),
                date_recolte_prevue=payload.get("date_recolte_prevue"),
                notes=payload.get("notes"),
            )
            session.add(element)
            session.commit()
            session.refresh(element)
            return {
                "id": element.id,
                "nom": element.nom,
                "type": element.type,
                "statut": element.statut,
            }

    return await executer_async(_query)


@router.patch("/jardin/{element_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_element_jardin(
    element_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un Ã©lÃ©ment du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = session.query(ElementJardin).filter(ElementJardin.id == element_id).first()
            if not element:
                raise HTTPException(status_code=404, detail="Ã‰lÃ©ment non trouvÃ©")

            for champ in ("nom", "type", "location", "statut", "date_plantation",
                          "date_recolte_prevue", "notes"):
                if champ in payload:
                    setattr(element, champ, payload[champ])

            session.commit()
            session.refresh(element)

            bridge_inventaire = None
            action = str(payload.get("action", "")).lower()
            statut = str(payload.get("statut", element.statut or "")).lower()
            if action == "recolte" or statut == "recolte":
                from src.services.ia.inter_modules import obtenir_service_bridges

                bridge_inventaire = obtenir_service_bridges().recolte_vers_stock_inventaire(
                    element_id=element.id,
                    quantite=float(payload.get("quantite_recoltee", 1.0) or 1.0),
                    emplacement=str(payload.get("emplacement_inventaire", "Frigo") or "Frigo"),
                )

            return {
                "id": element.id,
                "nom": element.nom,
                "type": element.type,
                "statut": element.statut,
                "bridge_inventaire": bridge_inventaire,
            }

    return await executer_async(_query)


@router.delete("/jardin/{element_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_element_jardin(
    element_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un Ã©lÃ©ment du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = session.query(ElementJardin).filter(ElementJardin.id == element_id).first()
            if not element:
                raise HTTPException(status_code=404, detail="Ã‰lÃ©ment non trouvÃ©")
            session.delete(element)
            session.commit()
            return MessageResponse(message=f"Ã‰lÃ©ment '{element.nom}' supprimÃ©")

    return await executer_async(_query)


@router.get("/jardin/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_ia_jardin(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """TÃ¢ches saisonniÃ¨res du jardin gÃ©nÃ©rÃ©es par IA (conseils pratiques pour la saison en cours)."""
    from src.services.maison.jardin_service import obtenir_jardin_service
    import asyncio

    service = obtenir_jardin_service()
    conseils_bruts = await service.generer_conseils_saison()

    # Transformer la rÃ©ponse texte en liste structurÃ©e de tÃ¢ches
    lignes = [l.strip() for l in conseils_bruts.splitlines() if l.strip()]
    taches = []
    for ligne in lignes:
        # Nettoyer les puces/numÃ©ros en dÃ©but de ligne
        for prefix in ("- ", "â€¢ ", "* "):
            if ligne.startswith(prefix):
                ligne = ligne[len(prefix):]
        if ligne and not ligne.endswith(":"):
            taches.append({"tache": ligne, "saison": service.obtenir_saison_actuelle()})

    return {"taches": taches, "total": len(taches)}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STOCKS MAISON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/stocks", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_stocks_maison(
    categorie: str | None = Query(None, description="Filtrer par catÃ©gorie"),
    alerte_stock: bool = Query(False, description="Afficher seulement les stocks bas"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les stocks de consommables maison."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            query = session.query(StockMaison)

            if categorie:
                query = query.filter(StockMaison.categorie == categorie)
            if alerte_stock:
                query = query.filter(StockMaison.quantite <= StockMaison.seuil_alerte)

            stocks = query.order_by(StockMaison.nom).all()

            return {
                "items": [
                    {
                        "id": s.id,
                        "nom": s.nom,
                        "categorie": s.categorie,
                        "quantite": s.quantite,
                        "unite": s.unite,
                        "seuil_alerte": s.seuil_alerte,
                        "emplacement": s.emplacement,
                        "prix_unitaire": float(s.prix_unitaire) if s.prix_unitaire else None,
                        "en_alerte": s.quantite <= s.seuil_alerte,
                    }
                    for s in stocks
                ],
            }

    return await executer_async(_query)


@router.post("/stocks", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_stock(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un stock de consommable maison."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = StockMaison(
                nom=payload["nom"],
                categorie=payload.get("categorie", "autre"),
                quantite=payload.get("quantite", 0),
                unite=payload.get("unite", "unitÃ©"),
                seuil_alerte=payload.get("seuil_alerte", 1),
                emplacement=payload.get("emplacement"),
                prix_unitaire=payload.get("prix_unitaire"),
            )
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return {
                "id": stock.id,
                "nom": stock.nom,
                "categorie": stock.categorie,
                "quantite": stock.quantite,
            }

    return await executer_async(_query)


@router.patch("/stocks/{stock_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_stock(
    stock_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un stock (quantitÃ©, seuil, etc.)."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = session.query(StockMaison).filter(StockMaison.id == stock_id).first()
            if not stock:
                raise HTTPException(status_code=404, detail="Stock non trouvÃ©")

            for champ in ("nom", "categorie", "quantite", "unite", "seuil_alerte",
                          "emplacement", "prix_unitaire"):
                if champ in payload:
                    setattr(stock, champ, payload[champ])

            session.commit()
            session.refresh(stock)
            return {
                "id": stock.id,
                "nom": stock.nom,
                "quantite": stock.quantite,
                "en_alerte": stock.quantite <= stock.seuil_alerte,
            }

    return await executer_async(_query)


@router.delete("/stocks/{stock_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_stock(
    stock_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un stock."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = session.query(StockMaison).filter(StockMaison.id == stock_id).first()
            if not stock:
                raise HTTPException(status_code=404, detail="Stock non trouvÃ©")
            session.delete(stock)
            session.commit()
            return MessageResponse(message=f"Stock '{stock.nom}' supprimÃ©")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALENDRIER DES SEMIS (JARDIN INTELLIGENT)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/jardin/calendrier-semis", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_calendrier_semis(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12), dÃ©faut: mois courant"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne le calendrier des semis pour le mois donnÃ©.

    Utilise le catalogue de plantes (data/plantes_catalogue.json) pour
    dÃ©terminer quoi semer, planter et rÃ©colter selon la saison.
    """
    import json
    from pathlib import Path

    mois_courant = mois or date.today().month

    NOMS_MOIS = [
        "", "Janvier", "FÃ©vrier", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "AoÃ»t", "Septembre", "Octobre", "Novembre", "DÃ©cembre",
    ]

    # Charger le catalogue de plantes
    catalogue_path = Path("data/reference/plantes_catalogue.json")
    if not catalogue_path.exists():
        return {
            "mois": mois_courant,
            "mois_nom": NOMS_MOIS[mois_courant],
            "a_semer": [],
            "a_planter": [],
            "a_recolter": [],
            "conseils": [],
        }

    with open(catalogue_path, encoding="utf-8") as f:
        catalogue = json.load(f)

    plantes = catalogue if isinstance(catalogue, list) else catalogue.get("plantes", [])

    a_semer = []
    a_planter = []
    a_recolter = []

    for plante in plantes:
        nom = plante.get("nom", "")
        semis = plante.get("mois_semis", plante.get("semis", []))
        plantation = plante.get("mois_plantation", plante.get("plantation", []))
        recolte = plante.get("mois_recolte", plante.get("recolte", []))

        if mois_courant in semis:
            a_semer.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_semis", "")})
        if mois_courant in plantation:
            a_planter.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_plantation", "")})
        if mois_courant in recolte:
            a_recolter.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_recolte", "")})

    return {
        "mois": mois_courant,
        "mois_nom": NOMS_MOIS[mois_courant],
        "a_semer": a_semer,
        "a_planter": a_planter,
        "a_recolter": a_recolter,
        "conseils": [],
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/nuisibles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_nuisibles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les traitements anti-nuisibles."""
    from src.services.maison import obtenir_nuisibles_crud_service

    def _query():
        service = obtenir_nuisibles_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/nuisibles/prochains", responses=REPONSES_LISTE)
@gerer_exception_api
async def prochains_traitements(
    jours: int = Query(30, ge=1, le=180, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Traitements Ã  effectuer prochainement."""
    from src.services.maison import obtenir_nuisibles_crud_service

    def _query():
        service = obtenir_nuisibles_crud_service()
        return {"items": service.get_prochains_traitements(jours_horizon=jours)}

    return await executer_async(_query)


@router.post("/nuisibles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_traitement_nuisible(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un traitement anti-nuisible."""
    from src.services.maison import obtenir_nuisibles_crud_service

    def _query():
        service = obtenir_nuisibles_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.patch("/nuisibles/{traitement_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_traitement_nuisible(
    traitement_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un traitement."""
    from src.services.maison import obtenir_nuisibles_crud_service

    def _query():
        service = obtenir_nuisibles_crud_service()
        return service.update(traitement_id, payload)

    return await executer_async(_query)


@router.delete("/nuisibles/{traitement_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_traitement_nuisible(
    traitement_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un traitement."""
    from src.services.maison import obtenir_nuisibles_crud_service

    def _query():
        service = obtenir_nuisibles_crud_service()
        service.delete(traitement_id)
        return MessageResponse(message="Traitement supprimÃ©")

    return await executer_async(_query)



