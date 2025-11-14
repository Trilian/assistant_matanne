# assistant_matanne/modules/bien_etre.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("Bien-être")
    st.subheader("Suivi du sommeil, humeur et activités personnelles (toi et Mathieu)")

    # Création des tables si nécessaire
    create_all_tables()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # -------------------------
        # Formulaire pour ajouter une entrée
        # -------------------------
        with st.expander("Ajouter une nouvelle entrée de bien-être"):
            entry_date = st.date_input("Date", value=date.today())
            username = st.selectbox("Utilisateur", ["Anne", "Mathieu"])
            mood = st.selectbox("Humeur", ["😊 Bien", "😐 Moyen", "😞 Mal"])
            sleep_hours = st.number_input("Heures de sommeil", min_value=0.0, max_value=24.0, step=0.5)
            activity = st.text_input("Activité principale")
            notes = st.text_area("Notes")
            if st.button("Ajouter l'entrée"):
                cursor.execute(
                    """INSERT INTO wellbeing_entries (child_id, date, mood, sleep_hours, activity, notes, username)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (None, entry_date.isoformat(), mood, sleep_hours, activity, notes, username)
                )
                conn.commit()
                st.success("Entrée ajoutée avec succès ✅")

        # -------------------------
        # Récupération des données adultes
        # -------------------------
        df = pd.read_sql(
            """SELECT date, mood, sleep_hours, activity, notes, username
               FROM wellbeing_entries
               WHERE child_id IS NULL""", conn
        )

        if df.empty:
            st.info("Aucune donnée de bien-être disponible pour les adultes")
            return

        # Affichage tableau
        st.dataframe(df[['username','date','mood','sleep_hours','activity','notes']])

        # Graphiques par utilisateur
        for user in df['username'].unique():
            user_df = df[df['username']==user]

            st.subheader(f"{user} : Humeur")
            mood_chart = alt.Chart(user_df).mark_circle(size=60).encode(
                x='date:T',
                y='mood:N',
                tooltip=['date','mood','sleep_hours','activity','notes']
            )
            st.altair_chart(mood_chart, use_container_width=True)

            st.subheader(f"{user} : Sommeil")
            sleep_chart = alt.Chart(user_df).mark_bar().encode(
                x='date:T',
                y='sleep_hours:Q',
                tooltip=['date','sleep_hours']
            )
            st.altair_chart(sleep_chart, use_container_width=True)

            st.subheader(f"{user} : Activités")
            activity_chart = alt.Chart(user_df).mark_bar().encode(
                x='date:T',
                y='activity:N',
                tooltip=['date','activity']
            )
            st.altair_chart(activity_chart, use_container_width=True)

        # Export CSV
        if st.button("Exporter données bien-être"):
            st.download_button("Télécharger CSV", df.to_csv(index=False), "bien_etre.csv", "text/csv")

    finally:
        conn.close()