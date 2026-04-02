"""
Bridge NIM5: Entretien → Budget maison.

Connecte les tâches d'entretien aux dépenses maison pour tracker les dépenses artisans/maintenance.
- Quand une tâche entretien est terminée avec un coût, créer une DepenseMaison
- Événement: entretien.termine -> budget.depense_entretien
"""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class EntretienBudgetBridgeService:
    """Bridge pour tracker les dépenses d'entretien dans le budget maison."""

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def enregistrer_depense_entretien(
        self,
        tache_id: int,
        montant_reel: Decimal,
        description: str = "",
        db: Session | None = None,
    ) -> dict | None:
        """Enregistre une dépense maison pour une tâche entretien terminée.

        Args:
            tache_id: ID de la tâche entretien
            montant_reel: Montant de la dépense (pour artisan, matériel, etc.)
            description: Description supplémentaire de la dépense
            db: Session base de données

        Returns:
            Dict avec les infos de la dépense créée ou None en cas d'erreur

        Événement émis: budget.depense_entretien_creee
        """
        from datetime import date

        from src.core.models.habitat import TacheEntretien
        from src.core.models.finances import DepenseMaison
        from src.services.core.events import obtenir_bus

        try:
            # Vérifier la tâche existe et est terminée
            tache = db.query(TacheEntretien).filter_by(id=tache_id).first()
            if not tache:
                logger.warning(f"Tâche entretien {tache_id} introuvable")
                return None

            if not tache.fait:
                logger.warning(f"Tâche {tache_id} n'est pas encore terminée")
                return None

            # Créer la dépense maison
            today = date.today()
            depense = DepenseMaison(
                categorie="entretien_maintenance",
                mois=today.month,
                annee=today.year,
                montant=montant_reel,
                fournisseur=f"{tache.nom} (tâche #{tache_id})",
                notes=f"{description or tache.description}\nLiée à: {tache.nom}",
            )

            db.add(depense)
            db.flush()

            # Émettre l'événement
            bus = obtenir_bus()
            bus.emettre(
                "budget.depense_entretien_creee",
                {
                    "depense_id": depense.id,
                    "tache_id": tache_id,
                    "montant": str(montant_reel),
                    "categorie": "entretien_maintenance",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            db.commit()

            logger.info(f"✅ Dépense entretien créée (#{depense.id}, {montant_reel}€) pour tâche #{tache_id}")

            return {
                "depense_id": depense.id,
                "tache_id": tache_id,
                "montant": float(montant_reel),
                "categorie": "entretien_maintenance",
                "nom_tache": tache.nom,
            }

        except Exception as e:
            logger.error(f"Erreur bridge entretien→budget: {e}")
            db.rollback()
            return None

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_depenses_par_entretien(self, limite: int = 10, db: Session | None = None) -> list[dict]:
        """Liste les dépenses maison récentes liées à l'entretien.

        Returns:
            Liste de dépenses avec détails
        """
        from src.core.models.finances import DepenseMaison

        depenses = (
            db.query(DepenseMaison)
            .filter(DepenseMaison.categorie == "entretien_maintenance")
            .order_by(DepenseMaison.cree_le.desc())
            .limit(limite)
            .all()
        )

        return [
            {
                "id": d.id,
                "montant": float(d.montant),
                "mois": d.mois,
                "annee": d.annee,
                "fournisseur": d.fournisseur,
                "notes": d.notes,
                "cree_le": d.cree_le.isoformat() if d.cree_le else None,
            }
            for d in depenses
        ]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("entretien_budget_bridge", tags={"bridges", "maison"})
def obtenir_entretien_budget_bridge() -> EntretienBudgetBridgeService:
    """Factory singleton pour le bridge Entretien → Budget."""
    return EntretienBudgetBridgeService()


# ═══════════════════════════════════════════════════════════
# EVENT SUBSCRIBERS
# ═══════════════════════════════════════════════════════════


def enregistrer_entretien_budget_subscribers() -> None:
    """Enregistre les subscribers pour le bridge Entretien → Budget."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    # Le bridge s'active via API ou manuel, pas automatiquement par événement
    logger.info("✅ Bridge Entretien → Budget enregistré")
