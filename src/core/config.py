"""
Configuration - Streamlit Cloud + Supabase + Mistral AI
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import streamlit as st
from typing import Optional


class Settings(BaseSettings):
    """Configuration simplifiée pour Streamlit Cloud"""

    # ===================================
    # APPLICATION
    # ===================================
    APP_NAME: str = "Assistant MaTanne v2"
    APP_VERSION: str = "2.0.0"
    ENV: str = Field(default="production")

    # ===================================
    # DATABASE (depuis st.secrets)
    # ===================================
    @property
    def DATABASE_URL(self) -> str:
        """Construit l'URL depuis les secrets Streamlit"""
        try:
            db = st.secrets["db"]
            return (
                f"postgresql://{db['user']}:{db['password']}"
                f"@{db['host']}:{db['port']}/{db['name']}"
                f"?sslmode=require"  # Obligatoire pour Supabase
            )
        except KeyError as e:
            raise ValueError(f"Secret DB manquant: {e}")

    # ===================================
    # MISTRAL AI (depuis st.secrets)
    # ===================================
    @property
    def MISTRAL_API_KEY(self) -> str:
        """Récupère la clé API Mistral"""
        try:
            return st.secrets["mistral"]["api_key"]
        except KeyError:
            raise ValueError("MISTRAL_API_KEY manquant dans les secrets")

    MISTRAL_MODEL: str = Field(default="mistral-small")
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
    ENABLE_WEATHER: bool = Field(default=False)  # Désactivé par défaut

    # ===================================
    # LIMITES
    # ===================================
    MAX_RECIPES_PER_USER: int = Field(default=1000)
    MAX_PROJECTS_PER_USER: int = Field(default=100)

    class Config:
        case_sensitive = False


# Instance globale
settings = Settings()