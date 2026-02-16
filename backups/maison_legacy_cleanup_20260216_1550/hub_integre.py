"""
Hub Maison Intégré - Centre de contrôle complet.

Assemble les composants UI pour :
- Plan interactif maison (multi-étages)
- Plan jardin avec zones
- Chronomètre entretien
- Dashboard temps passé
- Gestion statuts objets x courses x budget

Architecture:
┌──────────────────────────────────────────────────────────────┐
│                    🏠 HUB MAISON                              │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Plan     │ Jardin   │ Chrono   │ Temps    │ Objets          │
│ Maison   │ Zones    │ Entretien│ Dashboard│ à remplacer     │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
"""

import streamlit as st

from src.core.database import obtenir_contexte_db

# Import des tabs (extraits dans tabs/)
from src.modules.maison.tabs import (
    tab_chrono,
    tab_jardin,
    tab_objets,
    tab_plan_maison,
    tab_temps,
)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TABS_CONFIG = [
    ("🏠", "Plan Maison", "plan_maison"),
    ("🌳", "Jardin", "jardin"),
    ("⏱️", "Chronomètre", "chrono"),
    ("📊", "Temps", "temps"),
    ("🔧", "Objets", "objets"),
]

CSS_STYLES = """
<style>
.hub-header {
    background: linear-gradient(135deg, #2d3436 0%, #636e72 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hub-header h1 {
    margin: 0;
    font-size: 1.8rem;
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #3498db;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2c3e50;
}
.metric-label {
    font-size: 0.85rem;
    color: #7f8c8d;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# COMPOSANT: EN-TÊTE
# ═══════════════════════════════════════════════════════════


def render_header():
    """Affiche l'en-tête avec métriques rapides."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    metriques = _obtenir_metriques_rapides()

    st.markdown(
        """
        <div class="hub-header">
            <h1>🏠 Centre de Contrôle Maison</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔧 Objets à changer",
            metriques.get("objets_a_changer", 0),
            help="Objets marqués 'à changer' ou 'à acheter'",
        )

    with col2:
        st.metric(
            "⏱️ Temps ce mois",
            f"{metriques.get('temps_mois_heures', 0):.1f}h",
            help="Temps d'entretien ce mois",
        )

    with col3:
        st.metric(
            "🌱 Plantes",
            metriques.get("nb_plantes", 0),
            help="Nombre de plantes suivies",
        )

    with col4:
        st.metric(
            "💰 Budget travaux",
            f"{metriques.get('budget_travaux', 0):,.0f}€",
            help="Coûts travaux ce mois",
        )


def _obtenir_metriques_rapides() -> dict[str, int | float]:
    """Récupère les métriques pour le header."""
    from datetime import date

    metriques: dict[str, int | float] = {
        "objets_a_changer": 0,
        "temps_mois_heures": 0.0,
        "nb_plantes": 0,
        "budget_travaux": 0.0,
    }

    try:
        from sqlalchemy import extract, func

        from src.core.models import CoutTravaux, ObjetMaison, PlanteJardin, SessionTravail

        today = date.today()

        with obtenir_contexte_db() as db:
            metriques["objets_a_changer"] = (
                db.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_acheter", "a_reparer"]))
                .count()
            )

            temps_total = (
                db.query(func.sum(SessionTravail.duree_minutes))
                .filter(
                    extract("month", SessionTravail.debut) == today.month,
                    extract("year", SessionTravail.debut) == today.year,
                    SessionTravail.fin.isnot(None),
                )
                .scalar()
            )
            metriques["temps_mois_heures"] = (temps_total or 0) / 60

            metriques["nb_plantes"] = db.query(PlanteJardin).count()

            budget = (
                db.query(func.sum(CoutTravaux.montant))
                .filter(
                    extract("month", CoutTravaux.created_at) == today.month,
                    extract("year", CoutTravaux.created_at) == today.year,
                )
                .scalar()
            )
            metriques["budget_travaux"] = float(budget or 0)

    except Exception:
        pass

    return metriques


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Hub Maison Intégré."""
    render_header()

    tab_icons = [t[0] for t in TABS_CONFIG]
    tab_names = [t[1] for t in TABS_CONFIG]

    tabs = st.tabs([f"{icon} {name}" for icon, name in zip(tab_icons, tab_names, strict=False)])

    with tabs[0]:
        tab_plan_maison()

    with tabs[1]:
        tab_jardin()

    with tabs[2]:
        tab_chrono()

    with tabs[3]:
        tab_temps()

    with tabs[4]:
        tab_objets()


if __name__ == "__main__":
    app()
