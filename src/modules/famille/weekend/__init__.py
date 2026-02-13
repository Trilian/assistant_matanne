"""
Module Sorties Weekend - Planning et suggestions IA.

Fonctionnalités:
- ðŸ“… Planning weekend (samedi/dimanche)
- ðŸ’¡ Idées IA (selon météo + âge Jules + budget)
- ðŸ—ºï¸ Lieux testés & notés
- ðŸ’° Budget sorties
"""

# Import des fonctions pour exposer l'API publique
from .ai_service import WeekendAIService
from .components import (
    render_add_activity,
    render_day_activities,
    render_lieux_testes,
    render_noter_sortie,
    render_planning,
    render_suggestions,
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


def app():
    """Point d'entrée du module Weekend"""
    st.title("ðŸŽ‰ Sorties Weekend")

    saturday, sunday = get_next_weekend()
    st.caption(f"ðŸ“… {saturday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}")

    # Tabs
    tabs = st.tabs(
        ["ðŸ“… Planning", "ðŸ’¡ Suggestions IA", "ðŸ—ºï¸ Lieux testés", "âž• Ajouter", "â­ Noter"]
    )

    with tabs[0]:
        render_planning()

    with tabs[1]:
        render_suggestions()

    with tabs[2]:
        render_lieux_testes()

    with tabs[3]:
        render_add_activity()

    with tabs[4]:
        render_noter_sortie()


__all__ = [
    # Entry point
    "app",
    # AI Service
    "WeekendAIService",
    # Helpers
    "get_next_weekend",
    "get_weekend_activities",
    "get_budget_weekend",
    "get_lieux_testes",
    "get_age_jules_mois",
    "mark_activity_done",
    # UI
    "render_planning",
    "render_day_activities",
    "render_suggestions",
    "render_lieux_testes",
    "render_add_activity",
    "render_noter_sortie",
]
