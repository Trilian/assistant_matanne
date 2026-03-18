"""
Service Préférences Utilisateur - Persistance DB

Gère:
- PreferenceUtilisateur: Préférences familiales persistantes
- RetourRecette: Feedbacks 👍/👎 pour apprentissage IA

Remplace st.session_state par persistance PostgreSQL.
"""

import logging
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.modules.cuisine.schemas import (
    FeedbackRecette,
    PreferencesUtilisateur,
)

logger = logging.getLogger(__name__)

# ID utilisateur par défaut (famille Matanne)
DEFAULT_USER_ID = "matanne"


class UserPreferenceService:
    """Service pour gérer les préférences utilisateur en DB."""

    def __init__(self, user_id: str = DEFAULT_USER_ID):
        self.user_id = user_id

    @avec_session_db
    def charger_preferences(self, db: Session | None = None) -> PreferencesUtilisateur:
        """
        Charge les préférences depuis la DB.

        Returns:
            PreferencesUtilisateur avec valeurs DB ou défauts
        """
        from src.core.models import PreferenceUtilisateur

        stmt = select(PreferenceUtilisateur).where(PreferenceUtilisateur.user_id == self.user_id)
        db_pref = db.execute(stmt).scalar_one_or_none()

        if db_pref:
            logger.debug(f"Préférences chargées pour {self.user_id}")
            return self._db_to_dataclass(db_pref)

        # Créer les préférences par défaut
        logger.info(f"Création préférences par défaut pour {self.user_id}")
        default_prefs = self._get_default_preferences()
        self.sauvegarder_preferences(default_prefs, db=db)
        return default_prefs

    @avec_session_db
    def sauvegarder_preferences(
        self, prefs: PreferencesUtilisateur, db: Session | None = None
    ) -> bool:
        """
        Sauvegarde les préférences en DB (insert ou update).

        Args:
            prefs: PreferencesUtilisateur à sauvegarder

        Returns:
            True si succès
        """
        try:
            from src.core.models import PreferenceUtilisateur

            stmt = select(PreferenceUtilisateur).where(
                PreferenceUtilisateur.user_id == self.user_id
            )
            db_pref = db.execute(stmt).scalar_one_or_none()

            if db_pref:
                # Update existant
                self._update_db_from_dataclass(db_pref, prefs)
                db_pref.modifie_le = datetime.now(UTC)
            else:
                # Insert nouveau
                db_pref = self._dataclass_to_db(prefs)
                db.add(db_pref)

            db.commit()
            logger.info(f"✅ Préférences sauvegardées pour {self.user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde préférences: {e}")
            db.rollback()
            return False

    @avec_session_db
    def charger_feedbacks(self, db: Session | None = None) -> list[FeedbackRecette]:
        """
        Charge tous les feedbacks de l'utilisateur.

        Returns:
            Liste de FeedbackRecette
        """
        from src.core.models import RetourRecette

        stmt = (
            select(RetourRecette)
            .where(RetourRecette.user_id == self.user_id)
            .order_by(RetourRecette.cree_le.desc())
        )

        db_feedbacks = db.execute(stmt).scalars().all()

        feedbacks: list[FeedbackRecette] = []
        for fb in db_feedbacks:
            date_fb: date | None = fb.cree_le.date() if fb.cree_le else None
            feedbacks.append(
                FeedbackRecette(
                    recette_id=fb.recette_id,
                    recette_nom=fb.notes or f"Recette #{fb.recette_id}",  # nom stocké dans notes
                    feedback=fb.feedback,
                    date_feedback=date_fb,
                    contexte=fb.contexte,
                )
            )

        logger.debug(f"Chargé {len(feedbacks)} feedbacks pour {self.user_id}")
        return feedbacks

    @avec_session_db
    def ajouter_feedback(
        self,
        recette_nom: str,
        feedback: str,
        recette_id: int = 0,
        contexte: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """
        Ajoute ou met à jour un feedback sur une recette.

        Args:
            recette_nom: Nom de la recette (clé de recherche et stockage)
            feedback: "like", "dislike", ou "neutral"
            recette_id: ID de la recette (optionnel, 0 si inconnu)
            contexte: Contexte optionnel

        Returns:
            True si succès
        """
        try:
            from src.core.models import RetourRecette

            # Chercher par nom d'abord (plus fiable que l'ID pour les recettes IA)
            stmt = select(RetourRecette).where(
                RetourRecette.user_id == self.user_id, RetourRecette.notes == recette_nom
            )
            existing = db.execute(stmt).scalar_one_or_none()

            if existing:
                # Update
                existing.feedback = feedback
                existing.contexte = contexte
                logger.debug(f"Feedback mis à jour: {recette_nom} → {feedback}")
            else:
                # Insert
                new_fb = RetourRecette(
                    user_id=self.user_id,
                    recette_id=recette_id,
                    feedback=feedback,
                    contexte=contexte,
                    notes=recette_nom,
                )
                db.add(new_fb)
                logger.debug(f"Nouveau feedback: {recette_nom} → {feedback}")

            db.commit()
            return True

        except Exception as e:
            logger.error(f"❌ Erreur ajout feedback: {e}")
            db.rollback()
            return False

    @avec_session_db
    def supprimer_feedback(self, recette_id: int, db: Session | None = None) -> bool:
        """Supprime un feedback."""
        try:
            from src.core.models import RetourRecette

            stmt = select(RetourRecette).where(
                RetourRecette.user_id == self.user_id, RetourRecette.recette_id == recette_id
            )
            fb = db.execute(stmt).scalar_one_or_none()

            if fb:
                db.delete(fb)
                db.commit()
                logger.info(f"Feedback supprimé pour recette {recette_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Erreur suppression feedback: {e}")
            db.rollback()
            return False

    @avec_session_db
    def get_feedbacks_stats(self, db: Session | None = None) -> dict[str, int]:
        """
        Retourne les statistiques des feedbacks.

        Returns:
            Dict avec likes, dislikes, neutrals counts
        """
        from src.core.models import RetourRecette

        stmt = select(RetourRecette).where(RetourRecette.user_id == self.user_id)
        feedbacks = db.execute(stmt).scalars().all()

        stats = {"like": 0, "dislike": 0, "neutral": 0, "total": 0}
        for fb in feedbacks:
            stats[fb.feedback] = stats.get(fb.feedback, 0) + 1
            stats["total"] += 1

        return stats

    # -----------------------------------------------------------
    # HELPERS CONVERSION
    # -----------------------------------------------------------

    def _get_default_preferences(self) -> PreferencesUtilisateur:
        """Retourne les préférences par défaut pour la famille Matanne."""
        from src.modules.famille.age_utils import get_age_jules_mois

        return PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            jules_age_mois=get_age_jules_mois(),
            temps_semaine="normal",
            temps_weekend="long",
            aliments_exclus=[],
            aliments_favoris=["poulet", "pâtes", "gratins", "soupes"],
            poisson_par_semaine=2,
            vegetarien_par_semaine=1,
            viande_rouge_max=2,
            robots=["monsieur_cuisine", "cookeo", "four"],
            magasins_preferes=["Carrefour Drive", "Bio Coop", "Grand Frais", "Thiriet"],
        )

    def _db_to_dataclass(self, db_pref: "PreferenceUtilisateur") -> PreferencesUtilisateur:
        """Convertit PreferenceUtilisateur (DB) → PreferencesUtilisateur (dataclass)."""
        return PreferencesUtilisateur(
            nb_adultes=db_pref.nb_adultes,
            jules_present=db_pref.jules_present,
            jules_age_mois=db_pref.jules_age_mois,
            temps_semaine=db_pref.temps_semaine,
            temps_weekend=db_pref.temps_weekend,
            aliments_exclus=db_pref.aliments_exclus or [],
            aliments_favoris=db_pref.aliments_favoris or [],
            poisson_par_semaine=db_pref.poisson_par_semaine,
            vegetarien_par_semaine=db_pref.vegetarien_par_semaine,
            viande_rouge_max=db_pref.viande_rouge_max,
            robots=db_pref.robots or [],
            magasins_preferes=db_pref.magasins_preferes or [],
        )

    def _dataclass_to_db(self, prefs: PreferencesUtilisateur) -> "PreferenceUtilisateur":
        """Convertit PreferencesUtilisateur (dataclass) → PreferenceUtilisateur (DB)."""
        from src.core.models import PreferenceUtilisateur

        return PreferenceUtilisateur(
            user_id=self.user_id,
            nb_adultes=prefs.nb_adultes,
            jules_present=prefs.jules_present,
            jules_age_mois=prefs.jules_age_mois,
            temps_semaine=prefs.temps_semaine,
            temps_weekend=prefs.temps_weekend,
            aliments_exclus=prefs.aliments_exclus,
            aliments_favoris=prefs.aliments_favoris,
            poisson_par_semaine=prefs.poisson_par_semaine,
            vegetarien_par_semaine=prefs.vegetarien_par_semaine,
            viande_rouge_max=prefs.viande_rouge_max,
            robots=prefs.robots,
            magasins_preferes=prefs.magasins_preferes,
        )

    def _update_db_from_dataclass(
        self, db_pref: "PreferenceUtilisateur", prefs: PreferencesUtilisateur
    ):
        """Met à jour les champs DB depuis le dataclass."""
        db_pref.nb_adultes = prefs.nb_adultes
        db_pref.jules_present = prefs.jules_present
        db_pref.jules_age_mois = prefs.jules_age_mois
        db_pref.temps_semaine = prefs.temps_semaine
        db_pref.temps_weekend = prefs.temps_weekend
        db_pref.aliments_exclus = prefs.aliments_exclus
        db_pref.aliments_favoris = prefs.aliments_favoris
        db_pref.poisson_par_semaine = prefs.poisson_par_semaine
        db_pref.vegetarien_par_semaine = prefs.vegetarien_par_semaine
        db_pref.viande_rouge_max = prefs.viande_rouge_max
        db_pref.robots = prefs.robots
        db_pref.magasins_preferes = prefs.magasins_preferes


