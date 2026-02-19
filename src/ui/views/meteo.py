"""
Interface UI pour les alertes météo jardin.

Note: Ce fichier a été extrait depuis src/services/weather/service.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.integrations.weather.service import (
    NiveauAlerte,
    get_weather_garden_service,
)


def afficher_meteo_jardin():  # pragma: no cover
    """Interface Streamlit pour les alertes météo jardin."""
    st.subheader("🌤️ Météo & Jardin")

    service = get_weather_garden_service()

    # Configuration localisation
    with st.expander("📝 Configurer la localisation"):
        city = st.text_input(
            "Ville", value="Paris", key="weather_city", help="Entrez le nom de votre ville"
        )

        if st.button("🔍 Localiser", key="locate_btn"):
            if service.set_location_from_city(city):
                st.success(f"✅ Localisation mise à jour: {city}")
            else:
                st.error("Ville non trouvée")

    # Récupérer les prévisions
    previsions = service.get_previsions(7)

    if not previsions:
        st.error("❌ Impossible de récupérer les données météo")
        return

    # Alertes en premier
    alertes = service.generer_alertes(previsions)

    if alertes:
        st.markdown("### ⚠️ Alertes")
        for alerte in alertes:
            if alerte.niveau == NiveauAlerte.DANGER:
                st.error(f"**{alerte.titre}** - {alerte.message}")
            elif alerte.niveau == NiveauAlerte.ATTENTION:
                st.warning(f"**{alerte.titre}** - {alerte.message}")
            else:
                st.info(f"**{alerte.titre}** - {alerte.message}")

            st.caption(f"💡 {alerte.conseil_jardin}")

    st.markdown("---")

    # Prévisions 7 jours
    st.markdown("### 📅 Prévisions 7 jours")

    cols = st.columns(min(7, len(previsions)))

    for i, prev in enumerate(previsions[:7]):
        with cols[i]:
            jour_nom = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][prev.date.weekday()]

            st.markdown(f"**{jour_nom}**")
            st.markdown(f"### {prev.icone}")
            st.metric(
                label=prev.date.strftime("%d/%m"),
                value=f"{prev.temperature_max:.0f}°",
                delta=f"{prev.temperature_min:.0f}°",
            )

            if prev.precipitation_mm > 0:
                st.caption(f"🌧️ {prev.precipitation_mm}mm")
            if prev.vent_km_h > 30:
                st.caption(f"💨 {prev.vent_km_h:.0f}km/h")

    st.markdown("---")

    # Tabs pour détails
    tab1, tab2, tab3 = st.tabs(["💡 Conseils", "💧 Arrosage", "📊 Détails"])

    with tab1:
        conseils = service.generer_conseils(previsions[:3])

        if conseils:
            for conseil in conseils:
                priorite_badge = (
                    "🔴" if conseil.priorite == 1 else "🟡" if conseil.priorite == 2 else "🟢"
                )

                st.markdown(f"#### {conseil.icone} {conseil.titre} {priorite_badge}")
                st.write(conseil.description)

                if conseil.action_recommandee:
                    st.info(f"👉 {conseil.action_recommandee}")

                if conseil.plantes_concernees:
                    st.caption(f"🌱 Plantes concernées: {', '.join(conseil.plantes_concernees)}")

                st.markdown("---")
        else:
            st.info("Pas de conseil particulier pour aujourd'hui")

    with tab2:
        st.markdown("### 💧 Plan d'arrosage intelligent")

        surface = st.slider(
            "Surface du jardin (m²)",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            key="garden_surface",
        )

        plan = service.generer_plan_arrosage(7, surface)

        if plan:
            for jour in plan:
                jour_nom = [
                    "Lundi",
                    "Mardi",
                    "Mercredi",
                    "Jeudi",
                    "Vendredi",
                    "Samedi",
                    "Dimanche",
                ][jour.date.weekday()]

                col1, col2, col3 = st.columns([2, 1, 3])

                with col1:
                    st.write(f"**{jour_nom}** {jour.date.strftime('%d/%m')}")

                with col2:
                    if jour.besoin_arrosage:
                        st.markdown("💧 **Oui**")
                    else:
                        st.markdown("✅ Non")

                with col3:
                    st.caption(jour.raison)
                    if jour.quantite_recommandee_litres > 0:
                        st.caption(f"≈ {jour.quantite_recommandee_litres:.0f}L recommandés")
                    if jour.plantes_prioritaires:
                        st.caption(f"Priorité: {', '.join(jour.plantes_prioritaires)}")

    with tab3:
        st.markdown("### 📊 Détails météo")

        import pandas as pd

        data = []
        for prev in previsions:
            data.append(
                {
                    "Date": prev.date.strftime("%d/%m"),
                    "Condition": prev.condition,
                    "T° Min": f"{prev.temperature_min}°C",
                    "T° Max": f"{prev.temperature_max}°C",
                    "Pluie": f"{prev.precipitation_mm}mm",
                    "Prob. Pluie": f"{prev.probabilite_pluie}%",
                    "Vent": f"{prev.vent_km_h}km/h",
                    "UV": prev.uv_index,
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)


__all__ = [
    "afficher_meteo_jardin",
]
