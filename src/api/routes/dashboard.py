"""
Routes API pour le tableau de bord.

AgrÃ©gation des donnÃ©es de tous les modules pour la page d'accueil.
"""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["Tableau de bord"])


class DashboardConfigRequest(BaseModel):
    """Configuration personnalisÃ©e des widgets dashboard."""

    config_dashboard: dict[str, Any] = Field(default_factory=dict)


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_tableau_bord(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne les donnÃ©es agrÃ©gÃ©es du tableau de bord.

    Inclut: statistiques rapides, budget du mois, prochaines activitÃ©s, alertes.
    """

    def _query():
        with executer_avec_session() as session:
            from src.core.models import (
                ActiviteFamille,
                ArticleInventaire,
                BudgetFamille,
                Recette,
                Repas,
                StockMaison,
                TacheEntretien,
            )

            aujourd_hui = date.today()
            debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            fin_semaine = debut_semaine + timedelta(days=6)
            debut_mois = aujourd_hui.replace(day=1)

            # Statistiques rapides
            recettes_total = session.query(func.count(Recette.id)).scalar() or 0

            repas_semaine = (
                session.query(func.count(Repas.id))
                .filter(
                    Repas.date_repas >= debut_semaine,
                    Repas.date_repas <= fin_semaine,
                )
                .scalar()
                or 0
            )

            # TÃ¢ches entretien en retard
            taches_retard = (
                session.query(func.count(TacheEntretien.id))
                .filter(
                    TacheEntretien.prochaine_fois < aujourd_hui,
                    TacheEntretien.fait == False,  # noqa: E712
                )
                .scalar()
                or 0
            )

            # ActivitÃ©s Ã  venir (7 prochains jours)
            activites_a_venir = (
                session.query(func.count(ActiviteFamille.id))
                .filter(
                    ActiviteFamille.date_prevue >= aujourd_hui,
                    ActiviteFamille.date_prevue <= aujourd_hui + timedelta(days=7),
                )
                .scalar()
                or 0
            )

            # Stocks en alerte
            stocks_alerte = (
                session.query(func.count(StockMaison.id))
                .filter(StockMaison.quantite <= StockMaison.seuil_alerte)
                .scalar()
                or 0
            )

            # Budget du mois
            budget_total = (
                session.query(func.sum(BudgetFamille.montant))
                .filter(BudgetFamille.date >= debut_mois)
                .scalar()
                or 0
            )

            budget_par_cat = (
                session.query(
                    BudgetFamille.categorie,
                    func.sum(BudgetFamille.montant).label("total"),
                )
                .filter(BudgetFamille.date >= debut_mois)
                .group_by(BudgetFamille.categorie)
                .all()
            )

            # Prochaines activitÃ©s (5 max)
            prochaines = (
                session.query(ActiviteFamille)
                .filter(ActiviteFamille.date_prevue >= aujourd_hui)
                .order_by(ActiviteFamille.date_prevue.asc())
                .limit(5)
                .all()
            )

            # Alertes: articles inventaire bientÃ´t pÃ©rimÃ©s (7 jours)
            alertes = []
            try:
                articles_perissables = (
                    session.query(ArticleInventaire)
                    .filter(
                        ArticleInventaire.date_peremption.isnot(None),
                        ArticleInventaire.date_peremption
                        <= aujourd_hui + timedelta(days=7),
                        ArticleInventaire.date_peremption >= aujourd_hui,
                    )
                    .order_by(ArticleInventaire.date_peremption.asc())
                    .limit(10)
                    .all()
                )
                for a in articles_perissables:
                    jours = (a.date_peremption - aujourd_hui).days
                    alertes.append(
                        {
                            "type": "peremption",
                            "message": f"{a.nom} expire dans {jours} jour(s)",
                            "urgence": "haute" if jours <= 2 else "moyenne",
                        }
                    )
            except Exception as e:
                logger.warning("[dashboard] Alertes pÃ©remption non chargÃ©es: %s", e)

            if stocks_alerte > 0:
                alertes.append(
                    {
                        "type": "stock",
                        "message": f"{stocks_alerte} stock(s) maison en alerte",
                        "urgence": "moyenne",
                    }
                )

            if taches_retard > 0:
                alertes.append(
                    {
                        "type": "entretien",
                        "message": f"{taches_retard} tÃ¢che(s) d'entretien en retard",
                        "urgence": "haute" if taches_retard > 3 else "moyenne",
                    }
                )

            return {
                "statistiques": {
                    "recettes_total": recettes_total,
                    "repas_planifies_semaine": repas_semaine,
                    "articles_courses": 0,
                    "taches_entretien_en_retard": taches_retard,
                    "activites_a_venir": activites_a_venir,
                    "stocks_en_alerte": stocks_alerte,
                },
                "budget_mois": {
                    "total_mois": float(budget_total),
                    "par_categorie": {
                        cat: float(total) for cat, total in budget_par_cat
                    },
                },
                "prochaines_activites": [
                    {
                        "id": a.id,
                        "titre": a.titre,
                        "date_prevue": a.date_prevue.isoformat(),
                        "type_activite": a.type_activite,
                        "lieu": a.lieu,
                    }
                    for a in prochaines
                ],
                "alertes": alertes,
            }

    return await executer_async(_query)


@router.get("/cuisine", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_dashboard_cuisine(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Dashboard agrÃ©gÃ© spÃ©cifique au module cuisine.

    Retourne: repas du jour, compteur semaine, recettes totales,
    articles courses restants, alertes inventaire, Ã©tat batch cooking.
    """

    def _query():
        with executer_avec_session() as session:
            from src.core.models import ArticleInventaire, Recette, Repas
            from src.core.models.batch_cooking import SessionBatchCooking
            from src.core.models.courses import ArticleCourses, ListeCourses

            aujourd_hui = date.today()
            debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            fin_semaine = debut_semaine + timedelta(days=6)

            # Repas du jour avec nom de recette
            repas_jour = (
                session.query(Repas)
                .filter(Repas.date_repas == aujourd_hui)
                .all()
            )
            repas_aujourd_hui = [
                {
                    "type_repas": r.type_repas,
                    "recette_nom": r.recette.nom if r.recette else r.notes,
                }
                for r in repas_jour
            ]

            # Nombre de repas planifiÃ©s dans la semaine
            repas_semaine_count = (
                session.query(func.count(Repas.id))
                .filter(
                    Repas.date_repas >= debut_semaine,
                    Repas.date_repas <= fin_semaine,
                )
                .scalar()
                or 0
            )

            # Nombre total de recettes
            nb_recettes = session.query(func.count(Recette.id)).scalar() or 0

            # Articles Ã  acheter (non achetÃ©s, listes non archivÃ©es)
            articles_courses_restants = (
                session.query(func.count(ArticleCourses.id))
                .join(ListeCourses)
                .filter(
                    ArticleCourses.achete == False,  # noqa: E712
                    ListeCourses.archivee == False,  # noqa: E712
                )
                .scalar()
                or 0
            )

            # Alertes inventaire: stock bas OU pÃ©remption dans 7 jours
            alertes_inventaire = 0
            try:
                alertes_inventaire = (
                    session.query(func.count(ArticleInventaire.id))
                    .filter(
                        (ArticleInventaire.quantite <= ArticleInventaire.quantite_min)
                        | (
                            ArticleInventaire.date_peremption.isnot(None)
                            & (
                                ArticleInventaire.date_peremption
                                <= aujourd_hui + timedelta(days=7)
                            )
                        )
                    )
                    .scalar()
                    or 0
                )
            except Exception as e:
                logger.warning("[dashboard] MÃ©triques inventaire non chargÃ©es: %s", e)
            batch_session = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.statut == "en_cours")
                .first()
            )

            # Score anti-gaspillage : articles proches de la pÃ©remption / total
            total_inventaire = session.query(func.count(ArticleInventaire.id)).scalar() or 0
            score_anti_gaspillage = 100
            if total_inventaire > 0:
                articles_a_risque = alertes_inventaire
                score_anti_gaspillage = max(0, round(100 - (articles_a_risque / total_inventaire * 100)))

            # Repas Jules aujourd'hui (adaptations bÃ©bÃ©)
            repas_jules = [
                {
                    "type_repas": r.type_repas,
                    "plat_jules": r.plat_jules,
                    "notes_jules": r.notes_jules,
                    "adaptation_auto": r.adaptation_auto,
                }
                for r in repas_jour
                if r.plat_jules
            ]

            # Repas consommÃ©s cette semaine
            repas_consommes = (
                session.query(func.count(Repas.id))
                .filter(
                    Repas.date_repas >= debut_semaine,
                    Repas.date_repas <= fin_semaine,
                    Repas.consomme == True,  # noqa: E712
                )
                .scalar()
                or 0
            )

            return {
                "repas_aujourd_hui": repas_aujourd_hui,
                "repas_semaine_count": int(repas_semaine_count),
                "repas_consommes_semaine": int(repas_consommes),
                "nb_recettes": int(nb_recettes),
                "articles_courses_restants": int(articles_courses_restants),
                "alertes_inventaire": int(alertes_inventaire),
                "score_anti_gaspillage": score_anti_gaspillage,
                "repas_jules_aujourd_hui": repas_jules,
                "batch_en_cours": batch_session is not None,
                "batch_session_id": batch_session.id if batch_session else None,
            }

    return await executer_async(_query)


