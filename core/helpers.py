import logging
from functools import wraps
from datetime import datetime
import streamlit as st
import time
import traceback

# === CONFIGURATION DU LOGGER GLOBAL ===
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# === LOGGING ===
def log_function(func):
    """Décorateur pour tracer les fonctions critiques avec gestion d’erreurs."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logging.info(f"✅ {func.__name__} exécutée avec succès | args={args} kwargs={kwargs}")
            return result
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"❌ Erreur dans {func.__name__}: {e}\n{error_trace}")
            st.error(f"Une erreur est survenue dans '{func.__name__}': {e}")
            return None
    return wrapper


def log_event(message, level="info"):
    """Log libre pour événements personnalisés."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    if level == "error":
        logging.error(msg)
    elif level == "warning":
        logging.warning(msg)
    else:
        logging.info(msg)


# === UTILITAIRES STREAMLIT ===
def show_spinner(message="Chargement..."):
    """Contexte pratique pour spinner Streamlit."""
    return st.spinner(message)


def toast(message, type="success"):
    """Affiche un petit feedback utilisateur."""
    if type == "success":
        st.toast(message)
    elif type == "error":
        st.toast(f"❌ {message}")
    elif type == "warning":
        st.toast(f"⚠️ {message}")
    else:
        st.toast(f"ℹ️ {message}")


# === OUTILS DE FORMATAGE ===
def format_date(date_obj):
    """Format standard DD/MM/YYYY"""
    try:
        return datetime.fromisoformat(date_obj).strftime("%d/%m/%Y")
    except Exception:
        return str(date_obj)


def format_money(value):
    """Format d’affichage monétaire simplifié."""
    try:
        return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")
    except Exception:
        return value


# === OUTILS DIVERS ===
def timeit(func):
    """Décorateur pour mesurer le temps d’exécution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        log_event(f"{func.__name__} exécutée en {duration:.2f}s")
        return result
    return wrapper