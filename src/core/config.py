"""
Configuration - Configuration centralisée de l'application.
Tout harmonisé en français
"""

import logging
import os
from pathlib import Path

def _reload_env_files():
    """Recharge les fichiers .env (appelé à chaque accès config pour Streamlit)"""
    try:
        # Trouver le répertoire racine du projet (parent du dossier src)
        _config_dir = Path(__file__).parent.parent.parent
        _env_files = [_config_dir / ".env.local", _config_dir / ".env"]
        
        for env_path in _env_files:
            if env_path.exists():
                # Charger manuellement le fichier .env
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Retirer les guillemets
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                # Pour Streamlit : forcer le rechargement
                                os.environ[key] = value
    except Exception as e:
        # Ignorer les erreurs si le chargement échoue
        pass

# Charger une première fois au démarrage du module
_reload_env_files()

import streamlit as st
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    AI_RATE_LIMIT_DAILY,
    AI_RATE_LIMIT_HOURLY,
    CACHE_MAX_SIZE,
    CACHE_TTL_RECETTES,
    LOG_LEVEL_PRODUCTION,
)

# Configure logging early when config is imported
from .logging import configure_logging  # type: ignore

logger = logging.getLogger(__name__)



def _read_st_secret(section: str):
    """Lit de façon sûre une section de `st.secrets` si disponible.

    Retourne `None` si `st.secrets` n'est pas présent ou si la section manque.
    """
    try:
        if hasattr(st, "secrets"):
            return st.secrets.get(section)
    except Exception:
        # Ne pas propager les erreurs d'accès à Streamlit secrets
        return None

    return None


def _get_mistral_api_key_from_secrets() -> str | None:
    """Récupère la clé API Mistral des secrets Streamlit.
    
    Essaie plusieurs chemins avec logging TRÈS détaillé:
    1. st.secrets.get('mistral', {}).get('api_key') 
    2. st.secrets['mistral']['api_key']
    3. st.secrets.get('api_key') - fallback direct
    4. Itérer sur toutes les clés avec fallback
    """
    try:
        # Vérifier que streamlit est importé et initialisé
        import streamlit as st
        
        if not hasattr(st, "secrets"):
            logger.warning("❌ st.secrets n'existe pas (pas de fichier secrets.toml)")
            return None
            
        secrets = st.secrets
        if not secrets:
            logger.warning("❌ st.secrets est vide ou None")
            return None
        
        logger.warning(f"🔍 st.secrets type: {type(secrets)}")
        logger.warning(f"🔍 st.secrets has {len(secrets)} items")
        
        # Debug: afficher les clés présentes dans st.secrets
        try:
            clés = []
            try:
                clés = list(secrets.keys()) if hasattr(secrets, 'keys') else list(secrets)
            except:
                clés = []
            logger.warning(f"🔍 st.secrets clés: {clés}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de lister les clés: {e}")
        
        # Chemin 1: st.secrets.get('mistral', {}).get('api_key') - PLUS ROBUSTE
        try:
            mistral_section = secrets.get("mistral") if hasattr(secrets, 'get') else secrets["mistral"] if "mistral" in secrets else None
            if mistral_section:
                logger.warning(f"✅ 'mistral' section trouvée, type: {type(mistral_section)}")
                api_key = None
                if hasattr(mistral_section, 'get'):
                    api_key = mistral_section.get("api_key")
                elif isinstance(mistral_section, dict):
                    api_key = mistral_section.get("api_key")
                if api_key:
                    logger.warning(f"✅ API key trouvée via mistral.api_key: {str(api_key)[:20]}...")
                    return api_key
                else:
                    logger.warning(f"❌ st.secrets['mistral'] existe mais pas 'api_key' dedans")
            else:
                logger.warning("❌ 'mistral' pas trouvé dans st.secrets")
        except Exception as e:
            logger.warning(f"❌ Chemin 1 échoué: {type(e).__name__}: {e}")
        
        # Chemin 2: Accès direct via __getitem__
        try:
            api_key = secrets["mistral"]["api_key"]
            if api_key:
                logger.warning(f"✅ API key trouvée via secrets['mistral']['api_key']: {str(api_key)[:20]}...")
                return api_key
        except (KeyError, TypeError) as e:
            logger.warning(f"❌ Chemin 2 (direct access) échoué: {e}")
        except Exception:
            pass
        
        # Chemin 3: API key directement
        try:
            api_key = secrets.get("api_key") if hasattr(secrets, 'get') else secrets["api_key"] if "api_key" in secrets else None
            if api_key:
                logger.warning(f"✅ API key trouvée directement: {str(api_key)[:20]}...")
                return api_key
        except Exception as e:
            logger.warning(f"❌ Chemin 3 échoué: {e}")
        
        # Chemin 4: Recherche "mistral_api_key"
        try:
            api_key = secrets.get("mistral_api_key") if hasattr(secrets, 'get') else secrets["mistral_api_key"] if "mistral_api_key" in secrets else None
            if api_key:
                logger.warning(f"✅ API key trouvée via mistral_api_key: {str(api_key)[:20]}...")
                return api_key
        except Exception as e:
            logger.warning(f"❌ Chemin 4 échoué: {e}")
        
        # Chemin 5: Itération brute sur les clés
        try:
            for key in secrets:
                if "mistral" in str(key).lower() and "key" in str(key).lower():
                    value = secrets[key] if isinstance(secrets, dict) else getattr(secrets, key, None)
                    if value:
                        logger.warning(f"✅ API key trouvée via iteration: {str(value)[:20]}...")
                        return value
        except Exception as e:
            logger.warning(f"❌ Chemin 5 (iteration) échoué: {type(e).__name__}: {e}")
        
        logger.warning("❌ AUCUNE clé Mistral trouvée dans st.secrets après 5 chemins")
            
    except Exception as e:
        logger.warning(f"❌ Erreur critique accès secrets: {type(e).__name__}: {e}")
    
    return None



