"""
Module Planificateur de Repas - Gestion des préférences et feedbacks
"""

from ._common import (
    FeedbackRecette,
    PreferencesUtilisateur,
    get_user_preference_service,
    logger,
    st,
)


def charger_preferences() -> PreferencesUtilisateur:
    """
    Charge les préférences depuis la DB.

    Utilise un cache session_state pour éviter les requêtes répétées
    pendant la même session Streamlit.
    """
    # Cache en session pour éviter requêtes DB répétées
    if "user_preferences" in st.session_state:
        return st.session_state.user_preferences

    # Charger depuis DB
    try:
        service = get_user_preference_service()
        prefs = service.charger_preferences()
        st.session_state.user_preferences = prefs
        logger.info("✅ Préférences chargées depuis DB")
        return prefs
    except Exception as e:
        logger.error(f"❌ Erreur chargement préférences: {e}")
        # Fallback sur valeurs par défaut
        prefs = PreferencesUtilisateur(
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
        st.session_state.user_preferences = prefs
        return prefs


def sauvegarder_preferences(prefs: PreferencesUtilisateur) -> bool:
    """
    Sauvegarde les préférences en DB.

    Args:
        prefs: Préférences à sauvegarder

    Returns:
        True si succès
    """
    try:
        service = get_user_preference_service()
        success = service.sauvegarder_preferences(prefs)

        if success:
            # Mettre à jour le cache session
            st.session_state.user_preferences = prefs
            logger.info("✅ Préférences sauvegardées en DB")

        return success
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde préférences: {e}")
        # Fallback: sauvegarder en session seulement
        st.session_state.user_preferences = prefs
        return False


def charger_feedbacks() -> list[FeedbackRecette]:
    """
    Charge l'historique des feedbacks depuis la DB.

    Utilise un cache session pour les performances.
    """
    # Cache en session
    if "recipe_feedbacks" in st.session_state:
        return st.session_state.recipe_feedbacks

    try:
        service = get_user_preference_service()
        feedbacks = service.charger_feedbacks()
        st.session_state.recipe_feedbacks = feedbacks
        logger.debug(f"Chargé {len(feedbacks)} feedbacks depuis DB")
        return feedbacks
    except Exception as e:
        logger.error(f"❌ Erreur chargement feedbacks: {e}")
        st.session_state.recipe_feedbacks = []
        return []


def ajouter_feedback(recette_id: int, recette_nom: str, feedback: str, contexte: str = None):
    """
    Ajoute un feedback sur une recette en DB.

    Args:
        recette_id: ID de la recette
        recette_nom: Nom de la recette
        feedback: "like", "dislike", ou "neutral"
        contexte: Contexte optionnel
    """
    try:
        service = get_user_preference_service()
        success = service.ajouter_feedback(
            recette_id=recette_id, recette_nom=recette_nom, feedback=feedback, contexte=contexte
        )

        if success:
            # Mettre à jour le cache session
            fb = FeedbackRecette(
                recette_id=recette_id,
                recette_nom=recette_nom,
                feedback=feedback,
                contexte=contexte,
            )

            if "recipe_feedbacks" not in st.session_state:
                st.session_state.recipe_feedbacks = []

            # Remplacer si feedback existant
            st.session_state.recipe_feedbacks = [
                f for f in st.session_state.recipe_feedbacks if f.recette_id != recette_id
            ]
            st.session_state.recipe_feedbacks.append(fb)

            logger.info(f"✅ Feedback ajouté: {recette_nom} → {feedback}")

    except Exception as e:
        logger.error(f"❌ Erreur ajout feedback: {e}")
        # Fallback: sauvegarder en session seulement
        fb = FeedbackRecette(
            recette_id=recette_id,
            recette_nom=recette_nom,
            feedback=feedback,
            contexte=contexte,
        )
        if "recipe_feedbacks" not in st.session_state:
            st.session_state.recipe_feedbacks = []
        st.session_state.recipe_feedbacks = [
            f for f in st.session_state.recipe_feedbacks if f.recette_id != recette_id
        ]
        st.session_state.recipe_feedbacks.append(fb)
