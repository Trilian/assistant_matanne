"""
Fonctions utilitaires pour les préférences et heures silencieuses des notifications.

Vérification des types activés, gestion des périodes silencieuses
et décision d'envoi basée sur les préférences utilisateur.
"""

from datetime import datetime

from src.services.notifications.types import TypeNotification

# ═══════════════════════════════════════════════════════════
# VÉRIFICATION DES PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


def obtenir_mapping_types_notification() -> dict[TypeNotification, str]:
    """
    Retourne le mapping entre types de notification et préférences utilisateur.

    Returns:
        Dict {TypeNotification: nom_preference}
    """
    return {
        TypeNotification.STOCK_BAS: "alertes_stock",
        TypeNotification.PEREMPTION_ALERTE: "alertes_peremption",
        TypeNotification.PEREMPTION_CRITIQUE: "alertes_peremption",
        TypeNotification.RAPPEL_REPAS: "rappels_repas",
        TypeNotification.RAPPEL_ACTIVITE: "rappels_activites",
        TypeNotification.LISTE_PARTAGEE: "mises_a_jour_courses",
        TypeNotification.LISTE_MISE_A_JOUR: "mises_a_jour_courses",
        TypeNotification.RAPPEL_JALON: "rappels_famille",
        TypeNotification.RAPPEL_SANTE: "rappels_famille",
        TypeNotification.MISE_A_JOUR_SYSTEME: "mises_a_jour_systeme",
        TypeNotification.SYNC_TERMINEE: "mises_a_jour_systeme",
    }


def verifier_type_notification_active(
    type_notification: TypeNotification | str, preferences: dict
) -> bool:
    """
    Vérifie si un type de notification est activé pour l'utilisateur.

    Args:
        type_notification: Type de notification
        preferences: Dict des préférences utilisateur

    Returns:
        True si le type est activé
    """
    if isinstance(type_notification, str):
        try:
            type_notification = TypeNotification(type_notification)
        except ValueError:
            return True  # Type inconnu, activer par défaut

    mapping = obtenir_mapping_types_notification()
    pref_key = mapping.get(type_notification, None)

    if pref_key is None:
        return True  # Type sans préférence, activer par défaut

    return preferences.get(pref_key, True)


# ═══════════════════════════════════════════════════════════
# GESTION DES HEURES SILENCIEUSES
# ═══════════════════════════════════════════════════════════


def est_heures_silencieuses(
    heure_courante: int, heure_debut: int | None, heure_fin: int | None
) -> bool:
    """
    Vérifie si l'heure courante est dans la période silencieuse.

    Gère le cas où la période silencieuse passe par minuit
    (ex: 22h -> 7h).

    Args:
        heure_courante: Heure actuelle (0-23)
        heure_debut: Heure de début de silence (None = pas de silence)
        heure_fin: Heure de fin de silence

    Returns:
        True si dans les heures silencieuses
    """
    if heure_debut is None or heure_fin is None:
        return False

    # Valider l'heure
    if not 0 <= heure_courante <= 23:
        return False

    if heure_debut > heure_fin:
        # Passe par minuit (ex: 22h -> 7h)
        return heure_courante >= heure_debut or heure_courante < heure_fin
    else:
        # Normal (ex: 1h -> 6h)
        return heure_debut <= heure_courante < heure_fin


def peut_envoyer_pendant_silence(type_notification: TypeNotification | str) -> bool:
    """
    Vérifie si un type de notification peut être envoyé pendant les heures silencieuses.

    Certaines notifications critiques sont toujours envoyées.

    Args:
        type_notification: Type de notification

    Returns:
        True si peut être envoyé pendant silence
    """
    if isinstance(type_notification, str):
        try:
            type_notification = TypeNotification(type_notification)
        except ValueError:
            return False

    # Seules les alertes critiques passent
    types_critiques = {
        TypeNotification.PEREMPTION_CRITIQUE,
    }

    return type_notification in types_critiques


def doit_envoyer_notification(
    type_notification: TypeNotification | str,
    preferences: dict,
    heure_courante: int | None = None,
    nombre_envoyes_cette_heure: int = 0,
) -> tuple[bool, str]:
    """
    Vérifie si une notification doit être envoyée.

    Prend en compte:
    - Les préférences utilisateur
    - Les heures silencieuses
    - La limite par heure

    Args:
        type_notification: Type de notification
        preferences: Préférences utilisateur
        heure_courante: Heure actuelle (None = auto)
        nombre_envoyes_cette_heure: Nombre de notifications déjà envoyées cette heure

    Returns:
        Tuple (doit_envoyer, raison)
    """
    if heure_courante is None:
        heure_courante = datetime.now().hour

    # 1. Vérifier si le type est activé
    if not verifier_type_notification_active(type_notification, preferences):
        return False, "Type de notification désactivé"

    # 2. Vérifier les heures silencieuses
    heure_debut = preferences.get("heures_silencieuses_debut")
    heure_fin = preferences.get("heures_silencieuses_fin")

    if est_heures_silencieuses(heure_courante, heure_debut, heure_fin):
        if not peut_envoyer_pendant_silence(type_notification):
            return False, "Heures silencieuses actives"

    # 3. Vérifier la limite par heure
    max_par_heure = preferences.get("max_par_heure", 5)
    if nombre_envoyes_cette_heure >= max_par_heure:
        return False, f"Limite par heure atteinte ({max_par_heure})"

    return True, ""
