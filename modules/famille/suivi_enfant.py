# assistant_matanne/modules/suivi_enfant.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("Suivi de Jules 👶")
    st.subheader("Humeur, sommeil et développement au fil du temps")

    # --- S'assurer que la base est prête ---
    create_all_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # --- Identifier Jules dans la table child_profiles ---
    cursor.execute("SELECT id FROM child_profiles WHERE name = ?", ("Jules",))
    result = cursor.fetchone()
    if result:
        jules_id = result[0]
    else:
        cursor.execute(
            "INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)",
            ("Jules", "2024-06-22"),
        )
        conn.commit()
        jules_id = cursor.lastrowid

    # --------------------------
    # Formulaire d’ajout d’entrée
    # --------------------------
    with st.expander("Ajouter une nouvelle entrée pour Jules"):
        entry_date = st.date_input("Date", value=date.today())
        mood = st.selectbox("Humeur", ["😊 Bien", "😐 Moyen", "😞 Mal"])
        sleep_hours = st.number_input("Heures de sommeil", min_value=0.0, max_value=24.0, step=0.5)
        activity = st.text_input("Activité du jour (ex : crèche, promenade, motricité, etc.)")
        notes = st.text_area("Notes complémentaires (repas, santé, comportements...)")

        if st.button("Ajouter l'entrée de suivi"):
            cursor.execute(
                """INSERT INTO wellbeing_entries (child_id, date, mood, sleep_hours, activity, notes, username)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (jules_id, entry_date.isoformat(), mood, sleep_hours, activity, notes, "Jules"),
            )
            conn.commit()
            st.success("Entrée ajoutée pour Jules ✅")

    # --------------------------
    # Chargement des données existantes
    # --------------------------
    df = pd.read_sql(
        """SELECT date, mood, sleep_hours, activity, notes
           FROM wellbeing_entries
           WHERE child_id = ?""",
        conn,
        params=(jules_id,),
    )

    if df.empty:
        st.info("Aucune donnée de suivi enregistrée pour Jules.")
        return

    # --------------------------
    # Tableau et graphiques
    # --------------------------
    st.subheader("Historique des entrées")
    st.dataframe(df.sort_values("date", ascending=False))

    # Graphique humeur
    st.subheader("Humeur de Jules 🧸")
    mood_chart = alt.Chart(df).mark_circle(size=70, color="#6ab04c").encode(
        x="date:T", y="mood:N", tooltip=["date", "mood", "activity", "notes"]
    )
    st.altair_chart(mood_chart, use_container_width=True)

    # Graphique sommeil
    st.subheader("Sommeil 😴")
    sleep_chart = alt.Chart(df).mark_bar(color="#2980b9").encode(
        x="date:T", y="sleep_hours:Q", tooltip=["date", "sleep_hours"]
    )
    st.altair_chart(sleep_chart, use_container_width=True)

    # Activités
    st.subheader("Activités principales 🎈")
    act_chart = alt.Chart(df).mark_bar(color="#f39c12").encode(
        x="date:T", y="activity:N", tooltip=["date", "activity"]
    )
    st.altair_chart(act_chart, use_container_width=True)

    # --------------------------
    # Export CSV
    # --------------------------
    st.markdown("---")
    if st.button("📦 Exporter le suivi de Jules"):
        st.download_button(
            "Télécharger CSV",
            df.to_csv(index=False),
            "suivi_jules.csv",
            "text/csv",
        )

    conn.close()
