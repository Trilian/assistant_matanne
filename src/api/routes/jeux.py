"""
Routes API pour les jeux (Paris sportifs & Loto).

Endpoints pour:
- Équipes et matchs de football
- Paris sportifs
- Tirages et grilles de loto
- Statistiques de jeux
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.errors import REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/jeux", tags=["Jeux"])


# ═══════════════════════════════════════════════════════════
# ÉQUIPES
# ═══════════════════════════════════════════════════════════


@router.get("/equipes", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_equipes(
    championnat: str | None = Query(None, description="Filtrer par championnat"),
    search: str | None = Query(None, description="Recherche par nom"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les équipes de football."""
    from src.core.models import Equipe

    def _query():
        with executer_avec_session() as session:
            query = session.query(Equipe)

            if championnat:
                query = query.filter(Equipe.championnat == championnat)
            if search:
                safe_search = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(Equipe.nom.ilike(f"%{safe_search}%"))

            equipes = query.order_by(Equipe.championnat, Equipe.nom).all()

            return {
                "items": [
                    {
                        "id": e.id,
                        "nom": e.nom,
                        "nom_court": e.nom_court,
                        "championnat": e.championnat,
                        "pays": e.pays,
                        "matchs_joues": e.matchs_joues,
                        "victoires": e.victoires,
                        "nuls": e.nuls,
                        "defaites": e.defaites,
                        "buts_marques": e.buts_marques,
                        "buts_encaisses": e.buts_encaisses,
                        "points": e.points,
                    }
                    for e in equipes
                ],
            }

    return await executer_async(_query)


