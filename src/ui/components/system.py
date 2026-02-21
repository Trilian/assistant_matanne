"""
Widgets de santé système et activité.

Fournit des composants pour:
- Indicateurs de santé (DB, cache, API)
- Timeline d'activité récente
"""

import logging
from datetime import datetime

import streamlit as st

from src.ui.primitives.box import Box
from src.ui.primitives.text import Text
from src.ui.registry import composant_ui
from src.ui.tokens import Couleur, Espacement, Rayon, Typographie
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)


def indicateur_sante_systeme() -> dict:
    """
    Calcule les indicateurs de santé du système.

    Returns:
        Dict avec status et détails
    """
    status = {"global": "ok", "details": []}

    try:
        # Vérifier la connexion DB
        from src.core.db import verifier_connexion

        if verifier_connexion():
            status["details"].append(
                {"nom": "Base de données", "status": "ok", "message": "Connectée"}
            )
        else:
            status["details"].append(
                {"nom": "Base de données", "status": "error", "message": "Déconnectée"}
            )
            status["global"] = "error"
    except Exception as e:
        status["details"].append({"nom": "Base de données", "status": "error", "message": str(e)})
        status["global"] = "error"

    try:
        # Vérifier le cache
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache_stats = cache.obtenir_statistiques()
        hit_rate = float(cache_stats.get("hit_rate", "0%").replace("%", ""))

        if hit_rate >= 70:
            status["details"].append(
                {"nom": "Cache", "status": "ok", "message": f"Hit rate: {hit_rate:.0f}%"}
            )
        elif hit_rate >= 40:
            status["details"].append(
                {"nom": "Cache", "status": "warning", "message": f"Hit rate: {hit_rate:.0f}%"}
            )
            if status["global"] == "ok":
                status["global"] = "warning"
        else:
            status["details"].append(
                {"nom": "Cache", "status": "warning", "message": f"Hit rate bas: {hit_rate:.0f}%"}
            )
    except Exception:
        status["details"].append({"nom": "Cache", "status": "ok", "message": "Initialisé"})

    return status


@composant_ui("system", exemple="afficher_sante_systeme()", tags=["health", "monitoring"])
def afficher_sante_systeme():
    """Affiche les indicateurs de santé."""

    status = indicateur_sante_systeme()

    # Icône global
    icon_map = {"ok": "🟢", "warning": "🟡", "error": "🔴"}
    global_icon = icon_map.get(status["global"], "⚪")

    with st.expander(f"{global_icon} Santé Système", expanded=False):
        for detail in status["details"]:
            icon = icon_map.get(detail["status"], "⚪")
            st.write(f"{icon} **{detail['nom']}**: {detail['message']}")


@composant_ui(
    "system", exemple="afficher_timeline_systeme(activites)", tags=["timeline", "activity"]
)
def afficher_timeline_systeme(activites: list[dict], max_items: int = 5):
    """
    Affiche une timeline des activités système récentes.

    Args:
        activites: Liste {'date': datetime, 'action': str, 'type': str}
        max_items: Nombre max d'items à afficher
    """
    if not activites:
        st.info("Aucune activité récente")
        return

    # Icônes par type
    icones = {
        "recette": "🍽️",
        "inventaire": "📦",
        "courses": "🛒",
        "planning": "📅",
        "famille": "👨‍👩‍👦",
        "maison": "🏠",
    }

    st.markdown("### 📋 Activité Récente")

    for activite in activites[:max_items]:
        icone = icones.get(activite.get("type", ""), "📜")
        date_str = activite.get("date", "")
        if isinstance(date_str, datetime):
            date_str = date_str.strftime("%d/%m %H:%M")

        action = activite.get("action", "Action")

        # Box pour le conteneur flex de chaque item timeline
        item = Box(
            display="flex",
            align="center",
            p=Espacement.SM,
            my="0.3rem",
            bg=Couleur.BG_SUBTLE,
            radius=Rayon.MD,
        )
        item.child(
            f'<span style="margin-right: 0.8rem; font-size: {Typographie.ICON_SM};">{echapper_html(icone)}</span>'
        )
        item.child(
            f"<div>"
            f"{Text(action, weight='medium').html()}<br>"
            f"{Text(str(date_str), size='xs', color=Couleur.TEXT_SECONDARY, tag='small').html()}"
            f"</div>"
        )
        item.show()


# Alias rétrocompatibilité
afficher_timeline_activites = afficher_timeline_systeme
