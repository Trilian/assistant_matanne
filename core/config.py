import os
import yaml
import logging
from dotenv import load_dotenv

# === CHARGEMENT DES VARIABLES D’ENVIRONNEMENT ===
load_dotenv(dotenv_path="config/.env.example", override=True)

# === CHEMINS DE BASE ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIG_FILE = os.path.join(BASE_DIR, "config", "settings.yaml")

# === CONSTANTES GÉNÉRALES ===
APP_NAME = "Assistant MatAnne"
APP_VERSION = "4.0"
DB_PATH = os.getenv("DB_PATH", os.path.join(DATA_DIR, "app.db"))
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Clermont-Ferrand")
THEME = os.getenv("THEME", "light")

# === INITIALISATION DU LOGGING LOCAL ===
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def ensure_directories():
    """Crée les répertoires essentiels si absents."""
    for path in [DATA_DIR, LOGS_DIR]:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Dossier vérifié ou créé : {path}")

def load_yaml_settings():
    """Charge les paramètres depuis le fichier YAML."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config or {}
        else:
            logging.warning("⚠️ Aucun fichier settings.yaml trouvé, valeurs par défaut utilisées.")
            return {}
    except Exception as e:
        logging.error(f"Erreur de lecture settings.yaml : {e}")
        return {}

def get_setting(key, default=None):
    """Accès simplifié aux paramètres YAML."""
    config = load_yaml_settings()
    return config.get(key, default)

def get_app_info():
    """Retourne les infos générales de l’application."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "database": DB_PATH,
        "theme": THEME,
        "city": DEFAULT_CITY
    }

# === INITIALISATION ===
ensure_directories()
logging.info(f"{APP_NAME} (v{APP_VERSION}) initialisé avec succès.")