# assistant_matanne/modules/projets_maison.py
"""
Projets Maison — VERSION ULTRA (Phase 3 - Ultra)

Fonctionnalités :
- Dashboard projets + métriques
- CRUD projets & tâches (create / edit / delete) avec confirmations
- Vue Kanban (À faire / En cours / Terminé)
- Vue Liste & Vue Calendrier (export deadlines -> external_calendar_events)
- Anti-spam notifications (1 notification similaire / 24h)
- Export Excel (Projets + Tâches), CSV
- Calcul de progression (optionnel : persister colonne 'progression' via ALTER TABLE si l'utilisateur accepte)
- Robustesse row_factory (tuple/dict compatible)
- Pas de suppression automatique de schéma; modification du schéma faite uniquement si tu valides.
"""

import streamlit as st
import pandas as pd
import io
import json
import os
from datetime import datetime, timedelta, date
from core.database import get_connection
from core.helpers import log_function

# Optional calendar UI
try:
    from streamlit_calendar import calendar as streamlit_calendar_component
    CALENDAR_UI_OK = True
except Exception:
    CALENDAR_UI_OK = False

# Helpers
def to_dict_safe(row, cur):
    """Return dict from sqlite row whether cursor.row_factory is dict or tuple."""
    if isinstance(row, dict):
        return row
    # tuple-like: build dict from cursor.description
    cols = [d[0] for d in cur.description]
    return {cols[i]: row[i] for i in range(len(cols))}

def now_iso():
    return datetime.now().isoformat()

def date_iso(d):
    if isinstance(d, (date, datetime)):
        return d.isoformat()
    return str(d)

def notify_once(conn, user_id, module, message):
    """
    Insert a notification only if an identical message hasn't been created in the last 24 hours.
    """
    cur = conn.cursor()
    # normalize message simple
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    try:
        cur.execute(
            "SELECT id FROM user_notifications WHERE module = ? AND message = ? AND created_at >= ? LIMIT 1",
            (module, message, cutoff)
        )
        exists = cur.fetchone()
        if exists:
            return False
        cur.execute(
            "INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (?, ?, ?, ?, 0)",
            (user_id, module, message, now_iso())
        )
        conn.commit()
        return True
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False

def ensure_external_events_table(conn):
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS external_calendar_events (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        gcal_id TEXT UNIQUE,
                                                                        title TEXT,
                                                                        start_date TEXT,
                                                                        end_date TEXT,
                                                                        raw_json TEXT
                )
                """)
    cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_external_events_start ON external_calendar_events(start_date)
                """)
    conn.commit()

