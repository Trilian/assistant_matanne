# assistant_matanne/modules/suggestions.py
import streamlit as st
import pandas as pd
from datetime import datetime
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("💡 Suggestions de repas")
    st.subheader("Génération automatique et suivi des suggestions pour les enfants")

    create_all_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # --- Récupération des enfants ---
    cursor.execute("SELECT id, name FROM child_profiles")
    children = cursor.fetchall()
    if not children:
        st.warning("Aucun profil enfant disponible.")
        return

    child_dict = {name: cid for cid, name in children}
    selected_child = st.selectbox("Choisir un enfant", list(child_dict.keys()))
    child_id = child_dict[selected_child]

    # --- Récupération des batch meals à venir ---
    cursor.execute(
        """SELECT bm.id, bm.scheduled_date, r.name as recipe_name
           FROM batch_meals bm
                    LEFT JOIN recipes r ON bm.recipe_id = r.id
           WHERE bm.scheduled_date >= ?""",
        (datetime.today().isoformat(),)
    )
    batches = cursor.fetchall()

    if not batches:
        st.info("Aucun repas batch planifié à venir.")
        return

    # --- Génération ou affichage des suggestions ---
    st.subheader(f"Suggestions pour {selected_child}")
    for batch_id, scheduled_date, recipe_name in batches:
        # Vérifie si une suggestion existe déjà pour cet enfant
        cursor.execute(
            "SELECT id, status FROM suggestions WHERE batch_meal_id = ? AND child_id = ?",
            (batch_id, child_id)
        )
        sugg = cursor.fetchone()
        status = sugg[1] if sugg else "non proposée"

        st.markdown(f"**{scheduled_date} : {recipe_name}** – Statut : {status}")

        col1, col2, col3 = st.columns([0.3,0.3,0.4])
        with col1:
            if st.button("✔️ Accepter", key=f"accept_{batch_id}_{child_id}"):
                if sugg:
                    cursor.execute("UPDATE suggestions SET status = ? WHERE id = ?", ("accepté", sugg[0]))
                else:
                    cursor.execute(
                        "INSERT INTO suggestions (batch_meal_id, child_id, suggested_on, status) VALUES (?, ?, ?, ?)",
                        (batch_id, child_id, datetime.now().isoformat(), "accepté")
                    )
                # Historique
                cursor.execute(
                    "INSERT INTO suggestion_history (suggestion_id, acted_on, outcome) VALUES (?, ?, ?)",
                    (sugg[0] if sugg else cursor.lastrowid, datetime.now().isoformat(), "accepté")
                )
                conn.commit()
                st.success("Suggestion acceptée ✅")

        with col2:
            if st.button("❌ Refuser", key=f"reject_{batch_id}_{child_id}"):
                if sugg:
                    cursor.execute("UPDATE suggestions SET status = ? WHERE id = ?", ("refusé", sugg[0]))
                else:
                    cursor.execute(
                        "INSERT INTO suggestions (batch_meal_id, child_id, suggested_on, status) VALUES (?, ?, ?, ?)",
                        (batch_id, child_id, datetime.now().isoformat(), "refusé")
                    )
                # Historique
                cursor.execute(
                    "INSERT INTO suggestion_history (suggestion_id, acted_on, outcome) VALUES (?, ?, ?)",
                    (sugg[0] if sugg else cursor.lastrowid, datetime.now().isoformat(), "refusé")
                )
                conn.commit()
                st.warning("Suggestion refusée ❌")

        with col3:
            if status != "accepté" and status != "refusé":
                st.info("Suggestion non encore traitée")

        # Notification si non acceptée à moins d'1 jour
        if status == "non proposée" and datetime.fromisoformat(scheduled_date) <= datetime.today():
            cursor.execute(
                "INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (1, ?, ?, datetime('now'), 0)",
                ("Suggestions", f"Suggestion de repas '{recipe_name}' pour {selected_child} non traitée")
            )
            conn.commit()

    # --- Export CSV ---
    st.markdown("---")
    if st.button("📦 Exporter suggestions"):
        df_sugg = pd.read_sql(
            "SELECT * FROM suggestions",
            conn
        )
        df_hist = pd.read_sql(
            "SELECT * FROM suggestion_history",
            conn
        )
        with pd.ExcelWriter("suggestions_export.xlsx", engine="xlsxwriter") as writer:
            df_sugg.to_excel(writer, sheet_name="Suggestions", index=False)
            df_hist.to_excel(writer, sheet_name="Historique", index=False)
        with open("suggestions_export.xlsx", "rb") as f:
            st.download_button("Télécharger le fichier Excel", f, file_name="suggestions_export.xlsx")

    conn.close()
