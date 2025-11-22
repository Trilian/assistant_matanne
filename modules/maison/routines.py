# assistant_matanne/modules/routines.py
import streamlit as st
import pandas as pd
from datetime import datetime, date
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("⏰ Routines et Tâches")
    st.subheader("Suivi quotidien des routines pour les enfants")

    create_all_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # --- Sélection de l'enfant ---
    cursor.execute("SELECT id, name FROM child_profiles")
    children = cursor.fetchall()
    if not children:
        st.warning("Aucun enfant enregistré.")
        return

    child_dict = {name: cid for cid, name in children}
    selected_child = st.selectbox("Choisir un enfant", list(child_dict.keys()))
    child_id = child_dict[selected_child]

    # --- Récupération des routines ---
    cursor.execute("SELECT id, name FROM routines WHERE child_id = ?", (child_id,))
    routines = cursor.fetchall()

    # --- Formulaire ajout routine ---
    with st.expander("➕ Ajouter une routine"):
        routine_name = st.text_input("Nom de la routine")
        if st.button("Ajouter routine", key="add_routine"):
            if routine_name.strip():
                cursor.execute(
                    "INSERT INTO routines (name, child_id) VALUES (?, ?)",
                    (routine_name.strip(), child_id)
                )
                conn.commit()
                st.success(f"Routine '{routine_name}' ajoutée ✅")
                st.rerun()
            else:
                st.error("Le nom de routine est obligatoire.")

    if not routines:
        st.info("Aucune routine pour cet enfant.")
        conn.close()
        return

    # --- Affichage des routines et tâches ---
    for rid, rname in routines:
        st.markdown(f"### 🗂 {rname}")

        # Récupération tâches
        cursor.execute(
            "SELECT id, task_name, scheduled_time, status FROM routine_tasks WHERE routine_id = ?",
            (rid,)
        )
        tasks = cursor.fetchall()

        # Progression
        total = len(tasks)
        done = len([t for t in tasks if t[3] == "terminé"])
        progress = (done / total * 100) if total > 0 else 0
        st.progress(progress / 100)
        st.caption(f"Progression : {done}/{total} tâches ({progress:.0f} %)")

        # Ajouter tâche
        with st.expander(f"➕ Ajouter une tâche à {rname}"):
            task_name = st.text_input("Nom de la tâche", key=f"task_name_{rid}")
            scheduled_time = st.time_input("Heure prévue", datetime.now().time(), key=f"time_{rid}")
            if st.button("Ajouter tâche", key=f"add_task_{rid}"):
                if task_name.strip():
                    cursor.execute(
                        "INSERT INTO routine_tasks (routine_id, task_name, scheduled_time, status) VALUES (?, ?, ?, ?)",
                        (rid, task_name.strip(), scheduled_time.strftime("%H:%M"), "en cours")
                    )
                    conn.commit()
                    st.success(f"Tâche '{task_name}' ajoutée ✅")
                    st.rerun()
                else:
                    st.error("Le nom de tâche est obligatoire.")

        # Affichage tâches existantes
        if tasks:
            for tid, tname, ttime, status in tasks:
                overdue = False
                try:
                    # Vérifier si tâche non terminée et passée
                    now_time = datetime.now().strftime("%H:%M")
                    if status != "terminé" and ttime < now_time:
                        overdue = True
                except Exception:
                    pass

                cols = st.columns([0.5, 0.2, 0.2, 0.1])
                with cols[0]:
                    st.write(f"{'⚠️ ' if overdue else '• '} {tname}")
                with cols[1]:
                    new_status = st.selectbox(
                        "Statut", ["en cours", "terminé"],
                        index=(1 if status == "terminé" else 0),
                        key=f"status_{tid}"
                    )
                with cols[2]:
                    st.caption(f"🕒 {ttime}")
                with cols[3]:
                    if st.button("💾", key=f"save_{tid}"):
                        cursor.execute("UPDATE routine_tasks SET status = ? WHERE id = ?", (new_status, tid))
                        conn.commit()
                        st.toast(f"Tâche mise à jour : {tname}")
                        st.rerun()

                # Notification si tâche non terminée
                if overdue:
                    cursor.execute(
                        "INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (1, ?, ?, datetime('now'), 0)",
                        ("Routines", f"Tâche '{tname}' de la routine '{rname}' est en retard.")
                    )
                    conn.commit()

        st.markdown("---")

    # --- Export CSV ---
    st.markdown("### 📤 Exporter routines et tâches")
    if st.button("Exporter en CSV"):
        df_routines = pd.read_sql(
            "SELECT * FROM routines WHERE child_id = ?", conn, params=(child_id,)
        )
        df_tasks = pd.read_sql(
            "SELECT * FROM routine_tasks WHERE routine_id IN (SELECT id FROM routines WHERE child_id=?)",
            conn, params=(child_id,)
        )
        with pd.ExcelWriter("routines_export.xlsx", engine="xlsxwriter") as writer:
            df_routines.to_excel(writer, sheet_name="Routines", index=False)
            df_tasks.to_excel(writer, sheet_name="Tâches", index=False)
        with open("routines_export.xlsx", "rb") as f:
            st.download_button("Télécharger le fichier Excel", f, file_name="routines_export.xlsx")

    conn.close()