@log_function
def app():
    st.header("🏡 Projets Maison — Ultra")
    st.subheader("Suivi avancé des projets, tâches, échéances et export")

    # Defensive: attempt to create tables if schema_manager exists (non-destructive)
    try:
        from core.schema_manager import create_all_tables
        try:
            create_all_tables()
        except Exception:
            # non-fatal
            pass
    except Exception:
        pass

    conn = get_connection()
    conn.row_factory = None  # keep default; we'll adapt when fetching rows
    cur = conn.cursor()

    # Ensure external events table exists (used for calendar export)
    try:
        ensure_external_events_table(conn)
    except Exception:
        pass

    # --- TOP ACTIONS & FILTERS ---
    st.markdown("---")
    top_col1, top_col2, top_col3, top_col4 = st.columns([1,1,1,1])
    with top_col1:
        if st.button("🔄 Rafraîchir"):
            st.experimental_rerun()
    with top_col2:
        if st.button("📤 Exporter projets & tâches (Excel)"):
            try:
                cur.execute("SELECT * FROM projects")
                proj_rows = cur.fetchall()
                proj_cols = [c[0] for c in cur.description]
                df_proj = pd.DataFrame([dict(zip(proj_cols, r)) for r in proj_rows]) if proj_rows else pd.DataFrame(columns=proj_cols)

                cur.execute("SELECT * FROM project_tasks")
                task_rows = cur.fetchall()
                task_cols = [c[0] for c in cur.description]
                df_tasks = pd.DataFrame([dict(zip(task_cols, r)) for r in task_rows]) if task_rows else pd.DataFrame(columns=task_cols)

                # Excel in-memory
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df_proj.to_excel(writer, sheet_name="Projets", index=False)
                    df_tasks.to_excel(writer, sheet_name="Tâches", index=False)
                    writer.save()
                buf.seek(0)
                st.download_button("Télécharger Excel Projets", buf, file_name="projets_maison_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Erreur export Excel : {e}")

    with top_col3:
        if st.button("📥 Export deadlines → Agenda (local)"):
            # read all project tasks with due_date and insert into external_calendar_events
            try:
                cur.execute("""
                            SELECT p.name as project_name, t.task_name, t.due_date, p.id as project_id, t.id as task_id
                            FROM project_tasks t
                                     JOIN projects p ON p.id = t.project_id
                            WHERE t.due_date IS NOT NULL
                            """)
                rows = cur.fetchall()
                added = 0
                for r in rows:
                    rdict = dict(zip([c[0] for c in cur.description], r))
                    title = f"{rdict['project_name']} — {rdict['task_name']}"
                    start = rdict['due_date']
                    # Insert OR IGNORE by title+start to avoid duplicates; use gcal_id NULL
                    cur.execute("""
                                INSERT OR IGNORE INTO external_calendar_events (gcal_id, title, start_date, end_date, raw_json)
                        VALUES (?, ?, ?, ?, ?)
                                """, (None, title, start, start, json.dumps({"project_id": rdict["project_id"], "task_id": rdict["task_id"]})))
                    if cur.rowcount:
                        added += 1
                conn.commit()
                st.success(f"{added} échéances exportées vers `external_calendar_events`.")
            except Exception as e:
                st.error(f"Erreur export deadlines : {e}")

    with top_col4:
        view_mode = st.selectbox("Vue", ["Dashboard", "Kanban", "Liste", "Calendrier"], index=0)

    st.markdown("---")

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2,1,1])
    with filter_col1:
        q = st.text_input("Recherche (projet ou tâche)", "")
    with filter_col2:
        priority_filter = st.selectbox("Priorité", options=["Toutes","Basse","Moyenne","Haute"], index=0)
    with filter_col3:
        only_overdue = st.checkbox("Afficher seulement en retard", value=False)

    # --- LOAD DATA (robust)
    # projects
    try:
        cur.execute("SELECT id, name, description, start_date, end_date, priority FROM projects ORDER BY start_date DESC")
        proj_rows = cur.fetchall()
        proj_cols = [c[0] for c in cur.description]
        projets = [dict(zip(proj_cols, r)) for r in proj_rows]
    except Exception:
        projets = []

    # tasks
    try:
        cur.execute("SELECT id, project_id, task_name, status, due_date FROM project_tasks ORDER BY due_date IS NULL, due_date ASC")
        task_rows = cur.fetchall()
        task_cols = [c[0] for c in cur.description]
        tasks = [dict(zip(task_cols, r)) for r in task_rows]
    except Exception:
        tasks = []

    # Build quick lookups
    proj_map = {p['id']: p for p in projets}

    # Compute stats
    total_projects = len(projets)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if (t.get('status') or '').lower() in ("terminé","termine","done","finished")])
    overdue_tasks = 0
    for t in tasks:
        due = t.get('due_date')
        stat = (t.get('status') or '').lower()
        if due:
            try:
                if datetime.fromisoformat(str(due)).date() < datetime.now().date() and stat not in ("terminé","termine","done","finished"):
                    overdue_tasks += 1
            except Exception:
                pass

    avg_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # DASHBOARD
    if view_mode == "Dashboard":
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Projets", total_projects)
        col2.metric("⚙️ Progression moyenne", f"{avg_progress:.0f} %")
        col3.metric("⏰ Tâches en retard", overdue_tasks)
        st.markdown("### Projets récents")
        # Show concise table
        if projets:
            df_proj_mini = pd.DataFrame([{
                "id": p['id'],
                "name": p['name'],
                "start": p.get('start_date'),
                "end": p.get('end_date'),
                "priority": p.get('priority')
            } for p in projets])
            st.dataframe(df_proj_mini[['name','start','end','priority']], use_container_width=True)
        else:
            st.info("Aucun projet enregistré.")

    # KANBAN
    if view_mode == "Kanban":
        st.markdown("### Vue Kanban")
        # statuses bucket
        buckets = {"À faire": [], "En cours": [], "Terminé": []}
        for t in tasks:
            s = (t.get('status') or '').lower()
            if s in ("terminé","termine","done","finished"):
                buckets["Terminé"].append(t)
            elif s in ("en cours", "encours", "in progress"):
                buckets["En cours"].append(t)
            else:
                buckets["À faire"].append(t)

        cols = st.columns(3)
        status_keys = list(buckets.keys())
        for i, key in enumerate(status_keys):
            with cols[i]:
                st.markdown(f"#### {key} ({len(buckets[key])})")
                for t in buckets[key]:
                    proj = proj_map.get(t['project_id'], {"name": "—"})
                    due = t.get('due_date') or ""
                    overdue = ""
                    try:
                        if due and datetime.fromisoformat(str(due)).date() < datetime.now().date() and (t.get('status') or '').lower() not in ("terminé","termine"):
                            overdue = " ⚠️"
                    except Exception:
                        pass
                    st.markdown(f"- **{t['task_name']}** — _{proj['name']}_ {due}{overdue}")

                    # inline actions
                    c1, c2, c3 = st.columns([0.6,0.6,0.8])
                    with c1:
                        if st.button("→ status", key=f"status_move_{t['id']}"):
                            # cycle status
                            cur_status = (t.get('status') or '').lower()
                            new_status = "en cours" if cur_status not in ("en cours","encours") else "terminé"
                            try:
                                cur.execute("UPDATE project_tasks SET status = ? WHERE id = ?", (new_status, t['id']))
                                conn.commit()
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Impossible de mettre à jour le statut : {e}")
                    with c2:
                        if st.button("✏️", key=f"edit_task_{t['id']}"):
                            st.session_state["edit_task_id"] = t['id']
                            st.experimental_rerun()
                    with c3:
                        if st.button("🗑️", key=f"del_task_{t['id']}"):
                            if st.confirm(f"Supprimer la tâche '{t['task_name']}' ?"):
                                try:
                                    cur.execute("DELETE FROM project_tasks WHERE id = ?", (t['id'],))
                                    conn.commit()
                                    st.success("Tâche supprimée.")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Erreur suppression : {e}")

    # LISTE (détaillée)
    if view_mode == "Liste":
        st.markdown("### Liste complète")
        # Apply filters/search
        df_tasks_full = pd.DataFrame(tasks)
        if df_tasks_full.empty:
            st.info("Aucune tâche.")
        else:
            if q.strip():
                token = q.strip().lower()
                df_tasks_full = df_tasks_full[df_tasks_full['task_name'].str.lower().str.contains(token) | df_tasks_full['project_id'].astype(str).isin([str(pid) for pid,p in proj_map.items() if token in (p.get('name') or "").lower()])]
            if priority_filter != "Toutes":
                proj_ids = [p['id'] for p in projets if (p.get('priority') or "").lower() == priority_filter.lower()]
                df_tasks_full = df_tasks_full[df_tasks_full['project_id'].isin(proj_ids)]
            # Overdue filter
            if only_overdue:
                def is_overdue(row):
                    due = row.get('due_date')
                    stt = (row.get('status') or "").lower()
                    if not due:
                        return False
                    try:
                        return datetime.fromisoformat(str(due)).date() < datetime.now().date() and stt not in ("terminé","termine")
                    except Exception:
                        return False
                df_tasks_full = df_tasks_full[df_tasks_full.apply(is_overdue, axis=1)]
            st.dataframe(df_tasks_full, use_container_width=True)

            # Edit task inline
            st.markdown("### Actions sur une tâche")
            task_ids = df_tasks_full['id'].tolist()
            sel_tid = st.selectbox("Sélectionner tâche", options=task_ids)
            sel_row = df_tasks_full[df_tasks_full['id'] == sel_tid].iloc[0].to_dict()
            st.write(sel_row)
            new_status = st.selectbox("Nouveau statut", ["en cours","terminé"], index=1 if (sel_row.get('status') or '').lower() in ("terminé","termine") else 0)
            new_due = st.date_input("Nouvelle échéance", value=(datetime.fromisoformat(sel_row['due_date']).date() if sel_row.get('due_date') else date.today()))
            if st.button("Mettre à jour la tâche"):
                try:
                    cur.execute("UPDATE project_tasks SET status = ?, due_date = ? WHERE id = ?", (new_status, new_due.isoformat(), sel_tid))
                    conn.commit()
                    st.success("Tâche mise à jour.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erreur mise à jour : {e}")

    # CALENDRIER
    if view_mode == "Calendrier":
        st.markdown("### Calendrier des échéances")
        # Build events from tasks with due_date
        events = []
        for t in tasks:
            if not t.get('due_date'):
                continue
            proj_name = proj_map.get(t['project_id'], {}).get('name', 'Projet')
            title = f"{proj_name} — {t.get('task_name')}"
            events.append({
                "title": title,
                "start": t['due_date'],
                "end": t['due_date'],
                "color": "#ff9800" if (t.get('status') or '').lower() not in ("terminé","termine") else "#4caf50"
            })
        if CALENDAR_UI_OK and events:
            try:
                streamlit_calendar_component(events=events, options={
                    "initialView": "dayGridMonth",
                    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek,listWeek"},
                    "navLinks": True
                })
            except Exception as e:
                st.warning(f"Impossible d'afficher le calendrier visuel : {e}")
                st.table(pd.DataFrame(events))
        else:
            if not events:
                st.info("Aucune échéance à afficher.")
            else:
                st.table(pd.DataFrame(events))

    # --- CREATE / EDIT PROJECTS & TASKS UI ---
    st.markdown("---")
    st.subheader("✚ Créer / Éditer un projet")
    if "edit_project_id" not in st.session_state:
        st.session_state["edit_project_id"] = None

    if st.session_state["edit_project_id"]:
        # edit mode
        pid = st.session_state["edit_project_id"]
        cur.execute("SELECT id, name, description, start_date, end_date, priority FROM projects WHERE id = ?", (pid,))
        prow = cur.fetchone()
        if prow:
            p = dict(zip([c[0] for c in cur.description], prow))
            e_name = st.text_input("Nom du projet", p.get('name'))
            e_desc = st.text_area("Description", p.get('description') or "")
            e_start = st.date_input("Date début", value=(datetime.fromisoformat(p.get('start_date')).date() if p.get('start_date') else date.today()))
            e_end = st.date_input("Date fin prévue", value=(datetime.fromisoformat(p.get('end_date')).date() if p.get('end_date') else date.today()+timedelta(days=7)))
            e_prio = st.selectbox("Priorité", ["Basse","Moyenne","Haute"], index=["Basse","Moyenne","Haute"].index(p.get('priority') or "Moyenne"))
            if st.button("Enregistrer projet"):
                try:
                    cur.execute("UPDATE projects SET name=?, description=?, start_date=?, end_date=?, priority=? WHERE id = ?",
                                (e_name.strip(), e_desc.strip(), e_start.isoformat(), e_end.isoformat(), e_prio, pid))
                    conn.commit()
                    st.success("Projet mis à jour.")
                    st.session_state["edit_project_id"] = None
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erreur mise à jour projet : {e}")
            if st.button("Annuler édition"):
                st.session_state["edit_project_id"] = None
    else:
        with st.expander("➕ Ajouter un nouveau projet"):
            name = st.text_input("Nom du projet (nouveau)")
            desc = st.text_area("Description (nouveau)")
            start = st.date_input("Date de début (nouveau)", date.today())
            end = st.date_input("Date de fin prévue (nouveau)", date.today() + timedelta(days=7))
            priority = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute"], index=1, key="prio_new")
            if st.button("Créer projet (nouveau)"):
                if name.strip():
                    try:
                        cur.execute("INSERT INTO projects (name, description, start_date, end_date, priority) VALUES (?, ?, ?, ?, ?)",
                                    (name.strip(), desc.strip(), start.isoformat(), end.isoformat(), priority))
                        conn.commit()
                        st.success("Projet créé.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur création : {e}")
                else:
                    st.error("Le nom du projet est requis.")

    # Edit task modal (session driven)
    if "edit_task_id" in st.session_state and st.session_state["edit_task_id"]:
        tid = st.session_state["edit_task_id"]
        cur.execute("SELECT id, project_id, task_name, status, due_date FROM project_tasks WHERE id = ?", (tid,))
        trow = cur.fetchone()
        if trow:
            t = dict(zip([c[0] for c in cur.description], trow))
            st.markdown("### Édition tâche")
            new_name = st.text_input("Nom tâche", value=t.get('task_name'))
            new_status = st.selectbox("Statut", ["en cours","terminé"], index=1 if (t.get('status') or '').lower() in ("terminé","termine") else 0)
            new_due = st.date_input("Échéance", value=(datetime.fromisoformat(t.get('due_date')).date() if t.get('due_date') else date.today()))
            if st.button("Sauvegarder tâche"):
                try:
                    cur.execute("UPDATE project_tasks SET task_name=?, status=?, due_date=? WHERE id = ?", (new_name.strip(), new_status, new_due.isoformat(), tid))
                    conn.commit()
                    st.success("Tâche mise à jour.")
                    st.session_state["edit_task_id"] = None
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erreur sauvegarde tâche : {e}")
            if st.button("Annuler édition tâche"):
                st.session_state["edit_task_id"] = None

    # Option: persist progression column if user wants
    st.markdown("---")
    st.subheader("⚙️ Options avancées")
    if st.button("Calculer & afficher progression (ne modifie pas la BDD)"):
        # compute progression per project
        prog_rows = []
        for p in projets:
            pid = p['id']
            p_tasks = [t for t in tasks if t['project_id'] == pid]
            total = len(p_tasks)
            done = len([tt for tt in p_tasks if (tt.get('status') or '').lower() in ("terminé","termine","done")])
            prog = int((done / total * 100) if total > 0 else 0)
            prog_rows.append({"project_id": pid, "project_name": p['name'], "progression": prog})
        st.table(pd.DataFrame(prog_rows))
        st.info("Si tu veux enregistrer cette progression dans la table `projects`, utilise le bouton 'Persister progression'.")
    if st.button("Persister progression (ALTER TABLE)"):
        # ask user implicit consent: we'll ALTER TABLE to add 'progression' if missing
        try:
            # check if column exists
            cur.execute("PRAGMA table_info(projects)")
            cols = [r[1] for r in cur.fetchall()]
            if 'progression' not in cols:
                cur.execute("ALTER TABLE projects ADD COLUMN progression INTEGER DEFAULT 0")
                conn.commit()
            # update progression values
            for p in projets:
                pid = p['id']
                p_tasks = [t for t in tasks if t['project_id'] == pid]
                total = len(p_tasks)
                done = len([tt for tt in p_tasks if (tt.get('status') or '').lower() in ("terminé","termine","done")])
                prog = int((done / total * 100) if total > 0 else 0)
                cur.execute("UPDATE projects SET progression = ? WHERE id = ?", (prog, pid))
            conn.commit()
            st.success("Progression persistée dans la table `projects`.")
        except Exception as e:
            st.error(f"Impossible de persister la progression : {e}")

    # Clean up + final notifications for overdue tasks (but avoid spamming)
    # We'll create notifications for tasks in overdue_tasks but only one per message in last 24h
    try:
        for t in tasks:
            due = t.get('due_date')
            status = (t.get('status') or '').lower()
            if due and status not in ("terminé","termine","done"):
                try:
                    if datetime.fromisoformat(str(due)).date() < datetime.now().date():
                        project_name = proj_map.get(t['project_id'], {}).get('name', 'Projet')
                        msg = f"Tâche '{t.get('task_name')}' du projet '{project_name}' est en retard."
                        notify_once(conn, 1, "Projets Maison", msg)
                except Exception:
                    pass
    except Exception:
        pass

    # Close connection
    conn.close()