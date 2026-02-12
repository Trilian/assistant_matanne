"""
Module Jules - Activités adaptées, achats suggérés, conseils développement.

Fonctionnalités:
- 📊 Dashboard: âge, prochains achats suggérés
- 🎨 Activités du jour (adaptées 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandés)
- 💡 Conseils (propreté, sommeil, alimentation) - IA
"""

from ._common import st

# Import des fonctions pour exposer l'API publique
from .ai_service import JulesAIService
from .helpers import (
    get_age_jules, get_activites_pour_age, get_taille_vetements,
    get_achats_jules_en_attente
)
from .components import (
    render_dashboard, render_activites, render_shopping,
    render_achats_categorie, render_form_ajout_achat, render_conseils
)


def app():
    """Point d'entrée du module Jules"""
    st.title("👶 Jules")
    
    age = get_age_jules()
    st.caption(f"🎂 {age['mois']} mois • Né le {age['date_naissance'].strftime('%d/%m/%Y')}")
    
    # Tabs principaux
    tabs = st.tabs(["📊 Dashboard", "🎨 Activités", "🛒 Shopping", "💡 Conseils"])
    
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