@router.get("/equipes/{equipe_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_equipe(equipe_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère une équipe avec sa forme récente."""
    from src.core.models import Equipe

    def _query():
        with executer_avec_session() as session:
            equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
            if not equipe:
                raise HTTPException(status_code=404, detail="Équipe non trouvée")

            return {
                "id": equipe.id,
                "nom": equipe.nom,
                "nom_court": equipe.nom_court,
                "championnat": equipe.championnat,
                "pays": equipe.pays,
                "logo_url": equipe.logo_url,
                "matchs_joues": equipe.matchs_joues,
                "victoires": equipe.victoires,
                "nuls": equipe.nuls,
                "defaites": equipe.defaites,
                "buts_marques": equipe.buts_marques,
                "buts_encaisses": equipe.buts_encaisses,
                "points": equipe.points,
                "forme_recente": equipe.forme_recente,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# MATCHS
# ═══════════════════════════════════════════════════════════


@router.get("/matchs", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_matchs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    championnat: str | None = Query(None, description="Filtrer par championnat"),
    joue: bool | None = Query(None, description="Filtrer par statut joué/non joué"),
    date_debut: date | None = Query(None, description="Date minimum"),
    date_fin: date | None = Query(None, description="Date maximum"),
    cursor: str | None = Query(None, description="Curseur pour pagination cursor-based"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les matchs avec pagination offset ou cursor."""
    from src.core.models import Match

    def _query():
        with executer_avec_session() as session:
            query = session.query(Match)

            if championnat:
                query = query.filter(Match.championnat == championnat)
            if joue is not None:
                query = query.filter(Match.joue == joue)
            if date_debut:
                query = query.filter(Match.date_match >= date_debut)
            if date_fin:
                query = query.filter(Match.date_match <= date_fin)

            query = query.order_by(Match.date_match.desc())

            # Pagination cursor-based
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(query, cursor_params, Match)
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(items, page_size, cursor_field="id")

            # Pagination offset
            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "items": [
                    {
                        "id": m.id,
                        "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else None,
                        "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else None,
                        "championnat": m.championnat,
                        "journee": m.journee,
                        "date_match": m.date_match.isoformat(),
                        "heure": m.heure,
                        "score_domicile": m.score_domicile,
                        "score_exterieur": m.score_exterieur,
                        "resultat": m.resultat,
                        "joue": m.joue,
                        "cote_domicile": m.cote_domicile,
                        "cote_nul": m.cote_nul,
                        "cote_exterieur": m.cote_exterieur,
                    }
                    for m in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/matchs/{match_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_match(match_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère un match avec ses paris."""
    from src.core.models import Match

    def _query():
        with executer_avec_session() as session:
            match = session.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvé")

            return {
                "id": match.id,
                "equipe_domicile": {
                    "id": match.equipe_domicile.id,
                    "nom": match.equipe_domicile.nom,
                }
                if match.equipe_domicile
                else None,
                "equipe_exterieur": {
                    "id": match.equipe_exterieur.id,
                    "nom": match.equipe_exterieur.nom,
                }
                if match.equipe_exterieur
                else None,
                "championnat": match.championnat,
                "journee": match.journee,
                "date_match": match.date_match.isoformat(),
                "heure": match.heure,
                "score_domicile": match.score_domicile,
                "score_exterieur": match.score_exterieur,
                "resultat": match.resultat,
                "joue": match.joue,
                "cotes": {
                    "domicile": match.cote_domicile,
                    "nul": match.cote_nul,
                    "exterieur": match.cote_exterieur,
                },
                "prediction": {
                    "resultat": match.prediction_resultat,
                    "proba_dom": match.prediction_proba_dom,
                    "proba_nul": match.prediction_proba_nul,
                    "proba_ext": match.prediction_proba_ext,
                    "confiance": match.prediction_confiance,
                    "raison": match.prediction_raison,
                }
                if match.prediction_resultat
                else None,
                "paris": [
                    {
                        "id": p.id,
                        "type_pari": p.type_pari,
                        "prediction": p.prediction,
                        "cote": p.cote,
                        "mise": float(p.mise) if p.mise else 0,
                        "statut": p.statut,
                        "est_virtuel": p.est_virtuel,
                    }
                    for p in (match.paris or [])
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# PARIS SPORTIFS
# ═══════════════════════════════════════════════════════════


@router.get("/paris", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_paris(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    statut: str | None = Query(None, description="en_attente, gagne, perdu, annule"),
    est_virtuel: bool | None = Query(None, description="Paris virtuels ou réels"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les paris sportifs."""
    from src.core.models import PariSportif

    def _query():
        with executer_avec_session() as session:
            query = session.query(PariSportif)

            if statut:
                query = query.filter(PariSportif.statut == statut)
            if est_virtuel is not None:
                query = query.filter(PariSportif.est_virtuel == est_virtuel)

            total = query.count()
            items = (
                query.order_by(PariSportif.cree_le.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": p.id,
                        "match_id": p.match_id,
                        "type_pari": p.type_pari,
                        "prediction": p.prediction,
                        "cote": p.cote,
                        "mise": float(p.mise) if p.mise else 0,
                        "statut": p.statut,
                        "gain": float(p.gain) if p.gain else None,
                        "est_virtuel": p.est_virtuel,
                        "confiance_prediction": p.confiance_prediction,
                    }
                    for p in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/paris/stats", responses=REPONSES_LISTE)
@gerer_exception_api
async def statistiques_paris(
    est_virtuel: bool | None = Query(None, description="Stats paris virtuels ou réels"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les statistiques des paris sportifs."""
    from sqlalchemy import func

    from src.core.models import PariSportif

    def _query():
        with executer_avec_session() as session:
            query = session.query(PariSportif)

            if est_virtuel is not None:
                query = query.filter(PariSportif.est_virtuel == est_virtuel)

            # Stats globales
            total_paris = query.count()
            total_mise = query.with_entities(func.sum(PariSportif.mise)).scalar() or 0
            total_gain = (
                query.filter(PariSportif.statut == "gagne")
                .with_entities(func.sum(PariSportif.gain))
                .scalar()
                or 0
            )

            # Par statut
            par_statut = (
                query.with_entities(PariSportif.statut, func.count(PariSportif.id))
                .group_by(PariSportif.statut)
                .all()
            )

            # Taux de réussite
            resolus = sum(count for stat, count in par_statut if stat in ("gagne", "perdu"))
            gagnes = next((count for stat, count in par_statut if stat == "gagne"), 0)
            taux_reussite = (gagnes / resolus * 100) if resolus > 0 else 0

            return {
                "total_paris": total_paris,
                "total_mise": float(total_mise),
                "total_gain": float(total_gain),
                "benefice": float(total_gain - total_mise),
                "taux_reussite": round(taux_reussite, 1),
                "par_statut": {stat: count for stat, count in par_statut},
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# LOTO
# ═══════════════════════════════════════════════════════════


@router.get("/loto/tirages", responses=REPONSES_LISTE)
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


@router.get("/loto/grilles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_grilles_loto(
    est_virtuelle: bool | None = Query(None, description="Grilles virtuelles ou réelles"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les grilles de loto jouées."""
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
