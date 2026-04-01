"""
Service inter-modules : Anniversaires → Budget cadeaux.

IM-P2-7: Provisionner automatiquement une dépense "cadeau" dans le budget
quand un anniversaire approche.
"""

import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class AnniversairesBudgetInteractionService:
    """Service inter-modules Anniversaires → Budget."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def reserver_budget_previsionnel_j14(
        self,
        *,
        montant_defaut: float = 60.0,
        db=None,
    ) -> dict[str, Any]:
        """P5-15: reserve automatiquement un budget previsionnel a J-14."""
        from src.core.models import AnniversaireFamille, BudgetFamille

        anniversaires = db.query(AnniversaireFamille).all()
        reserves = []

        for anniv in anniversaires:
            jours_restants = getattr(anniv, "jours_restants", None)
            if jours_restants != 14:
                continue

            description = f"Reservation budget anniversaire J-14: {anniv.nom}"
            existe = db.query(BudgetFamille).filter(BudgetFamille.description == description).first()
            if existe:
                continue

            montant = self._estimer_budget_cadeau(anniv, montant_defaut)
            depense = BudgetFamille(
                date=date_type.today(),
                montant=montant,
                categorie="loisirs",
                description=description,
                magasin="",
                est_recurrent=False,
            )
            db.add(depense)
            reserves.append({"nom": anniv.nom, "montant": montant})

        if reserves:
            db.commit()

        return {
            "reserves": reserves,
            "nb_reservations": len(reserves),
            "message": f"{len(reserves)} reservation(s) budget J-14 creee(s).",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def provisionner_budget_cadeaux(
        self,
        *,
        jours_horizon: int = 30,
        montant_defaut: float = 50.0,
        db=None,
    ) -> dict[str, Any]:
        """Crée des provisions budget pour les anniversaires proches.

        Args:
            jours_horizon: fenêtre de détection des anniversaires (J)
            montant_defaut: montant provisionné par défaut
            db: Session DB

        Returns:
            Dict avec nombre de provisions créées
        """
        from src.core.models import AnniversaireFamille, BudgetFamille

        anniversaires = db.query(AnniversaireFamille).all()
        provisions_creees = 0
        details = []

        for anniv in anniversaires:
            jours_restants = getattr(anniv, "jours_restants", None)
            if jours_restants is None or not (0 <= jours_restants <= jours_horizon):
                continue

            description = f"Provision cadeau anniversaire {anniv.nom}"

            # Éviter les doublons sur le mois en cours
            existe = (
                db.query(BudgetFamille)
                .filter(
                    BudgetFamille.description == description,
                )
                .first()
            )
            if existe:
                continue

            montant = self._estimer_budget_cadeau(anniv, montant_defaut)
            depense = BudgetFamille(
                date=date_type.today(),
                montant=montant,
                categorie="loisirs",
                description=description,
                magasin="",
                est_recurrent=False,
            )
            db.add(depense)
            provisions_creees += 1
            details.append(
                {
                    "nom": anniv.nom,
                    "jours_restants": jours_restants,
                    "montant": montant,
                }
            )

        db.commit()

        # Émettre un événement récapitulatif
        if provisions_creees > 0:
            try:
                from src.services.core.events import obtenir_bus

                obtenir_bus().emettre(
                    "budget.modifie",
                    {
                        "action": "provision_anniversaires",
                        "nb_provisions": provisions_creees,
                    },
                    source="anniversaires_budget",
                )
            except Exception:
                logger.debug("Échec émission event provision anniversaires", exc_info=True)

        return {
            "ok": True,
            "provisions_creees": provisions_creees,
            "details": details,
            "message": f"{provisions_creees} provision(s) cadeau créée(s)",
        }

    def _estimer_budget_cadeau(self, anniv: Any, montant_defaut: float) -> float:
        """Estime le budget cadeau selon relation/âge."""
        relation = (getattr(anniv, "relation", "") or "").lower()
        age = getattr(anniv, "age", None)

        montant = montant_defaut
        if "enfant" in relation or "fils" in relation or "fille" in relation:
            montant += 20
        elif "parent" in relation or "maman" in relation or "papa" in relation:
            montant += 15

        if isinstance(age, int) and age < 10:
            montant += 10

        return round(montant, 2)


@service_factory("anniversaires_budget_interaction", tags={"famille", "budget", "anniversaires"})
def obtenir_service_anniversaires_budget_interaction() -> AnniversairesBudgetInteractionService:
    """Factory pour le service Anniversaires → Budget."""
    return AnniversairesBudgetInteractionService()
