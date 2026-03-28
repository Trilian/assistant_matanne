"""Settings - Configuration Pydantic centralisée.

Classe Parametres avec auto-détection des sources:
1. Variables d'environnement (via pydantic-settings / .env.local)
2. Valeurs par défaut

Toutes les valeurs passent par la validation Pydantic.
"""

from __future__ import annotations

import logging

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..constants import (
    AI_RATE_LIMIT_DAILY,
    AI_RATE_LIMIT_HOURLY,
    CACHE_MAX_SIZE,
    CACHE_TTL_RECETTES,
    LOG_LEVEL_PRODUCTION,
    SEUIL_PAGE_LENTE,
)
from .loader import _reload_env_files

logger = logging.getLogger(__name__)


class Parametres(BaseSettings):
    """
    Configuration centralisée avec auto-détection.

    Toutes les valeurs passent par la validation Pydantic.

    Ordre de priorité pour chaque paramètre :
    1. Variables d'environnement (via pydantic-settings)
    2. Fichier .env.local
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
    # Composants individuels chargés par pydantic-settings depuis env.
    # ═══════════════════════════════════════════════════════════

    DB_HOST: str | None = None
    """Hôte de la base de données (ex: xxx.supabase.co)."""

    DB_USER: str | None = None
    """Utilisateur de la base de données."""

    DB_PASSWORD: str | None = None
    """Mot de passe de la base de données."""

    DB_NAME: str | None = None
    """Nom de la base de données."""

    DB_PORT: str = "5432"
    """Port de la base de données."""

    db_url: str | None = Field(
        None,
        validation_alias=AliasChoices("DATABASE_URL", "db_url"),
    )
    """URL complète de la base de données (résolue depuis env vars ou composants)."""

    @property
    def DATABASE_URL(self) -> str:
        """
        URL de connexion PostgreSQL validée par Pydantic.

        La résolution depuis les env vars est effectuée
        une seule fois au démarrage via ``_resoudre_secrets``.

        Returns:
            URL de connexion PostgreSQL

        Raises:
            ValueError: Si aucune configuration trouvée
        """
        if self.db_url:
            return self.db_url
        raise ValueError(
            "[ERROR] Configuration DB manquante!\n\n"
            "Configure l'une de ces options:\n"
            "1. Variables d'environnement (.env.local):\n"
            "   DB_HOST, DB_USER, DB_PASSWORD, DB_NAME\n\n"
            "2. Variable DATABASE_URL:\n"
            "   DATABASE_URL='postgresql://user:pass@host/db'"
        )

    # ═══════════════════════════════════════════════════════════
    # IA (Mistral) — chargé par pydantic-settings depuis env.
    # ═══════════════════════════════════════════════════════════

    mistral_key: str | None = Field(
        None,
        validation_alias=AliasChoices("MISTRAL_API_KEY", "mistral_key"),
    )
    """Clé API Mistral résolue (depuis env vars)."""

    @property
    def MISTRAL_API_KEY(self) -> str:
        """
        Clé API Mistral validée par Pydantic.

        La résolution depuis les env vars est effectuée
        une seule fois au démarrage via ``_resoudre_secrets``.

        Returns:
            Clé API Mistral

        Raises:
            ValueError: Si clé introuvable
        """
        dummy = "sk-test-dummy-key-replace-with-real-key"
        if self.mistral_key and self.mistral_key != dummy:
            return self.mistral_key
        raise ValueError(
            "[ERROR] Clé API Mistral manquante!\n\n"
            "Configure dans .env.local:\n"
            "   MISTRAL_API_KEY='sk-xxx'"
        )

    MISTRAL_MODEL: str = "mistral-small-latest"
    """Modèle Mistral à utiliser."""

    MISTRAL_TIMEOUT: int = 60
    """Timeout API Mistral en secondes."""

    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"
    """URL de base API Mistral."""

    # ═══════════════════════════════════════════════════════════
    # APIS EXTERNES — chargées par pydantic-settings depuis env.
    # ═══════════════════════════════════════════════════════════

    FOOTBALL_DATA_API_KEY: str | None = None
    """Clé API Football-Data.org (optionnelle)."""

    GOOGLE_CLIENT_ID: str = ""
    """Client ID OAuth2 Google Calendar."""

    GOOGLE_CLIENT_SECRET: str = ""
    """Client Secret OAuth2 Google Calendar."""

    GOOGLE_REDIRECT_URI: str = ""
    """URI de redirection OAuth2 Google."""

    # ── WhatsApp Meta Business API ──

    META_WHATSAPP_TOKEN: str = ""
    """Token d'accès Meta WhatsApp Business API."""

    META_PHONE_NUMBER_ID: str = ""
    """ID du numéro de téléphone Meta WhatsApp Business."""

    WHATSAPP_VERIFY_TOKEN: str = ""
    """Token de vérification pour le webhook WhatsApp."""

    WHATSAPP_USER_NUMBER: str = ""
    """Numéro WhatsApp de l'utilisateur principal (format: 33612345678)."""

    # ── OpenWeatherMap ──

    OPENWEATHER_API_KEY: str = ""
    """Clé API OpenWeatherMap (gratuit < 1000 req/jour)."""

    OPENWEATHER_CITY: str = "Paris,FR"
    """Ville pour les prévisions météo (format: Ville,Code)."""

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

    REDIS_URL: str = ""
    """URL Redis pour cache distribué (ex: redis://localhost:6379/0). Vide = désactivé."""

    SENTRY_DSN: str = ""
    """DSN Sentry pour le error tracking (ex: https://xxx@sentry.io/yyy). Vide = désactivé."""

    # ═══════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════

    LOG_LEVEL: str = LOG_LEVEL_PRODUCTION
    """Niveau de log."""

    # ═══════════════════════════════════════════════════════════    # PERFORMANCE / MONITORING
    # ═════════════════════════════════════════════════════════════

    SEUIL_PAGE_LENTE: float = SEUIL_PAGE_LENTE
    """Seuil en secondes au-delà duquel une page est considérée lente (défaut: 2.0s)."""

    # ═══════════════════════════════════════════════════════════════════
    # FAMILLE - ALERTES
    # ═══════════════════════════════════════════════════════════════════

    VACANCES_ALERT_DAYS: int = 14
    """Seuil en jours pour afficher l'alerte/preview 'Vacances' dans le hub famille (défaut: 14 jours)."""

    # ═════════════════════════════════════════════════════════════
    # RÉSOLUTION DES SECRETS (env vars uniquement)
    # ═══════════════════════════════════════════════════════════

    @model_validator(mode="after")
    def _resoudre_secrets(self) -> Parametres:
        """Complète les valeurs depuis les variables d'environnement.

        Appelé une seule fois au démarrage. Les valeurs sont ensuite
        stockées dans les champs Pydantic validés.
        """
        self._resoudre_database_url()
        self._resoudre_mistral()
        return self

    def _resoudre_database_url(self) -> None:
        """Résout DATABASE_URL.

        Ordre de priorité:
        1. DATABASE_URL env var (déjà chargé dans db_url par pydantic-settings)
        2. Composants individuels DB_HOST/DB_USER/... (pydantic-settings)
        """
        if self.db_url:
            if "sslmode" not in self.db_url and "supabase" in self.db_url:
                self.db_url += "?sslmode=require"
            return

        if all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
            self.db_url = (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                f"?sslmode=require"
            )

    def _resoudre_mistral(self) -> None:
        """Résout MISTRAL_API_KEY depuis les env vars."""
        if not self.MISTRAL_MODEL:
            self.MISTRAL_MODEL = "mistral-small-latest"

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
        """Vérifie si la base de données est configurée."""
        return bool(self.db_url)

    def _verifier_mistral_configure(self) -> bool:
        """Vérifie si Mistral est configuré."""
        return bool(self.mistral_key)

    # Configuration Pydantic v2
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (SINGLETON)
# ═══════════════════════════════════════════════════════════

_parametres: Parametres | None = None
_logging_configured: bool = False
_parametres_lock = __import__("threading").Lock()


def obtenir_parametres() -> Parametres:
    """
    Récupère l'instance Parametres (thread-safe).

    Utilise un singleton avec rechargement des .env au premier appel.
    Le logging n'est configuré qu'une seule fois.

    Returns:
        Instance Parametres configurée
    """
    global _parametres, _logging_configured

    if _parametres is not None:
        return _parametres

    with _parametres_lock:
        if _parametres is not None:
            return _parametres

        # Charger .env files une seule fois
        _reload_env_files()

        instance = Parametres()

        # Configure logging une seule fois
        if not _logging_configured:
            try:
                from ..logging import configure_logging

                configure_logging(instance.LOG_LEVEL)
                _logging_configured = True
            except Exception as e:
                import logging
                logging.getLogger(__name__).debug(f"Configuration logging échouée: {e}")

        _parametres = instance

    return _parametres


def reinitialiser_parametres() -> Parametres:
    """Force le rechargement des paramètres (utile après changement .env)."""
    global _parametres
    with _parametres_lock:
        _parametres = None
    return obtenir_parametres()
