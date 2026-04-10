"""
Service inter-modules : Inventaire → Budget alimentation prévisionnel.

NIM1: Tracker le coût/ingrédient pour prévoir le budget nourriture.
Service qui agrège les achats par catégorie alimentaire + endpoint budget prévisionnel.
"""

import logging
from datetime import date as date_type
from datetime import timedelta
from typing import Any

from sqlalchemy import func

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class InventaireBudgetInteractionService:
    """Service inter-modules Inventaire → Budget alimentation prévisionnel."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_budget_previsionnel_par_inventaire(
        self,
        *,
        semaines_horizon: int = 4,
        db=None,
    ) -> dict[str, Any]:
        """Calcule le budget prévisionnel alimentation basé sur l'inventaire actuel.

        Agrège les articles de l'inventaire par catégorie, estime leur durée de consommation,
        et projette le budget nécessaire pour les 4 prochaines semaines.

        Args:
            semaines_horizon: Nombre de semaines à anticiper (défaut: 4)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec:
                - budget_previsionnel: Montant total estimé
                - par_categorie: Dict {catégorie: montant}
                - items_a_renouveler: Liste des articles à racheter
                - taux_couverture: % d'articles en stock vs période
        """
        from src.core.models.famille import BudgetFamille
        from src.core.models.inventaire import ArticleInventaire

        # Récupérer tous les articles en stock
        articles_en_stock = db.query(ArticleInventaire).filter(ArticleInventaire.quantite > 0).all()

        if not articles_en_stock:
            return {
                "budget_previsionnel": 0.0,
                "par_categorie": {},
                "items_a_renouveler": [],
                "taux_couverture": 0.0,
                "message": "Inventaire vide, impossible d'estimer le budget.",
            }

        # Calculer le prix moyen historique par catégorie des 4 dernières semaines
        date_limite = date_type.today() - timedelta(weeks=4)

        prix_moyen_par_cat = (
            db.query(
                BudgetFamille.categorie,
                func.avg(BudgetFamille.montant),
            )
            .filter(
                BudgetFamille.date >= date_limite,
                BudgetFamille.categorie.ilike("%alimentation%"),
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        prix_moyen_map = {cat: prix for cat, prix in prix_moyen_par_cat}

        # Grouper articles par catégorie et estimer la durée
        budget_par_cat = {}
        items_a_renouveler = []

        for article in articles_en_stock:
            cat = article.categorie or "autres"
            prix_unitaire = article.prix_unitaire or prix_moyen_map.get(cat, 2.5)

            # Estimer jours restants : quantité * durée_moyenne_consommation
            # Hypothèse: 1 article = 3 jours de consommation par défaut
            jours_restants = (article.quantite or 1) * 3
            semaines_couverture = jours_restants / 7

            # Si moins de 2 semaines de couverture, article à renouveler
            if semaines_couverture < 2:
                items_a_renouveler.append(
                    {
                        "article_id": article.id,
                        "nom": article.nom,
                        "quantite_actuelle": article.quantite,
                        "semaines_couverture": round(semaines_couverture, 2),
                        "estimation_cout_renouvellement": round(prix_unitaire * 10, 2),
                    }
                )

            # Ajouter au budget de la catégorie (coût pour renouveller stock faible)
            if cat not in budget_par_cat:
                budget_par_cat[cat] = 0.0
            budget_par_cat[cat] += prix_unitaire

        budget_total = sum(budget_par_cat.values())
        taux_couverture = (
            (len(articles_en_stock) - len(items_a_renouveler)) / len(articles_en_stock)
            if articles_en_stock
            else 0.0
        )

        logger.info(
            f"✅ Inventaire→Budget: Budget prévisionnel estimé à {budget_total}€ "
            f"({len(items_a_renouveler)} articles à renouveler)"
        )

        return {
            "budget_previsionnel": round(budget_total, 2),
            "par_categorie": {cat: round(montant, 2) for cat, montant in budget_par_cat.items()},
            "items_a_renouveler": items_a_renouveler,
            "taux_couverture": round(taux_couverture * 100, 1),
            "horizons_semaines": semaines_horizon,
            "message": f"Budget prévisionnel: {round(budget_total, 2)}€ pour {semaines_horizon} semaines.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def agréger_achats_par_categorie(
        self,
        *,
        jours_lookback: int = 30,
        db=None,
    ) -> dict[str, Any]:
        """Agrège les dépenses réelles par catégorie alimentaire sur une période.

        Args:
            jours_lookback: Nombre de jours à analyser (défaut: 30)
            db: Session DB

        Returns:
            Dict avec dépenses_par_cat, total, tickets_count
        """
        from src.core.models.famille import BudgetFamille

        date_limite = date_type.today() - timedelta(days=jours_lookback)

        resultats = (
            db.query(
                BudgetFamille.categorie,
                func.sum(BudgetFamille.montant),
                func.count(BudgetFamille.id),
            )
            .filter(
                BudgetFamille.date >= date_limite,
                BudgetFamille.categorie.ilike("%alimentation%"),
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        depenses_par_cat = {
            cat: {"montant": montant, "nb_tickets": count} for cat, montant, count in resultats
        }
        total = sum(item["montant"] for item in depenses_par_cat.values())

        logger.info(
            f"✅ Agrégation achats: {total}€ sur {jours_lookback} jours, {len(depenses_par_cat)} catégories."
        )

        return {
            "periode_jours": jours_lookback,
            "depenses_par_categorie": depenses_par_cat,
            "total_periode": round(total, 2),
            "moyenne_par_jour": round(total / jours_lookback, 2),
            "nb_tickets": sum(item["nb_tickets"] for item in depenses_par_cat.values()),
        }


@service_factory("inventaire_budget", tags={"cuisine", "budget", "inventaire"})
def get_inventaire_budget_service() -> InventaireBudgetInteractionService:
    """Factory pour le service inter-modules Inventaire→Budget."""
    return InventaireBudgetInteractionService()
