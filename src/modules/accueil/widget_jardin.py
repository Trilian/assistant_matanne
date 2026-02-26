"""
Mini-widget jardin pour le dashboard.

Affiche un aperçu compact du jardin:
- Prochains arrosages nécessaires (basé météo)
- Alertes plantes (gel, canicule)
- Prochaines actions jardin
"""

import logging

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("jardin_dashboard")


def _obtenir_donnees_jardin() -> dict:
    """Collecte les données jardin depuis les services existants.

    Returns:
        Dict avec alertes, conseils, arrosage.
    """
    donnees = {
        "alertes_meteo": [],
        "conseils": [],
        "zones": 0,
        "plantes_attention": 0,
    }

    # Alertes météo jardin
    try:
        from src.services.integrations.weather import obtenir_service_meteo

        service = obtenir_service_meteo()
        previsions = service.get_previsions(nb_jours=3)

        if previsions:
            # Vérifier gel
            for p in previsions:
                if p.temperature_min < 2:
                    donnees["alertes_meteo"].append(
                        {
                            "type": "gel",
                            "icone": "🥶",
                            "message": f"Gel prévu {p.date.strftime('%d/%m')} ({p.temperature_min:.0f}°C)",
                        }
                    )
                if p.temperature_max > 35:
                    donnees["alertes_meteo"].append(
                        {
                            "type": "canicule",
                            "icone": "🥵",
                            "message": f"Canicule {p.date.strftime('%d/%m')} ({p.temperature_max:.0f}°C)",
                        }
                    )

            # Conseils arrosage
            try:
                conseils = service.generer_conseils(previsions)
                if conseils:
                    donnees["conseils"] = [
                        {"icone": c.icone, "titre": c.titre, "description": c.description}
                        for c in conseils[:3]
                    ]
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"Météo jardin indisponible: {e}")

    # Zones jardin en DB
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ZoneJardin

        with obtenir_contexte_db() as session:
            donnees["zones"] = session.query(ZoneJardin).count()
    except Exception:
        pass

    return donnees


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=1800)  # Cache 30 min
def afficher_widget_jardin():
    """Affiche le mini-widget jardin."""
    donnees = _obtenir_donnees_jardin()

    # Ne pas afficher si pas de jardin configuré et pas d'alertes
    if not donnees["zones"] and not donnees["alertes_meteo"] and not donnees["conseils"]:
        return

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #E8F5E9, #C8E6C9)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": "4px solid #4CAF50",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    st.markdown("### 🌱 Jardin")

    # Alertes météo (prioritaire)
    if donnees["alertes_meteo"]:
        for alerte in donnees["alertes_meteo"][:2]:
            st.warning(f"{alerte['icone']} {alerte['message']}")

    # Conseils jardin
    if donnees["conseils"]:
        for conseil in donnees["conseils"][:2]:
            st.markdown(f"{conseil['icone']} **{conseil['titre']}**")
            st.caption(conseil["description"])

    # Nombre de zones
    if donnees["zones"]:
        st.caption(f"🌿 {donnees['zones']} zone(s) de jardin suivie(s)")

    # Navigation
    if st.button("🌻 Voir le jardin", key=_keys("nav_jardin")):
        from src.core.state import naviguer

        naviguer("maison.jardin")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_widget_jardin"]
