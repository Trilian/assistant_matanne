# assistant_matanne/modules/projets_maison.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("🏡 Projets Maison")
    st.subheader("Suivi des projets, travaux et tâches domestiques")

    create_all_tables()
    conn = get_connection()
    cur = conn.cursor()

    # --- Récupération projets et tâches ---
    cur.execute("SELECT * FROM projects ORDER BY start_date DESC")
    projets = cur.fetchall()

    # === TABLEAU DE BORD GLOBAL ===
    if projets:
        total_projects = len(projets)
        total_tasks = 0
        completed_tasks = 0
        overdue_projects = 0

        for pid, pname, pdesc, pstart, pend, pprio in projets:
            cur.execute("SELECT status, due_date FROM project_tasks WHERE project_id = ?", (pid,))
            tasks = cur.fetchall()
            total_tasks += len(tasks)
            completed_tasks += len([t for t in tasks if t[0] == "terminé"])

            try:
                end_date = datetime.fromisoformat(pend)
                if end_date.date() < datetime.now().date():
                    overdue_projects += 1
            except Exception:
                pass

        avg_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Projets", total_projects)
        col2.metric("⚙️ Progression moyenne", f"{avg_progress:.0f} %")
        col3.metric("⏰ En retard", overdue_projects)
        st.markdown("---")

    # === FORMULAIRE AJOUT PROJET ===
    with st.expander("➕ Ajouter un projet"):
        name = st.text_input("Nom du projet")
        desc = st.text_area("Description")
        start = st.date_input("Date de début", datetime.today())
        end = st.date_input("Date de fin prévue", datetime.today() + timedelta(days=7))
        priority = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute"])
        if st.button("Créer le projet"):
            if name.strip():
                cur.execute(
                    "INSERT INTO projects (name, description, start_date, end_date, priority) VALUES (?, ?, ?, ?, ?)",
                    (name.strip(), desc, start.isoformat(), end.isoformat(), priority),
                )
                conn.commit()
                st.success(f"Projet **{name}** ajouté ✅")
                st.rerun()
            else:
                st.error("Le nom du projet est obligatoire.")

    # === AFFICHAGE DES PROJETS ===
    if not projets:
        st.info("Aucun projet enregistré.")
        conn.close()
        return

    st.markdown("### 📋 Liste des projets")

    for pid, pname, pdesc, pstart, pend, pprio in projets:
        st.markdown(f"#### 🧱 {pname} ({pprio})")
        st.markdown(f"**Début :** {pstart} &nbsp;&nbsp; **Fin prévue :** {pend}")
        st.write(pdesc if pdesc else "_Pas de description_")

        cur.execute("SELECT id, task_name, status, due_date FROM project_tasks WHERE project_id = ?", (pid,))
        tasks = cur.fetchall()

        total = len(tasks)
        done = len([t for t in tasks if t[2] == "terminé"])
        progress = (done / total * 100) if total > 0 else 0
        st.progress(progress / 100)
        st.caption(f"Progression : {done}/{total} tâches ({progress:.0f} %)")

        if tasks:
            for tid, tname, status, due in tasks:
                overdue = False
                try:
                    if due and datetime.fromisoformat(due).date() < datetime.now().date() and status != "terminé":
                        overdue = True
                except Exception:
                    pass

                cols = st.columns([0.45, 0.25, 0.2, 0.1])
                with cols[0]:
                    st.write(f"{'⚠️ ' if overdue else '• '} {tname}")
                with cols[1]:
                    new_status = st.selectbox(
                        "Statut", ["en cours", "terminé"],
                        index=(1 if status == "terminé" else 0),
                        key=f"status_{tid}"
                    )
                with cols[2]:
                    if due:
                        st.caption(f"⏰ {due}")
                with cols[3]:
                    if st.button("💾", key=f"save_{tid}"):
                        cur.execute("UPDATE project_tasks SET status = ? WHERE id = ?", (new_status, tid))
                        conn.commit()
                        st.toast(f"Tâche mise à jour : {tname}")
                        st.rerun()

                # Notification automatique si tâche en retard
                if overdue:
                    cur.execute(
                        "INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (1, ?, ?, datetime('now'), 0)",
                        ("Projets Maison", f"Tâche '{tname}' du projet '{pname}' est en retard."),
                    )
                    conn.commit()

        else:
            st.info("Aucune tâche pour ce projet.")

        # Ajout tâche
        with st.expander(f"➕ Ajouter une tâche à {pname}"):
            tname = st.text_input("Nom de la tâche", key=f"new_task_{pid}")
            t_due = st.date_input("Échéance", datetime.today() + timedelta(days=3), key=f"due_{pid}")
            if st.button("Ajouter la tâche", key=f"add_task_{pid}"):
                if tname.strip():
                    cur.execute(
                        "INSERT INTO project_tasks (project_id, task_name, status, due_date) VALUES (?, ?, ?, ?)",
                        (pid, tname.strip(), "en cours", t_due.isoformat()),
                    )
                    conn.commit()
                    st.success(f"Tâche **{tname}** ajoutée ✅")
                    st.rerun()
                else:
                    st.error("Nom de tâche obligatoire.")

        st.markdown("---")

    # === EXPORT CSV ===
    st.markdown("### 📤 Exporter les projets")
    if st.button("Exporter en CSV"):
        cur.execute("SELECT * FROM projects")
        df_projects = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
        cur.execute("SELECT * FROM project_tasks")
        df_tasks = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
        with pd.ExcelWriter("projets_maison_export.xlsx", engine="xlsxwriter") as writer:
            df_projects.to_excel(writer, sheet_name="Projets", index=False)
            df_tasks.to_excel(writer, sheet_name="Tâches", index=False)
        with open("projets_maison_export.xlsx", "rb") as f:
            st.download_button("Télécharger le fichier Excel", f, file_name="projets_maison_export.xlsx")

    conn.close()
