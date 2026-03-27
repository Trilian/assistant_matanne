"""
Routes API pour le tableau de bord.

Agrégation des données de tous les modules pour la page d'accueil.
"""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/dashboard", tags=["Tableau de bord"])


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
            except Exception:
                pass  # ArticleInventaire peut ne pas avoir date_peremption

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
            except Exception:
                pass

            # Session batch cooking en cours
            batch_session = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.statut == "en_cours")
                .first()
            )

            return {
                "repas_aujourd_hui": repas_aujourd_hui,
                "repas_semaine_count": int(repas_semaine_count),
                "nb_recettes": int(nb_recettes),
                "articles_courses_restants": int(articles_courses_restants),
                "alertes_inventaire": int(alertes_inventaire),
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
