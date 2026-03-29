"""
Routes API pour le tableau de bord.

Agrégation des données de tous les modules pour la page d'accueil.
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
    """Configuration personnalisée des widgets dashboard."""

    config_dashboard: dict[str, Any] = Field(default_factory=dict)


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_tableau_bord(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne les données agrégées du tableau de bord.

    Inclut: statistiques rapides, budget du mois, prochaines activités, alertes.
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

            # Tâches entretien en retard
            taches_retard = (
                session.query(func.count(TacheEntretien.id))
                .filter(
                    TacheEntretien.prochaine_fois < aujourd_hui,
                    TacheEntretien.fait == False,  # noqa: E712
                )
                .scalar()
                or 0
            )

            # Activités à venir (7 prochains jours)
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

            # Prochaines activités (5 max)
            prochaines = (
                session.query(ActiviteFamille)
                .filter(ActiviteFamille.date_prevue >= aujourd_hui)
                .order_by(ActiviteFamille.date_prevue.asc())
                .limit(5)
                .all()
            )

            # Alertes: articles inventaire bientôt périmés (7 jours)
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
                logger.warning("[dashboard] Alertes péremption non chargées: %s", e)

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
                        "message": f"{taches_retard} tâche(s) d'entretien en retard",
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
    Dashboard agrégé spécifique au module cuisine.

    Retourne: repas du jour, compteur semaine, recettes totales,
    articles courses restants, alertes inventaire, état batch cooking.
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

            # Nombre de repas planifiés dans la semaine
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

            # Articles à acheter (non achetés, listes non archivées)
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

            # Alertes inventaire: stock bas OU péremption dans 7 jours
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
                logger.warning("[dashboard] Métriques inventaire non chargées: %s", e)
            batch_session = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.statut == "en_cours")
                .first()
            )

            # Score anti-gaspillage : articles proches de la péremption / total
            total_inventaire = session.query(func.count(ArticleInventaire.id)).scalar() or 0
            score_anti_gaspillage = 100
            if total_inventaire > 0:
                articles_a_risque = alertes_inventaire
                score_anti_gaspillage = max(0, round(100 - (articles_a_risque / total_inventaire * 100)))

            # Repas Jules aujourd'hui (adaptations bébé)
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

            # Repas consommés cette semaine
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
        "Génère un bilan mensuel enrichi par l'IA : dépenses, repas planifiés, "
        "activités et entretien, avec une synthèse narrative."
    ),
)
@gerer_exception_api
async def bilan_mensuel(
    mois: str | None = None,
    user: dict = Depends(require_auth),
) -> dict:
    """
    Retourne les données agrégées du mois + synthèse IA.

    Le paramètre `mois` est au format YYYY-MM (ex: 2025-06).
    Si absent, utilise le mois courant.
    """
    from src.services.rapports.bilan_mensuel import get_bilan_mensuel_service

    service = get_bilan_mensuel_service()
    return await service.generer_bilan(mois=mois)


@router.get(
    "/score-bienetre",
    responses=REPONSES_LISTE,
    summary="Score bien-etre global",
    description="Calcule le score bien-etre hebdomadaire (alimentation + nutrition + activités).",
)
@gerer_exception_api
async def obtenir_score_bien_etre(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le score bien-etre pour la semaine courante."""

    def _query():
        from src.services.dashboard.score_bienetre import get_score_bien_etre_service

        service = get_score_bien_etre_service()
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
    """Retourne la configuration widgets enregistrée pour l'utilisateur."""

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
    summary="Mettre à jour la config dashboard",
)
@gerer_exception_api
async def sauvegarder_config_dashboard(
    payload: DashboardConfigRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde la configuration personnalisée du dashboard."""

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
                "message": "Configuration dashboard sauvegardée",
                "config_dashboard": pref.config_dashboard,
            }

    return await executer_async(_query)


@router.get(
    "/alertes-contextuelles",
    responses=REPONSES_LISTE,
    summary="Alertes météo contextuelles cross-modules",
)
@gerer_exception_api
async def obtenir_alertes_contextuelles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne des alertes météo/action cross-modules pour les 48h à venir."""
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
            logger.warning("[dashboard] Météo non disponible pour alertes: %s", e)

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
                    "message": "Penser à protéger les plantes extérieures et vérifier les équipements sensibles.",
                    "action": "Mettre les pots fragiles à l'abri",
                }
            )
        if temperatures and max(temperatures) >= 30:
            alertes.append(
                {
                    "type": "canicule",
                    "module": "famille",
                    "icone": "sun",
                    "titre": "Chaleur élevée",
                    "message": "Prévoir plus d'eau, des repas frais et limiter les sorties aux heures chaudes.",
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
                    "message": "Les activités extérieures risquent d'être perturbées dans les 48 prochaines heures.",
                    "action": "Prévoir une alternative intérieure",
                }
            )
        if vent and max(vent) >= 45:
            alertes.append(
                {
                    "type": "vent",
                    "module": "maison",
                    "icone": "wind",
                    "titre": "Vent fort",
                    "message": "Sécuriser le mobilier extérieur et vérifier les objets légers dans le jardin.",
                    "action": "Ranger ou fixer les objets extérieurs",
                }
            )

        return {"items": alertes[:3], "total": len(alertes[:3])}

    return await _fetch_alertes()


