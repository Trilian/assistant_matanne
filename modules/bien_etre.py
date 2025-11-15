# assistant_matanne/modules/bien_etre.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from core.database import get_connection
from core.helpers import log_function


@log_function
def app():
    st.header("Bien-être")
    st.subheader("Suivi du sommeil, humeur et activités personnelles (toi et Mathieu)")

    # Connexion DB
    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    try:

        # ============================================================
        # AJOUT NOUVELLE ENTRÉE
        # ============================================================
        with st.expander("➕ Ajouter une entrée de bien-être"):
            entry_date = st.date_input("Date", value=date.today())
            username = st.selectbox("Utilisateur", ["Anne", "Mathieu"])
            mood = st.selectbox("Humeur", ["😊 Bien", "😐 Moyen", "😞 Mal"])
            sleep_hours = st.number_input("Heures de sommeil", min_value=0.0, max_value=24.0, step=0.5)
            activity = st.text_input("Activité principale")
            notes = st.text_area("Notes")

            if st.button("Ajouter l'entrée"):
                try:
                    cursor.execute(
                        """
                        INSERT INTO wellbeing_entries (child_id, date, mood, sleep_hours, activity, notes, username)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (None, entry_date.isoformat(), mood, sleep_hours, activity.strip(), notes.strip(), username)
                    )
                    conn.commit()
                    st.success("Entrée ajoutée avec succès ! 🎉")
                    st.session_state["refresh"] = not st.session_state["refresh"]
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout : {e}")

        # ============================================================
        # CHARGEMENT DES DONNÉES
        # ============================================================
        try:
            df = pd.read_sql(
                """
                SELECT date, mood, sleep_hours, activity, notes, username
                FROM wellbeing_entries
                WHERE child_id IS NULL
                ORDER BY date DESC
                """,
                conn
            )
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {e}")
            return

        if df.empty:
            st.info("Aucune donnée de bien-être disponible pour l'instant.")
            return

        # ============================================================
        # AFFICHAGE TABLEAU
        # ============================================================
        st.subheader("📋 Historique bien-être")
        st.dataframe(df, use_container_width=True)

        # ============================================================
        # GRAPHIQUES PAR UTILISATEUR
        # ============================================================
        for user in df["username"].unique():
            user_df = df[df["username"] == user]

            st.markdown(f"---")
            st.subheader(f"💬 {user} — Humeur")

            try:
                mood_chart = alt.Chart(user_df).mark_circle(size=60).encode(
                    x=alt.X('date:T', title="Date"),
                    y=alt.Y('mood:N', title="Humeur"),
                    tooltip=['date', 'mood', 'sleep_hours', 'activity', 'notes']
                )
                st.altair_chart(mood_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur graphique humeur ({user}) : {e}")

            st.subheader(f"😴 {user} — Sommeil")
            try:
                sleep_chart = alt.Chart(user_df).mark_bar().encode(
                    x=alt.X('date:T', title="Date"),
                    y=alt.Y('sleep_hours:Q', title="Heures dormies"),
                    tooltip=['date', 'sleep_hours']
                )
                st.altair_chart(sleep_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur graphique sommeil ({user}) : {e}")

            st.subheader(f"🎯 {user} — Activités")
            try:
                # Activités : compter occurrence par jour
                activity_chart = alt.Chart(user_df).mark_bar().encode(
                    x=alt.X('date:T', title="Date"),
                    y=alt.Y('activity:N', title="Activité"),
                    tooltip=['date', 'activity']
                )
                st.altair_chart(activity_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur graphique activités ({user}) : {e}")

        # ============================================================
        # EXPORT CSV
        # ============================================================
        st.markdown("---")
        if st.button("📤 Exporter données bien-être"):
            st.download_button(
                "Télécharger CSV",
                df.to_csv(index=False),
                "bien_etre.csv",
                "text/csv"
            )

    finally:
        conn.close()