class Parametres(BaseSettings):
    """
    Configuration centralisée avec auto-détection.

    Ordre de priorité pour chaque paramètre :
    1. st.secrets (Streamlit Cloud)
    2. Variables d'environnement
    3. Valeur par défaut
    """

    # ═══════════════════════════════════════════════════════════
    # APPLICATION
    # ═══════════════════════════════════════════════════════════

    APP_NAME: str = "Assistant MaTanne"
    """Nom de l'application."""

    APP_VERSION: str = "2.0.0"
    """Version de l'application."""

    ENV: str = Field(default="production")
    """Environnement (production, development, test)."""

    DEBUG: bool = Field(default=False)
    """Mode debug activé."""

    # ═══════════════════════════════════════════════════════════
    # BASE DE DONNÉES (Supabase PostgreSQL)
    # ═══════════════════════════════════════════════════════════

    @property
    def DATABASE_URL(self) -> str:
        """
        Construction URL base de données avec fallbacks.

        Ordre de priorité:
        1. st.secrets["db"]
        2. Variables d'environnement individuelles
        3. Variable DATABASE_URL complète

        Returns:
            URL de connexion PostgreSQL

        Raises:
            ValueError: Si aucune configuration trouvée
        """
        # 1. Secrets Streamlit (prioritaire en production)
        # 1. Streamlit Secrets (prioritaire en production)
        db = _read_st_secret("db")
        if db:
            try:
                return (
                    f"postgresql://{db['user']}:{db['password']}"
                    f"@{db['host']}:{db['port']}/{db['name']}"
                    f"?sslmode=require"
                )
            except Exception:
                logger.debug("st.secrets['db'] présente mais format inattendu")

        # 2. Variables d'environnement individuelles
        hote = os.getenv("DB_HOST")
        utilisateur = os.getenv("DB_USER")
        mot_de_passe = os.getenv("DB_PASSWORD")
        nom = os.getenv("DB_NAME")
        port = os.getenv("DB_PORT", "5432")

        if all([hote, utilisateur, mot_de_passe, nom]):
            return (
                f"postgresql://{utilisateur}:{mot_de_passe}"
                f"@{hote}:{port}/{nom}"
                f"?sslmode=require"
            )

        # 3. DATABASE_URL complète
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if "sslmode" not in db_url and "supabase" in db_url:
                db_url += "?sslmode=require"
            return db_url

        # 4. Échec - guide utilisateur
        raise ValueError(
            "❌ Configuration DB manquante!\n\n"
            "Configure l'une de ces options:\n"
            "1. Streamlit Secrets (.streamlit/secrets.toml):\n"
            "   [db]\n"
            "   host = 'xxx.supabase.co'\n"
            "   port = '5432'\n"
            "   name = 'postgres'\n"
            "   user = 'postgres'\n"
            "   password = 'xxx'\n\n"
            "2. Variables d'environnement:\n"
            "   DB_HOST, DB_USER, DB_PASSWORD, DB_NAME\n\n"
            "3. Variable DATABASE_URL:\n"
            "   DATABASE_URL='postgresql://user:pass@host/db'"
        )

    # ═══════════════════════════════════════════════════════════
    # IA (Mistral)
    # ═══════════════════════════════════════════════════════════

    @property
    def MISTRAL_API_KEY(self) -> str:
        """
        Clé API Mistral avec fallbacks optimisés pour Streamlit Cloud.

        Ordre de priorité:
        1. MISTRAL_API_KEY env var (dev local depuis .env.local)
        2. st.secrets["mistral"]["api_key"] (Streamlit Cloud)

        Returns:
            Clé API Mistral

        Raises:
            ValueError: Si clé introuvable (sauf en Streamlit Cloud)
        """
        # 1. Variable d'environnement (PREMIÈRE PRIORITÉ - dev local)
        cle = os.getenv("MISTRAL_API_KEY")
        if cle and cle.strip():
            logger.info("✅ Clé API Mistral chargée depuis variable d'environnement")
            return cle

        # 2. Secrets Streamlit - Essayer plusieurs chemins (Streamlit Cloud)
        api_key = _get_mistral_api_key_from_secrets()
        if api_key and api_key.strip():
            logger.info("✅ Clé API Mistral chargée depuis st.secrets (Streamlit Cloud)")
            return api_key

        # Erreur: aucune clé trouvée
        is_cloud = _is_streamlit_cloud()
        env_info = "Streamlit Cloud" if is_cloud else "Dev Local"
        
        # En Streamlit Cloud, on lance une erreur MAIS on la laisse remonter
        # Le ClientIA.appeler() attendra le prochain appel quand st.secrets sera disponible
        raise ValueError(
            f"❌ Clé API Mistral manquante ({env_info})!\n\n"
            "Configure l'une de ces options:\n"
            "1. Fichier .env.local (Dev local):\n"
            "   MISTRAL_API_KEY='sk-xxx' ou autre format\n\n"
            "2. Streamlit Secrets (Cloud):\n"
            "   [mistral]\n"
            "   api_key = 'sk-xxx' ou autre format"
        )

    @property
    def MISTRAL_MODEL(self) -> str:
        """
        Modèle Mistral à utiliser.

        Returns:
            Nom du modèle
        """
        try:
            return st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
        except Exception:
            return os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    MISTRAL_TIMEOUT: int = 60
    """Timeout API Mistral en secondes."""

    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"
    """URL de base API Mistral."""

    # ═══════════════════════════════════════════════════════════
    # RATE LIMITING
    # ═══════════════════════════════════════════════════════════

    RATE_LIMIT_DAILY: int = AI_RATE_LIMIT_DAILY
    """Limite d'appels IA par jour."""

    RATE_LIMIT_HOURLY: int = AI_RATE_LIMIT_HOURLY
    """Limite d'appels IA par heure."""

    # ═══════════════════════════════════════════════════════════
    # CACHE
    # ═══════════════════════════════════════════════════════════

    CACHE_ENABLED: bool = True
    """Cache activé."""

    CACHE_DEFAULT_TTL: int = CACHE_TTL_RECETTES
    """TTL cache par défaut (secondes)."""

    CACHE_MAX_SIZE: int = CACHE_MAX_SIZE
    """Taille maximale du cache."""

    # ═══════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════

    LOG_LEVEL: str = LOG_LEVEL_PRODUCTION
    """Niveau de log."""

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES HELPERS
    # ═══════════════════════════════════════════════════════════

    def est_production(self) -> bool:
        """
        Vérifie si l'environnement est production.

        Returns:
            True si production
        """
        return self.ENV.lower() == "production"

    def est_developpement(self) -> bool:
        """
        Vérifie si l'environnement est développement.

        Returns:
            True si développement
        """
        return self.ENV.lower() in ["development", "dev"]

    def obtenir_config_publique(self) -> dict:
        """
        Exporte la configuration sans les secrets (pour debug).

        Returns:
            Dict avec configuration publique uniquement
        """
        return {
            "nom_app": self.APP_NAME,
            "version": self.APP_VERSION,
            "environnement": self.ENV,
            "debug": self.DEBUG,
            "modele_mistral": self.MISTRAL_MODEL,
            "cache_active": self.CACHE_ENABLED,
            "niveau_log": self.LOG_LEVEL,
            "db_configuree": self._verifier_db_configuree(),
            "mistral_configure": self._verifier_mistral_configure(),
        }

    def _verifier_db_configuree(self) -> bool:
        """
        Vérifie si la base de données est configurée.

        Returns:
            True si configurée
        """
        try:
            _ = self.DATABASE_URL
            return True
        except Exception:
            return False

    def _verifier_mistral_configure(self) -> bool:
        """
        Vérifie si Mistral est configuré.

        Returns:
            True si configuré
        """
        try:
            _ = self.MISTRAL_API_KEY
            return True
        except Exception:
            return False

    # Configuration Pydantic v2
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore les champs supplémentaires (évite l'erreur "Extra inputs are not permitted")
    )


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (SINGLETON)
# ═══════════════════════════════════════════════════════════

_parametres: Parametres | None = None


def obtenir_parametres() -> Parametres:
    """
    Récupère l'instance Parametres.
    
    Important: Avec Streamlit qui redémarre, on recrée l'instance
    à chaque appel pour recharger les variables d'environnement.

    Returns:
        Instance Parametres configurée
    """
    global _parametres
    
    # Recharger .env files à chaque appel (important pour Streamlit qui redémarre)
    _reload_env_files()
    
    # Toujours recréer l'instance pour Streamlit (pas de cache singleton)
    # Cela garantit que os.environ est relu
    _parametres = Parametres()
    
    # Configure logging according to loaded settings
    try:
        configure_logging(_parametres.LOG_LEVEL)
    except Exception:
        # Fallback: continue if logging config échoue
        pass

    logger.info(f"✅ Configuration chargée: {_parametres.APP_NAME} v{_parametres.APP_VERSION}")
    return _parametres
