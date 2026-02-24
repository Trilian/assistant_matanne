"""
Sentry - Intégration error tracking pour la production.

Ce module fournit:
- Initialisation Sentry avec configuration automatique
- Capture d'exceptions avec contexte enrichi
- Intégration avec le système de correlation_id
- Filtrage des PII et secrets

Usage::

    from src.core.monitoring.sentry import initialiser_sentry, capturer_exception

    # Au démarrage de l'application
    initialiser_sentry()

    # Capture manuelle d'exception
    try:
        operation_risquee()
    except Exception as e:
        capturer_exception(e, contexte={"utilisateur": "123"})
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_sentry_initialise = False


def _est_sentry_disponible() -> bool:
    """Vérifie si sentry-sdk est installé."""
    try:
        import sentry_sdk  # noqa: F401

        return True
    except ImportError:
        return False


def initialiser_sentry(
    dsn: str | None = None,
    environnement: str | None = None,
    release: str | None = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
) -> bool:
    """
    Initialise Sentry pour le error tracking.

    Args:
        dsn: DSN Sentry (par défaut depuis SENTRY_DSN env var)
        environnement: Environnement (production, staging, dev)
        release: Version de l'application
        traces_sample_rate: Taux d'échantillonnage des traces (0.0-1.0)
        profiles_sample_rate: Taux d'échantillonnage des profils (0.0-1.0)

    Returns:
        True si Sentry a été initialisé, False sinon

    Example:
        >>> from src.core.monitoring.sentry import initialiser_sentry
        >>> initialiser_sentry()  # Utilise SENTRY_DSN depuis env
        True
    """
    global _sentry_initialise

    if _sentry_initialise:
        logger.debug("Sentry déjà initialisé")
        return True

    if not _est_sentry_disponible():
        logger.warning("sentry-sdk non installé, error tracking désactivé")
        return False

    # Récupérer DSN depuis env si non fourni
    dsn = dsn or os.getenv("SENTRY_DSN")
    if not dsn:
        logger.info("SENTRY_DSN non configuré, Sentry désactivé")
        return False

    # Déterminer l'environnement
    environnement = environnement or os.getenv("SENTRY_ENVIRONMENT", "development")

    # Déterminer la release
    release = release or os.getenv("SENTRY_RELEASE", _obtenir_version_app())

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        # Configuration des intégrations
        integrations = [
            LoggingIntegration(
                level=logging.INFO,  # Capturer les logs INFO+
                event_level=logging.ERROR,  # Créer des events pour ERROR+
            ),
        ]

        # Ajouter intégration SQLAlchemy si disponible
        try:
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            integrations.append(SqlalchemyIntegration())
        except ImportError:
            pass

        sentry_sdk.init(
            dsn=dsn,
            environment=environnement,
            release=release,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=integrations,
            # Filtrer les PII
            send_default_pii=False,
            # Hooks de filtrage
            before_send=_filtrer_event,
            before_breadcrumb=_filtrer_breadcrumb,
        )

        _sentry_initialise = True
        logger.info(f"✅ Sentry initialisé (env={environnement}, release={release})")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur initialisation Sentry: {e}")
        return False


def capturer_exception(
    exception: Exception | None = None,
    contexte: dict[str, Any] | None = None,
    tags: dict[str, str] | None = None,
    niveau: str = "error",
) -> str | None:
    """
    Capture une exception dans Sentry.

    Args:
        exception: Exception à capturer (ou None pour l'exception courante)
        contexte: Données contextuelles additionnelles
        tags: Tags pour filtrage dans Sentry
        niveau: Niveau de log (error, warning, info)

    Returns:
        Event ID Sentry ou None si non capturé

    Example:
        >>> try:
        ...     risque()
        ... except Exception as e:
        ...     event_id = capturer_exception(e, contexte={"user_id": "123"})
    """
    if not _sentry_initialise:
        logger.debug("Sentry non initialisé, exception non capturée")
        return None

    try:
        import sentry_sdk

        # Ajouter contexte
        if contexte:
            sentry_sdk.set_context("contexte_app", contexte)

        # Ajouter tags
        if tags:
            for key, value in tags.items():
                sentry_sdk.set_tag(key, value)

        # Ajouter correlation_id si disponible
        try:
            from src.core.observability.context import _contexte_execution

            ctx = _contexte_execution.get()
            if ctx and ctx.correlation_id:
                sentry_sdk.set_tag("correlation_id", ctx.correlation_id)
                if ctx.operation:
                    sentry_sdk.set_tag("operation", ctx.operation)
        except Exception:
            pass

        # Capturer l'exception
        if exception:
            return sentry_sdk.capture_exception(exception)
        else:
            return sentry_sdk.capture_exception()

    except Exception as e:
        logger.error(f"Erreur capture Sentry: {e}")
        return None


def capturer_message(
    message: str,
    niveau: str = "info",
    contexte: dict[str, Any] | None = None,
) -> str | None:
    """
    Envoie un message à Sentry.

    Args:
        message: Message à envoyer
        niveau: Niveau (info, warning, error)
        contexte: Données contextuelles

    Returns:
        Event ID Sentry ou None
    """
    if not _sentry_initialise:
        return None

    try:
        import sentry_sdk

        if contexte:
            sentry_sdk.set_context("contexte_app", contexte)

        return sentry_sdk.capture_message(message, level=niveau)

    except Exception as e:
        logger.error(f"Erreur message Sentry: {e}")
        return None


def definir_utilisateur(
    user_id: str | None = None,
    email: str | None = None,
    username: str | None = None,
) -> None:
    """
    Définit l'utilisateur courant pour Sentry.

    Args:
        user_id: Identifiant unique
        email: Email (optionnel)
        username: Nom d'utilisateur (optionnel)
    """
    if not _sentry_initialise:
        return

    try:
        import sentry_sdk

        user_data = {}
        if user_id:
            user_data["id"] = user_id
        if email:
            user_data["email"] = email
        if username:
            user_data["username"] = username

        if user_data:
            sentry_sdk.set_user(user_data)

    except Exception:
        pass


def ajouter_breadcrumb(
    message: str,
    categorie: str = "app",
    niveau: str = "info",
    data: dict[str, Any] | None = None,
) -> None:
    """
    Ajoute un breadcrumb pour le debugging.

    Args:
        message: Message du breadcrumb
        categorie: Catégorie (navigation, http, query, etc.)
        niveau: Niveau (debug, info, warning, error)
        data: Données additionnelles
    """
    if not _sentry_initialise:
        return

    try:
        import sentry_sdk

        sentry_sdk.add_breadcrumb(
            message=message, category=categorie, level=niveau, data=data or {}
        )

    except Exception:
        pass


def _filtrer_event(event: dict, hint: dict) -> dict | None:
    """
    Filtre les events avant envoi à Sentry.

    Supprime les informations sensibles (PII, secrets).
    """
    # Filtrer les secrets des messages d'erreur
    if "exception" in event:
        for exception in event.get("exception", {}).get("values", []):
            value = exception.get("value", "")
            # Masquer les patterns sensibles
            for pattern in ["password", "token", "api_key", "secret"]:
                if pattern in value.lower():
                    exception["value"] = "[FILTERED]"
                    break

    # Filtrer les données de requête sensibles
    if "request" in event:
        request = event["request"]
        if "headers" in request:
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                if header in request["headers"]:
                    request["headers"][header] = "[FILTERED]"

    return event


def _filtrer_breadcrumb(crumb: dict, hint: dict) -> dict | None:
    """Filtre les breadcrumbs sensibles."""
    # Filtrer les requêtes avec credentials
    message = crumb.get("message", "")
    if any(x in message.lower() for x in ["password", "token", "secret"]):
        return None

    return crumb


def _obtenir_version_app() -> str:
    """Récupère la version de l'application depuis pyproject.toml."""
    try:
        import tomllib
        from pathlib import Path

        pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "unknown")
    except Exception:
        pass

    return os.getenv("APP_VERSION", "unknown")


def est_sentry_actif() -> bool:
    """Vérifie si Sentry est actif."""
    return _sentry_initialise
