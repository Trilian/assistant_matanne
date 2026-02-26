"""
Module Météo Locale — Widget météo pour la famille.

Affiche la météo actuelle et les prévisions 7 jours via Open-Meteo
(API gratuite, pas de clé nécessaire). Inclut des suggestions
d'activités familiales adaptées au temps.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.meteo_service import MeteoService, get_meteo_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("meteo")


@profiler_rerun("meteo")
def app():
    """Point d'entrée module Météo."""
    st.title("🌤️ Météo Locale")
    st.caption("Prévisions et suggestions d'activités familiales")

    with error_boundary(titre="Erreur météo"):
        service = get_meteo_service()

        # Configuration ville
        with st.expander("📍 Localisation", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input(
                    "Latitude",
                    value=48.8566,
                    format="%.4f",
                    key=_keys("lat"),
                )
            with col2:
                lon = st.number_input(
                    "Longitude",
                    value=2.3522,
                    format="%.4f",
                    key=_keys("lon"),
                )
            st.caption("💡 Par défaut: Paris. Changez les coordonnées pour votre ville.")

        # Récupérer les données (avec coordonnées personnalisées)
        service_custom = MeteoService(lat=lat, lon=lon)
        meteo = service_custom.obtenir_meteo()

        if not meteo:
            st.warning("⚠️ Impossible de récupérer les données météo. Vérifiez votre connexion.")
            return

        # Météo actuelle
        actuelle = meteo.actuelle
        st.subheader(f"{actuelle.emoji} Actuellement")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ Température", f"{actuelle.temperature}°C")
        with col2:
            st.metric("🌡️ Ressenti", f"{actuelle.temperature_ressentie}°C")
        with col3:
            st.metric("💧 Humidité", f"{actuelle.humidite}%")
        with col4:
            st.metric("💨 Vent", f"{actuelle.vent_kmh} km/h")

        st.info(f"{actuelle.emoji} {actuelle.description}")

        st.divider()

        # Prévisions 7 jours
        st.subheader("📅 Prévisions 7 jours")

        if meteo.previsions:
            cols = st.columns(min(7, len(meteo.previsions)))
            for i, prev in enumerate(meteo.previsions[:7]):
                with cols[i]:
                    # prev.date est une chaîne "YYYY-MM-DD"
                    from datetime import datetime as dt

                    try:
                        jour_dt = dt.strptime(prev.date, "%Y-%m-%d")
                        jour_nom = jour_dt.strftime("%a %d")
                    except (ValueError, TypeError):
                        jour_nom = prev.date
                    st.markdown(f"**{jour_nom}**")
                    st.markdown(f"### {prev.emoji}")
                    st.caption(f"🔺 {prev.temp_max}°C")
                    st.caption(f"🔻 {prev.temp_min}°C")
                    if prev.precip_mm > 0:
                        st.caption(f"🌧️ {prev.precip_mm}mm")

        st.divider()

        # Suggestions familiales
        if meteo.suggestions:
            st.subheader("💡 Suggestions pour la famille")
            for suggestion in meteo.suggestions:
                st.markdown(f"- {suggestion}")
