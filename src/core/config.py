"""
Configuration - Configuration centralisée de l'application.
Tout harmonisé en français
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import streamlit as st
import os
from typing import Optional
import logging

from .constants import (
    LOG_LEVEL_PRODUCTION,
    LOG_LEVEL_DEVELOPMENT,
    AI_RATE_LIMIT_DAILY,
    AI_RATE_LIMIT_HOURLY,
    CACHE_TTL_RECETTES,
    CACHE_MAX_SIZE
)

logger = logging.getLogger(__name__)


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
        Clé API Mistral avec fallbacks.

        Ordre de priorité:
        1. st.secrets["mistral"]["api_key"]
        2. MISTRAL_API_KEY env var

        Returns:
            Clé API Mistral

        Raises:
            ValueError: Si clé introuvable
        """
        # 1. Secrets Streamlit
        try:
            if hasattr(st, "secrets") and "mistral" in st.secrets:
                return st.secrets["mistral"]["api_key"]
        except Exception:
            pass

        # 2. Variable d'environnement
        cle = os.getenv("MISTRAL_API_KEY")
        if cle:
            return cle

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
        """
        Modèle Mistral à utiliser.

        Returns:
            Nom du modèle
        """
        try:
            return st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
        except:
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
        except:
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
        except:
            return False

    class Config:
        """Configuration Pydantic."""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (SINGLETON)
# ═══════════════════════════════════════════════════════════

_parametres: Optional[Parametres] = None


def obtenir_parametres() -> Parametres:
    """
    Récupère l'instance Parametres (singleton).

    Returns:
        Instance Parametres configurée
    """
    global _parametres
    if _parametres is None:
        _parametres = Parametres()
        logger.info(f"✅ Configuration chargée: {_parametres.APP_NAME} v{_parametres.APP_VERSION}")
    return _parametres