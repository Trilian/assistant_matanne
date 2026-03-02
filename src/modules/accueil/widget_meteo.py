"""
Widget météo du jour avec impact sur les activités planifiées.

Affiche la météo actuelle et croise les données avec les événements
planifiés pour signaler les impacts potentiels (pluie → sortie compromise, etc.).
"""

import logging
from datetime import date, timedelta

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)

_keys = KeyNamespace("meteo_dashboard")


# ═══════════════════════════════════════════════════════════
# LOGIQUE MÉTIER (pure)
# ═══════════════════════════════════════════════════════════


def _evaluer_impact_meteo(meteo, evenements: list[dict]) -> list[dict]:
    """Évalue l'impact de la météo sur les activités planifiées.

    Args:
        meteo: MeteoJour du jour.
        evenements: Liste d'événements planifiés (dicts avec 'titre', 'lieu', etc.).

    Returns:
        Liste de dicts {icone, message, niveau} décrivant les impacts.
    """
    impacts = []

    if not meteo or not evenements:
        return impacts

    # Pluie forte
    if meteo.probabilite_pluie > 60 or meteo.precipitation_mm > 5:
        activites_ext = [
            e
            for e in evenements
            if any(
                mot in (e.get("titre", "") + " " + e.get("lieu", "")).lower()
                for mot in [
                    "parc",
                    "jardin",
                    "promenade",
                    "piscine",
                    "pique",
                    "sortie",
                    "vélo",
                    "plage",
                    "balade",
                    "forêt",
                    "zoo",
                    "marché",
                    "plein air",
                    "extérieur",
                ]
            )
        ]
        for act in activites_ext:
            impacts.append(
                {
                    "icone": "🌧️",
                    "message": f"Pluie prévue ({meteo.probabilite_pluie}%) — "
                    f"'{act.get('titre', 'Activité')}' pourrait être compromise",
                    "niveau": "warning",
                }
            )

    # Froid
    if meteo.temperature_min < 5:
        impacts.append(
            {
                "icone": "🥶",
                "message": f"Températures basses ({meteo.temperature_min:.0f}°C min) — "
                "pensez à couvrir Jules chaudement",
                "niveau": "info",
            }
        )

    # Canicule
    if meteo.temperature_max > 32:
        impacts.append(
            {
                "icone": "🥵",
                "message": f"Fortes chaleurs ({meteo.temperature_max:.0f}°C) — "
                "prévoyez eau et crème solaire",
                "niveau": "warning",
            }
        )

    # Vent fort
    if meteo.vent_km_h > 40:
        impacts.append(
            {
                "icone": "💨",
                "message": f"Vent fort ({meteo.vent_km_h:.0f} km/h) — "
                "évitez les activités extérieures exposées",
                "niveau": "info",
            }
        )

    # UV élevé
    if meteo.uv_index >= 8:
        impacts.append(
            {
                "icone": "☀️",
                "message": f"UV très élevé (index {meteo.uv_index}) — crème solaire indispensable",
                "niveau": "warning",
            }
        )

    # Beau temps encourageant
    if (
        meteo.temperature_max >= 18
        and meteo.probabilite_pluie < 20
        and meteo.vent_km_h < 25
        and not impacts
    ):
        impacts.append(
            {
                "icone": "🌞",
                "message": "Conditions idéales pour une sortie en famille !",
                "niveau": "success",
            }
        )

    return impacts


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=1800)  # Cache 30 min
def afficher_widget_meteo():
    """Widget météo du jour avec impacts sur les activités."""
    try:
        from src.services.integrations.weather import obtenir_service_meteo

        service = obtenir_service_meteo()
        previsions = service.get_previsions(nb_jours=2)

        if not previsions:
            st.info("🌤️ Données météo indisponibles")
            return

        meteo_jour = previsions[0]  # Aujourd'hui
        meteo_demain = previsions[1] if len(previsions) > 1 else None
    except Exception as e:
        logger.debug(f"Service météo indisponible: {e}")
        st.info("🌤️ Données météo indisponibles")
        return

    # Charger les événements du jour pour évaluer l'impact
    evenements = _charger_evenements_aujourdhui()
    impacts = _evaluer_impact_meteo(meteo_jour, evenements)

    # ── Carte météo principale (full-width, sans sub-colonnes) ──
    icone = meteo_jour.icone or "🌤️"
    condition = echapper_html(meteo_jour.condition or "Données en cours")
    t_max = f"{meteo_jour.temperature_max:.0f}"
    t_min = f"{meteo_jour.temperature_min:.0f}"
    pluie = f"{meteo_jour.probabilite_pluie}"
    vent = f"{meteo_jour.vent_km_h:.0f}"
    uv = f"{meteo_jour.uv_index}"

    lever_coucher = ""
    if meteo_jour.lever_soleil and meteo_jour.coucher_soleil:
        lever_coucher = (
            f'<div style="background:#f1f5f9;padding:4px 10px;border-radius:6px;'
            f'white-space:nowrap;">🌅 {meteo_jour.lever_soleil[:5]}–{meteo_jour.coucher_soleil[:5]}</div>'
        )

    StyleSheet.inject()
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{Couleur.BG_METEO_START},{Couleur.BG_METEO_END});'
        f'border-radius:{Rayon.XL};padding:{Espacement.LG};margin-bottom:{Espacement.MD};">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
        f'<span style="font-size:2.5rem;line-height:1;">{icone}</span>'
        f"<div>"
        f'<div style="font-size:1.9rem;font-weight:700;line-height:1;">{t_max}°C</div>'
        f'<div style="font-size:0.85rem;color:{Sem.ON_SURFACE_SECONDARY};">{t_min}° / {t_max}° — {condition}</div>'
        f"</div>"
        f"</div>"
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;font-size:0.82rem;">'
        f'<div style="background:#f1f5f9;padding:4px 10px;border-radius:6px;white-space:nowrap;">💧 Pluie {pluie}%</div>'
        f'<div style="background:#f1f5f9;padding:4px 10px;border-radius:6px;white-space:nowrap;">💨 Vent {vent} km/h</div>'
        f'<div style="background:#f1f5f9;padding:4px 10px;border-radius:6px;white-space:nowrap;">☀️ UV {uv}</div>'
        f"{lever_coucher}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Impacts sur les activités (compacts)
    if impacts:
        for impact in impacts:
            if impact["niveau"] == "warning":
                st.warning(f"{impact['icone']} {impact['message']}")
            elif impact["niveau"] == "success":
                st.success(f"{impact['icone']} {impact['message']}")
            else:
                st.info(f"{impact['icone']} {impact['message']}")

    # Aperçu demain (compact)
    if meteo_demain:
        icone_demain = meteo_demain.icone or "🌤️"
        st.caption(
            f"**Demain:** {icone_demain} {meteo_demain.temperature_min:.0f}°/"
            f"{meteo_demain.temperature_max:.0f}°C — {meteo_demain.condition}"
        )


def _charger_evenements_aujourdhui() -> list[dict]:
    """Charge les événements planifiés pour aujourd'hui."""
    evenements = []

    # Événements du planning
    try:
        from src.modules.planning.timeline_ui import charger_events_periode

        aujourdhui = date.today()
        events = charger_events_periode(aujourdhui, aujourdhui + timedelta(days=1))
        if events:
            evenements.extend(events)
    except Exception:
        pass

    # Activités famille planifiées
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ActiviteFamille

        aujourdhui = date.today()
        with obtenir_contexte_db() as session:
            activites = (
                session.query(ActiviteFamille)
                .filter(ActiviteFamille.date_activite == aujourdhui)
                .all()
            )
            for act in activites:
                evenements.append(
                    {
                        "titre": act.nom or act.type_activite or "Activité",
                        "lieu": getattr(act, "lieu", "") or "",
                    }
                )
    except Exception:
        pass

    return evenements


__all__ = ["afficher_widget_meteo"]
