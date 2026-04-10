"""
Service pour les interactions inter-modules Budget × Jeux.

IM3: Alerte paris > seuil semaine
IM8: Gain jeux → journal/budget
"""

import logging
from datetime import datetime, timedelta

from src.api.schemas import MessageResponse
from src.core.decorators import avec_session_db
from src.core.db import obtenir_contexte_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BudgetJeuxInteractionService:
    """Service pour les interactions inter-modules Budget × Jeux."""

    @avec_session_db
    def verifier_alerte_paris_semaine(self, user_id: str, db=None) -> dict:
        """Vérifie si les paris de la semaine dépassent le seuil (IM3).

        Args:
            user_id: ID de l'utilisateur
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec alerte_declenche (bool), cumul, seuil, message
        """
        from datetime import date, timedelta
        from src.core.models import PariSportif
        from src.core.models.family import UserPreferences

        # Récupérer le seuil depuis les préférences
        prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        seuil = 100.0  # Défaut
        if prefs and isinstance(prefs.preferences, dict):
            seuil = float(prefs.preferences.get("seuil_paris_semaine", 100.0))

        # Calculer le cumul de cette semaine
        debut_semaine = date.today() - timedelta(days=date.today().weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        cumul = (
            db.query(PariSportif)
            .filter(
                PariSportif.user_id == user_id,
                PariSportif.cree_le >= debut_semaine,
                PariSportif.cree_le <= fin_semaine,
            )
            .with_entities(db.func.sum(PariSportif.mise))
            .scalar() or 0.0
        )

        alerte_declenche = cumul > seuil

        if alerte_declenche:
            logger.warning(
                f"⚠️ Alerte budget paris: {cumul}€ > {seuil}€ pour l'utilisateur {user_id}"
            )
            self._emettre_alerte_paris(user_id, cumul, seuil)

        return {
            "alerte_declenche": alerte_declenche,
            "cumul_semaine": cumul,
            "seuil": seuil,
            "message": f"Paris cette semaine: {cumul}€ / {seuil}€",
        }

    def _emettre_alerte_paris(self, user_id: str, cumul: float, seuil: float) -> None:
        """Émet une alerte pour le dépassement du budget paris.

        Args:
            user_id: ID de l'utilisateur
            cumul: Cumul des paris
            seuil: Seuil configuré
        """
        from src.services.core.event_bus import obtenir_bus

        message = f"Alerte budget: {cumul}€ dépasse le seuil hebdo de {seuil}€"
        try:
            obtenir_bus().emettre(
                "jeux.alerte_budget",
                {
                    "user_id": user_id,
                    "cumul": cumul,
                    "seuil": seuil,
                    "message": message,
                },
                source="jeux",
            )
            logger.info(f"✅ Newsletter alerte budget émise pour {user_id}")
        except Exception as e:
            logger.error(f"Erreur émission alerte budget: {e}")

    @avec_session_db
    def noter_gain_jeux(
        self,
        user_id: str,
        montant_gain: float,
        type_jeu: str = "paris",
        description: str = "",
        db=None,
    ) -> dict:
        """Ajoute automatiquement un gain de jeu au journal et budget (IM8).

        Args:
            user_id: ID de l'utilisateur
            montant_gain: Montant du gain
            type_jeu: Type de jeu (paris, loto, etc.)
            description: Description du gain
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec id_journal, id_budget, message
        """
        from src.core.models import NoteMemo, BudgetLigne
        from datetime import datetime

        try:
            # Ajouter au journal
            note = NoteMemo(
                user_id=user_id,
                titre=f"Gain {type_jeu}: +{montant_gain}€",
                contenu=f"Gain de {montant_gain}€ au {type_jeu}. {description}",
                categorie="jeux",
                date_note=datetime.now(),
            )
            db.add(note)
            db.flush()

            # Ajouter une ligne au budget
            ligne = BudgetLigne(
                user_id=user_id,
                type_ligne="revenu",
                montant=montant_gain,
                libelle=f"Gain {type_jeu}",
                date_ligne=datetime.now(),
                categorie="jeux",
                description=description,
            )
            db.add(ligne)
            db.commit()

            logger.info(
                f"✅ Gain {type_jeu} de {montant_gain}€ noté pour {user_id}"
            )
            return {
                "id_journal": note.id,
                "id_budget": ligne.id,
                "message": f"Gain de {montant_gain}€ enregistré",
            }
        except Exception as e:
            logger.error(f"Erreur notation gain jeux: {e}")
            db.rollback()
            return {"error": str(e)}


@service_factory("budget_jeux_interaction", tags={"jeux", "budget"})
def obtenir_service_budget_jeux_interaction() -> BudgetJeuxInteractionService:
    """Factory pour le service Budget × Jeux."""
    return BudgetJeuxInteractionService()
