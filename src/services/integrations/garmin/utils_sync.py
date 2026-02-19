"""
Fonctions de validation, synchronisation et paramètres API Garmin.

Validation des configurations OAuth et tokens, vérification
de la nécessité de synchronisation, génération de plages de dates
et construction des paramètres d'appel API.
"""

from datetime import date, datetime, timedelta

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def validate_oauth_config(config: dict) -> tuple[bool, list[str]]:
    """
    Valide la configuration OAuth Garmin.

    Args:
        config: Dict avec les clés de configuration

    Returns:
        Tuple (is_valid, list_of_errors)
    """
    errors = []

    required_keys = [
        "consumer_key",
        "consumer_secret",
        "request_token_url",
        "access_token_url",
        "authorize_url",
    ]

    for key in required_keys:
        if not config.get(key):
            errors.append(f"Clé manquante: {key}")

    # Vérifier les URLs
    url_keys = ["request_token_url", "access_token_url", "authorize_url", "api_base_url"]
    for key in url_keys:
        url = config.get(key, "")
        if url and not url.startswith("https://"):
            errors.append(f"URL non sécurisée: {key} doit commencer par https://")

    return len(errors) == 0, errors


def validate_garmin_token(token_data: dict) -> tuple[bool, str]:
    """
    Valide qu'un token Garmin est utilisable.

    Args:
        token_data: Dict avec oauth_token, oauth_token_secret

    Returns:
        Tuple (is_valid, error_message)
    """
    if not token_data:
        return False, "Aucun token fourni"

    if not token_data.get("oauth_token"):
        return False, "oauth_token manquant"

    if not token_data.get("oauth_token_secret"):
        return False, "oauth_token_secret manquant"

    # Vérifier l'expiration si présente
    expires_at = token_data.get("expires_at")
    if expires_at:
        if isinstance(expires_at, datetime):
            if expires_at < datetime.utcnow():
                return False, "Token expiré"
        elif isinstance(expires_at, int | float):
            if datetime.fromtimestamp(expires_at) < datetime.utcnow():
                return False, "Token expiré"

    return True, ""


def is_sync_needed(last_sync: datetime | None, min_interval_minutes: int = 30) -> bool:
    """
    Détermine si une synchronisation est nécessaire.

    Args:
        last_sync: Date/heure de la dernière sync
        min_interval_minutes: Intervalle minimum entre syncs

    Returns:
        True si une sync est nécessaire
    """
    if last_sync is None:
        return True

    elapsed = datetime.utcnow() - last_sync
    return elapsed > timedelta(minutes=min_interval_minutes)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE DATES ET PÉRIODES
# ═══════════════════════════════════════════════════════════


def get_sync_date_range(days_back: int = 7) -> tuple[date, date]:
    """
    Calcule la plage de dates pour la synchronisation.

    Args:
        days_back: Nombre de jours en arrière

    Returns:
        Tuple (start_date, end_date)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def date_to_garmin_timestamp(d: date) -> int:
    """
    Convertit une date en timestamp Garmin (début de journée).

    Args:
        d: Date à convertir

    Returns:
        Timestamp en secondes
    """
    return int(datetime.combine(d, datetime.min.time()).timestamp())


def build_api_params(start_date: date, end_date: date) -> dict:
    """
    Construit les paramètres de requête API Garmin.

    Args:
        start_date: Date de début
        end_date: Date de fin

    Returns:
        Dict de paramètres pour l'API
    """
    return {
        "uploadStartTimeInSeconds": date_to_garmin_timestamp(start_date),
        "uploadEndTimeInSeconds": int(datetime.combine(end_date, datetime.max.time()).timestamp()),
    }
