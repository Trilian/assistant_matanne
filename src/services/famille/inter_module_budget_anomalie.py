"""
Service inter-modules : Budget anomalie → Notification proactive.

B7 (I3): Détecter les anomalies de budget (+30% sur une catégorie
par rapport au mois précédent) et envoyer une notification proactive.
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy import extract, func

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Seuil de hausse pour déclencher une alerte (%)
SEUIL_ANOMALIE_PCT = 30.0

# Catégories surveillées
CATEGORIES_SURVEILLEES = [
    "alimentation",
    "restaurant",
    "loisirs",
    "transport",
    "sante",
    "vetements",
    "abonnements",
]


class BudgetAnomalieNotificationService:
    """Bridge budget anomalie → notification proactive."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def detecter_et_notifier_anomalies(
        self,
        *,
        seuil_pct: float = SEUIL_ANOMALIE_PCT,
        db=None,
    ) -> dict[str, Any]:
        """Détecte les catégories avec une hausse >seuil_pct vs mois précédent.

        Compare les dépenses du mois en cours avec celles du mois précédent.
        Si une catégorie dépasse le seuil, émet un événement et envoie
        une notification proactive.

        Args:
            seuil_pct: seuil de hausse en % (défaut: 30%)
            db: Session DB

        Returns:
            Dict avec anomalies détectées, notifications envoyées
        """
        from src.core.models.finances import Depense

        aujourd_hui = date.today()
        mois_courant = aujourd_hui.month
        annee_courante = aujourd_hui.year

        # Mois précédent
        if mois_courant == 1:
            mois_prec = 12
            annee_prec = annee_courante - 1
        else:
            mois_prec = mois_courant - 1
            annee_prec = annee_courante

        # Dépenses mois courant par catégorie
        depenses_courantes = dict(
            db.query(
                Depense.categorie,
                func.sum(Depense.montant),
            )
            .filter(
                extract("month", Depense.date) == mois_courant,
                extract("year", Depense.date) == annee_courante,
                Depense.categorie.in_(CATEGORIES_SURVEILLEES),
            )
            .group_by(Depense.categorie)
            .all()
        )

        # Dépenses mois précédent par catégorie
        depenses_precedentes = dict(
            db.query(
                Depense.categorie,
                func.sum(Depense.montant),
            )
            .filter(
                extract("month", Depense.date) == mois_prec,
                extract("year", Depense.date) == annee_prec,
                Depense.categorie.in_(CATEGORIES_SURVEILLEES),
            )
            .group_by(Depense.categorie)
            .all()
        )

        anomalies = []
        for cat in CATEGORIES_SURVEILLEES:
            montant_courant = float(depenses_courantes.get(cat, 0) or 0)
            montant_prec = float(depenses_precedentes.get(cat, 0) or 0)

            if montant_prec <= 0:
                continue

            hausse_pct = ((montant_courant - montant_prec) / montant_prec) * 100

            if hausse_pct >= seuil_pct:
                anomalies.append(
                    {
                        "categorie": cat,
                        "montant_courant": round(montant_courant, 2),
                        "montant_precedent": round(montant_prec, 2),
                        "hausse_pct": round(hausse_pct, 1),
                        "ecart": round(montant_courant - montant_prec, 2),
                    }
                )

        # Envoyer notifications si anomalies détectées
        notifications_envoyees = 0
        for anomalie in anomalies:
            self._envoyer_notification_anomalie(anomalie)
            self._emettre_evenement_anomalie(anomalie)
            notifications_envoyees += 1

        if anomalies:
            logger.info(
                f"🔔 Budget: {len(anomalies)} anomalie(s) détectée(s) — "
                f"catégories: {[a['categorie'] for a in anomalies]}"
            )

        return {
            "anomalies": anomalies,
            "nb_anomalies": len(anomalies),
            "notifications_envoyees": notifications_envoyees,
            "seuil_pct": seuil_pct,
            "message": (
                f"{len(anomalies)} anomalie(s) budget détectée(s) "
                f"(seuil: +{seuil_pct}% vs mois précédent)."
            ),
        }

    def _envoyer_notification_anomalie(self, anomalie: dict) -> None:
        """Envoie une notification pour une anomalie budget."""
        try:
            from src.services.core.notifications import obtenir_dispatcher_notifications

            dispatcher = obtenir_dispatcher_notifications()
            cat = anomalie["categorie"]
            hausse = anomalie["hausse_pct"]
            montant = anomalie["montant_courant"]
            ecart = anomalie["ecart"]

            message = (
                f"⚠️ Alerte budget {cat}\n"
                f"Hausse de +{hausse}% vs mois dernier\n"
                f"Ce mois: {montant}€ (+{ecart}€)\n"
                f"Pensez à ajuster vos dépenses."
            )

            dispatcher.envoyer(
                titre=f"Budget: +{hausse}% en {cat}",
                message=message,
                canaux=["push", "ntfy"],
                priorite="haute" if hausse >= 50 else "normale",
            )
        except Exception as e:
            logger.warning(f"Notification anomalie budget échouée: {e}")

    def _emettre_evenement_anomalie(self, anomalie: dict) -> None:
        """Émet un événement bus pour l'anomalie détectée."""
        try:
            from src.services.core.events import obtenir_bus

            obtenir_bus().emettre(
                "budget.depassement",
                {
                    "categorie": anomalie["categorie"],
                    "hausse_pct": anomalie["hausse_pct"],
                    "montant_courant": anomalie["montant_courant"],
                    "montant_precedent": anomalie["montant_precedent"],
                    "source": "anomalie_mensuelle",
                },
                source="budget_anomalie",
            )
        except Exception as e:
            logger.warning(f"Événement anomalie budget échoué: {e}")


@service_factory("budget_anomalie_notification", tags={"budget", "notifications", "anomalie"})
def obtenir_service_budget_anomalie() -> BudgetAnomalieNotificationService:
    """Factory pour le bridge budget anomalie → notifications."""
    return BudgetAnomalieNotificationService()
