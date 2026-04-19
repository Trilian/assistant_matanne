"""Routes API jeux - Paris Sportifs (Equipes, Matchs, Bankroll, Series, Predictions, Cotes historique).

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
from src.api.schemas.jeux import AnalyseIARequest, GenererGrilleRequest
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter()

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ÉQUIPES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MATCHS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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

            query = query.order_by(Match.date_match.desc(), Match.id.desc())

            # Pagination cursor-based
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(
                    query,
                    cursor_params,
                    Match,
                    cursor_field="date_match",  # FIX B12: match l'ordre principal
                    secondary_field="id",  # Stable tie-breaker
                )
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(
                    items,
                    page_size,
                    cursor_field="date_match",  # FIX B12: match l'ordre
                    secondary_field="id",  # FIX B12: ti-breaker unique
                )

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


@router.get("/paris/matchs", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_matchs_expert(
    league: str | None = Query(None, description="Filtrer par championnat"),
    date_min: date | None = Query(None, description="Date minimum"),
    date_max: date | None = Query(None, description="Date maximum"),
    ev_min: float | None = Query(None, description="Expected Value minimum (0-1)"),
    confidence_min: float | None = Query(None, description="Confiance IA minimum (0-1)"),
    pattern: str | None = Query(None, description="Pattern statistique détecté"),
    search: str | None = Query(None, description="Recherche équipe"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les matchs avec filtres avancés pour la vue Expert.

    Filtre par championnat, dates, EV, confiance IA, patterns statistiques.
    Retourne toutes les données nécessaires pour l'analyse experte.
    """
    from sqlalchemy import and_, func, or_

    from src.core.models import Equipe, Match

    def _query():
        with executer_avec_session() as session:
            # Query de base sur Match
            query = session.query(Match)

            # Filtre par championnat (mapping league -> championnat)
            if league:
                league_mapping = {
                    "ligue_1": "Ligue 1",
                    "premier_league": "Premier League",
                    "la_liga": "La Liga",
                    "bundesliga": "Bundesliga",
                    "serie_a": "Serie A",
                }
                championnat = league_mapping.get(league, league)
                query = query.filter(Match.championnat == championnat)

            # Filtre par dates
            if date_min:
                query = query.filter(Match.date_match >= date_min)
            if date_max:
                query = query.filter(Match.date_match <= date_max)

            # Filtres uniquement sur matchs non joués avec prédictions
            query = query.filter(Match.joue == False)
            query = query.filter(Match.prediction_resultat.isnot(None))

            # Filtre par confiance IA
            if confidence_min is not None:
                query = query.filter(Match.prediction_confiance >= confidence_min)

            # Filtre par Expected Value (calculé: meilleure_proba * meilleure_cote - 1)
            if ev_min is not None:
                # Filtre approximatif - le calcul exact EV nécessite de déterminer meilleure cote/proba
                # On utilise la confiance comme proxy pour filtrage initial
                query = query.filter(Match.prediction_confiance >= (ev_min / 0.20 + 0.5))

            # Filtre par recherche équipe
            if search:
                safe_search = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(
                    or_(
                        Match.equipe_domicile.has(Equipe.nom.ilike(f"%{safe_search}%")),
                        Match.equipe_exterieur.has(Equipe.nom.ilike(f"%{safe_search}%")),
                    )
                )

            # Ordre par date (prochains matchs d'abord)
            query = query.order_by(Match.date_match.asc())

            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            # Construction des résultats avec calcul EV
            matchs_data = []
            for m in items:
                # Calcul Expected Value
                ev = None
                if m.prediction_proba_dom and m.cote_domicile:
                    ev_dom = m.prediction_proba_dom * m.cote_domicile - 1
                    ev = ev_dom
                if m.prediction_proba_nul and m.cote_nul:
                    ev_nul = m.prediction_proba_nul * m.cote_nul - 1
                    if ev is None or ev_nul > ev:
                        ev = ev_nul
                if m.prediction_proba_ext and m.cote_exterieur:
                    ev_ext = m.prediction_proba_ext * m.cote_exterieur - 1
                    if ev is None or ev_ext > ev:
                        ev = ev_ext

                # Filtre final par EV (après calcul exact)
                if ev_min is not None and (ev is None or ev < ev_min):
                    total -= 1
                    continue

                # Détection simple des patterns pour la vue expert.
                pattern_detecte = None
                confiance = float(m.prediction_confiance) if m.prediction_confiance else 0.0
                if ev is not None and ev >= 0.15 and confiance >= 0.7:
                    pattern_detecte = "hot_hand"
                elif ev is not None and ev <= -0.05 and confiance < 0.45:
                    pattern_detecte = "regression_risk"
                elif ev is not None and ev > 0.08:
                    pattern_detecte = "high_ev"

                matchs_data.append(
                    {
                        "id": m.id,
                        "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else "?",
                        "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                        "date_match": m.date_match.isoformat(),
                        "championnat": m.championnat,
                        "cote_domicile": float(m.cote_domicile) if m.cote_domicile else None,
                        "cote_nul": float(m.cote_nul) if m.cote_nul else None,
                        "cote_exterieur": float(m.cote_exterieur) if m.cote_exterieur else None,
                        "ev": float(ev) if ev is not None else None,
                        "prediction_ia": m.prediction_resultat,
                        "proba_ia": (
                            float(m.prediction_proba_dom)
                            if m.prediction_resultat == "domicile"
                            else float(m.prediction_proba_nul)
                            if m.prediction_resultat == "nul"
                            else float(m.prediction_proba_ext)
                            if m.prediction_resultat == "exterieur"
                            else None
                        )
                        if m.prediction_resultat
                        else None,
                        "confiance_ia": float(m.prediction_confiance)
                        if m.prediction_confiance
                        else None,
                        "pattern_detecte": pattern_detecte,
                        "forme_domicile": m.equipe_domicile.forme_recente
                        if m.equipe_domicile
                        else None,
                        "forme_exterieur": m.equipe_exterieur.forme_recente
                        if m.equipe_exterieur
                        else None,
                    }
                )

            return {
                "items": matchs_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BANKROLL & MONEY MANAGEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/bankroll/{user_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_bankroll(
    user_id: int,
    bankroll_initiale: float = Query(1000, description="Bankroll de départ"),
    jours: int = Query(30, description="Historique sur N jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Obtient la bankroll actuelle et l'historique."""
    from src.services.jeux.bankroll_manager import get_bankroll_manager

    def _query():
        manager = get_bankroll_manager()

        # Calculer bankroll actuelle
        bankroll_actuelle = manager.calculer_bankroll_actuelle(
            user_id=user_id, bankroll_initiale=bankroll_initiale
        )

        # Obtenir historique
        historique = manager.obtenir_historique_bankroll(
            user_id=user_id, bankroll_initiale=bankroll_initiale, jours=jours
        )

        # Calculer variation et ROI
        variation_totale = bankroll_actuelle - bankroll_initiale

        # Calculer ROI depuis les paris
        with executer_avec_session() as session:
            from sqlalchemy import func

            from src.core.models import PariSportif

            total_mises = (
                session.query(func.coalesce(func.sum(PariSportif.mise), 0))
                .filter(PariSportif.user_id == user_id)
                .scalar()
                or 0
            )

            total_gains = (
                session.query(func.coalesce(func.sum(PariSportif.gain), 0))
                .filter(PariSportif.user_id == user_id, PariSportif.statut == "gagne")
                .scalar()
                or 0
            )

            roi = manager.calculer_roi(total_mises, total_gains)

        return {
            "bankroll_actuelle": bankroll_actuelle,
            "bankroll_initiale": bankroll_initiale,
            "variation_totale": variation_totale,
            "roi": roi,
            "historique": historique,
        }

    return await executer_async(_query)


@router.get("/bankroll/suggestion-mise", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suggerer_mise_kelly(
    bankroll: float = Query(..., description="Bankroll actuelle"),
    edge: float = Query(..., description="Expected value (EV)"),
    cote: float = Query(..., description="Cote décimale"),
    confiance_ia: float = Query(70, description="Confiance de l'IA (0-100)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggère une mise optimale selon le critère de Kelly fractionnaire."""
    from src.services.jeux.bankroll_manager import get_bankroll_manager

    def _query():
        manager = get_bankroll_manager()

        suggestion = manager.suggerer_mise(
            bankroll=bankroll, edge=edge, cote=cote, confiance_ia=confiance_ia
        )

        return {
            "mise_suggeree": suggestion.mise_suggeree,
            "mise_kelly_complete": suggestion.mise_kelly_complete,
            "fraction_utilisee": suggestion.fraction_utilisee,
            "edge": suggestion.edge,
            "pourcentage_bankroll": suggestion.pourcentage_bankroll,
            "confiance": suggestion.confiance,
            "message": suggestion.message,
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PARIS SPORTIFS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


@router.get("/paris/analyse-patterns/{user_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def analyser_patterns_utilisateur(
    user_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Analyse les patterns de paris de l'utilisateur pour détecter les biais cognitifs.

    Retourne:
    - regression_moyenne: Alerte si série exceptionnelle (hot/cold streak)
    - hot_hand: Alerte si clustering de victoires (illusion main chaude)
    - gamblers_fallacy: Alerte si augmentation mise après perte (erreur du parieur)
    """
    from src.services.jeux.series_statistiques import SeriesStatistiquesService

    def _query():
        service = SeriesStatistiquesService()

        # Analyser les patterns
        resultats = service.analyser_patterns_utilisateur(user_id)

        # Formater pour le frontend
        response = {}

        if resultats.get("regression_moyenne"):
            r = resultats["regression_moyenne"]
            response["regression_moyenne"] = {
                "alerte": r.alerte,
                "severite": r.severite,
                "message": r.message,
                "details": r.details,
                "type_pattern": r.type_pattern,
            }

        if resultats.get("hot_hand"):
            r = resultats["hot_hand"]
            response["hot_hand"] = {
                "alerte": r.alerte,
                "severite": r.severite,
                "message": r.message,
                "details": r.details,
                "type_pattern": r.type_pattern,
            }

        if resultats.get("gamblers_fallacy"):
            r = resultats["gamblers_fallacy"]
            response["gamblers_fallacy"] = {
                "alerte": r.alerte,
                "severite": r.severite,
                "message": r.message,
                "details": r.details,
                "type_pattern": r.type_pattern,
            }

        return response

    return await executer_async(_query)


@router.get("/patterns", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_patterns_jeux(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les patterns jeux (hot hand, régression, gambler's fallacy) de l'utilisateur connecté."""
    from src.services.jeux.series_statistiques import SeriesStatistiquesService

    user_id = user.get("sub") or user.get("id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Identifiant utilisateur manquant")

    def _query() -> dict[str, Any]:
        service = SeriesStatistiquesService()
        resultats = service.analyser_patterns_utilisateur(int(user_id))

        payload: dict[str, Any] = {
            "user_id": int(user_id),
            "items": [],
            "resume": {
                "hot_hand": False,
                "regression_moyenne": False,
                "gamblers_fallacy": False,
            },
        }

        for cle in ("hot_hand", "regression_moyenne", "gamblers_fallacy"):
            pattern = resultats.get(cle)
            if not pattern:
                continue

            alerte = bool(getattr(pattern, "alerte", False))
            payload["resume"][cle] = alerte
            payload["items"].append(
                {
                    "type": cle,
                    "alerte": alerte,
                    "severite": getattr(pattern, "severite", "info"),
                    "message": getattr(pattern, "message", ""),
                    "details": getattr(pattern, "details", {}),
                }
            )

        return payload

    return await executer_async(_query)


@router.post("/paris", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_pari(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau pari sportif."""
    from decimal import Decimal

    from src.core.models import Match, PariSportif

    def _query():
        with executer_avec_session() as session:
            mise = Decimal(str(payload.get("mise", 0)))

            match = session.query(Match).filter(Match.id == payload["match_id"]).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvé")

            pari = PariSportif(
                match_id=payload["match_id"],
                type_pari=payload.get("type_pari", "1N2"),
                prediction=payload["prediction"],
                cote=payload["cote"],
                mise=mise,
                est_virtuel=payload.get("est_virtuel", True),
                notes=payload.get("notes"),
            )
            session.add(pari)
            session.commit()
            session.refresh(pari)
            return {
                "id": pari.id,
                "match_id": pari.match_id,
                "prediction": pari.prediction,
                "cote": pari.cote,
                "mise": float(pari.mise),
                "est_virtuel": pari.est_virtuel,
                "statut": pari.statut,
            }

    return await executer_async(_query)


@router.patch("/paris/{pari_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_pari(
    pari_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un pari (statut, gain, etc.)."""
    from decimal import Decimal

    from src.core.models import HistoriqueJeux, PariSportif

    def _query():
        with executer_avec_session() as session:
            pari = session.query(PariSportif).filter(PariSportif.id == pari_id).first()
            if not pari:
                raise HTTPException(status_code=404, detail="Pari non trouvé")

            ancien_statut = pari.statut
            ancien_gain = Decimal(str(pari.gain or 0))

            if "statut" in payload:
                pari.statut = payload["statut"]
            if "gain" in payload:
                pari.gain = Decimal(str(payload["gain"]))
            if "notes" in payload:
                pari.notes = payload["notes"]

            statut_change = ancien_statut != pari.statut
            mise = Decimal(str(pari.mise or 0))
            gain = Decimal(str(pari.gain or 0))
            event_payload: dict[str, Any] | None = None

            # Mise à jour de l'historique jeux (budgets jeux/famille séparés).
            if statut_change and not pari.est_virtuel:
                historique = (
                    session.query(HistoriqueJeux)
                    .filter(HistoriqueJeux.date == date.today(), HistoriqueJeux.type_jeu == "paris")
                    .first()
                )
                if historique is None:
                    historique = HistoriqueJeux(date=date.today(), type_jeu="paris")
                    session.add(historique)
                    session.flush()

                def _ajuster_historique(
                    statut: str, mise_val: Decimal, gain_val: Decimal, sens: int
                ) -> None:
                    if statut not in {"gagne", "perdu"}:
                        return
                    historique.nb_paris = max(0, int(historique.nb_paris or 0) + sens)
                    historique.mises_totales = Decimal(str(historique.mises_totales or 0)) + (
                        mise_val * sens
                    )

                    if statut == "gagne":
                        historique.paris_gagnes = max(0, int(historique.paris_gagnes or 0) + sens)
                        historique.gains_totaux = Decimal(str(historique.gains_totaux or 0)) + (
                            gain_val * sens
                        )
                    elif statut == "perdu":
                        historique.paris_perdus = max(0, int(historique.paris_perdus or 0) + sens)

                _ajuster_historique(ancien_statut, mise, ancien_gain, -1)
                _ajuster_historique(pari.statut, mise, gain, +1)

            session.commit()
            session.refresh(pari)

            if statut_change and pari.statut in {"gagne", "perdu", "annule"}:
                event_payload = {
                    "pari_id": pari.id,
                    "statut": pari.statut,
                    "gain": float(pari.gain) if pari.gain else 0.0,
                    "mise": float(pari.mise) if pari.mise else 0.0,
                    "est_virtuel": bool(pari.est_virtuel),
                }

            return {
                "id": pari.id,
                "statut": pari.statut,
                "gain": float(pari.gain) if pari.gain else None,
                "mise": float(pari.mise),
                "_event_payload": event_payload,
            }

    resultat = await executer_async(_query)

    event_payload = resultat.pop("_event_payload", None) if isinstance(resultat, dict) else None
    if event_payload:
        try:
            from src.services.core.events import obtenir_bus

            obtenir_bus().emettre(
                "paris.resultat_enregistre",
                event_payload,
                source="api.jeux_paris.modifier_pari",
            )
        except Exception as exc:
            logger.debug("Emission event paris.resultat_enregistre ignorée: %s", exc)

    return resultat


@router.delete("/paris/{pari_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_pari(
    pari_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un pari."""
    from src.core.models import PariSportif

    def _query():
        with executer_avec_session() as session:
            pari = session.query(PariSportif).filter(PariSportif.id == pari_id).first()
            if not pari:
                raise HTTPException(status_code=404, detail="Pari non trouvé")
            session.delete(pari)
            session.commit()
            return MessageResponse(message="Pari supprimé")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SÉRIES & ALERTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/series", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_series(
    type_jeu: str | None = Query(None, description="paris, loto, euromillions"),
    seuil: float = Query(2.0, ge=0),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détecte les opportunités (séries avec value >= seuil)."""
    from src.services.jeux import obtenir_series_service

    def _query():
        svc = obtenir_series_service()
        series = svc.detecter_opportunites(type_jeu=type_jeu, seuil=seuil)
        return {
            "items": [
                {
                    "id": s.id,
                    "type_jeu": s.type_jeu,
                    "marche": s.marche,
                    "championnat": s.championnat,
                    "serie_actuelle": s.serie_actuelle,
                    "frequence": s.frequence,
                    "value": s.value,
                    "niveau_opportunite": svc.niveau_opportunite(s.value),
                }
                for s in (series or [])
            ]
        }

    return await executer_async(_query)


@router.get("/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_alertes(
    type_jeu: str | None = Query(None, description="paris, loto, euromillions"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les alertes non notifiées."""
    from src.services.jeux import obtenir_series_service

    def _query():
        svc = obtenir_series_service()
        alertes = svc.obtenir_alertes_non_notifiees(type_jeu=type_jeu)
        return {
            "items": [
                {
                    "id": a.id,
                    "type_jeu": a.type_jeu,
                    "marche": a.marche,
                    "championnat": a.championnat,
                    "value_alerte": a.value_alerte,
                    "serie_alerte": a.serie_alerte,
                    "frequence_alerte": a.frequence_alerte,
                    "seuil_utilise": a.seuil_utilise,
                    "notifie": a.notifie,
                    "date_creation": a.cree_le.isoformat() if a.cree_le else None,
                }
                for a in (alertes or [])
            ]
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PRÉDICTIONS & VALUE BETS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/paris/predictions/{match_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def prediction_match(
    match_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Prédiction IA pour un match donné."""
    from src.core.models import Match
    from src.services.jeux import obtenir_prediction_service

    def _query():
        with executer_avec_session() as session:
            match = session.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvé")

            # Construire les données de forme
            forme_dom = {
                "victoires": match.equipe_domicile.victoires if match.equipe_domicile else 0,
                "nuls": match.equipe_domicile.nuls if match.equipe_domicile else 0,
                "defaites": match.equipe_domicile.defaites if match.equipe_domicile else 0,
                "buts_marques": match.equipe_domicile.buts_marques if match.equipe_domicile else 0,
                "buts_encaisses": match.equipe_domicile.buts_encaisses
                if match.equipe_domicile
                else 0,
                "forme_recente": match.equipe_domicile.forme_recente
                if match.equipe_domicile
                else None,
            }
            forme_ext = {
                "victoires": match.equipe_exterieur.victoires if match.equipe_exterieur else 0,
                "nuls": match.equipe_exterieur.nuls if match.equipe_exterieur else 0,
                "defaites": match.equipe_exterieur.defaites if match.equipe_exterieur else 0,
                "buts_marques": match.equipe_exterieur.buts_marques
                if match.equipe_exterieur
                else 0,
                "buts_encaisses": match.equipe_exterieur.buts_encaisses
                if match.equipe_exterieur
                else 0,
                "forme_recente": match.equipe_exterieur.forme_recente
                if match.equipe_exterieur
                else None,
            }
            h2h = {}
            cotes = {}
            if match.cote_domicile:
                cotes["domicile"] = match.cote_domicile
            if match.cote_nul:
                cotes["nul"] = match.cote_nul
            if match.cote_exterieur:
                cotes["exterieur"] = match.cote_exterieur

            svc = obtenir_prediction_service()
            pred = svc.predire_resultat_match(forme_dom, forme_ext, h2h, cotes or None)

            return {
                "match_id": match.id,
                "equipe_domicile": match.equipe_domicile.nom if match.equipe_domicile else None,
                "equipe_exterieur": match.equipe_exterieur.nom if match.equipe_exterieur else None,
                "resultat": pred.prediction,
                "probas": pred.probabilites,
                "confiance": pred.confiance,
                "niveau_confiance": pred.niveau_confiance,
                "raisons": pred.raisons,
                "conseil": pred.conseil,
            }

    return await executer_async(_query)


@router.get("/paris/value-bets", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_value_bets(
    seuil_ev: float = Query(5.0, ge=0, description="Seuil edge % minimum"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les value bets (matchs avec edge > seuil)."""
    from src.core.models import Match
    from src.services.jeux import obtenir_odds_data_service, obtenir_prediction_service

    def _query():
        with executer_avec_session() as session:
            today = date.today()
            matchs = (
                session.query(Match)
                .filter(
                    Match.date_match >= today,
                    Match.joue.is_(False),
                    Match.cote_domicile.isnot(None),
                )
                .order_by(Match.date_match)
                .limit(30)
                .all()
            )
            odds_svc = obtenir_odds_data_service()
            pred_svc = obtenir_prediction_service()
            value_bets = []
            for m in matchs:
                try:
                    forme_dom = {
                        "victoires": m.equipe_domicile.victoires if m.equipe_domicile else 0,
                        "nuls": m.equipe_domicile.nuls if m.equipe_domicile else 0,
                        "defaites": m.equipe_domicile.defaites if m.equipe_domicile else 0,
                        "buts_marques": m.equipe_domicile.buts_marques if m.equipe_domicile else 0,
                        "buts_encaisses": m.equipe_domicile.buts_encaisses
                        if m.equipe_domicile
                        else 0,
                    }
                    forme_ext = {
                        "victoires": m.equipe_exterieur.victoires if m.equipe_exterieur else 0,
                        "nuls": m.equipe_exterieur.nuls if m.equipe_exterieur else 0,
                        "defaites": m.equipe_exterieur.defaites if m.equipe_exterieur else 0,
                        "buts_marques": m.equipe_exterieur.buts_marques
                        if m.equipe_exterieur
                        else 0,
                        "buts_encaisses": m.equipe_exterieur.buts_encaisses
                        if m.equipe_exterieur
                        else 0,
                    }
                    pred = pred_svc.predire_resultat_match(
                        forme_dom,
                        forme_ext,
                        {},
                        {
                            "domicile": m.cote_domicile,
                            "nul": m.cote_nul,
                            "exterieur": m.cote_exterieur,
                        },
                    )
                    # Trouver la meilleure proba vs cote
                    mapping = {
                        "domicile": (pred.probabilites.get("domicile", 0), m.cote_domicile),
                        "nul": (pred.probabilites.get("nul", 0), m.cote_nul),
                        "exterieur": (pred.probabilites.get("exterieur", 0), m.cote_exterieur),
                    }
                    for type_pari, (proba, cote) in mapping.items():
                        if proba and cote and proba > 0:
                            edge_info = odds_svc.calculer_edge(cote, proba)
                            if edge_info.get("edge_pct", 0) >= seuil_ev:
                                value_bets.append(
                                    {
                                        "match_id": m.id,
                                        "equipe_domicile": m.equipe_domicile.nom
                                        if m.equipe_domicile
                                        else None,
                                        "equipe_exterieur": m.equipe_exterieur.nom
                                        if m.equipe_exterieur
                                        else None,
                                        "date_match": m.date_match.isoformat(),
                                        "cote_bookmaker": cote,
                                        "proba_estimee": proba,
                                        "edge_pct": edge_info.get("edge_pct", 0),
                                        "ev": edge_info.get("ev", 0),
                                        "type_pari": type_pari,
                                        "prediction": pred.prediction,
                                    }
                                )
                except Exception:
                    continue
            value_bets.sort(key=lambda x: x["edge_pct"], reverse=True)
            return {"items": value_bets[:20]}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HISTORIQUE COTES (Heatmap)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/paris/cotes-historique/{match_id}", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_historique_cotes(
    match_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère l'historique des cotes d'un match pour heatmap."""
    from src.core.models import CoteHistorique

    def _query():
        with executer_avec_session() as session:
            historique = (
                session.query(CoteHistorique)
                .filter(CoteHistorique.match_id == match_id)
                .order_by(CoteHistorique.date_capture)
                .all()
            )
            if not historique:
                return {
                    "match_id": match_id,
                    "nb_points": 0,
                    "points": [],
                    "message": "Aucun historique disponible pour ce match",
                }
            return {
                "match_id": match_id,
                "nb_points": len(historique),
                "points": [
                    {
                        "timestamp": h.date_capture.isoformat(),
                        "cote_domicile": h.cote_domicile,
                        "cote_nul": h.cote_nul,
                        "cote_exterieur": h.cote_exterieur,
                        "cote_over_25": h.cote_over_25,
                        "cote_under_25": h.cote_under_25,
                        "bookmaker": h.bookmaker,
                    }
                    for h in historique
                ],
            }

    return await executer_async(_query)
