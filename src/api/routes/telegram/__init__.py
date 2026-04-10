"""Package Telegram — sous-modules du webhook bot Telegram.

Re-exporte ``router`` pour compatibilité avec ``main.py``.
Re-exporte des fonctions internes pour compatibilité des tests existants.
"""

from ._callbacks import (
    _obtenir_message_id,
    _traiter_callback_action_article,
    _traiter_callback_courses,
    _traiter_callback_menu,
    _traiter_callback_planning,
    _traiter_callback_sondage_repas,
    _traiter_callback_toggle_article,
    _traiter_reponse_rapide_ok,
)
from ._cuisine import (
    _ajouter_article_liste,
    _envoyer_courses_commande,
    _envoyer_inventaire_commande,
    _envoyer_planning_commande,
    _envoyer_recette_commande,
    _envoyer_repas_du_soir,
    _envoyer_repas_moment,
    _envoyer_resume_batch_cooking,
)
from ._dispatcher import _dispatcher_commande_telegram
from ._famille import (
    _envoyer_activites_samedi,
    _envoyer_digest_commande,
    _envoyer_projection_budget_telegram,
    _envoyer_rapport_hebdo,
    _envoyer_recap_journee,
    _envoyer_resume_weekend,
)

# Re-exports pour compatibilité des tests (test_webhooks_telegram_callbacks.py)
from ._helpers import _extraire_id_depuis_callback, _normaliser_texte, _obtenir_url_app
from ._maison import _envoyer_rappels_groupes, _envoyer_resume_energie, _envoyer_resume_jardin
from ._outils import (
    _creer_note_rapide_telegram,
    _envoyer_aide_photo_telegram,
    _lancer_minuteur_telegram,
    _traiter_photo_frigo_telegram,
)
from ._routes import router
from ._schemas import (
    COMMANDES_TELEGRAM,
    EnvoyerCoursesTelegramRequest,
    EnvoyerPlanningTelegramRequest,
)

__all__ = [
    "router",
    "COMMANDES_TELEGRAM",
    # Helpers
    "_extraire_id_depuis_callback",
    "_normaliser_texte",
    "_obtenir_url_app",
    # Callbacks
    "_traiter_callback_action_article",
    "_traiter_callback_courses",
    "_traiter_callback_menu",
    "_traiter_callback_planning",
    "_traiter_callback_sondage_repas",
    "_traiter_callback_toggle_article",
    "_traiter_reponse_rapide_ok",
    "_obtenir_message_id",
    # Dispatcher
    "_dispatcher_commande_telegram",
    # Cuisine
    "_ajouter_article_liste",
    "_envoyer_courses_commande",
    "_envoyer_inventaire_commande",
    "_envoyer_planning_commande",
    "_envoyer_recette_commande",
    "_envoyer_repas_du_soir",
    "_envoyer_repas_moment",
    "_envoyer_resume_batch_cooking",
    # Famille
    "_envoyer_activites_samedi",
    "_envoyer_projection_budget_telegram",
    "_envoyer_rapport_hebdo",
    "_envoyer_recap_journee",
    "_envoyer_resume_weekend",
    # Maison
    "_envoyer_rappels_groupes",
    "_envoyer_resume_energie",
    "_envoyer_resume_jardin",
    # Outils
    "_creer_note_rapide_telegram",
    "_envoyer_aide_photo_telegram",
    "_lancer_minuteur_telegram",
    "_traiter_photo_frigo_telegram",
    # Schemas
    "EnvoyerPlanningTelegramRequest",
    "EnvoyerCoursesTelegramRequest",
]