# -----------------------------------------------------------
# FACTORY
# -----------------------------------------------------------

from src.services.core.registry import service_factory


@service_factory("preferences_utilisateur", tags={"utilisateur", "config"})
def _creer_service_preferences_defaut() -> UserPreferenceService:
    """Factory interne pour le registre (utilisateur par défaut)."""
    return UserPreferenceService(DEFAULT_USER_ID)


# Cache par user_id pour supporter le multi-utilisateur
_preferences_par_user: dict[str, UserPreferenceService] = {}


def obtenir_service_preferences_utilisateur(
    user_id: str = DEFAULT_USER_ID,
) -> UserPreferenceService:
    """Factory pour obtenir le service de préférences (thread-safe, multi-utilisateur).

    Retourne l'instance du registre pour l'utilisateur par défaut,
    ou crée une instance dédiée pour les autres utilisateurs.
    """
    if user_id == DEFAULT_USER_ID:
        return _creer_service_preferences_defaut()
    if user_id not in _preferences_par_user:
        _preferences_par_user[user_id] = UserPreferenceService(user_id)
    return _preferences_par_user[user_id]


def get_user_preference_service(user_id: str = DEFAULT_USER_ID) -> UserPreferenceService:
    """Factory pour obtenir le service de préférences (alias anglais)."""
    return obtenir_service_preferences_utilisateur(user_id)
