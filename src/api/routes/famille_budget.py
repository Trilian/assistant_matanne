"""
Routes API Famille â€” Budget familial.

Sous-routeur inclus dans famille.py.
"""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])


def executer_avec_session():
    """Compat tests: délègue au module parent famille pour patch centralisé."""
    from src.api.routes import famille as famille_routes

    return famille_routes.executer_avec_session()


async def executer_async(func):
    """Compat tests: délègue au module parent famille pour patch centralisé."""
    from src.api.routes import famille as famille_routes

    return await famille_routes.executer_async(func)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BUDGET FAMILIAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/budget", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_depenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    categorie: str | None = Query(None, description="Filtrer par catÃ©gorie"),
    date_debut: date | None = Query(None),
    date_fin: date | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les dÃ©penses familiales."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(BudgetFamille)

            if categorie:
                query = query.filter(BudgetFamille.categorie == categorie)
            if date_debut:
                query = query.filter(BudgetFamille.date >= date_debut)
            if date_fin:
                query = query.filter(BudgetFamille.date <= date_fin)

            total = query.count()
            items = (
                query.order_by(BudgetFamille.date.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": d.id,
                        "date": d.date.isoformat(),
                        "categorie": d.categorie,
                        "description": d.description,
                        "montant": d.montant,
                        "magasin": d.magasin,
                        "est_recurrent": d.est_recurrent,
                    }
                    for d in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/budget/stats", responses=REPONSES_LISTE)
@gerer_exception_api
async def statistiques_budget(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: int | None = Query(None, ge=2020, le=2030, description="AnnÃ©e"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les statistiques du budget familial."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(BudgetFamille)

            # Filtrer par pÃ©riode si spÃ©cifiÃ©
            if mois and annee:
                query = query.filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
            elif annee:
                query = query.filter(func.extract("year", BudgetFamille.date) == annee)

            # Total
            total = query.with_entities(func.sum(BudgetFamille.montant)).scalar() or 0

            # Par catÃ©gorie
            par_categorie = (
                query.with_entities(
                    BudgetFamille.categorie, func.sum(BudgetFamille.montant).label("total")
                )
                .group_by(BudgetFamille.categorie)
                .all()
            )

            return {
                "total": float(total),
                "par_categorie": {cat: float(montant) for cat, montant in par_categorie},
                "periode": {"mois": mois, "annee": annee},
            }

    return await executer_async(_query)


@router.post("/budget", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_depense(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une dÃ©pense au budget familial."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            depense = BudgetFamille(
                date=payload.get("date", date.today().isoformat()),
                categorie=payload["categorie"],
                description=payload.get("description"),
                montant=payload["montant"],
                magasin=payload.get("magasin"),
                est_recurrent=payload.get("est_recurrent", False),
                frequence_recurrence=payload.get("frequence_recurrence"),
                notes=payload.get("notes"),
            )
            session.add(depense)
            session.commit()
            session.refresh(depense)
            return {
                "id": depense.id,
                "date": depense.date.isoformat(),
                "categorie": depense.categorie,
                "montant": depense.montant,
            }

    return await executer_async(_query)


@router.delete("/budget/{depense_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une dÃ©pense du budget."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            depense = session.query(BudgetFamille).filter(BudgetFamille.id == depense_id).first()
            if not depense:
                raise HTTPException(status_code=404, detail="DÃ©pense non trouvÃ©e")
            session.delete(depense)
            session.commit()
            return MessageResponse(message="DÃ©pense supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BUDGET IA â€” PrÃ©dictions, Anomalies, Ã‰conomies
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _charger_historique_budget_6_mois(session: Any) -> list[dict[str, Any]]:
    """Charge l'historique des dÃ©penses familiales sur les 6 derniers mois.

    Retourne une liste de 6 entrÃ©es (du plus ancien au plus rÃ©cent),
    chacune avec: mois, annee, total, par_categorie.
    """
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille

    aujourd_hui = datetime.now()
    mois_courant = aujourd_hui.month
    annee_courante = aujourd_hui.year

    historique = []
    for i in range(6):
        m = mois_courant - i
        a = annee_courante
        if m <= 0:
            m += 12
            a -= 1

        depenses_mois = (
            session.query(
                BudgetFamille.categorie,
                func.sum(BudgetFamille.montant).label("total"),
            )
            .filter(
                func.extract("month", BudgetFamille.date) == m,
                func.extract("year", BudgetFamille.date) == a,
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        par_cat = {cat: float(total) for cat, total in depenses_mois}
        historique.append(
            {"mois": m, "annee": a, "total": sum(par_cat.values()), "par_categorie": par_cat}
        )

    historique.reverse()
    return historique


@router.get("/budget/analyse-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def analyse_budget_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse complÃ¨te du budget avec prÃ©dictions, anomalies et suggestions."""
    from src.services.famille.budget_ai import obtenir_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            historique = _charger_historique_budget_6_mois(session)

            depenses_courant = historique[-1]["par_categorie"] if historique else {}
            if len(historique) > 1:
                moyennes: dict[str, float] = {}
                for h in historique[:-1]:
                    for cat, v in h.get("par_categorie", {}).items():
                        moyennes[cat] = moyennes.get(cat, 0) + v
                nb_mois_prec = len(historique) - 1
                moyennes = {cat: v / nb_mois_prec for cat, v in moyennes.items()}
            else:
                moyennes = {}

            return {
                "historique": historique,
                "depenses_courant": depenses_courant,
                "moyennes": moyennes,
                "total_moyen": sum(moyennes.values()),
            }

    donnees = await executer_async(_query)

    # Enrichir avec les dÃ©penses maison (vue consolidÃ©e)
    depenses_maison: dict[str, float] = {}
    try:
        from datetime import datetime as _dt

        from src.services.maison import obtenir_depenses_crud_service

        svc_maison = obtenir_depenses_crud_service()
        deps = svc_maison.get_depenses_mois(_dt.now().month, _dt.now().year)
        for d in deps or []:
            cat_key = f"maison:{d.categorie}"
            depenses_maison[cat_key] = depenses_maison.get(cat_key, 0) + float(d.montant)
    except Exception as e:
        logger.warning("[famille] DÃ©penses maison non chargÃ©es pour budget IA: %s", e)

    service = obtenir_budget_ai_service()
    predictions = service.predire_budget_mensuel(donnees["historique"])
    anomalies = service.detecter_anomalies(donnees["depenses_courant"], donnees["moyennes"])
    suggestions = service.suggerer_economies(donnees["moyennes"], donnees["total_moyen"])

    total_famille = sum(donnees["depenses_courant"].values())
    total_maison = sum(depenses_maison.values())

    return {
        "predictions": predictions.model_dump() if predictions else None,
        "anomalies": [a.model_dump() for a in anomalies],
        "suggestions": [s.model_dump() for s in suggestions],
        "historique": donnees["historique"],
        "depenses_maison_mois": depenses_maison,
        "total_consolide": total_famille + total_maison,
    }


@router.get("/budget/predictions", responses=REPONSES_LISTE)
@gerer_exception_api
async def predictions_budget(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """PrÃ©dictions du budget pour le mois prochain."""
    from src.services.famille.budget_ai import obtenir_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            return _charger_historique_budget_6_mois(session)

    historique = await executer_async(_query)
    service = obtenir_budget_ai_service()
    predictions = service.predire_budget_mensuel(historique)

    return {
        "predictions": predictions.model_dump() if predictions else None,
        "historique": historique,
    }


@router.get("/budget/anomalies", responses=REPONSES_LISTE)
@gerer_exception_api
async def anomalies_budget(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tecte les anomalies dans les dÃ©penses du mois courant."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille
    from src.services.famille.budget_ai import obtenir_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = datetime.now()
            mois_courant = aujourd_hui.month
            annee_courante = aujourd_hui.year

            # Mois courant
            courant = (
                session.query(
                    BudgetFamille.categorie,
                    func.sum(BudgetFamille.montant).label("total"),
                )
                .filter(
                    func.extract("month", BudgetFamille.date) == mois_courant,
                    func.extract("year", BudgetFamille.date) == annee_courante,
                )
                .group_by(BudgetFamille.categorie)
                .all()
            )
            depenses_courant = {cat: float(total) for cat, total in courant}

            # Moyennes 5 mois prÃ©cÃ©dents
            moyennes = {}
            for i in range(1, 6):
                m = mois_courant - i
                a = annee_courante
                if m <= 0:
                    m += 12
                    a -= 1
                deps = (
                    session.query(
                        BudgetFamille.categorie,
                        func.sum(BudgetFamille.montant).label("total"),
                    )
                    .filter(
                        func.extract("month", BudgetFamille.date) == m,
                        func.extract("year", BudgetFamille.date) == a,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for cat, total in deps:
                    moyennes[cat] = moyennes.get(cat, 0) + float(total)

            moyennes = {cat: v / 5 for cat, v in moyennes.items()}

            return {"depenses_courant": depenses_courant, "moyennes": moyennes}

    donnees = await executer_async(_query)
    service = obtenir_budget_ai_service()
    anomalies = service.detecter_anomalies(donnees["depenses_courant"], donnees["moyennes"])

    return {"anomalies": [a.model_dump() for a in anomalies]}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SHOPPING FAMILIAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BUDGET â€” RÃ‰SUMÃ‰ MENSUEL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/budget/resume-mois", responses=REPONSES_LISTE)
@gerer_exception_api
async def resume_budget_mois(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le rÃ©sumÃ© des achats du mois courant vs prÃ©cÃ©dent."""
    from src.core.models import AchatFamille

    def _query():
        today = date.today()
        with executer_avec_session() as session:
            # Mois courant
            debut_courant = today.replace(day=1)
            achats_courant = (
                session.query(AchatFamille)
                .filter(
                    AchatFamille.achete == True,  # noqa: E712
                    AchatFamille.date_achat >= debut_courant,
                )
                .all()
            )
            total_courant = sum((a.prix_reel or a.prix_estime or 0) for a in achats_courant)

            # Calcul dÃ©but du mois prÃ©cÃ©dent
            if today.month == 1:
                debut_prec = today.replace(year=today.year - 1, month=12, day=1)
                fin_prec = today.replace(day=1)
            else:
                debut_prec = today.replace(month=today.month - 1, day=1)
                fin_prec = debut_courant

            achats_prec = (
                session.query(AchatFamille)
                .filter(
                    AchatFamille.achete == True,  # noqa: E712
                    AchatFamille.date_achat >= debut_prec,
                    AchatFamille.date_achat < fin_prec,
                )
                .all()
            )
            total_prec = sum((a.prix_reel or a.prix_estime or 0) for a in achats_prec)

            variation = None
            if total_prec and total_prec > 0:
                variation = round((total_courant - total_prec) / total_prec * 100, 1)

            par_categorie: dict[str, float] = {}
            for a in achats_courant:
                par_categorie[a.categorie] = par_categorie.get(a.categorie, 0) + (
                    a.prix_reel or a.prix_estime or 0
                )

            return {
                "mois_courant": debut_courant.strftime("%Y-%m"),
                "total_courant": total_courant,
                "total_precedent": total_prec if total_prec else None,
                "variation_pct": variation,
                "achats_par_categorie": par_categorie,
            }

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONFIG GARDE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
