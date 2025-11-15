# assistant_matanne/modules/calendrier.py
import streamlit as st
import pandas as pd
from core.database import get_connection
from core.helpers import log_function
from datetime import datetime
import os
import json

# GOOGLE API ------------------------------------------------------
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_LIBS_OK = True
except:
    GOOGLE_LIBS_OK = False

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_gcal_service():
    if not GOOGLE_LIBS_OK:
        raise RuntimeError("Google API libraries missing.")

    creds = None
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except:
            creds = None

    if not creds or not creds.valid:
        if os.path.exists("credentials.json"):
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as f:
                f.write(creds.to_json())
        else:
            raise FileNotFoundError("credentials.json missing")

    return build('calendar', 'v3', credentials=creds)


# FULLCALENDAR UI ---------------------------------------------------
try:
    from streamlit_calendar import calendar as calendar_ui
    CALENDAR_UI_OK = True
except:
    CALENDAR_UI_OK = False


# UTILITAIRES DB ----------------------------------------------------
def ensure_external_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS external_calendar_events (
                                                                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           gcal_id TEXT UNIQUE,
                                                                           title TEXT,
                                                                           start_date TEXT,
                                                                           end_date TEXT,
                                                                           raw_json TEXT
                   )
                   """)
    conn.commit()

def safe_query(conn, query, label="données"):
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        st.warning(f"Impossible de charger {label} : {e}")
        return pd.DataFrame()


def collect_events(conn):
    """Fusionne routines + projets + repas + événements externes."""
    events = []

    # Routines
    df1 = safe_query(conn, """
                           SELECT r.name AS title,
                                  t.scheduled_time AS start,
                                  NULL AS end,
               'routine' AS type,
               json_object('routine_id', r.id, 'task', t.task_name) AS meta
                           FROM routines r
                               LEFT JOIN routine_tasks t ON r.id = t.routine_id
                           WHERE t.scheduled_time IS NOT NULL
                           """, "routines")
    if not df1.empty: events.append(df1)

    # Projets
    df2 = safe_query(conn, """
                           SELECT p.name || ' - ' || t.task_name AS title,
                                  t.due_date AS start,
                                  NULL AS end,
               'project' AS type,
               json_object('project_id', p.id, 'status', t.status) AS meta
                           FROM projects p
                               LEFT JOIN project_tasks t ON p.id = t.project_id
                           WHERE t.due_date IS NOT NULL
                           """, "project tasks")
    if not df2.empty: events.append(df2)

    # Repas planifiés
    df3 = safe_query(conn, """
                           SELECT r.name AS title,
                                  b.scheduled_date AS start,
                                  NULL AS end,
               'meal' AS type,
               json_object('batch_id', b.id) AS meta
                           FROM batch_meals b
                               LEFT JOIN recipes r ON r.id = b.recipe_id
                           WHERE b.scheduled_date IS NOT NULL
                           """, "repas")
    if not df3.empty: events.append(df3)

    # Événements externes Google
    df4 = safe_query(conn, """
                           SELECT title, start_date AS start, end_date AS end, 'external' AS type, raw_json AS meta
                           FROM external_calendar_events
                           """, "événements externes")
    if not df4.empty: events.append(df4)

    if not events:
        return pd.DataFrame(columns=["title","start","end","type","meta"])

    df = pd.concat(events, ignore_index=True)
    df = df.dropna(subset=["start"])
    return df


# MODULE ------------------------------------------------------------
@log_function
def app():
    st.header("📅 Calendrier complet")
    st.subheader("Routines • Projets • Repas • Agenda externe")

    conn = get_connection()
    ensure_external_table(conn)

    df = collect_events(conn)

    # ACTIONS
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Rafraîchir"):
            st.experimental_rerun()

    with col2:
        if st.button("📤 Exporter vers Google Calendar"):
            if not GOOGLE_LIBS_OK:
                st.error("Google API non installée.")
            else:
                try:
                    service = get_gcal_service()
                    nb = 0
                    for _, ev in df[df.type != "external"].iterrows():
                        body = {
                            "summary": ev["title"],
                            "start": {"date": ev["start"][:10]},
                            "end": {"date": ev["end"][:10] if ev["end"] else ev["start"][:10]}
                        }
                        service.events().insert(calendarId="primary", body=body).execute()
                        nb += 1
                    st.success(f"{nb} événements exportés.")
                except Exception as e:
                    st.error(f"Erreur export : {e}")

    with col3:
        if st.button("📥 Importer depuis Google Calendar"):
            if not GOOGLE_LIBS_OK:
                st.error("Google API non installée.")
            else:
                try:
                    service = get_gcal_service()
                    events = service.events().list(calendarId="primary", singleEvents=True).execute().get("items", [])
                    cur = conn.cursor()
                    imported = 0
                    for e in events:
                        sid = e.get("id")
                        start = e.get("start", {}).get("date") or e.get("start", {}).get("dateTime")
                        end = e.get("end", {}).get("date") or e.get("end", {}).get("dateTime")
                        title = e.get("summary", "Sans titre")

                        if not start: continue

                        cur.execute("""
                                    INSERT OR IGNORE INTO external_calendar_events
                            (gcal_id, title, start_date, end_date, raw_json)
                            VALUES (?, ?, ?, ?, ?)
                                    """, (sid, title, start, end, json.dumps(e)))
                        imported += 1

                    conn.commit()
                    st.success(f"{imported} événements importés.")
                    df = collect_events(conn)
                except Exception as e:
                    st.error(f"Erreur import : {e}")

    st.markdown("---")

    # AFFICHAGE CALENDRIER
    if CALENDAR_UI_OK:
        st.subheader("🗓️ Vue mensuelle")
        events_payload = []
        for _, row in df.iterrows():
            events_payload.append({
                "title": row["title"],
                "start": row["start"],
                "end": row["end"],
                "color": (
                    "#2196f3" if row["type"] == "routine" else
                    "#ff9800" if row["type"] == "project" else
                    "#4caf50" if row["type"] == "meal" else
                    "#9c27b0"
                )
            })

        try:
            calendar_ui(events=events_payload, options={
                "initialView": "dayGridMonth",
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,listWeek",
                }
            })
        except Exception as e:
            st.warning(f"Affichage calendrier impossible : {e}")
            st.dataframe(df)
    else:
        st.warning("⚠️ streamlit-calendar non installé → affichage en tableau")
        st.dataframe(df)

    conn.close()