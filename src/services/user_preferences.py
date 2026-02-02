"""
Service Préférences Utilisateur - Persistance DB

Gère:
- UserPreference: Préférences familiales persistantes
- RecipeFeedback: Feedbacks 👍/👎 pour apprentissage IA

Remplace st.session_state par persistance PostgreSQL.
"""

import logging
from typing import Optional
from datetime import datetime, timezone, date

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.decorators import with_db_session
from src.core.models import UserPreference, RecipeFeedback
from src.domains.cuisine.logic.schemas import (
    PreferencesUtilisateur,
    FeedbackRecette,
)

logger = logging.getLogger(__name__)

# ID utilisateur par défaut (famille Matanne)
DEFAULT_USER_ID = "matanne"


class UserPreferenceService:
    """Service pour gérer les préférences utilisateur en DB."""
    
    def __init__(self, user_id: str = DEFAULT_USER_ID):
        self.user_id = user_id
    
    @with_db_session
    def charger_preferences(self, db: Optional[Session] = None) -> PreferencesUtilisateur:
        """
        Charge les préférences depuis la DB.
        
        Returns:
            PreferencesUtilisateur avec valeurs DB ou défauts
        """
        stmt = select(UserPreference).where(UserPreference.user_id == self.user_id)
        db_pref = db.execute(stmt).scalar_one_or_none()
        
        if db_pref:
            logger.debug(f"Préférences chargées pour {self.user_id}")
            return self._db_to_dataclass(db_pref)
        
        # Créer les préférences par défaut
        logger.info(f"Création préférences par défaut pour {self.user_id}")
        default_prefs = self._get_default_preferences()
        self.sauvegarder_preferences(default_prefs, db=db)
        return default_prefs
    
    @with_db_session
    def sauvegarder_preferences(self, prefs: PreferencesUtilisateur, db: Optional[Session] = None) -> bool:
        """
        Sauvegarde les préférences en DB (insert ou update).
        
        Args:
            prefs: PreferencesUtilisateur à sauvegarder
            
        Returns:
            True si succès
        """
        try:
            stmt = select(UserPreference).where(UserPreference.user_id == self.user_id)
            db_pref = db.execute(stmt).scalar_one_or_none()
            
            if db_pref:
                # Update existant
                self._update_db_from_dataclass(db_pref, prefs)
                db_pref.updated_at = datetime.now(timezone.utc)
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
    
    @with_db_session
    def charger_feedbacks(self, db: Optional[Session] = None) -> list[FeedbackRecette]:
        """
        Charge tous les feedbacks de l'utilisateur.
        
        Returns:
            Liste de FeedbackRecette
        """
        stmt = select(RecipeFeedback).where(
            RecipeFeedback.user_id == self.user_id
        ).order_by(RecipeFeedback.created_at.desc())
        
        db_feedbacks = db.execute(stmt).scalars().all()
        
        feedbacks: list[FeedbackRecette] = []
        for fb in db_feedbacks:
            date_fb: Optional[date] = fb.created_at.date() if fb.created_at else None
            feedbacks.append(FeedbackRecette(
                recette_id=fb.recette_id,
                recette_nom=fb.notes or f"Recette #{fb.recette_id}",  # nom stocké dans notes
                feedback=fb.feedback,
                date_feedback=date_fb,
                contexte=fb.contexte,
            ))
        
        logger.debug(f"Chargé {len(feedbacks)} feedbacks pour {self.user_id}")
        return feedbacks
    
    @with_db_session
    def ajouter_feedback(
        self, 
        recette_id: int, 
        recette_nom: str, 
        feedback: str, 
        contexte: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """
        Ajoute ou met à jour un feedback sur une recette.
        
        Args:
            recette_id: ID de la recette
            recette_nom: Nom de la recette (stocké dans notes)
            feedback: "like", "dislike", ou "neutral"
            contexte: Contexte optionnel
            
        Returns:
            True si succès
        """
        try:
            # Vérifier si feedback existe déjà
            stmt = select(RecipeFeedback).where(
                RecipeFeedback.user_id == self.user_id,
                RecipeFeedback.recette_id == recette_id
            )
            existing = db.execute(stmt).scalar_one_or_none()
            
            if existing:
                # Update
                existing.feedback = feedback
                existing.contexte = contexte
                existing.notes = recette_nom
                logger.debug(f"Feedback mis à jour: {recette_nom} → {feedback}")
            else:
                # Insert
                new_fb = RecipeFeedback(
                    user_id=self.user_id,
                    recette_id=recette_id,
                    feedback=feedback,
                    contexte=contexte,
                    notes=recette_nom,  # Stocker le nom dans notes
                )
                db.add(new_fb)
                logger.debug(f"Nouveau feedback: {recette_nom} → {feedback}")
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout feedback: {e}")
            db.rollback()
            return False
    
    @with_db_session
    def supprimer_feedback(self, recette_id: int, db: Optional[Session] = None) -> bool:
        """Supprime un feedback."""
        try:
            stmt = select(RecipeFeedback).where(
                RecipeFeedback.user_id == self.user_id,
                RecipeFeedback.recette_id == recette_id
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
    
    @with_db_session
    def get_feedbacks_stats(self, db: Optional[Session] = None) -> dict[str, int]:
        """
        Retourne les statistiques des feedbacks.
        
        Returns:
            Dict avec likes, dislikes, neutrals counts
        """
        stmt = select(RecipeFeedback).where(RecipeFeedback.user_id == self.user_id)
        feedbacks = db.execute(stmt).scalars().all()
        
        stats = {"like": 0, "dislike": 0, "neutral": 0, "total": 0}
        for fb in feedbacks:
            stats[fb.feedback] = stats.get(fb.feedback, 0) + 1
            stats["total"] += 1
        
        return stats
    
    # ═══════════════════════════════════════════════════════════
    # HELPERS CONVERSION
    # ═══════════════════════════════════════════════════════════
    
    def _get_default_preferences(self) -> PreferencesUtilisateur:
        """Retourne les préférences par défaut pour la famille Matanne."""
        return PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            jules_age_mois=19,
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
    
    def _db_to_dataclass(self, db_pref: UserPreference) -> PreferencesUtilisateur:
        """Convertit UserPreference (DB) → PreferencesUtilisateur (dataclass)."""
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
    
    def _dataclass_to_db(self, prefs: PreferencesUtilisateur) -> UserPreference:
        """Convertit PreferencesUtilisateur (dataclass) → UserPreference (DB)."""
        return UserPreference(
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
    
    def _update_db_from_dataclass(self, db_pref: UserPreference, prefs: PreferencesUtilisateur):
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


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_preference_service: Optional[UserPreferenceService] = None


def get_user_preference_service(user_id: str = DEFAULT_USER_ID) -> UserPreferenceService:
    """Factory pour obtenir le service de préférences."""
    global _preference_service
    if _preference_service is None or _preference_service.user_id != user_id:
        _preference_service = UserPreferenceService(user_id)
    return _preference_service