@router.get(
    "/bilan-mensuel",
    responses=REPONSES_LISTE,
    summary="Bilan mensuel IA",
    description=(
        "GÃ©nÃ¨re un bilan mensuel enrichi par l'IA : dÃ©penses, repas planifiÃ©s, "
        "activitÃ©s et entretien, avec une synthÃ¨se narrative."
    ),
)
@gerer_exception_api
async def bilan_mensuel(
    mois: str | None = None,
    user: dict = Depends(require_auth),
) -> dict:
    """
    Retourne les donnÃ©es agrÃ©gÃ©es du mois + synthÃ¨se IA.

    Le paramÃ¨tre `mois` est au format YYYY-MM (ex: 2025-06).
    Si absent, utilise le mois courant.
    """
    from src.services.rapports.bilan_mensuel import obtenir_bilan_mensuel_service

    service = obtenir_bilan_mensuel_service()
    return await service.generer_bilan(mois=mois)


@router.get(
    "/score-bienetre",
    responses=REPONSES_LISTE,
    summary="Score bien-etre global",
    description="Calcule le score bien-etre hebdomadaire (alimentation + nutrition + activitÃ©s).",
)
@gerer_exception_api
async def obtenir_score_bien_etre(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le score bien-etre pour la semaine courante."""

    def _query():
        from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

        service = obtenir_score_bien_etre_service()
        return service.calculer_score()

    return await executer_async(_query)


@router.get(
    "/config",
    responses=REPONSES_LISTE,
    summary="Lire la config dashboard",
)
@gerer_exception_api
async def lire_config_dashboard(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne la configuration widgets enregistrÃ©e pour l'utilisateur."""

    def _query():
        from src.core.models.user_preferences import PreferenceUtilisateur

        with executer_avec_session() as session:
            pref = session.query(PreferenceUtilisateur).first()
            if not pref:
                return {"config_dashboard": {}}
            return {"config_dashboard": pref.config_dashboard or {}}

    return await executer_async(_query)


@router.put(
    "/config",
    responses=REPONSES_LISTE,
    summary="Mettre Ã  jour la config dashboard",
)
@gerer_exception_api
async def sauvegarder_config_dashboard(
    payload: DashboardConfigRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde la configuration personnalisÃ©e du dashboard."""

    def _query():
        from src.core.models.user_preferences import PreferenceUtilisateur

        with executer_avec_session() as session:
            pref = session.query(PreferenceUtilisateur).first()
            if pref is None:
                pref = PreferenceUtilisateur(user_id="matanne")
                session.add(pref)
            pref.config_dashboard = payload.config_dashboard
            session.commit()
            return {
                "message": "Configuration dashboard sauvegardÃ©e",
                "config_dashboard": pref.config_dashboard,
            }

    return await executer_async(_query)


@router.get(
    "/alertes-contextuelles",
    responses=REPONSES_LISTE,
    summary="Alertes mÃ©tÃ©o contextuelles cross-modules",
)
@gerer_exception_api
async def obtenir_alertes_contextuelles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne des alertes mÃ©tÃ©o/action cross-modules pour les 48h Ã  venir."""
    import httpx

    async def _fetch_alertes() -> dict[str, Any]:
        alertes: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                reponse = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": 50.63,
                        "longitude": 3.06,
                        "hourly": "temperature_2m,precipitation_probability,windspeed_10m",
                        "forecast_days": 2,
                    },
                )
                reponse.raise_for_status()
                data = reponse.json().get("hourly", {})
        except Exception as e:
            data = {}
            logger.warning("[dashboard] MÃ©tÃ©o non disponible pour alertes: %s", e)

        temperatures = data.get("temperature_2m", []) or []
        pluie = data.get("precipitation_probability", []) or []
        vent = data.get("windspeed_10m", []) or []

        if temperatures and min(temperatures) <= 0:
            alertes.append(
                {
                    "type": "gel",
                    "module": "maison",
                    "icone": "snowflake",
                    "titre": "Risque de gel",
                    "message": "Penser Ã  protÃ©ger les plantes extÃ©rieures et vÃ©rifier les Ã©quipements sensibles.",
                    "action": "Mettre les pots fragiles Ã  l'abri",
                }
            )
        if temperatures and max(temperatures) >= 30:
            alertes.append(
                {
                    "type": "canicule",
                    "module": "famille",
                    "icone": "sun",
                    "titre": "Chaleur Ã©levÃ©e",
                    "message": "PrÃ©voir plus d'eau, des repas frais et limiter les sorties aux heures chaudes.",
                    "action": "Adapter le planning de Jules et les repas",
                }
            )
        if pluie and max(pluie) >= 65:
            alertes.append(
                {
                    "type": "pluie",
                    "module": "planning",
                    "icone": "cloud-rain",
                    "titre": "Pluie probable",
                    "message": "Les activitÃ©s extÃ©rieures risquent d'Ãªtre perturbÃ©es dans les 48 prochaines heures.",
                    "action": "PrÃ©voir une alternative intÃ©rieure",
                }
            )
        if vent and max(vent) >= 45:
            alertes.append(
                {
                    "type": "vent",
                    "module": "maison",
                    "icone": "wind",
                    "titre": "Vent fort",
                    "message": "SÃ©curiser le mobilier extÃ©rieur et vÃ©rifier les objets lÃ©gers dans le jardin.",
                    "action": "Ranger ou fixer les objets extÃ©rieurs",
                }
            )

        return {"items": alertes[:3], "total": len(alertes[:3])}

    return await _fetch_alertes()


