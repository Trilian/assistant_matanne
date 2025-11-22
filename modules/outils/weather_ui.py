import streamlit as st
from core.services.weather_service import get_weather
from core.helpers import log_event, log_function
import pandas as pd
import altair as alt
import io

@log_function
def app():
    st.header("🌤️ Météo – Prévisions locales")

    ville = st.text_input("Entrez votre ville", value="Clermont-Ferrand")

    if st.button("🔍 Obtenir la météo"):
        try:
            data = get_weather(ville)
        except Exception as e:
            st.error(f"Erreur lors de la récupération météo : {e}")
            log_event(f"Erreur météo : {e}", level="error")
            return

        if not data:
            st.warning("Aucune donnée météo disponible.")
            return

        # --- Données principales avec valeurs par défaut ---
        current_temp = data.get("current_temp", "N/A")
        condition = data.get("condition", "Inconnue")
        humidity = data.get("humidity", "N/A")

        st.metric("Température actuelle", f"{current_temp} °C")
        st.metric("Condition", condition)
        st.metric("Humidité", f"{humidity} %")

        # --- Alertes météo ---
        alerts = []
        try:
            temp_val = float(current_temp)
            if temp_val > 30:
                alerts.append("☀️ Canicule : pensez à vous hydrater.")
            elif temp_val < 0:
                alerts.append("❄️ Risque de gel : protégez vos plantes.")
        except ValueError:
            pass

        if isinstance(condition, str) and "rain" in condition.lower():
            alerts.append("🌧 Pluie prévue.")

        if alerts:
            st.warning("\n".join(alerts))
        else:
            st.info("Aucune alerte particulière.")

        # --- Prévisions ---
        forecast = data.get("forecast", [])
        if forecast and isinstance(forecast, list):
            df = pd.DataFrame(forecast)

            # Vérification et nettoyage du DataFrame
            df.columns = [c.lower() for c in df.columns]
            required_cols = [col for col in ["date", "temp"] if col in df.columns]

            if not required_cols:
                st.warning("Les prévisions météo sont incomplètes (colonnes manquantes).")
                st.write("Colonnes disponibles :", list(df.columns))
                return

            # Convertir la date
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            st.write("### 📈 Évolution des températures")
            try:
                tooltip_cols = [col for col in ["date", "temp", "condition"] if col in df.columns]

                chart = alt.Chart(df).mark_line(point=True).encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("temp:Q", title="Température (°C)"),
                    tooltip=tooltip_cols
                )
                st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Graphique non disponible : {e}")

            # --- Détails table ---
            st.write("### Détails des prévisions")
            st.dataframe(df.head(), use_container_width=True)

            # --- Export CSV ---
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Exporter les prévisions CSV",
                data=csv_buffer.getvalue(),
                file_name=f"meteo_{ville.lower()}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune prévision disponible pour les prochains jours.")