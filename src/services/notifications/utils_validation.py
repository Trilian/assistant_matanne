"""
Fonctions utilitaires pour la gestion des compteurs et la validation des notifications.

Génération et parsing des clés de compteur horaire,
validation des abonnements push et des préférences utilisateur.
"""

from datetime import datetime

# ═══════════════════════════════════════════════════════════
# COMPTEUR DE NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


def generer_cle_compteur(user_id: str, dt: datetime | None = None) -> str:
    """
    Génère une clé pour le compteur de notifications par heure.

    Args:
        user_id: ID de l'utilisateur
        dt: Date/heure (défaut: maintenant)

    Returns:
        Clé au format user_id_YYYYMMDDHH
    """
    if dt is None:
        dt = datetime.now()
    return f"{user_id}_{dt.strftime('%Y%m%d%H')}"


def parser_cle_compteur(key: str) -> tuple[str, datetime | None]:
    """
    Parse une clé de compteur pour extraire user_id et heure.

    Args:
        key: Clé au format user_id_YYYYMMDDHH

    Returns:
        Tuple (user_id, datetime)
    """
    if "_" not in key:
        return key, None

    parts = key.rsplit("_", 1)
    user_id = parts[0]

    try:
        dt = datetime.strptime(parts[1], "%Y%m%d%H")
        return user_id, dt
    except ValueError:
        return user_id, None


def doit_reinitialiser_compteur(derniere_cle: str, cle_courante: str) -> bool:
    """
    Vérifie si le compteur doit être remis à zéro (nouvelle heure).

    Args:
        derniere_cle: Dernière clé utilisée
        cle_courante: Clé actuelle

    Returns:
        True si les clés sont différentes (nouvelle heure)
    """
    return derniere_cle != cle_courante


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_abonnement(subscription: dict) -> tuple[bool, str]:
    """
    Valide un abonnement push.

    Args:
        subscription: Dict avec endpoint, keys

    Returns:
        Tuple (is_valid, error_message)
    """
    if not subscription.get("endpoint"):
        return False, "Endpoint manquant"

    if not subscription["endpoint"].startswith("https://"):
        return False, "Endpoint doit être HTTPS"

    keys = subscription.get("keys", {})
    if not keys.get("p256dh"):
        return False, "Clé p256dh manquante"

    if not keys.get("auth"):
        return False, "Clé auth manquante"

    return True, ""


def valider_preferences(preferences: dict) -> tuple[bool, list[str]]:
    """
    Valide les préférences de notification.

    Args:
        preferences: Dict des préférences

    Returns:
        Tuple (is_valid, list_of_warnings)
    """
    warnings = []

    # Vérifier les heures silencieuses
    heure_debut = preferences.get("heures_silencieuses_debut")
    heure_fin = preferences.get("heures_silencieuses_fin")

    if heure_debut is not None and not 0 <= heure_debut <= 23:
        warnings.append("heures_silencieuses_debut doit être entre 0 et 23")

    if heure_fin is not None and not 0 <= heure_fin <= 23:
        warnings.append("heures_silencieuses_fin doit être entre 0 et 23")

    # Vérifier max_par_heure
    max_par_heure = preferences.get("max_par_heure", 5)
    if max_par_heure < 1:
        warnings.append("max_par_heure doit être >= 1")
    elif max_par_heure > 100:
        warnings.append("max_par_heure semble élevé (>100)")

    return len(warnings) == 0, warnings
