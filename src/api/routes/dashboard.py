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


def _score_lettre_vers_points(note: str | None) -> int | None:
    mapping = {"A": 100, "B": 80, "C": 60, "D": 40, "E": 20}
    if not note:
        return None
    return mapping.get(str(note).upper())


def _calculer_budget_unifie(session: Any, mois: int, annee: int) -> dict[str, Any]:
    """Agrège les dépenses famille/maison et le net jeux pour un mois donné."""
    from src.core.models import BudgetFamille, DepenseMaison, PariSportif

    total_famille = (
        session.query(func.sum(BudgetFamille.montant))
        .filter(
            func.extract("month", BudgetFamille.date) == mois,
            func.extract("year", BudgetFamille.date) == annee,
        )
        .scalar()
        or 0
    )
    total_maison = (
        session.query(func.sum(DepenseMaison.montant))
        .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
        .scalar()
        or 0
    )
    mises_jeux = (
        session.query(func.sum(PariSportif.mise))
        .filter(
            func.extract("month", PariSportif.cree_le) == mois,
            func.extract("year", PariSportif.cree_le) == annee,
            PariSportif.est_virtuel == False,  # noqa: E712
        )
        .scalar()
        or 0
    )
    gains_jeux = (
        session.query(func.sum(PariSportif.gain))
        .filter(
            func.extract("month", PariSportif.cree_le) == mois,
            func.extract("year", PariSportif.cree_le) == annee,
            PariSportif.est_virtuel == False,  # noqa: E712
        )
        .scalar()
        or 0
    )

    net_jeux = float(gains_jeux) - float(mises_jeux)
    depenses_hors_jeux = float(total_famille) + float(total_maison)

    return {
        "mois": f"{mois:02d}/{annee}",
        "famille": {"depenses": float(total_famille)},
        "maison": {"depenses": float(total_maison)},
        "jeux": {
            "mises": float(mises_jeux),
            "gains": float(gains_jeux),
            "net": net_jeux,
        },
        "totaux": {
            "depenses_hors_jeux": depenses_hors_jeux,
            "depenses_avec_mises_jeux": depenses_hors_jeux + float(mises_jeux),
            "impact_global_avec_jeux": depenses_hors_jeux - net_jeux,
        },
    }


