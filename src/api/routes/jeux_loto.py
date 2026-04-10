"""Routes API jeux - Loto (Tirages, Grilles, Statistiques, Generation IA).

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
    AnalyseGrilleLotoResponse,
    AnalyseIARequest,
    GenererGrilleRequest,
    GrilleGenereeResponse,
    GrilleIAPondereeResponse,
    GrilleLotoResponse,
    NumeroRetardResponse,
    StatsLotoResponse,
    TirageLotoResponse,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOTO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/loto/tirages", response_model=list[TirageLotoResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_tirages_loto(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tirages du loto."""
    from src.core.models import TirageLoto

    def _query():
        with executer_avec_session() as session:
            query = session.query(TirageLoto)

            total = query.count()
            items = (
                query.order_by(TirageLoto.date_tirage.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": t.id,
                        "date_tirage": t.date_tirage.isoformat(),
                        "numeros": t.numeros,
                        "numero_chance": t.numero_chance,
                        "numeros_str": t.numeros_str,
                        "jackpot_euros": t.jackpot_euros,
                        "gagnants_rang1": t.gagnants_rang1,
                    }
                    for t in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/loto/grilles", response_model=list[GrilleLotoResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_grilles_loto(
    est_virtuelle: bool | None = Query(None, description="Grilles virtuelles ou rÃ©elles"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les grilles de loto jouÃ©es."""
    from src.core.models import GrilleLoto

    def _query():
        with executer_avec_session() as session:
            query = session.query(GrilleLoto)
            if est_virtuelle is not None:
                query = query.filter(GrilleLoto.est_virtuelle == est_virtuelle)
            grilles = query.order_by(GrilleLoto.id.desc()).limit(100).all()
            return {
                "items": [
                    {
                        "id": g.id,
                        "tirage_id": g.tirage_id,
                        "numeros": [g.numero_1, g.numero_2, g.numero_3, g.numero_4, g.numero_5],
                        "numero_chance": g.numero_chance,
                        "est_virtuelle": g.est_virtuelle,
                        "source_prediction": g.source_prediction,
                    }
                    for g in grilles
                ],
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOTO STATS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/loto/stats", response_model=StatsLotoResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def stats_loto(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques des numÃ©ros Loto (frÃ©quences, chauds, froids)."""
    from src.services.jeux import obtenir_loto_data_service

    def _query():
        svc = obtenir_loto_data_service()
        stats = svc.calculer_toutes_statistiques()

        frequences = {}
        chauds = []
        froids = []

        if stats and stats.numeros_principaux:
            for num, stat in stats.numeros_principaux.items():
                frequences[num] = stat.frequence
            sorted_nums = sorted(
                stats.numeros_principaux.items(), key=lambda x: x[1].frequence, reverse=True
            )
            chauds = [n for n, _ in sorted_nums[:10]]
            froids = [n for n, _ in sorted_nums[-10:]]

        retard = svc.obtenir_numeros_en_retard(seuil_value=1.5)
        retard_data = [
            {
                "numero": n.numero,
                "type_numero": n.type_numero,
                "serie_actuelle": n.serie_actuelle,
                "frequence": n.frequence,
                "derniere_sortie": n.derniere_sortie.isoformat() if n.derniere_sortie else None,
                "value": n.value,
            }
            for n in (retard or [])
        ]

        return {
            "total_tirages": stats.total_tirages if stats else 0,
            "frequences_numeros": frequences,
            "numeros_chauds": chauds,
            "numeros_froids": froids,
            "numeros_retard": retard_data,
        }

    return await executer_async(_query)


@router.get(
    "/loto/numeros-retard", response_model=list[NumeroRetardResponse], responses=REPONSES_LISTE
)
@gerer_exception_api
async def numeros_retard_loto(
    seuil: float = Query(2.0, ge=0),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """NumÃ©ros en retard avec value >= seuil."""
    from src.services.jeux import obtenir_loto_data_service

    def _query():
        svc = obtenir_loto_data_service()
        retard = svc.obtenir_numeros_en_retard(seuil_value=seuil)
        return {
            "items": [
                {
                    "numero": n.numero,
                    "type_numero": n.type_numero,
                    "serie_actuelle": n.serie_actuelle,
                    "frequence": n.frequence,
                    "derniere_sortie": n.derniere_sortie.isoformat() if n.derniere_sortie else None,
                    "value": n.value,
                }
                for n in (retard or [])
            ]
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION DE GRILLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/loto/generer-grille", response_model=GrilleGenereeResponse, responses=REPONSES_CRUD_CREATION
)
@gerer_exception_api
async def generer_grille_loto(
    payload: GenererGrilleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re une grille Loto (statistique, alÃ©atoire ou IA)."""
    import random

    from src.services.jeux import obtenir_loto_data_service

    def _query():
        strategie = payload.strategie.value
        if strategie == "aleatoire":
            numeros = sorted(random.sample(range(1, 50), 5))
            chance = random.randint(1, 10)
            return {"numeros": numeros, "special": [chance], "strategie": strategie}
        svc = obtenir_loto_data_service()
        stats = svc.calculer_toutes_statistiques()
        if not stats or not stats.numeros_principaux:
            numeros = sorted(random.sample(range(1, 50), 5))
            chance = random.randint(1, 10)
            return {"numeros": numeros, "special": [chance], "strategie": strategie}
        # Weighted sampling par value
        nums = list(range(1, 50))
        weights = []
        for n in nums:
            stat = stats.numeros_principaux.get(n)
            if stat:
                w = max(stat.value, 0.1)
            else:
                w = 0.1
            weights.append(w)
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
        # Chance
        chance_nums = list(range(1, 11))
        chance_weights = []
        for n in chance_nums:
            stat = stats.numeros_chance.get(n)
            if stat:
                w = max(stat.value, 0.1)
            else:
                w = 0.1
            chance_weights.append(w)
        chance = random.choices(chance_nums, weights=chance_weights, k=1)[0]
        result = {"numeros": sorted(numeros), "special": [chance], "strategie": strategie}
        if payload.sauvegarder:
            from src.services.jeux import obtenir_loto_crud_service

            loto_svc = obtenir_loto_crud_service()
            loto_svc.sauvegarder_grille(
                numeros=sorted(numeros),
                numero_chance=chance,
                strategie=strategie,
            )
        return result

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION & ANALYSE IA AVANCÃ‰E
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/loto/generer-grille-ia-ponderee",
    response_model=GrilleIAPondereeResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def generer_grille_ia_ponderee(
    mode: str = Query("equilibre", pattern="^(chauds|froids|equilibre)$"),
    sauvegarder: bool = Query(False),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    GÃ©nÃ¨re une grille Loto intelligente avec Mistral IA.

    Modes:
    - chauds: privilÃ©gie les numÃ©ros sortis rÃ©cemment (frÃ©quents)
    - froids: privilÃ©gie les numÃ©ros en retard (Ã©cart Ã©levÃ©)
    - equilibre: mix des deux stratÃ©gies (recommandÃ©)
    """
    from src.services.jeux import (
        obtenir_jeux_ai_service,
        obtenir_loto_crud_service,
        obtenir_loto_data_service,
    )

    def _query():
        # RÃ©cupÃ©rer les statistiques
        data_svc = obtenir_loto_data_service()
        stats_obj = data_svc.calculer_toutes_statistiques()

        if not stats_obj or not stats_obj.numeros_principaux:
            raise HTTPException(
                status_code=400,
                detail="Aucune statistique disponible. Importez des tirages d'abord.",
            )

        # Formater pour l'IA
        stats_dict = {}
        for num, stat in stats_obj.numeros_principaux.items():
            stats_dict[num] = {
                "freq": stat.frequence,
                "ecart": stat.dernier_ecart,
                "dernier": stat.dernier_tirage.isoformat() if stat.dernier_tirage else None,
            }

        # GÃ©nÃ©rer avec IA
        ai_svc = obtenir_jeux_ai_service()
        grille = ai_svc.generer_grille_ia_ponderee(stats_dict, mode)

        # Sauvegarder si demandÃ©
        if sauvegarder:
            loto_svc = obtenir_loto_crud_service()
            loto_svc.sauvegarder_grille(
                numeros=grille["numeros"],
                numero_chance=grille["numero_chance"],
                strategie=f"ia_{mode}",
            )

        return {
            "numeros": grille["numeros"],
            "numero_chance": grille["numero_chance"],
            "mode": mode,
            "analyse": grille.get("analyse", "Grille gÃ©nÃ©rÃ©e par IA"),
            "confiance": grille.get("confiance", 0.5),
            "sauvegardee": sauvegarder,
        }

    return await executer_async(_query)


@router.post(
    "/loto/analyser-grille",
    response_model=AnalyseGrilleLotoResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def analyser_grille_joueur(
    numeros: list[int] = Query(..., description="5 numÃ©ros de 1 Ã  49"),
    numero_chance: int = Query(..., ge=1, le=10),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse une grille Loto avec critique IA Mistral."""
    from src.services.jeux import obtenir_jeux_ai_service, obtenir_loto_data_service

    # Validation
    if len(numeros) != 5:
        raise HTTPException(status_code=400, detail="Exactement 5 numÃ©ros requis")
    if any(n < 1 or n > 49 for n in numeros):
        raise HTTPException(status_code=400, detail="NumÃ©ros doivent Ãªtre entre 1 et 49")
    if len(set(numeros)) != 5:
        raise HTTPException(status_code=400, detail="Pas de numÃ©ros en double")

    def _query():
        # Stats
        data_svc = obtenir_loto_data_service()
        stats_obj = data_svc.calculer_toutes_statistiques()
        stats_dict = {}
        if stats_obj and stats_obj.numeros_principaux:
            for num, stat in stats_obj.numeros_principaux.items():
                stats_dict[num] = {
                    "freq": stat.frequence,
                    "ecart": stat.dernier_ecart,
                }
        # Analyse IA
        ai_svc = obtenir_jeux_ai_service()
        analyse = ai_svc.analyser_grille_joueur(numeros, numero_chance, stats_dict)
        return {
            "grille": {"numeros": sorted(numeros), "numero_chance": numero_chance},
            "note": analyse.get("note", 5),
            "points_forts": analyse.get("points_forts", []),
            "points_faibles": analyse.get("points_faibles", []),
            "recommandations": analyse.get("recommandations", []),
            "appreciation": analyse.get("appreciation", "Grille analysÃ©e."),
        }

    return await executer_async(_query)
