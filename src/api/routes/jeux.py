"""
Routes API pour les jeux (Paris sportifs & Loto).

Endpoints pour:
- Ã‰quipes et matchs de football
- Paris sportifs
- Tirages et grilles de loto
- Statistiques de jeux
- SÃ©ries et alertes (loi des sÃ©ries)
- PrÃ©dictions et value bets
- Jeu responsable
- Euromillions
- Dashboard agrÃ©gÃ©
- Performance et analytics
- Analyse IA
- Backtest
- Notifications
"""

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
    AutoExclusionRequest,
    EnregistrerMiseRequest,
    GenererGrilleRequest,
    ModifierLimiteRequest,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/jeux", tags=["Jeux"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰QUIPES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/equipes", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_equipes(
    championnat: str | None = Query(None, description="Filtrer par championnat"),
    search: str | None = Query(None, description="Recherche par nom"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les Ã©quipes de football."""
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
    """RÃ©cupÃ¨re une Ã©quipe avec sa forme rÃ©cente."""
    from src.core.models import Equipe

    def _query():
        with executer_avec_session() as session:
            equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
            if not equipe:
                raise HTTPException(status_code=404, detail="Ã‰quipe non trouvÃ©e")

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
    joue: bool | None = Query(None, description="Filtrer par statut jouÃ©/non jouÃ©"),
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
    """RÃ©cupÃ¨re un match avec ses paris."""
    from src.core.models import Match

    def _query():
        with executer_avec_session() as session:
            match = session.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvÃ©")

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
    pattern: str | None = Query(None, description="Pattern statistique dÃ©tectÃ©"),
    search: str | None = Query(None, description="Recherche Ã©quipe"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les matchs avec filtres avancÃ©s pour la vue Expert.
    
    Filtre par championnat, dates, EV, confiance IA, patterns statistiques.
    Retourne toutes les donnÃ©es nÃ©cessaires pour l'analyse experte.
    """
    from src.core.models import Match, Equipe
    from sqlalchemy import or_, and_, func

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

            # Filtres uniquement sur matchs non jouÃ©s avec prÃ©dictions
            query = query.filter(Match.joue == False)
            query = query.filter(Match.prediction_resultat.isnot(None))

            # Filtre par confiance IA
            if confidence_min is not None:
                query = query.filter(Match.prediction_confiance >= confidence_min)

            # Filtre par Expected Value (calculÃ©: meilleure_proba * meilleure_cote - 1)
            if ev_min is not None:
                # Filtre approximatif - le calcul exact EV nÃ©cessite de dÃ©terminer meilleure cote/proba
                # On utilise la confiance comme proxy pour filtrage initial
                query = query.filter(Match.prediction_confiance >= (ev_min / 0.20 + 0.5))

            # Filtre par recherche Ã©quipe
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

            # Construction des rÃ©sultats avec calcul EV
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

                # Filtre final par EV (aprÃ¨s calcul exact)
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

                matchs_data.append({
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
                    ) if m.prediction_resultat else None,
                    "confiance_ia": float(m.prediction_confiance) if m.prediction_confiance else None,
                    "pattern_detecte": pattern_detecte,
                    "forme_domicile": m.equipe_domicile.forme_recente if m.equipe_domicile else None,
                    "forme_exterieur": m.equipe_exterieur.forme_recente if m.equipe_exterieur else None,
                })

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
    bankroll_initiale: float = Query(1000, description="Bankroll de dÃ©part"),
    jours: int = Query(30, description="Historique sur N jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Obtient la bankroll actuelle et l'historique."""
    from src.services.jeux.bankroll_manager import get_bankroll_manager

    def _query():
        manager = get_bankroll_manager()
        
        # Calculer bankroll actuelle
        bankroll_actuelle = manager.calculer_bankroll_actuelle(
            user_id=user_id,
            bankroll_initiale=bankroll_initiale
        )
        
        # Obtenir historique
        historique = manager.obtenir_historique_bankroll(
            user_id=user_id,
            bankroll_initiale=bankroll_initiale,
            jours=jours
        )
        
        # Calculer variation et ROI
        variation_totale = bankroll_actuelle - bankroll_initiale
        
        # Calculer ROI depuis les paris
        with executer_avec_session() as session:
            from src.core.models import PariSportif
            from sqlalchemy import func
            
            total_mises = session.query(func.coalesce(func.sum(PariSportif.mise), 0)).filter(
                PariSportif.user_id == user_id
            ).scalar() or 0
            
            total_gains = session.query(func.coalesce(func.sum(PariSportif.gain), 0)).filter(
                PariSportif.user_id == user_id,
                PariSportif.statut == "gagne"
            ).scalar() or 0
            
            roi = manager.calculer_roi(total_mises, total_gains)
        
        return {
            "bankroll_actuelle": bankroll_actuelle,
            "bankroll_initiale": bankroll_initiale,
            "variation_totale": variation_totale,
            "roi": roi,
            "historique": historique
        }

    return await executer_async(_query)


@router.get("/bankroll/suggestion-mise", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suggerer_mise_kelly(
    bankroll: float = Query(..., description="Bankroll actuelle"),
    edge: float = Query(..., description="Expected value (EV)"),
    cote: float = Query(..., description="Cote dÃ©cimale"),
    confiance_ia: float = Query(70, description="Confiance de l'IA (0-100)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """SuggÃ¨re une mise optimale selon le critÃ¨re de Kelly fractionnaire."""
    from src.services.jeux.bankroll_manager import get_bankroll_manager

    def _query():
        manager = get_bankroll_manager()
        
        suggestion = manager.suggerer_mise(
            bankroll=bankroll,
            edge=edge,
            cote=cote,
            confiance_ia=confiance_ia
        )
        
        return {
            "mise_suggeree": suggestion.mise_suggeree,
            "mise_kelly_complete": suggestion.mise_kelly_complete,
            "fraction_utilisee": suggestion.fraction_utilisee,
            "edge": suggestion.edge,
            "pourcentage_bankroll": suggestion.pourcentage_bankroll,
            "confiance": suggestion.confiance,
            "message": suggestion.message
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
    est_virtuel: bool | None = Query(None, description="Paris virtuels ou rÃ©els"),
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
    est_virtuel: bool | None = Query(None, description="Stats paris virtuels ou rÃ©els"),
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

            # Taux de rÃ©ussite
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
    Analyse les patterns de paris de l'utilisateur pour dÃ©tecter les biais cognitifs.
    
    Retourne:
    - regression_moyenne: Alerte si sÃ©rie exceptionnelle (hot/cold streak)
    - hot_hand: Alerte si clustering de victoires (illusion main chaude)
    - gamblers_fallacy: Alerte si augmentation mise aprÃ¨s perte (erreur du parieur)
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
                "type_pattern": r.type_pattern
            }
        
        if resultats.get("hot_hand"):
            r = resultats["hot_hand"]
            response["hot_hand"] = {
                "alerte": r.alerte,
                "severite": r.severite,
                "message": r.message,
                "details": r.details,
                "type_pattern": r.type_pattern
            }
        
        if resultats.get("gamblers_fallacy"):
            r = resultats["gamblers_fallacy"]
            response["gamblers_fallacy"] = {
                "alerte": r.alerte,
                "severite": r.severite,
                "message": r.message,
                "details": r.details,
                "type_pattern": r.type_pattern
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
    """CrÃ©e un nouveau pari sportif."""
    from decimal import Decimal

    from src.core.models import Match, PariSportif
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        with executer_avec_session() as session:
            # Garde-fou budget responsable
            mise = Decimal(str(payload.get("mise", 0)))
            if mise > 0 and not payload.get("est_virtuel", True):
                svc_resp = obtenir_responsable_gaming_service()
                check = svc_resp.verifier_mise_autorisee(mise)
                if not check.get("autorisee", True):
                    raise HTTPException(
                        status_code=402,
                        detail=check.get("raison") or "Limite de mise mensuelle atteinte",
                    )

            match = session.query(Match).filter(Match.id == payload["match_id"]).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvÃ©")

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
    """Met Ã  jour un pari (statut, gain, etc.)."""
    from decimal import Decimal

    from src.core.models import PariSportif

    def _query():
        with executer_avec_session() as session:
            pari = session.query(PariSportif).filter(PariSportif.id == pari_id).first()
            if not pari:
                raise HTTPException(status_code=404, detail="Pari non trouvÃ©")

            if "statut" in payload:
                pari.statut = payload["statut"]
            if "gain" in payload:
                pari.gain = Decimal(str(payload["gain"]))
            if "notes" in payload:
                pari.notes = payload["notes"]

            session.commit()
            session.refresh(pari)
            return {
                "id": pari.id,
                "statut": pari.statut,
                "gain": float(pari.gain) if pari.gain else None,
                "mise": float(pari.mise),
            }

    return await executer_async(_query)


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
                raise HTTPException(status_code=404, detail="Pari non trouvÃ©")
            session.delete(pari)
            session.commit()
            return MessageResponse(message="Pari supprimÃ©")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOTO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
# DASHBOARD AGRÃ‰GÃ‰
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/dashboard", responses=REPONSES_LISTE)
@gerer_exception_api
async def dashboard_jeux(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Dashboard agrÃ©gÃ© : opportunitÃ©s, matchs du jour, budget, KPIs."""
    from sqlalchemy import func

    from src.core.models import Match, PariSportif
    from src.services.jeux import (
        obtenir_loto_data_service,
        obtenir_responsable_gaming_service,
        obtenir_series_service,
    )

    def _query():
        with executer_avec_session() as session:
            series_svc = obtenir_series_service()
            responsable_svc = obtenir_responsable_gaming_service()
            loto_data_svc = obtenir_loto_data_service()

            # 1. OpportunitÃ©s (sÃ©ries avec value >= 2.0)
            opportunites_raw = series_svc.detecter_opportunites(seuil=2.0)
            opportunites = [
                {
                    "id": s.id,
                    "type_jeu": s.type_jeu,
                    "marche": s.marche,
                    "championnat": s.championnat,
                    "serie_actuelle": s.serie_actuelle,
                    "frequence": s.frequence,
                    "value": s.value,
                    "niveau_opportunite": series_svc.niveau_opportunite(s.value),
                }
                for s in (opportunites_raw or [])[:5]
            ]

            # 2. Matchs du jour
            today = date.today()
            matchs_jour = (
                session.query(Match)
                .filter(Match.date_match == today, Match.joue.is_(False))
                .order_by(Match.heure)
                .limit(10)
                .all()
            )
            matchs_data = [
                {
                    "id": m.id,
                    "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else None,
                    "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else None,
                    "championnat": m.championnat,
                    "heure": m.heure,
                    "cote_domicile": m.cote_domicile,
                    "cote_nul": m.cote_nul,
                    "cote_exterieur": m.cote_exterieur,
                    "prediction": {
                        "resultat": m.prediction_resultat,
                        "confiance": m.prediction_confiance,
                    }
                    if m.prediction_resultat
                    else None,
                }
                for m in matchs_jour
            ]

            # 3. Loto numÃ©ros en retard
            try:
                numeros_retard_raw = loto_data_svc.obtenir_numeros_en_retard(seuil_value=2.0)
                loto_retard = [
                    {
                        "numero": n.numero,
                        "type_numero": n.type_numero,
                        "serie_actuelle": n.serie_actuelle,
                        "frequence": n.frequence,
                        "value": n.value,
                    }
                    for n in (numeros_retard_raw or [])[:5]
                ]
            except Exception:
                loto_retard = []

            # 4. Budget responsable
            try:
                budget_raw = responsable_svc.obtenir_suivi_mensuel()
                budget = {
                    "limite": budget_raw.get("limite_mensuelle", 50.0),
                    "mises_cumulees": budget_raw.get("mises_cumulees", 0.0),
                    "pourcentage_utilise": budget_raw.get("pourcentage", 0.0),
                    "reste_disponible": budget_raw.get("reste_disponible", 50.0),
                    "cooldown_actif": budget_raw.get("cooldown_actif", False),
                    "auto_exclusion_jusqu_a": str(budget_raw["auto_exclusion"])
                    if budget_raw.get("auto_exclusion")
                    else None,
                }
            except Exception:
                budget = {
                    "limite": 50.0,
                    "mises_cumulees": 0.0,
                    "pourcentage_utilise": 0.0,
                    "reste_disponible": 50.0,
                    "cooldown_actif": False,
                    "auto_exclusion_jusqu_a": None,
                }

            # 5. KPIs du mois
            debut_mois = today.replace(day=1)
            stats = (
                session.query(
                    func.count(PariSportif.id),
                    func.coalesce(func.sum(PariSportif.mise), 0),
                    func.coalesce(
                        func.sum(
                            func.case(
                                (PariSportif.statut == "gagne", PariSportif.gain),
                                else_=0,
                            )
                        ),
                        0,
                    ),
                )
                .filter(PariSportif.cree_le >= debut_mois)
                .first()
            )
            nb_paris, total_mise, total_gain = stats or (0, 0, 0)
            total_mise_f = float(total_mise)
            total_gain_f = float(total_gain)
            roi_mois = ((total_gain_f - total_mise_f) / total_mise_f * 100) if total_mise_f > 0 else 0.0

            resolus = (
                session.query(func.count(PariSportif.id))
                .filter(
                    PariSportif.cree_le >= debut_mois,
                    PariSportif.statut.in_(["gagne", "perdu"]),
                )
                .scalar()
                or 0
            )
            gagnes = (
                session.query(func.count(PariSportif.id))
                .filter(PariSportif.cree_le >= debut_mois, PariSportif.statut == "gagne")
                .scalar()
                or 0
            )
            taux = (gagnes / resolus * 100) if resolus > 0 else 0.0

            paris_actifs = (
                session.query(func.count(PariSportif.id))
                .filter(PariSportif.statut == "en_attente")
                .scalar()
                or 0
            )

            kpis = {
                "roi_mois": round(roi_mois, 1),
                "taux_reussite_mois": round(taux, 1),
                "benefice_mois": round(total_gain_f - total_mise_f, 2),
                "paris_actifs": paris_actifs,
            }

            return {
                "opportunites": opportunites,
                "matchs_jour": matchs_data,
                "value_bets": [],
                "loto_retard": loto_retard,
                "budget": budget,
                "kpis": kpis,
                "analyse_ia": None,
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SÃ‰RIES & ALERTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/series", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_series(
    type_jeu: str | None = Query(None, description="paris, loto, euromillions"),
    seuil: float = Query(2.0, ge=0),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tecte les opportunitÃ©s (sÃ©ries avec value >= seuil)."""
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
    """Liste les alertes non notifiÃ©es."""
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
# PRÃ‰DICTIONS & VALUE BETS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/paris/predictions/{match_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def prediction_match(
    match_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """PrÃ©diction IA pour un match donnÃ©."""
    from src.core.models import Match
    from src.services.jeux import obtenir_prediction_service

    def _query():
        with executer_avec_session() as session:
            match = session.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise HTTPException(status_code=404, detail="Match non trouvÃ©")

            # Construire les donnÃ©es de forme
            forme_dom = {
                "victoires": match.equipe_domicile.victoires if match.equipe_domicile else 0,
                "nuls": match.equipe_domicile.nuls if match.equipe_domicile else 0,
                "defaites": match.equipe_domicile.defaites if match.equipe_domicile else 0,
                "buts_marques": match.equipe_domicile.buts_marques if match.equipe_domicile else 0,
                "buts_encaisses": match.equipe_domicile.buts_encaisses if match.equipe_domicile else 0,
                "forme_recente": match.equipe_domicile.forme_recente if match.equipe_domicile else None,
            }
            forme_ext = {
                "victoires": match.equipe_exterieur.victoires if match.equipe_exterieur else 0,
                "nuls": match.equipe_exterieur.nuls if match.equipe_exterieur else 0,
                "defaites": match.equipe_exterieur.defaites if match.equipe_exterieur else 0,
                "buts_marques": match.equipe_exterieur.buts_marques if match.equipe_exterieur else 0,
                "buts_encaisses": match.equipe_exterieur.buts_encaisses if match.equipe_exterieur else 0,
                "forme_recente": match.equipe_exterieur.forme_recente if match.equipe_exterieur else None,
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
                        "buts_encaisses": m.equipe_domicile.buts_encaisses if m.equipe_domicile else 0,
                    }
                    forme_ext = {
                        "victoires": m.equipe_exterieur.victoires if m.equipe_exterieur else 0,
                        "nuls": m.equipe_exterieur.nuls if m.equipe_exterieur else 0,
                        "defaites": m.equipe_exterieur.defaites if m.equipe_exterieur else 0,
                        "buts_marques": m.equipe_exterieur.buts_marques if m.equipe_exterieur else 0,
                        "buts_encaisses": m.equipe_exterieur.buts_encaisses if m.equipe_exterieur else 0,
                    }
                    pred = pred_svc.predire_resultat_match(forme_dom, forme_ext, {}, {
                        "domicile": m.cote_domicile,
                        "nul": m.cote_nul,
                        "exterieur": m.cote_exterieur,
                    })

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
                                value_bets.append({
                                    "match_id": m.id,
                                    "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else None,
                                    "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else None,
                                    "date_match": m.date_match.isoformat(),
                                    "cote_bookmaker": cote,
                                    "proba_estimee": proba,
                                    "edge_pct": edge_info.get("edge_pct", 0),
                                    "ev": edge_info.get("ev", 0),
                                    "type_pari": type_pari,
                                    "prediction": pred.prediction,
                                })
                except Exception:
                    continue

            value_bets.sort(key=lambda x: x["edge_pct"], reverse=True)
            return {"items": value_bets[:20]}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOTO STATS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/loto/stats", responses=REPONSES_LISTE)
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
            sorted_nums = sorted(stats.numeros_principaux.items(), key=lambda x: x[1].frequence, reverse=True)
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


@router.get("/loto/numeros-retard", responses=REPONSES_LISTE)
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
# EUROMILLIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/euromillions/tirages", responses=REPONSES_LISTE)
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


@router.get("/euromillions/grilles", responses=REPONSES_LISTE)
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


@router.post("/euromillions/grilles", status_code=201, responses=REPONSES_CRUD_CREATION)
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


@router.get("/euromillions/stats", responses=REPONSES_LISTE)
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


@router.get("/euromillions/grilles-expert", responses=REPONSES_LISTE)
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
    from datetime import datetime

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
                    (GrilleEuromillions.explication.ilike(f"%{safe_search}%")) |
                    (GrilleEuromillions.strategie.ilike(f"%{safe_search}%"))
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
                items.append({
                    "id": g.id,
                    "numeros": g.numeros,
                    "etoiles": g.etoiles,
                    "date_tirage": g.date_tirage.isoformat() if g.date_tirage else None,
                    "strategie": g.strategie or "inconnue",
                    "qualite": g.qualite or 0,
                    "explication": g.explication or "",
                    "distribution": g.distribution or {},
                    "backtest": g.backtest if hasattr(g, "backtest") else None,
                    "statut": g.statut if hasattr(g, "statut") else "en_attente"
                })
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0
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
            "distribution": grille.distribution
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION DE GRILLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/loto/generer-grille", responses=REPONSES_CRUD_CREATION)
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
        available = list(zip(nums, weights))
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


@router.get("/stats/personnelles/{user_id}")
@gerer_exception_api
async def obtenir_stats_personnelles(
    user_id: int,
    periode: int = Query(30, description="PÃ©riode en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    RÃ©cupÃ¨re les statistiques personnelles d'un utilisateur.
    
    Retourne:
    - ROI global
    - Win rate par type
    - Meilleurs patterns
    - Ã‰volution mensuelle
    """
    
    def _query():
        from src.services.jeux.stats_personnelles import StatsPersonnellesService
        
        service = StatsPersonnellesService()
        
        roi_data = service.calculer_roi_global(user_id, jours=periode)
        winrate_data = service.calculer_win_rate(user_id, jours=periode)
        patterns_data = service.analyser_patterns_gagnants(user_id, jours=periode * 3)  # 3Ã— pÃ©riode pour patterns
        evolution_data = service.obtenir_evolution_mensuelle(user_id, mois=6)
        
        return {
            "roi": roi_data,
            "win_rate": winrate_data,
            "patterns": patterns_data,
            "evolution": evolution_data["evolution"]
        }
    
    return await executer_async(_query)


@router.post("/euromillions/generer-grille", responses=REPONSES_CRUD_CREATION)
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
        available = list(zip(nums, weights))
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
        star_weights = [max(float(freq_stars.get(str(s), freq_stars.get(s, 0.1))), 0.1) for s in stars]

        etoiles = []
        available_stars = list(zip(stars, star_weights))
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PERFORMANCE & ANALYTICS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/performance", responses=REPONSES_LISTE)
@gerer_exception_api
async def performance_jeux(
    mois: int | None = Query(None, ge=1, le=24, description="Nombre de mois (dÃ©faut: 6)"),
    type_jeu: str | None = Query(None, description="paris ou loto"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Performance globale avec analytics par mois, championnat, type de pari."""
    from sqlalchemy import extract, func

    from src.core.models import Match, PariSportif

    nb_mois = mois or 6

    def _query():
        with executer_avec_session() as session:
            today = date.today()
            date_debut = today.replace(day=1)
            for _ in range(nb_mois - 1):
                date_debut = (date_debut - __import__("datetime").timedelta(days=1)).replace(day=1)

            base_q = session.query(PariSportif).filter(PariSportif.cree_le >= date_debut)

            # Global stats
            total = base_q.count()
            total_mise = float(base_q.with_entities(func.sum(PariSportif.mise)).scalar() or 0)
            total_gain = float(
                base_q.filter(PariSportif.statut == "gagne")
                .with_entities(func.sum(PariSportif.gain))
                .scalar()
                or 0
            )
            resolus = base_q.filter(PariSportif.statut.in_(["gagne", "perdu"])).count()
            gagnes = base_q.filter(PariSportif.statut == "gagne").count()
            taux = (gagnes / resolus * 100) if resolus > 0 else 0.0
            roi = ((total_gain - total_mise) / total_mise * 100) if total_mise > 0 else 0.0

            # Par mois
            par_mois_raw = (
                base_q.with_entities(
                    extract("year", PariSportif.cree_le).label("annee"),
                    extract("month", PariSportif.cree_le).label("mois_num"),
                    func.count(PariSportif.id),
                    func.sum(PariSportif.mise),
                    func.sum(
                        func.case(
                            (PariSportif.statut == "gagne", PariSportif.gain),
                            else_=0,
                        )
                    ),
                )
                .group_by("annee", "mois_num")
                .order_by("annee", "mois_num")
                .all()
            )
            par_mois = []
            best_roi, worst_roi = None, None
            best_mois, worst_mois = None, None
            cumul_bankroll = 0.0
            for annee, mois_num, nb, mise_m, gain_m in par_mois_raw:
                mise_f = float(mise_m or 0)
                gain_f = float(gain_m or 0)
                benefice_m = gain_f - mise_f
                cumul_bankroll += benefice_m
                roi_m = ((gain_f - mise_f) / mise_f * 100) if mise_f > 0 else 0.0
                label = f"{int(annee)}-{int(mois_num):02d}"
                par_mois.append({
                    "mois": label,
                    "roi": round(roi_m, 1),
                    "nb_paris": nb,
                    "benefice": round(benefice_m, 2),
                    "bankroll_cumul": round(cumul_bankroll, 2),
                })
                if best_roi is None or roi_m > best_roi:
                    best_roi, best_mois = roi_m, label
                if worst_roi is None or roi_m < worst_roi:
                    worst_roi, worst_mois = roi_m, label

            # SÃ©ries gagnantes/perdantes
            paris_ordonnes = (
                base_q.filter(PariSportif.statut.in_(["gagne", "perdu"]))
                .order_by(PariSportif.cree_le)
                .with_entities(PariSportif.statut)
                .all()
            )
            max_win, max_lose, cur_win, cur_lose = 0, 0, 0, 0
            for (statut,) in paris_ordonnes:
                if statut == "gagne":
                    cur_win += 1
                    cur_lose = 0
                else:
                    cur_lose += 1
                    cur_win = 0
                max_win = max(max_win, cur_win)
                max_lose = max(max_lose, cur_lose)

            # Par championnat (jointure PariSportif â†’ Match)
            par_champ_raw = (
                session.query(
                    Match.championnat,
                    func.count(PariSportif.id),
                    func.sum(func.case((PariSportif.statut == "gagne", 1), else_=0)),
                    func.sum(PariSportif.mise),
                    func.sum(func.case((PariSportif.statut == "gagne", PariSportif.gain), else_=0)),
                )
                .join(PariSportif, PariSportif.match_id == Match.id)
                .filter(PariSportif.cree_le >= date_debut)
                .group_by(Match.championnat)
                .all()
            )
            par_championnat = {}
            for champ, nb_c, gag_c, mise_c, gain_c in par_champ_raw:
                mise_f = float(mise_c or 0)
                gain_f = float(gain_c or 0)
                par_championnat[str(champ)] = {
                    "nb": nb_c,
                    "gagnes": int(gag_c or 0),
                    "taux": round(int(gag_c or 0) / nb_c * 100, 1) if nb_c > 0 else 0.0,
                    "roi": round((gain_f - mise_f) / mise_f * 100, 1) if mise_f > 0 else 0.0,
                }

            # Par type_pari
            par_type_raw = (
                base_q.with_entities(
                    PariSportif.type_pari,
                    func.count(PariSportif.id),
                    func.sum(func.case((PariSportif.statut == "gagne", 1), else_=0)),
                )
                .filter(PariSportif.statut.in_(["gagne", "perdu"]))
                .group_by(PariSportif.type_pari)
                .all()
            )
            par_type_pari = {}
            for type_p, nb_t, gag_t in par_type_raw:
                par_type_pari[str(type_p)] = {
                    "nb": nb_t,
                    "gagnes": int(gag_t or 0),
                    "taux": round(int(gag_t or 0) / nb_t * 100, 1) if nb_t > 0 else 0.0,
                }

            return {
                "roi": round(roi, 1),
                "taux_reussite": round(taux, 1),
                "benefice": round(total_gain - total_mise, 2),
                "nb_paris": total,
                "par_mois": par_mois,
                "par_championnat": par_championnat,
                "par_type_pari": par_type_pari,
                "meilleur_mois": best_mois,
                "pire_mois": worst_mois,
                "serie_gagnante_max": max_win,
                "serie_perdante_max": max_lose,
            }

    return await executer_async(_query)


@router.get("/performance/confiance", responses=REPONSES_LISTE)
@gerer_exception_api
async def performance_par_confiance(
    mois: int | None = Query(None, ge=1, le=24, description="Nombre de mois Ã  analyser (dÃ©faut: 6)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Distribution taux de rÃ©ussite par tranche de confiance IA (0-25%, 25-50%, 50-75%, 75-100%)."""
    from sqlalchemy import func

    from src.core.models import PariSportif

    nb_mois = mois or 6

    def _query():
        with executer_avec_session() as session:
            today = date.today()
            date_debut = today.replace(day=1)
            for _ in range(nb_mois - 1):
                date_debut = (date_debut - __import__("datetime").timedelta(days=1)).replace(day=1)

            paris = (
                session.query(PariSportif)
                .filter(
                    PariSportif.cree_le >= date_debut,
                    PariSportif.statut.in_(["gagne", "perdu"]),
                    PariSportif.confiance_prediction.isnot(None),
                )
                .with_entities(PariSportif.confiance_prediction, PariSportif.statut)
                .all()
            )

            tranches = {
                "0-25": {"nb": 0, "gagnes": 0},
                "25-50": {"nb": 0, "gagnes": 0},
                "50-75": {"nb": 0, "gagnes": 0},
                "75-100": {"nb": 0, "gagnes": 0},
            }
            for conf, statut in paris:
                if conf is None:
                    continue
                c = float(conf) * 100 if float(conf) <= 1.0 else float(conf)
                if c < 25:
                    k = "0-25"
                elif c < 50:
                    k = "25-50"
                elif c < 75:
                    k = "50-75"
                else:
                    k = "75-100"
                tranches[k]["nb"] += 1
                if statut == "gagne":
                    tranches[k]["gagnes"] += 1

            result = []
            for tranche, vals in tranches.items():
                nb = vals["nb"]
                gag = vals["gagnes"]
                result.append({
                    "tranche": tranche,
                    "nb": nb,
                    "gagnes": gag,
                    "taux": round(gag / nb * 100, 1) if nb > 0 else 0.0,
                })
            return {"tranches": result, "total": sum(t["nb"] for t in result)}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RÃ‰SUMÃ‰ MENSUEL IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/resume-mensuel", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def resume_mensuel(
    mois: str | None = Query(None, description="Format YYYY-MM (dÃ©faut: mois courant)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©sumÃ© mensuel IA avec analyse Mistral enrichie."""
    from sqlalchemy import func

    from src.core.models import PariSportif
    from src.services.jeux import obtenir_jeux_ai_service

    def _query():
        today = date.today()
        if mois:
            parts = mois.split("-")
            if len(parts) != 2:
                raise HTTPException(status_code=400, detail="Format YYYY-MM attendu")
            annee, mois_num = int(parts[0]), int(parts[1])
        else:
            annee, mois_num = today.year, today.month

        debut = date(annee, mois_num, 1)
        if mois_num == 12:
            fin = date(annee + 1, 1, 1)
        else:
            fin = date(annee, mois_num + 1, 1)

        with executer_avec_session() as session:
            q = session.query(PariSportif).filter(
                PariSportif.cree_le >= debut,
                PariSportif.cree_le < fin,
            )
            total = q.count()
            mise = float(q.with_entities(func.sum(PariSportif.mise)).scalar() or 0)
            gain = float(
                q.filter(PariSportif.statut == "gagne")
                .with_entities(func.sum(PariSportif.gain))
                .scalar()
                or 0
            )
            resolus = q.filter(PariSportif.statut.in_(["gagne", "perdu"])).count()
            gagnes = q.filter(PariSportif.statut == "gagne").count()
            taux = (gagnes / resolus * 100) if resolus > 0 else 0.0
            roi = ((gain - mise) / mise * 100) if mise > 0 else 0.0

            kpis = {
                "roi_mois": round(roi, 1),
                "taux_reussite_mois": round(taux, 1),
                "benefice_mois": round(gain - mise, 2),
                "paris_actifs": q.filter(PariSportif.statut == "en_attente").count(),
                "nb_paris_total": total,
            }

            mois_str = f"{annee}-{mois_num:02d}"

            # GÃ©nÃ©rer le rÃ©sumÃ© IA enrichi
            try:
                ai_svc = obtenir_jeux_ai_service()
                resume = ai_svc.generer_resume_mensuel(mois_str, kpis)
                return resume
            except Exception as e:
                logger.warning(f"Erreur IA rÃ©sumÃ© mensuel, fallback: {e}")
                # Fallback simple si IA Ã©choue
                points_forts = []
                points_faibles = []
                if roi > 0:
                    points_forts.append(f"ROI positif de {roi:.1f}%")
                else:
                    points_faibles.append(f"ROI nÃ©gatif de {roi:.1f}%")
                if taux >= 50:
                    points_forts.append(f"Taux de rÃ©ussite de {taux:.1f}%")
                elif resolus > 0:
                    points_faibles.append(f"Taux de rÃ©ussite bas: {taux:.1f}%")

                return {
                    "mois": mois_str,
                    "analyse": f"En {mois_num:02d}/{annee}, vous avez placÃ© {total} paris pour un ROI de {roi:.1f}%.",
                    "points_forts": points_forts or ["Aucun point fort ce mois"],
                    "points_faibles": points_faibles or ["Performances Ã  amÃ©liorer"],
                    "recommandations": [
                        "Continuez Ã  privilÃ©gier les value bets avec edge > 5%",
                        "Respectez votre budget mensuel de jeu responsable",
                    ],
                    "kpis": kpis,
                }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JEU RESPONSABLE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/responsable/suivi", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suivi_responsable(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suivi mensuel du budget jeu responsable avec sÃ©rie actuelle."""
    from datetime import date

    from src.core.models import PariSportif
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        raw = svc.obtenir_suivi_mensuel()

        # Calculer la sÃ©rie actuelle (pertes/gains consÃ©cutifs rÃ©cents)
        with executer_avec_session() as session:
            paris_recents = (
                session.query(PariSportif.statut)
                .filter(PariSportif.statut.in_(["gagne", "perdu"]))
                .order_by(PariSportif.cree_le.desc())
                .limit(20)
                .all()
            )

        serie_nb = 0
        serie_type = None
        for (statut,) in paris_recents:
            if serie_type is None:
                serie_type = statut
                serie_nb = 1
            elif statut == serie_type:
                serie_nb += 1
            else:
                break

        return {
            "limite": raw.get("limite_mensuelle", 50.0),
            "mises_cumulees": raw.get("mises_cumulees", 0.0),
            "pourcentage_utilise": raw.get("pourcentage", 0.0),
            "reste_disponible": raw.get("reste_disponible", 50.0),
            "alertes": raw.get("alertes", {}),
            "cooldown_actif": raw.get("cooldown_actif", False),
            "auto_exclusion_jusqu_a": str(raw["auto_exclusion"])
            if raw.get("auto_exclusion")
            else None,
            "serie_actuelle": {
                "type": serie_type,
                "nb": serie_nb,
                "alerte_active": serie_type == "perdu" and serie_nb >= 5,
            } if serie_type else None,
        }

    return await executer_async(_query)


@router.get("/responsable/verifier-mise", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def verifier_mise(
    montant: float = Query(..., gt=0, description="Montant de la mise Ã  vÃ©rifier"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """VÃ©rifie si une mise est autorisÃ©e par le budget."""
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        result = svc.verifier_mise_autorisee(Decimal(str(montant)))
        return {
            "autorise": result.get("autorisee", True),
            "raison": result.get("raison"),
            "reste_apres": result.get("reste_apres", 0),
        }

    return await executer_async(_query)


@router.post("/responsable/enregistrer-mise", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def enregistrer_mise(
    payload: EnregistrerMiseRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une mise dans le suivi responsable."""
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        result = svc.enregistrer_mise(Decimal(str(payload.montant)), payload.type_jeu)
        return result

    return await executer_async(_query)


@router.put("/responsable/limite", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_limite(
    payload: ModifierLimiteRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie la limite mensuelle de jeu."""
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        svc.modifier_limite(Decimal(str(payload.nouvelle_limite)))
        return {"limite": payload.nouvelle_limite, "message": "Limite mise Ã  jour"}

    return await executer_async(_query)


@router.post("/responsable/auto-exclusion", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def activer_auto_exclusion(
    payload: AutoExclusionRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Active l'auto-exclusion pour N jours."""
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        date_fin = svc.activer_auto_exclusion(payload.nb_jours)
        return {
            "auto_exclusion_jusqu_a": str(date_fin),
            "nb_jours": payload.nb_jours,
            "message": f"Auto-exclusion activÃ©e jusqu'au {date_fin}",
        }

    return await executer_async(_query)


@router.get("/responsable/historique", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_limites(
    nb_mois: int = Query(12, ge=1, le=24),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des limites et mises sur les N derniers mois."""
    from src.services.jeux import obtenir_responsable_gaming_service

    def _query():
        svc = obtenir_responsable_gaming_service()
        historique = svc.obtenir_historique_limites(nb_mois=nb_mois)
        return {"items": historique or []}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/ocr-ticket", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def analyser_ticket_ocr_jeux(
    file: UploadFile = File(..., description="Photo du ticket de jeu (JPEG/PNG/WebP)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse OCR d'un ticket loto/euromillions via IA vision."""
    contenu = await file.read()
    from src.services.utilitaires.ocr_service import obtenir_ocr_service

    service = obtenir_ocr_service()
    try:
        service.valider_upload_image(file.content_type, contenu, "JPEG, PNG, WebP")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resultat = service.extraire_ticket(contenu)

    if not resultat:
        return {
            "success": False,
            "message": "Analyse OCR impossible. Essayez une photo plus nette et bien cadrÃ©e.",
            "donnees": None,
        }

    return {
        "success": True,
        "message": "Ticket analysÃ© avec succÃ¨s",
        "donnees": service.formater_donnees_jeux(resultat),
    }


@router.post("/analyse-ia", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def analyse_ia(
    payload: AnalyseIARequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©clenche une analyse IA (paris ou loto)."""
    from src.services.jeux import obtenir_jeux_ai_service

    def _query():
        svc = obtenir_jeux_ai_service()

        if payload.type == "paris":
            result = svc.analyser_paris(
                opportunites=payload.data.get("opportunites", []),
                competition=payload.data.get("competition", "GÃ©nÃ©ral"),
            )
        else:
            result = svc.analyser_loto(
                numeros_retard=payload.data.get("numeros_retard", []),
                type_numero=payload.data.get("type_numero", "principal"),
            )

        return {
            "resume": result.resume,
            "points_cles": result.points_cles,
            "recommandations": result.recommandations,
            "avertissement": result.avertissement,
            "confiance": result.confiance,
            "genere_le": result.genere_le.isoformat() if result.genere_le else None,
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION & ANALYSE IA AVANCÃ‰E (Phase U)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/loto/generer-grille-ia-ponderee", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def generer_grille_ia_ponderee(
    mode: str = Query("equilibre", regex="^(chauds|froids|equilibre)$"),
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
    from src.services.jeux import obtenir_jeux_ai_service, obtenir_loto_crud_service, obtenir_loto_data_service

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


@router.post("/loto/analyser-grille", responses=REPONSES_CRUD_CREATION)
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HISTORIQUE COTES (Phase T - Heatmap)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/paris/cotes-historique/{match_id}", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_historique_cotes(
    match_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©cupÃ¨re l'historique des cotes d'un match pour heatmap."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BACKTEST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/backtest", responses=REPONSES_LISTE)
@gerer_exception_api
async def backtest_jeux(
    type_jeu: str = Query("loto", description="loto, euromillions ou paris"),
    seuil_value: float = Query(2.0, ge=0),
    nb_tirages: int = Query(100, ge=10, le=1000),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Backtest des stratÃ©gies sur les donnÃ©es historiques."""
    from src.services.jeux import (
        obtenir_backtest_service,
        obtenir_euromillions_crud_service,
        obtenir_loto_crud_service,
    )

    def _query():
        backtest_svc = obtenir_backtest_service()

        if type_jeu == "loto":
            loto_svc = obtenir_loto_crud_service()
            tirages = loto_svc.charger_tirages(limite=nb_tirages)
            result = backtest_svc.backtester_loto(tirages, seuil_value=seuil_value)
        elif type_jeu == "euromillions":
            euro_svc = obtenir_euromillions_crud_service()
            tirages_euro = euro_svc.obtenir_tirages(limite=nb_tirages)
            tirages_normalises = [
                {
                    "numeros": t.get("numeros", []),
                    "date": t.get("date_tirage"),
                }
                for t in tirages_euro
            ]
            result = backtest_svc.backtester_loto(tirages_normalises, seuil_value=seuil_value)
        else:
            result = backtest_svc.backtester_paris([], marche="1x2", seuil_value=seuil_value)

        return {
            "type_jeu": type_jeu,
            "nb_predictions": result.nb_predictions if result else 0,
            "nb_correctes": result.nb_correctes if result else 0,
            "taux_reussite": result.taux_reussite if result else 0.0,
            "tirages_moyens": result.tirages_moyens_avant_realisation if result else 0.0,
            "seuil_value": seuil_value,
            "avertissement": "Les performances passÃ©es ne prÃ©jugent pas des rÃ©sultats futurs.",
        }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NOTIFICATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/notifications", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_notifications(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les notifications non lues."""
    from src.services.jeux import obtenir_notification_jeux_service

    def _query():
        svc = obtenir_notification_jeux_service()
        notifs = svc.obtenir_non_lues()
        return {
            "items": [
                {
                    "id": n.id,
                    "type": n.type.value if hasattr(n.type, "value") else str(n.type),
                    "titre": n.titre,
                    "message": n.message,
                    "urgence": n.urgence.value if hasattr(n.urgence, "value") else str(n.urgence),
                    "type_jeu": n.type_jeu,
                    "lue": n.lue,
                    "date_creation": n.cree_le.isoformat() if n.cree_le else None,
                }
                for n in (notifs or [])
            ],
            "total_non_lues": svc.compter_non_lues(),
        }

    return await executer_async(_query)


@router.post("/notifications/{notification_id}/lue", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def marquer_notification_lue(
    notification_id: str,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Marque une notification comme lue."""
    from src.services.jeux import obtenir_notification_jeux_service

    def _query():
        svc = obtenir_notification_jeux_service()
        success = svc.marquer_lue(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification non trouvÃ©e")
        return MessageResponse(message="Notification marquÃ©e comme lue")

    return await executer_async(_query)

