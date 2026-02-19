"""
Module Sorties Weekend - Planning et suggestions IA.

Fonctionnalités:
- 📅 Planning weekend (samedi/dimanche)
- 💡 Idées IA (selon météo + âge Jules + budget)
- 🗺️ Lieux testés & notés
- 💰 Budget sorties
"""

# Import des fonctions pour exposer l'API publique
from .ai_service import WeekendAIService
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


def app():
    """Point d'entrée du module Weekend"""
    st.title("🎉 Sorties Weekend")

    saturday, sunday = get_next_weekend()
    st.caption(f"📅 {saturday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}")

    # Tabs
    tabs = st.tabs(["📅 Planning", "💡 Suggestions IA", "🗺️ Lieux testés", "➕ Ajouter", "⭐ Noter"])

    with tabs[0]:
        afficher_planning()

    with tabs[1]:
        afficher_suggestions()

    with tabs[2]:
        afficher_lieux_testes()

    with tabs[3]:
        afficher_add_activity()

    with tabs[4]:
        afficher_noter_sortie()


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
    "afficher_planning",
    "afficher_day_activities",
    "afficher_suggestions",
    "afficher_lieux_testes",
    "afficher_add_activity",
    "afficher_noter_sortie",
]
