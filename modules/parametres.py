# assistant_matanne/modules/parametres.py
"""
Paramètres - Phase 5
- Multi-profils
- Centre de notifications
- Sauvegarde (backup) locale
- Export / Import de configuration
- Conserve les fonctionnalités existantes
"""

import streamlit as st
import json
import os
import sqlite3
import shutil
import zipfile
from datetime import datetime
from io import BytesIO
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

# Defaults
BACKUP_DIR = "data/backups"
DEFAULT_SETTINGS = {"theme": "light", "notifications": True, "backup_auto": False}


# -------------------------------------------------------------------------
# TABLES LOCALES (profils et notifications internes)
# -------------------------------------------------------------------------
def ensure_local_tables(conn):
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
                                                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                     user_id INTEGER,
                                                     profile_name TEXT,
                                                     role TEXT,
                                                     preferences TEXT,
                                                     FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_notifications (
                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          user_id INTEGER,
                                                          module TEXT,
                                                          message TEXT,
                                                          created_at TEXT DEFAULT (datetime('now')),
            read INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
    )

    conn.commit()


# -------------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------------
def get_single_user_row(cursor):
    cursor.execute("SELECT id, username, settings FROM users LIMIT 1")
    return cursor.fetchone()


def ensure_single_user(cursor):
    row = get_single_user_row(cursor)
    if not row:
        cursor.execute(
            "INSERT INTO users (username, settings) VALUES (?, ?)",
            ("Anne", json.dumps(DEFAULT_SETTINGS, ensure_ascii=False)),
        )
        cursor.connection.commit()
        return get_single_user_row(cursor)
    return row


