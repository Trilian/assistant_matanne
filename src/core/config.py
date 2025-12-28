"""
Configuration Application - Version Simplifiée
Centralise TOUTE la configuration avec fallbacks intelligents
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import streamlit as st
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration centralisée avec auto-detection"""

    # ═══════════════════════════════════════════════════════════
    # APPLICATION
    # ═══════════════════════════════════════════════════════════
    APP_NAME: str = "Assistant MaTanne"
    APP_VERSION: str = "2.0.0"
    ENV: str = Field(default="production")
    DEBUG: bool = Field(default=False)

    # ═══════════════════════════════════════════════════════════
    # DATABASE (Supabase)
    # ═══════════════════════════════════════════════════════════

    @property
    def DATABASE_URL(self) -> str:
        """
        Construction URL base de données avec fallbacks

        Ordre de priorité:
        1. st.secrets["db"]
        2. Variables d'environnement individuelles
        3. Variable DATABASE_URL directe
        """
        # 1. Secrets Streamlit (prioritaire)
        try:
            if hasattr(st, "secrets") and "db" in st.secrets:
                db = st.secrets["db"]
                return (
                    f"postgresql://{db['user']}:{db['password']}"
                    f"@{db['host']}:{db['port']}/{db['name']}"
                    f"?sslmode=require"
                )
        except Exception as e:
            logger.debug(f"st.secrets['db'] non disponible: {e}")

        # 2. Variables d'environnement
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        name = os.getenv("DB_NAME")
        port = os.getenv("DB_PORT", "5432")

        if all([host, user, password, name]):
            return (
                f"postgresql://{user}:{password}"
                f"@{host}:{port}/{name}"
                f"?sslmode=require"
            )

        # 3. DATABASE_URL complète
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if "sslmode" not in db_url and "supabase" in db_url:
                db_url += "?sslmode=require"
            return db_url

        # 4. Échec
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
        Clé API Mistral avec fallbacks

        Ordre:
        1. st.secrets["mistral"]["api_key"]
        2. MISTRAL_API_KEY env var
        """
        # 1. Secrets Streamlit
        try:
            if hasattr(st, "secrets") and "mistral" in st.secrets:
                return st.secrets["mistral"]["api_key"]
        except Exception:
            pass

        # 2. Variable d'environnement
        key = os.getenv("MISTRAL_API_KEY")
        if key:
            return key

        raise ValueError(
            "❌ Clé API Mistral manquante!\n\n"
            "Configure l'une de ces options:\n"
            "1. Streamlit Secrets:\n"
            "   [mistral]\n"
            "   api_key = 'xxx'\n\n"
            "2. Variable d'environnement:\n"
            "   MISTRAL_API_KEY='xxx'"
        )

    @property
    def MISTRAL_MODEL(self) -> str:
        """Modèle Mistral à utiliser"""
        try:
            return st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
        except:
            return os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    MISTRAL_TIMEOUT: int = 60
    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"

    # ═══════════════════════════════════════════════════════════
    # RATE LIMITING
    # ═══════════════════════════════════════════════════════════
    RATE_LIMIT_DAILY: int = 100
    RATE_LIMIT_HOURLY: int = 30

    # ═══════════════════════════════════════════════════════════
    # CACHE
    # ═══════════════════════════════════════════════════════════
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 100  # Nombre max d'items en cache

    # ═══════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════
    LOG_LEVEL: str = "INFO"

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def is_production(self) -> bool:
        """Check si environnement de production"""
        return self.ENV.lower() == "production"

    def is_development(self) -> bool:
        """Check si environnement de développement"""
        return self.ENV.lower() in ["development", "dev"]

    def get_safe_config(self) -> dict:
        """
        Export config sans secrets pour debug

        Returns:
            Dict avec config publique uniquement
        """
        return {
            "app_name": self.APP_NAME,
            "version": self.APP_VERSION,
            "environment": self.ENV,
            "debug": self.DEBUG,
            "mistral_model": self.MISTRAL_MODEL,
            "cache_enabled": self.CACHE_ENABLED,
            "log_level": self.LOG_LEVEL,
            "db_configured": self._check_db_configured(),
            "mistral_configured": self._check_mistral_configured(),
        }

    def _check_db_configured(self) -> bool:
        """Vérifie si DB est configurée"""
        try:
            _ = self.DATABASE_URL
            return True
        except:
            return False

    def _check_mistral_configured(self) -> bool:
        """Vérifie si Mistral est configuré"""
        try:
            _ = self.MISTRAL_API_KEY
            return True
        except:
            return False

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (SINGLETON)
# ═══════════════════════════════════════════════════════════

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Récupère l'instance Settings (singleton)

    Returns:
        Instance Settings configurée
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info(f"✅ Configuration chargée: {_settings.APP_NAME} v{_settings.APP_VERSION}")
    return _settings


# Alias pour compatibilité
settings = get_settings()