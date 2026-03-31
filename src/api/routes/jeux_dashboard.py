"""Routes API jeux - Dashboard, Performance, Resume Mensuel, Analyse IA, Backtest, Notifications.

Sous-module de jeux.py. Le routeur n'a pas de prefixe ici,
car le prefixe /api/v1/jeux est defini dans jeux.py (agregateur).
"""

from __future__ import annotations

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
import logging

logger = logging.getLogger(__name__)

router = APIRouter()








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
        obtenir_series_service,
    )
    def _query():
        with executer_avec_session() as session:
            series_svc = obtenir_series_service()
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
            # 4. KPIs du mois
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
                "kpis": kpis,
                "analyse_ia": None,
            }
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