@router.get(
    "/resume-hebdo-ia",
    responses=REPONSES_LISTE,
    summary="Resume hebdomadaire IA contextualise",
)
@gerer_exception_api
async def obtenir_resume_hebdo_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne un resume IA de la semaine avec contexte multi-modules."""

    def _query() -> dict[str, Any]:
        from src.services.dashboard.resume_famille_ia import obtenir_service_resume_famille_ia

        service = obtenir_service_resume_famille_ia()
        return service.generer_resume_hebdo()

    return await executer_async(_query)


@router.get(
    "/anomalies-financieres",
    responses=REPONSES_LISTE,
    summary="Anomalies financiÃ¨res cross-modules",
)
@gerer_exception_api
async def obtenir_anomalies_financieres(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Detecte les anomalies de depenses du mois vs N-1/N-2."""
    def _query() -> dict[str, Any]:
        from src.services.dashboard.anomalies_financieres import (
            obtenir_service_anomalies_financieres,
        )

        service = obtenir_service_anomalies_financieres()
        return service.detecter_anomalies()

    return await executer_async(_query)


@router.get(
    "/points-famille",
    responses=REPONSES_LISTE,
    summary="Points famille gamification",
)
@gerer_exception_api
async def obtenir_points_famille(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les points famille consolidÃ©s (sport, alimentation, anti-gaspi)."""

    def _query():
        from src.services.dashboard.points_famille import obtenir_points_famille_service

        service = obtenir_points_famille_service()
        return service.calculer_points()

    return await executer_async(_query)

