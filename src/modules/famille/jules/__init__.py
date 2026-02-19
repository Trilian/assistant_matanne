"""
Module Jules - Activités adaptées, achats suggérés, conseils développement.

Fonctionnalités:
- 📊 Dashboard: âge, prochains achats suggérés
- 🎨 Activités du jour (adaptées 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandés)
- 💡 Conseils (propreté, sommeil, alimentation) - IA
"""

# Import des fonctions pour exposer l'API publique
from .ai_service import JulesAIService
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


def app():
    """Point d'entrée du module Jules"""
    st.title("👶 Jules")

    age = get_age_jules()
    st.caption(f"🎂 {age['mois']} mois • Né le {age['date_naissance'].strftime('%d/%m/%Y')}")

    # Tabs principaux
    tabs = st.tabs(["📊 Dashboard", "🎨 Activités", "🛒 Shopping", "💡 Conseils"])

    with tabs[0]:
        afficher_dashboard()

    with tabs[1]:
        afficher_activites()

    with tabs[2]:
        afficher_shopping()

    with tabs[3]:
        afficher_conseils()


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
    "afficher_dashboard",
    "afficher_activites",
    "afficher_shopping",
    "afficher_achats_categorie",
    "afficher_form_ajout_achat",
    "afficher_conseils",
]
