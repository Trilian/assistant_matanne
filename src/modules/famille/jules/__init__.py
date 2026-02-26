"""
Module Jules - Activités adaptées, achats suggérés, conseils développement.

Fonctionnalités:
- 📊 Dashboard: âge, prochains achats suggérés
- 🎨 Activités du jour (adaptées 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandés)
- 💡 Conseils (propreté, sommeil, alimentation) - IA
"""

# Import des fonctions pour exposer l'API publique
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("jules")

from src.services.famille.jules_ai import obtenir_jules_ai_service

from .components import (
    afficher_achats_categorie,
    afficher_activites,
    afficher_conseils,
    afficher_dashboard,
    afficher_form_ajout_achat,
    afficher_shopping,
)
from .utils import (
    get_achats_jules_en_attente,
    get_activites_pour_age,
    get_age_jules,
    get_taille_vetements,
    st,
)


@profiler_rerun("jules")
def app():
    """Point d'entrée du module Jules"""
    st.title("👶 Jules")

    age = get_age_jules()
    st.caption(f"🎂 {age['mois']} mois • Né le {age['date_naissance'].strftime('%d/%m/%Y')}")

    # Tabs avec deep linking URL
    TAB_LABELS = ["📊 Dashboard", "🎨 Activités", "🛒 Shopping", "💡 Conseils", "💬 Assistant"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    with tabs[0]:
        with error_boundary(titre="Erreur dashboard Jules"):
            afficher_dashboard()

    with tabs[1]:
        with error_boundary(titre="Erreur activités Jules"):
            afficher_activites()

    with tabs[2]:
        with error_boundary(titre="Erreur shopping Jules"):
            afficher_shopping()

    with tabs[3]:
        with error_boundary(titre="Erreur conseils Jules"):
            afficher_conseils()

    with tabs[4]:
        with error_boundary(titre="Erreur assistant Jules"):
            from src.ui.components import afficher_chat_contextuel

            st.caption("Posez vos questions sur Jules à l'assistant IA")
            afficher_chat_contextuel("jules", context_extra={"age_mois": age["mois"]})


__all__ = [
    # Entry point
    "app",
    # AI Service (via factory)
    "obtenir_jules_ai_service",
    # Helpers
    "get_age_jules",
    "get_activites_pour_age",
    "get_taille_vetements",
    "get_achats_jules_en_attente",
    # UI
    "afficher_dashboard",
    "afficher_activites",
    "afficher_shopping",
    "afficher_achats_categorie",
    "afficher_form_ajout_achat",
    "afficher_conseils",
]
