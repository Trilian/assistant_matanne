import sqlite3
import os
import streamlit as st
from core.helpers import log_event

DB_PATH = "data/app.db"

def get_connection():
    """Connexion SQLite robuste avec gestion des erreurs."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        log_event(f"Erreur lors de la connexion à la base : {e}", level="error")
        st.error(f"Erreur de connexion à la base : {e}")
        return None


def test_connection():
    """Teste la validité de la base de données."""
    try:
        conn = get_connection()
        if conn:
            conn.execute("SELECT 1")
            conn.close()
            log_event("✅ Connexion DB OK")
            return True
    except sqlite3.Error as e:
        log_event(f"Erreur DB : {e}", level="error")
        st.error("Base de données corrompue. Tentative de réparation...")
        repair_database()
    return False


def repair_database():
    """Tentative de recréation d'une base corrompue."""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        conn = get_connection()
        log_event("Base SQLite recréée après erreur.")
        st.success("Base de données réparée avec succès.")
        conn.close()
    except Exception as e:
        log_event(f"Échec de la réparation de la base : {e}", level="error")
        st.error(f"Impossible de réparer la base : {e}")


def close_connection(conn):
    """Ferme la connexion proprement."""
    try:
        if conn:
            conn.close()
            log_event("Connexion DB fermée proprement.")
    except Exception as e:
        log_event(f"Erreur lors de la fermeture de la connexion : {e}", level="warning")