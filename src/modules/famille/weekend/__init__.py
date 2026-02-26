"""
Module Sorties Weekend - Planning et suggestions IA.

Fonctionnalités:
- 📅 Planning weekend (samedi/dimanche)
- 💡 Idées IA (selon météo + âge Jules + budget)
- 🗺️ Lieux testés & notés
- 💰 Budget sorties
"""

# Import des fonctions pour exposer l'API publique
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("weekend")

from src.services.famille.weekend_ai import obtenir_weekend_ai_service

from .components import (
    afficher_add_activity,
    afficher_day_activities,
    afficher_lieux_testes,
    afficher_noter_sortie,
    afficher_planning,
    afficher_suggestions,
)
from .utils import (
    get_age_jules_mois,
    get_budget_weekend,
    get_lieux_testes,
    get_next_weekend,
    get_weekend_activities,
    mark_activity_done,
    st,
)


@profiler_rerun("weekend")
def app():
    """Point d'entrée du module Weekend"""
    st.title("🎉 Sorties Weekend")

    saturday, sunday = get_next_weekend()
    st.caption(f"📅 {saturday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}")

    # Tabs avec deep linking URL
    TAB_LABELS = [
        "📅 Planning",
        "💡 Suggestions IA",
        "🗺️ Lieux testés",
        "➕ Ajouter",
        "⭐ Noter",
        "💬 Assistant",
    ]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    with tabs[0]:
        with error_boundary(titre="Erreur planning weekend"):
            afficher_planning()

    with tabs[1]:
        with error_boundary(titre="Erreur suggestions weekend"):
            afficher_suggestions()

    with tabs[2]:
        with error_boundary(titre="Erreur lieux testés"):
            afficher_lieux_testes()

    with tabs[3]:
        with error_boundary(titre="Erreur ajout activité"):
            afficher_add_activity()

    with tabs[4]:
        with error_boundary(titre="Erreur notation"):
            afficher_noter_sortie()

    with tabs[5]:
        with error_boundary(titre="Erreur assistant weekend"):
            from src.ui.components import afficher_chat_contextuel

            st.caption("Posez vos questions sorties à l'assistant IA")
            afficher_chat_contextuel("weekend")


__all__ = [
    # Entry point
    "app",
    # AI Service (via factory)
    "obtenir_weekend_ai_service",
    # Helpers
    "get_next_weekend",
    "get_weekend_activities",
    "get_budget_weekend",
    "get_lieux_testes",
    "get_age_jules_mois",
    "mark_activity_done",
    # UI
    "afficher_planning",
    "afficher_day_activities",
    "afficher_suggestions",
    "afficher_lieux_testes",
    "afficher_add_activity",
    "afficher_noter_sortie",
]
