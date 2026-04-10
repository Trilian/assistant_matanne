"""
Service inter-modules : Courses total → Budget catégorie alimentation.

Quand une liste de courses est validée/complétée,
synchroniser le total comme dépense dans la catégorie alimentation du budget.
"""

import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class CoursesBudgetInteractionService:
    """Service inter-modules Courses → Budget alimentation."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_total_courses_vers_budget(
        self,
        liste_id: int,
        montant_total: float,
        magasin: str = "",
        *,
        db=None,
    ) -> dict[str, Any]:
        """Enregistre le total d'une liste de courses comme dépense alimentation.

        Args:
            liste_id: ID de la liste de courses
            montant_total: Montant total des courses
            magasin: Nom du magasin (optionnel)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec depense_id, montant, message
        """
        if montant_total <= 0:
            return {"message": "Montant nul ou négatif, aucune dépense créée."}

        from src.core.models import BudgetFamille

        depense = BudgetFamille(
            date=date_type.today(),
            montant=montant_total,
            categorie="alimentation",
            description=f"Courses (liste #{liste_id})",
            magasin=magasin,
            est_recurrent=False,
        )
        db.add(depense)
        db.commit()
        db.refresh(depense)

        # Émettre événement budget
        self._emettre_evenement_budget(depense.id, montant_total)

        logger.info(
            f"✅ Courses→Budget: {montant_total}€ enregistrés en alimentation "
            f"(liste #{liste_id}, magasin={magasin or 'N/A'})"
        )

        return {
            "depense_id": depense.id,
            "montant": montant_total,
            "categorie": "alimentation",
            "message": f"Dépense de {montant_total}€ ajoutée au budget alimentation.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def estimer_budget_courses_mensuel(
        self, *, mois: int | None = None, annee: int | None = None, db=None
    ) -> dict[str, Any]:
        """Calcule le total des dépenses courses/alimentation du mois.

        Args:
            mois: Mois à analyser (défaut: mois courant)
            annee: Année à analyser (défaut: année courante)
            db: Session DB

        Returns:
            Dict avec total_mois, nb_achats, moyenne_par_achat
        """
        from sqlalchemy import extract, func

        from src.core.models import BudgetFamille

        mois = mois or date_type.today().month
        annee = annee or date_type.today().year

        resultats = (
            db.query(
                func.sum(BudgetFamille.montant),
                func.count(BudgetFamille.id),
            )
            .filter(
                extract("month", BudgetFamille.date) == mois,
                extract("year", BudgetFamille.date) == annee,
                BudgetFamille.categorie.in_(["alimentation", "courses"]),
            )
            .first()
        )

        total = float(resultats[0] or 0)
        nb_achats = int(resultats[1] or 0)
        moyenne = total / nb_achats if nb_achats > 0 else 0.0

        return {
            "total_mois": total,
            "nb_achats": nb_achats,
            "moyenne_par_achat": round(moyenne, 2),
            "mois": mois,
            "annee": annee,
        }

    def _emettre_evenement_budget(self, depense_id: int, montant: float) -> None:
        """Émet un événement budget.modifie pour la synchronisation."""
        try:
            from src.services.core.events import obtenir_bus

            obtenir_bus().emettre(
                "budget.modifie",
                {
                    "depense_id": depense_id,
                    "categorie": "alimentation",
                    "montant": montant,
                    "action": "depense_ajoutee",
                    "source_module": "courses",
                },
                source="courses_budget",
            )
        except Exception as e:
            logger.warning(f"Erreur émission événement budget: {e}")


@service_factory("courses_budget_interaction", tags={"cuisine", "budget", "courses"})
def obtenir_service_courses_budget() -> CoursesBudgetInteractionService:
    """Factory pour le service Courses → Budget."""
    return CoursesBudgetInteractionService()