@router.get(
    "/anomalies-financieres",
    responses=REPONSES_LISTE,
    summary="Anomalies financières cross-modules",
)
@gerer_exception_api
async def obtenir_anomalies_financieres(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détecte les anomalies de dépenses entre famille, maison et jeux."""
    from datetime import date

    from src.core.models import BudgetFamille, DepenseMaison, PariSportif

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            aujourd_hui = date.today()
            mois = aujourd_hui.month
            annee = aujourd_hui.year

            # Famille - dépenses du mois courant par catégorie
            depenses_famille = (
                session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant).label("total"))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
                .group_by(BudgetFamille.categorie)
                .all()
            )

            # Référence famille = moyenne des 3 mois précédents
            moyennes_famille: dict[str, float] = {}
            for i in range(1, 4):
                m = mois - i
                a = annee
                if m <= 0:
                    m += 12
                    a -= 1
                rows = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant).label("total"))
                    .filter(
                        func.extract("month", BudgetFamille.date) == m,
                        func.extract("year", BudgetFamille.date) == a,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for cat, total in rows:
                    moyennes_famille[cat] = moyennes_famille.get(cat, 0.0) + float(total or 0.0)

            moyennes_famille = {cat: total / 3 for cat, total in moyennes_famille.items()}

            # Maison - dépenses du mois courant par catégorie
            depenses_maison = (
                session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant).label("total"))
                .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
                .group_by(DepenseMaison.categorie)
                .all()
            )

            moyennes_maison: dict[str, float] = {}
            for i in range(1, 4):
                m = mois - i
                a = annee
                if m <= 0:
                    m += 12
                    a -= 1
                rows = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant).label("total"))
                    .filter(DepenseMaison.mois == m, DepenseMaison.annee == a)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for cat, total in rows:
                    moyennes_maison[cat] = moyennes_maison.get(cat, 0.0) + float(total or 0.0)

            moyennes_maison = {cat: total / 3 for cat, total in moyennes_maison.items()}

            # Jeux - net mensuel
            mises_jeux = (
                session.query(func.sum(PariSportif.mise))
                .filter(
                    func.extract("month", PariSportif.cree_le) == mois,
                    func.extract("year", PariSportif.cree_le) == annee,
                )
                .scalar()
                or 0
            )
            gains_jeux = (
                session.query(func.sum(PariSportif.gain))
                .filter(
                    func.extract("month", PariSportif.cree_le) == mois,
                    func.extract("year", PariSportif.cree_le) == annee,
                )
                .scalar()
                or 0
            )

            items: list[dict[str, Any]] = []

            def _ajouter_anomalie(module: str, categorie: str, courant: float, moyenne: float) -> None:
                if moyenne <= 0:
                    return
                ecart = ((courant - moyenne) / moyenne) * 100
                if ecart < 20:
                    return
                gravite = "haute" if ecart >= 50 else ("moyenne" if ecart >= 30 else "faible")
                items.append(
                    {
                        "module": module,
                        "categorie": categorie,
                        "valeur_courante": round(courant, 2),
                        "moyenne_reference": round(moyenne, 2),
                        "ecart_pourcentage": round(ecart, 1),
                        "gravite": gravite,
                        "message": f"{module.capitalize()} / {categorie}: +{ecart:.1f}% vs moyenne 3 mois.",
                    }
                )

            for cat, total in depenses_famille:
                _ajouter_anomalie("famille", cat, float(total or 0), moyennes_famille.get(cat, 0.0))

            for cat, total in depenses_maison:
                _ajouter_anomalie("maison", cat, float(total or 0), moyennes_maison.get(cat, 0.0))

            net_jeux = float(gains_jeux) - float(mises_jeux)
            if float(mises_jeux) >= 80 and net_jeux < -20:
                pertes_pct = (abs(net_jeux) / float(mises_jeux)) * 100 if float(mises_jeux) else 0
                items.append(
                    {
                        "module": "jeux",
                        "categorie": "bankroll",
                        "valeur_courante": round(net_jeux, 2),
                        "moyenne_reference": 0.0,
                        "ecart_pourcentage": round(pertes_pct, 1),
                        "gravite": "haute" if pertes_pct >= 40 else "moyenne",
                        "message": f"Jeux: perte nette mensuelle de {abs(net_jeux):.2f} EUR.",
                    }
                )

            items.sort(key=lambda x: {"haute": 3, "moyenne": 2, "faible": 1}.get(x["gravite"], 0), reverse=True)

            total_famille = float(sum(float(v or 0) for _, v in depenses_famille))
            total_maison = float(sum(float(v or 0) for _, v in depenses_maison))

            return {
                "items": items,
                "total": len(items),
                "synthese": {
                    "depenses_famille_mois": round(total_famille, 2),
                    "depenses_maison_mois": round(total_maison, 2),
                    "net_jeux_mois": round(net_jeux, 2),
                },
            }

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
    """Retourne les points famille consolidés (sport, alimentation, anti-gaspi)."""

    def _query():
        from src.services.dashboard.points_famille import get_points_famille_service

        service = get_points_famille_service()
        return service.calculer_points()

    return await executer_async(_query)
