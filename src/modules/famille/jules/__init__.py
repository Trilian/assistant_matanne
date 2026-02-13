"""
Module Jules - Activités adaptées, achats suggérés, conseils développement.

Fonctionnalités:
- ðŸ“Š Dashboard: âge, prochains achats suggérés
- ðŸŽ¨ Activités du jour (adaptées 19 mois)
- ðŸ›’ Shopping Jules (vêtements taille actuelle, jouets recommandés)
- ðŸ’¡ Conseils (propreté, sommeil, alimentation) - IA
"""

# Import des fonctions pour exposer l'API publique
from .ai_service import JulesAIService
from .components import (
    render_achats_categorie,
    render_activites,
    render_conseils,
    render_dashboard,
    render_form_ajout_achat,
    render_shopping,
)
from .utils import (
    get_achats_jules_en_attente,
    get_activites_pour_age,
    get_age_jules,
    get_taille_vetements,
    st,
)


def app():
    """Point d'entrée du module Jules"""
    st.title("ðŸ‘¶ Jules")

    age = get_age_jules()
    st.caption(f"ðŸŽ‚ {age['mois']} mois • Né le {age['date_naissance'].strftime('%d/%m/%Y')}")

    # Tabs principaux
    tabs = st.tabs(["ðŸ“Š Dashboard", "ðŸŽ¨ Activités", "ðŸ›’ Shopping", "ðŸ’¡ Conseils"])

    with tabs[0]:
        render_dashboard()

    with tabs[1]:
        render_activites()

    with tabs[2]:
        render_shopping()

    with tabs[3]:
        render_conseils()


__all__ = [
    # Entry point
    "app",
    # AI Service
    "JulesAIService",
    # Helpers
    "get_age_jules",
    "get_activites_pour_age",
    "get_taille_vetements",
    "get_achats_jules_en_attente",
    # UI
    "render_dashboard",
    "render_activites",
    "render_shopping",
    "render_achats_categorie",
    "render_form_ajout_achat",
    "render_conseils",
]
