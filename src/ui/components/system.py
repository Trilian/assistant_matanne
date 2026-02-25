"""
Widgets de santé système et activité.

Fournit des composants pour:
- Indicateurs de santé (DB, cache, IA, métriques) via SanteSysteme
- Timeline d'activité récente
"""

import logging
from datetime import datetime

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.registry import composant_ui
from src.ui.tokens import Espacement, Rayon, Typographie
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)


@composant_ui("system", exemple="indicateur_sante_systeme()", tags=("health", "monitoring", "pure"))
@st.cache_data(ttl=30, show_spinner=False)
def indicateur_sante_systeme() -> dict:
    """
    Calcule les indicateurs de santé du système via SanteSysteme.

    Utilise verifier_sante_globale() comme source de vérité unique
    (DB, cache, IA, métriques, + checks enregistrés).
    Caché 30s pour éviter les checks répétitifs.

    Returns:
        Dict avec status global et détails par composant
    """
    try:
        from src.core.monitoring.health import StatutSante, verifier_sante_globale

        rapport = verifier_sante_globale(inclure_db=True)

        _status_map = {
            StatutSante.SAIN: "ok",
            StatutSante.DEGRADE: "warning",
            StatutSante.CRITIQUE: "error",
            StatutSante.INCONNU: "warning",
        }

        # Noms lisibles pour l'UI
        _noms_fr = {
            "database": "Base de données",
            "cache": "Cache",
            "ia": "Intelligence Artificielle",
            "metriques": "Métriques",
        }

        details = []
        for nom, composant in rapport.composants.items():
            details.append(
                {
                    "nom": _noms_fr.get(nom, nom.capitalize()),
                    "status": _status_map.get(composant.statut, "warning"),
                    "message": composant.message or composant.statut.name,
                    "duree_ms": round(composant.duree_verification_ms, 1),
                }
            )

        # Statut global
        if rapport.sain:
            has_degraded = any(c.statut == StatutSante.DEGRADE for c in rapport.composants.values())
            global_status = "warning" if has_degraded else "ok"
        else:
            global_status = "error"

        return {"global": global_status, "details": details}

    except Exception as e:
        logger.warning(f"Health check indisponible: {e}")
        return {
            "global": "warning",
            "details": [{"nom": "Système", "status": "warning", "message": str(e)}],
        }


@composant_ui("system", exemple="afficher_sante_systeme()", tags=["health", "monitoring"])
def afficher_sante_systeme():
    """Affiche les indicateurs de santé via SanteSysteme."""

    status = indicateur_sante_systeme()

    # Icône global
    icon_map = {"ok": "🟢", "warning": "🟡", "error": "🔴"}
    global_icon = icon_map.get(status["global"], "⚪")

    with st.expander(f"{global_icon} Santé Système", expanded=False):
        for detail in status["details"]:
            icon = icon_map.get(detail["status"], "⚪")
            duree = f" ({detail['duree_ms']}ms)" if detail.get("duree_ms") else ""
            st.write(f"{icon} **{detail['nom']}**: {detail['message']}{duree}")


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

        item_cls = StyleSheet.create_class(
            {
                "display": "flex",
                "align-items": "center",
                "padding": Espacement.SM,
                "margin": "0.3rem 0",
                "background": Sem.SURFACE_ALT,
                "border-radius": Rayon.MD,
            }
        )

        safe_action = echapper_html(action)
        safe_date = echapper_html(str(date_str))
        safe_icone = echapper_html(icone)

        StyleSheet.inject()
        st.markdown(
            f'<div class="{item_cls}">'
            f'<span style="margin-right: 0.8rem; font-size: {Typographie.ICON_SM};">{safe_icone}</span>'
            f"<div>"
            f'<span style="font-weight: 500;">{safe_action}</span><br>'
            f'<small style="font-size: 0.75rem; color: {Sem.ON_SURFACE_SECONDARY};">{safe_date}</small>'
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# Alias rétrocompatibilité
afficher_timeline_activites = afficher_timeline_systeme