def _calculer_score_ecologique(session: Any) -> dict[str, Any]:
    """Construit un score écologique transversal cuisine + maison."""
    from src.core.models import ActionEcologique, ArticleInventaire
    from src.core.models.maison_extensions import ReleveCompteur

    aujourd_hui = date.today()
    debut_mois = aujourd_hui.replace(day=1)
    debut_historique = debut_mois - timedelta(days=180)

    total_inventaire = session.query(func.count(ArticleInventaire.id)).scalar() or 0
    articles_a_risque = (
        session.query(func.count(ArticleInventaire.id))
        .filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption <= aujourd_hui + timedelta(days=7),
        )
        .scalar()
        or 0
    )
    score_anti_gaspillage = 100
    if total_inventaire > 0:
        score_anti_gaspillage = max(
            0,
            round(100 - ((articles_a_risque / total_inventaire) * 100)),
        )

    notes_ecoscore: list[int | None] = []
    if hasattr(ArticleInventaire, "ecoscore"):
        notes_ecoscore = [
            _score_lettre_vers_points(item[0])
            for item in session.query(ArticleInventaire.ecoscore)
            .filter(ArticleInventaire.ecoscore.isnot(None))
            .all()
        ]
    notes_ecoscore_valides = [note for note in notes_ecoscore if note is not None]
    score_produits = (
        round(sum(notes_ecoscore_valides) / len(notes_ecoscore_valides))
        if notes_ecoscore_valides
        else None
    )

    score_cuisine = round(
        score_anti_gaspillage * (0.65 if score_produits is not None else 1.0)
        + (score_produits or 0) * (0.35 if score_produits is not None else 0.0)
    )

    releves = (
        session.query(
            ReleveCompteur.type_compteur,
            func.date_trunc("month", ReleveCompteur.date_releve).label("mois"),
            func.sum(ReleveCompteur.consommation_periode).label("conso"),
        )
        .filter(
            ReleveCompteur.consommation_periode.isnot(None),
            ReleveCompteur.date_releve >= debut_historique,
        )
        .group_by(
            ReleveCompteur.type_compteur,
            func.date_trunc("month", ReleveCompteur.date_releve),
        )
        .order_by(
            ReleveCompteur.type_compteur.asc(),
            func.date_trunc("month", ReleveCompteur.date_releve).asc(),
        )
        .all()
    )

    releves_par_type: dict[str, list[float]] = {}
    for type_compteur, _, consommation in releves:
        releves_par_type.setdefault(str(type_compteur), []).append(float(consommation or 0))

    scores_energie: list[int] = []
    for valeurs in releves_par_type.values():
        if not valeurs:
            continue
        courante = valeurs[-1]
        reference = (sum(valeurs[:-1]) / len(valeurs[:-1])) if len(valeurs) > 1 else courante
        ecart_pct = abs(((courante - reference) / reference) * 100) if reference else 0.0
        scores_energie.append(max(0, round(100 - min(100, ecart_pct))))

    score_energie = round(sum(scores_energie) / len(scores_energie)) if scores_energie else 70

    nb_actions_ecologiques = (
        session.query(func.count(ActionEcologique.id))
        .filter(ActionEcologique.actif.is_(True))
        .scalar()
        or 0
    )
    economie_mensuelle = (
        session.query(func.sum(ActionEcologique.economie_mensuelle))
        .filter(ActionEcologique.actif.is_(True))
        .scalar()
        or 0
    )
    economie_mensuelle_float = float(economie_mensuelle or 0)
    score_eco_actions = max(
        25,
        min(100, round((nb_actions_ecologiques * 18) + min(46.0, economie_mensuelle_float * 2))),
    )

    score_maison = round((score_energie * 0.6) + (score_eco_actions * 0.4))
    score_global = round((score_cuisine * 0.55) + (score_maison * 0.45))

    niveau = "excellent"
    if score_global < 45:
        niveau = "critique"
    elif score_global < 65:
        niveau = "vigilance"
    elif score_global < 80:
        niveau = "bon"

    leviers: list[str] = []
    if score_anti_gaspillage < 75:
        leviers.append("Réduire les produits proches de péremption dans l'inventaire.")
    if score_energie < 75:
        leviers.append("Surveiller les consommations énergétiques anormales du mois.")
    if score_eco_actions < 60:
        leviers.append("Activer davantage d'actions écologiques suivies côté maison.")
    if score_produits is not None and score_produits < 65:
        leviers.append("Favoriser plus de produits avec un éco-score A/B dans l'inventaire.")
    if not leviers:
        leviers.append("Maintenir le rythme actuel: les indicateurs écologiques restent bien orientés.")

    return {
        "score_global": score_global,
        "niveau": niveau,
        "modules": {
            "cuisine": {
                "score": score_cuisine,
                "anti_gaspillage": score_anti_gaspillage,
                "produits_ecoscores": score_produits,
            },
            "maison": {
                "score": score_maison,
                "energie": score_energie,
                "eco_actions": score_eco_actions,
                "economie_mensuelle_estimee": round(economie_mensuelle_float, 2),
            },
        },
        "leviers_prioritaires": leviers[:3],
    }


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
            from src.core.models import (
                AnnonceHabitat,
                ProjetDecoHabitat,
                ZoneJardinHabitat,
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

            habitat_alertes = (
                session.query(func.count(AnnonceHabitat.id))
                .filter(AnnonceHabitat.statut.in_(["alerte", "nouveau"]))
                .scalar()
                or 0
            )
            budget_deco = (
                session.query(func.sum(ProjetDecoHabitat.budget_depense))
                .scalar()
                or 0
            )
            zones_jardin = session.query(func.count(ZoneJardinHabitat.id)).scalar() or 0
            if habitat_alertes > 0:
                alertes.append(
                    {
                        "type": "habitat",
                        "message": f"{habitat_alertes} annonce(s) habitat a qualifier",
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

            # B8: Documents expirés ou expirant bientôt
            try:
                from src.core.models import DocumentFamille

                docs_expires = (
                    session.query(func.count(DocumentFamille.id))
                    .filter(
                        DocumentFamille.date_expiration.isnot(None),
                        DocumentFamille.actif.is_(True),
                        DocumentFamille.date_expiration < aujourd_hui,
                    )
                    .scalar()
                    or 0
                )
                docs_bientot = (
                    session.query(func.count(DocumentFamille.id))
                    .filter(
                        DocumentFamille.date_expiration.isnot(None),
                        DocumentFamille.actif.is_(True),
                        DocumentFamille.date_expiration >= aujourd_hui,
                        DocumentFamille.date_expiration <= aujourd_hui + timedelta(days=30),
                    )
                    .scalar()
                    or 0
                )
                if docs_expires > 0:
                    alertes.append({
                        "type": "document_expire",
                        "message": f"{docs_expires} document(s) expiré(s) à renouveler",
                        "urgence": "haute",
                    })
                if docs_bientot > 0:
                    alertes.append({
                        "type": "document_bientot",
                        "message": f"{docs_bientot} document(s) expirent dans les 30 jours",
                        "urgence": "moyenne",
                    })
            except Exception as e:
                logger.warning("[dashboard] Alertes documents non chargées: %s", e)

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
                "habitat": {
                    "alertes": int(habitat_alertes),
                    "budget_deco_depense": float(budget_deco),
                    "zones_jardin": int(zones_jardin),
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


@router.get("/budget-unifie", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_budget_unifie(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne la vue budgétaire unifiée (famille + maison + jeux)."""

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = date.today()
            return _calculer_budget_unifie(
                session=session,
                mois=aujourd_hui.month,
                annee=aujourd_hui.year,
            )

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
    "/score-ecologique",
    responses=REPONSES_LISTE,
    summary="Score écologique transversal",
)
@gerer_exception_api
async def obtenir_score_ecologique(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Agrège anti-gaspillage, produits éco-scorés, énergie et éco-actions."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return _calculer_score_ecologique(session)

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
    "/tendances-ia",
    responses=REPONSES_LISTE,
    summary="Detection de tendances multi-domaines (6 mois)",
)
@gerer_exception_api
async def obtenir_tendances_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Detecte des tendances 3-6 mois sur budget unifie et energie.

    Endpoint orienté aide a la decision: il fournit des signaux interpretes,
    sans se substituer a une analyse financiere ou energetique experte.
    """

    def _classer_tendance(valeurs: list[float]) -> tuple[str, float]:
        if len(valeurs) < 2:
            return "insuffisant", 0.0
        pente = (valeurs[-1] - valeurs[0]) / (len(valeurs) - 1)
        moyenne = sum(valeurs) / len(valeurs) if valeurs else 0.0
        variation_pct = (pente / moyenne * 100) if moyenne else 0.0
        if variation_pct > 3:
            return "hausse", round(variation_pct, 1)
        if variation_pct < -3:
            return "baisse", round(variation_pct, 1)
        return "stable", round(variation_pct, 1)

    def _query() -> dict[str, Any]:
        from src.core.models.maison_extensions import ReleveCompteur

        today = date.today()

        # Fenetre glissante sur 6 mois (inclus mois courant)
        mois_annee: list[tuple[int, int]] = []
        m = today.month
        a = today.year
        for _ in range(6):
            mois_annee.append((m, a))
            m -= 1
            if m == 0:
                m = 12
                a -= 1
        mois_annee.reverse()

        with executer_avec_session() as session:
            points_budget: list[dict[str, Any]] = []
            points_energie: list[dict[str, Any]] = []

            for mois, annee in mois_annee:
                budget = _calculer_budget_unifie(session, mois=mois, annee=annee)
                points_budget.append(
                    {
                        "mois": f"{annee}-{mois:02d}",
                        "valeur": float(budget["totaux"]["depenses_hors_jeux"]),
                    }
                )

                conso = (
                    session.query(func.sum(ReleveCompteur.consommation_periode))
                    .filter(
                        ReleveCompteur.type_compteur == "electricite",
                        func.extract("month", ReleveCompteur.date_releve) == mois,
                        func.extract("year", ReleveCompteur.date_releve) == annee,
                    )
                    .scalar()
                    or 0
                )
                points_energie.append(
                    {
                        "mois": f"{annee}-{mois:02d}",
                        "valeur": float(conso),
                    }
                )

            tendance_budget, variation_budget = _classer_tendance(
                [p["valeur"] for p in points_budget]
            )
            tendance_energie, variation_energie = _classer_tendance(
                [p["valeur"] for p in points_energie]
            )

            insights: list[str] = []
            if tendance_budget == "hausse":
                insights.append(
                    f"Depenses budget hors jeux en hausse (~{variation_budget}%/mois): verifier les categories dominantes."
                )
            elif tendance_budget == "baisse":
                insights.append(
                    f"Depenses budget hors jeux en baisse (~{abs(variation_budget)}%/mois): dynamique economique positive."
                )

            if tendance_energie == "hausse":
                insights.append(
                    f"Consommation electrique en hausse (~{variation_energie}%/mois): investiguer les appareils energivores."
                )
            elif tendance_energie == "baisse":
                insights.append(
                    f"Consommation electrique en baisse (~{abs(variation_energie)}%/mois): optimisation energetique en cours."
                )

            if not insights:
                insights.append("Tendances globalement stables sur 6 mois.")

            return {
                "periode": {
                    "debut": points_budget[0]["mois"] if points_budget else None,
                    "fin": points_budget[-1]["mois"] if points_budget else None,
                    "nb_mois": len(points_budget),
                },
                "budget": {
                    "tendance": tendance_budget,
                    "variation_pct_mensuelle": variation_budget,
                    "points": points_budget,
                },
                "energie": {
                    "tendance": tendance_energie,
                    "variation_pct_mensuelle": variation_energie,
                    "points": points_energie,
                },
                "insights": insights,
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
    """Retourne les points famille consolidÃ©s (sport, alimentation, anti-gaspi)."""

    def _query():
        from src.services.dashboard.points_famille import obtenir_points_famille_service

        service = obtenir_points_famille_service()
        return service.calculer_points()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# GAMIFICATION — Badges & historique (Phase 9)
# ═══════════════════════════════════════════════════════════


@router.get(
    "/badges/catalogue",
    responses=REPONSES_LISTE,
    summary="Catalogue des badges sport + nutrition",
)
@gerer_exception_api
async def obtenir_catalogue_badges(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le catalogue complet des badges disponibles."""
    from src.services.dashboard.badges_triggers import obtenir_catalogue_badges as catalogue

    return {"items": catalogue(), "total": len(catalogue())}


@router.get(
    "/badges/utilisateur",
    responses=REPONSES_LISTE,
    summary="Badges d'un utilisateur avec progression",
)
@gerer_exception_api
async def obtenir_badges_utilisateur(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les badges d'un utilisateur avec leur état de progression."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        user_id = user.get("user_id") or user.get("id", 1)
        badges = service.obtenir_badges_utilisateur(user_id=int(user_id))
        obtenus = [b for b in badges if b.get("obtenu")]
        return {
            "items": badges,
            "total": len(badges),
            "obtenus": len(obtenus),
        }

    return await executer_async(_query)


@router.post(
    "/badges/evaluer",
    responses=REPONSES_LISTE,
    summary="Évaluer et attribuer les badges mérités",
)
@gerer_exception_api
async def evaluer_badges(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Évalue les conditions de badges et attribue ceux mérités."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        nouveaux = service.evaluer_et_attribuer()
        return {
            "nouveaux_badges": nouveaux,
            "total_nouveaux": len(nouveaux),
        }

    return await executer_async(_query)


@router.get(
    "/historique-points",
    responses=REPONSES_LISTE,
    summary="Historique des points sur N semaines",
)
@gerer_exception_api
async def obtenir_historique_points(
    nb_semaines: int = 8,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne l'évolution des points sport + nutrition sur N semaines."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        user_id = user.get("user_id") or user.get("id", 1)
        historique = service.obtenir_historique_points(
            user_id=int(user_id), nb_semaines=nb_semaines
        )
        return {"items": historique, "total": len(historique)}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# B8: Documents expirés — widget dashboard
# ═══════════════════════════════════════════════════════════


@router.get(
    "/documents-expirants",
    responses=REPONSES_LISTE,
    summary="Documents famille expirants ou expirés",
)
@gerer_exception_api
async def obtenir_documents_expirants(
    jours_horizon: int = 60,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les documents famille expirants (widget dashboard B8).

    Inclut les documents déjà expirés et ceux qui expirent dans les N prochains jours.
    """

    def _query():
        with executer_avec_session() as session:
            from src.core.models import DocumentFamille

            aujourd_hui = date.today()
            limite = aujourd_hui + timedelta(days=jours_horizon)

            documents = (
                session.query(DocumentFamille)
                .filter(
                    DocumentFamille.date_expiration.isnot(None),
                    DocumentFamille.actif.is_(True),
                    DocumentFamille.date_expiration <= limite,
                )
                .order_by(DocumentFamille.date_expiration.asc())
                .all()
            )

            items = []
            nb_expires = 0
            nb_bientot = 0

            for doc in documents:
                jours_restants = (doc.date_expiration - aujourd_hui).days
                est_expire = jours_restants < 0

                if est_expire:
                    nb_expires += 1
                    severite = "danger"
                elif jours_restants <= 7:
                    nb_bientot += 1
                    severite = "danger"
                elif jours_restants <= 30:
                    nb_bientot += 1
                    severite = "warning"
                else:
                    severite = "info"

                items.append({
                    "id": doc.id,
                    "titre": doc.titre,
                    "categorie": doc.categorie,
                    "membre_famille": doc.membre_famille,
                    "date_expiration": doc.date_expiration.isoformat(),
                    "jours_restants": jours_restants,
                    "est_expire": est_expire,
                    "severite": severite,
                })

            return {
                "items": items,
                "total": len(items),
                "nb_expires": nb_expires,
                "nb_bientot": nb_bientot,
                "message": (
                    f"{nb_expires} document(s) expiré(s), "
                    f"{nb_bientot} expirent bientôt."
                ),
            }

    return await executer_async(_query)

