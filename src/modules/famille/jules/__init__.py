"""
Module Jules - ActivitÃes adaptÃees, achats suggÃerÃes, conseils dÃeveloppement.

FonctionnalitÃes:
- ðŸ“Š Dashboard: âge, prochains achats suggÃerÃes
- ðŸŽ¨ ActivitÃes du jour (adaptÃees 19 mois)
- ðŸ›’ Shopping Jules (vêtements taille actuelle, jouets recommandÃes)
- ðŸ’¡ Conseils (propretÃe, sommeil, alimentation) - IA
"""

from .utils import st

# Import des fonctions pour exposer l'API publique
from .ai_service import JulesAIService
from .utilitaires import (
    get_age_jules, get_activites_pour_age, get_taille_vetements,
    get_achats_jules_en_attente
)
from .components import (
    render_dashboard, render_activites, render_shopping,
    render_achats_categorie, render_form_ajout_achat, render_conseils
)


def app():
    """Point d'entrÃee du module Jules"""
    st.title("ðŸ‘¶ Jules")
    
    age = get_age_jules()
    st.caption(f"ðŸŽ‚ {age['mois']} mois â€¢ NÃe le {age['date_naissance'].strftime('%d/%m/%Y')}")
    
    # Tabs principaux
    tabs = st.tabs(["ðŸ“Š Dashboard", "ðŸŽ¨ ActivitÃes", "ðŸ›’ Shopping", "ðŸ’¡ Conseils"])
    
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
