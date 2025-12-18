"""
Configuration Robuste avec Fallbacks
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import streamlit as st
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuration avec support secrets Streamlit + .env"""

    # ===================================
    # APPLICATION
    # ===================================
    APP_NAME: str = "Assistant MaTanne v2"
    APP_VERSION: str = "2.0.0"
    ENV: str = Field(default="production")
    DEBUG: bool = Field(default=False)

    # ===================================
    # DATABASE - avec fallbacks
    # ===================================
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        """Construit l'URL avec fallbacks intelligents"""
        # 1. Essayer st.secrets d'abord
        if hasattr(st, "secrets") and "db" in st.secrets:
            try:
                db = st.secrets["db"]
                return (
                    f"postgresql://{db['user']}:{db['password']}"
                    f"@{db['host']}:{db['port']}/{db['name']}"
                    f"?sslmode=require"
                )
            except KeyError:
                pass

        # 2. Fallback sur variables d'environnement
        if all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT or 5432}/{self.DB_NAME}"
                f"?sslmode=require"
            )

        # 3. Variable DATABASE_URL directe
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Forcer SSL si Supabase
            if "supabase" in db_url and "sslmode" not in db_url:
                db_url += "?sslmode=require"
            return db_url

        raise ValueError(
            "Configuration DB manquante. Configure soit:\n"
            "1. st.secrets['db'] (Streamlit Cloud)\n"
            "2. Variables d'env DB_HOST, DB_USER, etc.\n"
            "3. DATABASE_URL"
        )

    # ===================================
    # MISTRAL AI - avec fallbacks
    # ===================================
    MISTRAL_API_KEY: Optional[str] = None

    @property
    def get_mistral_key(self) -> str:
        """Récupère clé Mistral avec fallbacks"""
        # 1. st.secrets
        if hasattr(st, "secrets") and "mistral" in st.secrets:
            try:
                return st.secrets["mistral"]["api_key"]
            except KeyError:
                pass

        # 2. Variable d'instance
        if self.MISTRAL_API_KEY:
            return self.MISTRAL_API_KEY

        # 3. Variable d'env
        key = os.getenv("MISTRAL_API_KEY")
        if key:
            return key

        raise ValueError(
            "Clé Mistral manquante. Configure:\n"
            "1. st.secrets['mistral']['api_key']\n"
            "2. MISTRAL_API_KEY env var"
        )

    MISTRAL_MODEL: str = Field(default="mistral-small-latest")
    MISTRAL_TIMEOUT: int = Field(default=30)

    # ===================================
    # PARAMÈTRES IA
    # ===================================
    AI_DEFAULT_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    AI_DEFAULT_MAX_TOKENS: int = Field(default=500, ge=1, le=2000)

    # ===================================
    # FONCTIONNALITÉS
    # ===================================
    ENABLE_AI: bool = Field(default=True)
    ENABLE_WEATHER: bool = Field(default=False)
    ENABLE_CACHE: bool = Field(default=True)
    ENABLE_RATE_LIMIT: bool = Field(default=True)

    # ===================================
    # LIMITES
    # ===================================
    MAX_RECIPES_PER_USER: int = Field(default=1000)
    MAX_PROJECTS_PER_USER: int = Field(default=100)
    MAX_CACHE_SIZE: int = Field(default=100)

    # Rate Limiting
    RATE_LIMIT_HOURLY: int = Field(default=30)
    RATE_LIMIT_DAILY: int = Field(default=100)

    # ===================================
    # LOGGING
    # ===================================
    LOG_LEVEL: str = Field(default="INFO")

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid:
            return "INFO"
        return v.upper()

    # ===================================
    # HELPERS
    # ===================================
    def is_production(self) -> bool:
        """Vérifie si en prod"""
        return self.ENV.lower() == "production"

    def is_development(self) -> bool:
        """Vérifie si en dev"""
        return self.ENV.lower() == "development"

    def to_dict(self) -> dict:
        """Export config pour debug"""
        return {
            "APP_NAME": self.APP_NAME,
            "APP_VERSION": self.APP_VERSION,
            "ENV": self.ENV,
            "ENABLE_AI": self.ENABLE_AI,
            "ENABLE_CACHE": self.ENABLE_CACHE,
            "MISTRAL_MODEL": self.MISTRAL_MODEL,
            # Ne jamais logger les secrets !
            "DB_CONFIGURED": bool(self.DB_HOST or self.DATABASE_URL),
            "MISTRAL_CONFIGURED": bool(self.MISTRAL_API_KEY),
        }

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# ===================================
# INSTANCE GLOBALE LAZY-LOADED
# ===================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Récupère settings avec lazy loading
    Évite les erreurs au démarrage
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Alias pour compatibilité
settings = get_settings()
