"""Package Telegram — sous-modules du webhook bot Telegram.

Re-exporte ``router`` pour compatibilité avec ``main.py``.
Re-exporte des fonctions internes pour compatibilité des tests existants.
"""

from ._routes import router

# Re-exports pour compatibilité des tests (test_webhooks_telegram_callbacks.py)
from ._helpers import _extraire_id_depuis_callback, _normaliser_texte, _obtenir_url_app
from ._callbacks import (
    _traiter_callback_action_article,
    _traiter_callback_courses,
    _traiter_callback_menu,
    _traiter_callback_planning,
    _traiter_callback_sondage_repas,
    _traiter_callback_toggle_article,
    _traiter_reponse_rapide_ok,
    _obtenir_message_id,
)
from ._dispatcher import _dispatcher_commande_telegram
from ._cuisine import (
    _envoyer_courses_commande,
    _envoyer_planning_commande,
    _envoyer_repas_du_soir,
    _envoyer_repas_moment,
    _ajouter_article_liste,
)
from ._famille import _envoyer_activites_samedi
from ._outils import _traiter_photo_frigo_telegram
from ._schemas import COMMANDES_TELEGRAM, EnvoyerPlanningTelegramRequest, EnvoyerCoursesTelegramRequest

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
    "_envoyer_courses_commande",
    "_envoyer_planning_commande",
    "_envoyer_repas_du_soir",
    "_envoyer_repas_moment",
    "_ajouter_article_liste",
    # Famille
    "_envoyer_activites_samedi",
    # Outils
    "_traiter_photo_frigo_telegram",
    # Schemas
    "EnvoyerPlanningTelegramRequest",
    "EnvoyerCoursesTelegramRequest",
]