def backup_database_file(db_path, dest_dir=BACKUP_DIR):
    os.makedirs(dest_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(dest_dir, f"app_db_backup_{ts}.db")
    shutil.copy2(db_path, dest)
    return dest


def create_backup_zip(db_path, dest_dir=BACKUP_DIR):
    os.makedirs(dest_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(dest_dir, f"backup_{ts}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, arcname=os.path.basename(db_path))
    return zip_path


# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
@log_function
def app():
    st.header("⚙️ Paramètres")
    st.subheader("Gestion des profils, notifications et sauvegardes")

    # Ensure core + local tables
    create_all_tables()
    conn = get_connection()
    ensure_local_tables(conn)
    cur = conn.cursor()

    # Ensure a main user exists
    user_row = ensure_single_user(cur)
    user_id, username, settings_blob = user_row

    # Parse JSON safely
    try:
        settings = json.loads(settings_blob or "{}")
    except:
        settings = {}

    merged_settings = DEFAULT_SETTINGS.copy()
    merged_settings.update(settings)
    settings = merged_settings

    # ---------------------------------------------------------------------
    # PROFILS UTILISATEURS
    # ---------------------------------------------------------------------
    st.markdown("### 🧑 Profils utilisateur")

    cur.execute(
        "SELECT id, profile_name, role, preferences FROM user_profiles WHERE user_id = ?",
        (user_id,),
    )
    profiles = cur.fetchall()

    profile_names = [p[1] for p in profiles] if profiles else []
    active_profile = st.selectbox("Profil actif", ["(Global) " + username] + profile_names)

    # Ajouter profil
    with st.expander("➕ Ajouter un profil"):
        new_name = st.text_input("Nom du profil", key="new_profile_name")
        role = st.selectbox("Rôle", ["parent", "enfant", "autre"])
        if st.button("Créer le profil"):
            if not new_name:
                st.error("Un nom est requis.")
            else:
                pref = json.dumps({"theme": "light", "notifications": True})
                cur.execute(
                    "INSERT INTO user_profiles (user_id, profile_name, role, preferences) VALUES (?, ?, ?, ?)",
                    (user_id, new_name.strip(), role, pref),
                )
                conn.commit()
                st.success(f"Profil '{new_name}' créé")
                st.experimental_rerun()

    # Modifier profils
    if profiles:
        st.markdown("#### Gérer les profils existants")
        for pid, pname, prole, ppref in profiles:
            with st.expander(f"{pname} ({prole})"):
                try:
                    prefs = json.loads(ppref or "{}")
                except:
                    prefs = {}

                p_theme = st.selectbox(
                    "Thème (profil)", ["light", "dark"],
                    index=0 if prefs.get("theme", "light") == "light" else 1,
                    key=f"theme_{pid}"
                )
                p_notif = st.checkbox(
                    "Notifications profil",
                    value=prefs.get("notifications", True),
                    key=f"notif_{pid}"
                )

                if st.button(f"Enregistrer profil {pname}", key=f"save_profile_{pid}"):
                    prefs.update({"theme": p_theme, "notifications": p_notif})
                    cur.execute(
                        "UPDATE user_profiles SET preferences = ? WHERE id = ?",
                        (json.dumps(prefs, ensure_ascii=False), pid),
                    )
                    conn.commit()
                    st.success(f"Profil {pname} mis à jour")

                if st.button(f"Supprimer profil {pname}", key=f"del_profile_{pid}"):
                    cur.execute("DELETE FROM user_profiles WHERE id = ?", (pid,))
                    conn.commit()
                    st.success(f"Profil {pname} supprimé")
                    st.experimental_rerun()

    st.markdown("---")

    # ---------------------------------------------------------------------
    # PARAMÈTRES GLOBAUX
    # ---------------------------------------------------------------------
    st.markdown("### ⚙️ Paramètres globaux")

    new_username = st.text_input("Nom d'utilisateur principal", value=username)
    theme_choice = st.radio(
        "Thème global", ["light", "dark"],
        index=0 if settings.get("theme", "light") == "light" else 1,
    )
    notif_choice = st.checkbox(
        "Activer notifications globales",
        value=settings.get("notifications", True)
    )
    backup_auto = st.checkbox(
        "Sauvegarde automatique hebdomadaire (local)",
        value=settings.get("backup_auto", False)
    )

    if st.button("💾 Enregistrer paramètres globaux"):
        settings.update({
            "theme": theme_choice,
            "notifications": notif_choice,
            "backup_auto": backup_auto,
        })
        cur.execute(
            "UPDATE users SET username = ?, settings = ? WHERE id = ?",
            (new_username, json.dumps(settings, ensure_ascii=False), user_id),
        )
        conn.commit()
        st.success("Paramètres globaux enregistrés")

    # ---------------------------------------------------------------------
    # CENTRE DE NOTIFICATIONS
    # ---------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🔔 Centre de notifications")

    cur.execute(
        "SELECT COUNT(*) FROM user_notifications WHERE user_id = ? AND read = 0",
        (user_id,),
    )
    unread_count = cur.fetchone()[0]
    st.write(f"Notifications non lues : **{unread_count}**")

    if st.button("Marquer toutes comme lues"):
        cur.execute(
            "UPDATE user_notifications SET read = 1 WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        st.success("Toutes les notifications marquées comme lues")
        st.experimental_rerun()

    cur.execute(
        "SELECT id, module, message, created_at, read FROM user_notifications "
        "WHERE user_id = ? ORDER BY created_at DESC LIMIT 200",
        (user_id,),
    )
    notifs = cur.fetchall()

    if notifs:
        for nid, module, message, created_at, read in notifs:
            cols = st.columns([0.85, 0.15])
            with cols[0]:
                status = "✅" if read else "🔔"
                st.markdown(
                    f"{status} **[{module}]** {message}<br><small>{created_at}</small>",
                    unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("✔️", key=f"mark_{nid}"):
                    cur.execute(
                        "UPDATE user_notifications SET read = 1 WHERE id = ?",
                        (nid,)
                    )
                    conn.commit()
                    st.experimental_rerun()
    else:
        st.info("Aucune notification enregistrée.")

    # ---------------------------------------------------------------------
    # BACKUP / EXPORT / IMPORT
    # ---------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 💾 Sauvegardes et import/export")

    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Backup manual
    if st.button("Créer une sauvegarde locale (DB)"):

        try:
            db_path = conn.execute("PRAGMA database_list").fetchall()[0][2]
            zip_path = create_backup_zip(db_path)
            st.success(f"Sauvegarde créée : {zip_path}")
        except Exception as e:
            st.error(f"Échec backup : {e}")

    # List backups
    st.markdown("#### Sauvegardes locales")
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip") or f.endswith(".db")],
        reverse=True
    )

    if backups:
        for b in backups:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(b)
            with col2:
                bp = os.path.join(BACKUP_DIR, b)
                with open(bp, "rb") as fh:
                    data = fh.read()
                st.download_button("Télécharger", data, file_name=b, key=f"dl_{b}")
                if st.button("Supprimer", key=f"del_{b}"):
                    os.remove(bp)
                    st.experimental_rerun()
    else:
        st.info("Aucune sauvegarde trouvée.")

    # Export configuration
    if st.button("Exporter configuration (JSON)"):

        export = {}

        cur.execute("SELECT id, username, settings FROM users")
        export["users"] = [
            {"id": r[0], "username": r[1], "settings": json.loads(r[2] or "{}")}
            for r in cur.fetchall()
        ]

        cur.execute(
            "SELECT id, user_id, profile_name, role, preferences FROM user_profiles"
        )
        export["profiles"] = [
            {
                "id": r[0],
                "user_id": r[1],
                "profile_name": r[2],
                "role": r[3],
                "preferences": json.loads(r[4] or "{}"),
            }
            for r in cur.fetchall()
        ]

        cur.execute(
            "SELECT id, user_id, module, message, created_at, read FROM user_notifications"
        )
        export["notifications"] = [
            {
                "id": r[0],
                "user_id": r[1],
                "module": r[2],
                "message": r[3],
                "created_at": r[4],
                "read": r[5],
            }
            for r in cur.fetchall()
        ]

        b = BytesIO()
        b.write(json.dumps(export, indent=2, ensure_ascii=False).encode("utf-8"))
        st.download_button(
            "Télécharger configuration",
            b.getvalue(),
            file_name="config_assistant_matanne.json",
            mime="application/json",
        )

    # Import configuration
    uploaded = st.file_uploader(
        "Importer une configuration JSON (fusionne ou remplace)", type=["json"]
    )

    if uploaded:
        try:
            raw = uploaded.read()
            payload = json.loads(raw)

            # -------------------------------
            # FIX — empêcher les sqlite3.Row
            # -------------------------------

            if "users" in payload and payload["users"]:
                first = payload["users"][0]

                # sécuriser username
                new_username = first.get("username", username)
                if isinstance(new_username, sqlite3.Row):
                    new_username = new_username["username"]

                # sécuriser settings
                raw_settings = first.get("settings", {})
                if isinstance(raw_settings, sqlite3.Row):
                    raw_settings = dict(raw_settings)

                cur.execute(
                    "UPDATE users SET username = ?, settings = ? WHERE id = ?",
                    (
                        str(new_username),
                        json.dumps(raw_settings, ensure_ascii=False),
                        user_id,
                    ),
                )

            if "profiles" in payload:
                for p in payload["profiles"]:

                    # securiser preferences
                    prefs = p.get("preferences", {})
                    if isinstance(prefs, sqlite3.Row):
                        prefs = dict(prefs)

                    # éviter doublons
                    cur.execute(
                        "SELECT id FROM user_profiles WHERE user_id = ? AND profile_name = ?",
                        (user_id, p["profile_name"]),
                    )
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT INTO user_profiles (user_id, profile_name, role, preferences) "
                            "VALUES (?, ?, ?, ?)",
                            (
                                user_id,
                                p["profile_name"],
                                p.get("role", "parent"),
                                json.dumps(prefs, ensure_ascii=False),
                            ),
                        )

            if "notifications" in payload:
                for n in payload["notifications"]:
                    cur.execute(
                        "INSERT INTO user_notifications (user_id, module, message, created_at, read) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            user_id,
                            n.get("module", "import"),
                            n.get("message", ""),
                            n.get("created_at", datetime.now().isoformat()),
                            int(n.get("read", 0)),
                        ),
                    )

            conn.commit()
            st.success("Configuration importée et fusionnée.")
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Échec import : {e}")

    conn.close()
