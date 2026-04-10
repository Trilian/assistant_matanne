"""Routes API jeux - Euromillions (Tirages, Grilles, Statistiques, Generation IA).

Sous-module de jeux.py. Le routeur n'a pas de prefixe ici,
car le prefixe /api/v1/jeux est defini dans jeux.py (agregateur).
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.jeux import (
    AnalyseIARequest,
    GenererGrilleRequest,
    GrilleEuromillionsResponse,
    GrilleExpertEuromillionsResponse,
    GrilleGenereeResponse,
    StatsEuromillionsResponse,
    TirageEuromillionsResponse,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EUROMILLIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get(
    "/euromillions/tirages",
    response_model=list[TirageEuromillionsResponse],
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def lister_tirages_euromillions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tirages Euromillions."""
    from src.services.jeux import obtenir_euromillions_crud_service

    def _query():
        svc = obtenir_euromillions_crud_service()
        tirages = svc.obtenir_tirages(limite=page_size)
        return {"items": tirages or []}

    return await executer_async(_query)


@router.get(
    "/euromillions/grilles",
    response_model=list[GrilleEuromillionsResponse],
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def lister_grilles_euromillions(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les grilles Euromillions jouÃ©es."""
    from src.services.jeux import obtenir_euromillions_crud_service

    def _query():
        svc = obtenir_euromillions_crud_service()
        grilles = svc.obtenir_grilles(limite=100)
        return {"items": grilles or []}

    return await executer_async(_query)


@router.post(
    "/euromillions/grilles",
    status_code=201,
    response_model=GrilleEuromillionsResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def creer_grille_euromillions(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une grille Euromillions."""
    from src.services.jeux import obtenir_euromillions_crud_service

    numeros = payload.get("numeros", [])
    etoiles = payload.get("etoiles", [])
    if len(numeros) != 5 or len(etoiles) != 2:
        raise HTTPException(status_code=400, detail="5 numÃ©ros et 2 Ã©toiles requis")
    if not all(1 <= n <= 50 for n in numeros):
        raise HTTPException(status_code=400, detail="NumÃ©ros entre 1 et 50")
    if not all(1 <= e <= 12 for e in etoiles):
        raise HTTPException(status_code=400, detail="Ã‰toiles entre 1 et 12")

    def _query():
        svc = obtenir_euromillions_crud_service()
        grille_id = svc.enregistrer_grille(
            numeros=sorted(numeros),
            etoiles=sorted(etoiles),
            source=payload.get("source", "manuel"),
            est_virtuelle=payload.get("est_virtuelle", True),
            mise=Decimal(str(payload.get("mise", "2.50"))),
            notes=payload.get("notes"),
        )
        return {"id": grille_id, "numeros": sorted(numeros), "etoiles": sorted(etoiles)}

    return await executer_async(_query)


@router.get(
    "/euromillions/stats", response_model=StatsEuromillionsResponse, responses=REPONSES_LISTE
)
@gerer_exception_api
async def stats_euromillions(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques des numÃ©ros Euromillions."""
    from src.core.models.jeux import StatistiquesEuromillions

    def _query():
        with executer_avec_session() as session:
            stats = (
                session.query(StatistiquesEuromillions)
                .order_by(StatistiquesEuromillions.date_calcul.desc())
                .first()
            )
            if not stats:
                return {
                    "total_tirages": 0,
                    "frequences_numeros": {},
                    "frequences_etoiles": {},
                    "numeros_chauds": [],
                    "numeros_froids": [],
                    "numeros_retard": [],
                    "etoiles_chaudes": [],
                    "etoiles_froides": [],
                }
            return {
                "total_tirages": stats.nb_tirages_analyses,
                "frequences_numeros": stats.frequences_numeros or {},
                "frequences_etoiles": stats.frequences_etoiles or {},
                "numeros_chauds": stats.numeros_chauds or [],
                "numeros_froids": stats.numeros_froids or [],
                "numeros_retard": stats.numeros_retard or [],
                "etoiles_chaudes": stats.etoiles_chaudes or [],
                "etoiles_froides": stats.etoiles_froides or [],
            }

    return await executer_async(_query)


@router.get(
    "/euromillions/grilles-expert",
    response_model=list[GrilleExpertEuromillionsResponse],
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def lister_grilles_expert_euromillions(
    strategie: str | None = Query(None, description="equilibree, frequences, retards, ia_creative"),
    qualite_min: float | None = Query(None, ge=0, le=100, description="Seuil de qualitÃ©"),
    date_min: str | None = Query(None, description="Date min YYYY-MM-DD"),
    date_max: str | None = Query(None, description="Date max YYYY-MM-DD"),
    search: str | None = Query(None, description="Recherche texte"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les grilles Euromillions avec analyse expert.

    Retourne qualitÃ©, distribution, backtest pour chaque grille.
    """
    from src.core.models.jeux import GrilleEuromillions

    def _query():
        with executer_avec_session() as session:
            query = session.query(GrilleEuromillions)

            # Filtres
            if strategie:
                query = query.filter(GrilleEuromillions.strategie == strategie)

            if qualite_min is not None:
                query = query.filter(GrilleEuromillions.qualite >= qualite_min)

            if date_min:
                date_obj = datetime.fromisoformat(date_min)
                query = query.filter(GrilleEuromillions.date_tirage >= date_obj)

            if date_max:
                date_obj = datetime.fromisoformat(date_max)
                query = query.filter(GrilleEuromillions.date_tirage <= date_obj)

            if search:
                safe_search = search.replace("%", "\\%").replace("_", "\\_")
                # Recherche dans explication ou strategie
                query = query.filter(
                    (GrilleEuromillions.explication.ilike(f"%{safe_search}%"))
                    | (GrilleEuromillions.strategie.ilike(f"%{safe_search}%"))
                )

            total = query.count()
            grilles = (
                query.order_by(GrilleEuromillions.date_tirage.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            items = []
            for g in grilles:
                items.append(
                    {
                        "id": g.id,
                        "numeros": g.numeros,
                        "etoiles": g.etoiles,
                        "date_tirage": g.date_tirage.isoformat() if g.date_tirage else None,
                        "strategie": g.strategie or "inconnue",
                        "qualite": g.qualite or 0,
                        "explication": g.explication or "",
                        "distribution": g.distribution or {},
                        "backtest": g.backtest if hasattr(g, "backtest") else None,
                        "statut": g.statut if hasattr(g, "statut") else "en_attente",
                    }
                )

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.post("/euromillions/generer-grille-ia", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def generer_grille_ia_euromillions(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    GÃ©nÃ¨re une grille Euromillions avec IA.
    StratÃ©gies disponibles:
    - equilibree: Mix frÃ©quences + retards (dÃ©faut)
    - frequences: NumÃ©ros chauds
    - retards: NumÃ©ros en retard
    - ia_creative: GÃ©nÃ©ration crÃ©ative par Mistral
    """
    from src.services.jeux.euromillions_ia import obtenir_euromillions_ia_service

    def _query():
        service = obtenir_euromillions_ia_service()
        strategie = payload.get("strategie", "equilibree")
        # Calculer stats une seule fois
        stats = service.calculer_statistiques(jours=365)
        # GÃ©nÃ©rer selon stratÃ©gie
        if strategie == "frequences":
            grille = service.generer_grille_frequences(stats)
        elif strategie == "retards":
            grille = service.generer_grille_retards(stats)
        elif strategie == "ia_creative":
            grille = service.generer_grille_ia_creative(stats)
        else:  # equilibree par dÃ©faut
            grille = service.generer_grille_equilibree(stats)
        return {
            "numeros": grille.numeros,
            "etoiles": grille.etoiles,
            "qualite": grille.qualite,
            "strategie": grille.strategie,
            "explication": grille.explication,
            "distribution": grille.distribution,
        }

    return await executer_async(_query)


@router.post(
    "/euromillions/generer-grille",
    response_model=GrilleGenereeResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def generer_grille_euromillions(
    payload: GenererGrilleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re une grille Euromillions (statistique, alÃ©atoire ou IA)."""
    import random

    def _query():
        strategie = payload.strategie.value
        if strategie == "aleatoire":
            numeros = sorted(random.sample(range(1, 51), 5))
            etoiles = sorted(random.sample(range(1, 13), 2))
            return {"numeros": numeros, "special": etoiles, "strategie": strategie}
        from src.core.models.jeux import StatistiquesEuromillions

        with executer_avec_session() as session:
            stats = (
                session.query(StatistiquesEuromillions)
                .order_by(StatistiquesEuromillions.date_calcul.desc())
                .first()
            )
        if not stats or not stats.frequences_numeros:
            numeros = sorted(random.sample(range(1, 51), 5))
            etoiles = sorted(random.sample(range(1, 13), 2))
            return {"numeros": numeros, "special": etoiles, "strategie": strategie}
        # Weighted sampling for numbers
        freq_nums = stats.frequences_numeros or {}
        nums = list(range(1, 51))
        weights = [max(float(freq_nums.get(str(n), freq_nums.get(n, 0.1))), 0.1) for n in nums]
        numeros = []
        available = list(zip(nums, weights, strict=False))
        for _ in range(5):
            chosen = random.choices(
                [x[0] for x in available],
                weights=[x[1] for x in available],
                k=1,
            )[0]
            numeros.append(chosen)
            available = [(n, w) for n, w in available if n != chosen]
        # Stars
        freq_stars = stats.frequences_etoiles or {}
        stars = list(range(1, 13))
        star_weights = [
            max(float(freq_stars.get(str(s), freq_stars.get(s, 0.1))), 0.1) for s in stars
        ]
        etoiles = []
        available_stars = list(zip(stars, star_weights, strict=False))
        for _ in range(2):
            chosen = random.choices(
                [x[0] for x in available_stars],
                weights=[x[1] for x in available_stars],
                k=1,
            )[0]
            etoiles.append(chosen)
            available_stars = [(s, w) for s, w in available_stars if s != chosen]
        result = {"numeros": sorted(numeros), "special": sorted(etoiles), "strategie": strategie}
        if payload.sauvegarder:
            from src.services.jeux import obtenir_euromillions_crud_service

            svc = obtenir_euromillions_crud_service()
            svc.enregistrer_grille(
                numeros=sorted(numeros),
                etoiles=sorted(etoiles),
                source=strategie,
            )
        return result

    return await executer_async(_query)
