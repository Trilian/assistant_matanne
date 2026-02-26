"""
Views - Vues UI extraites des services (PEP 562 lazy imports).

Ce package contient les fonctions d'affichage (afficher_*)
qui ont été extraites des services pour respecter la séparation des responsabilités.

Structure:
- notifications.py: UI des notifications push/préférences
- meteo.py: UI météo pour jardin et activités
- sauvegarde.py: UI de backup/restauration
- authentification.py: UI d'authentification et profil
- historique.py: UI de l'historique d'activité
- import_recettes.py: UI d'import de recettes depuis URL
- synchronisation.py: UI de synchronisation Web/PWA
- jeux.py: UI du module jeux/paris
"""

from __future__ import annotations

import importlib
from typing import Any

# ═══════════════════════════════════════════════════════════
# Mapping paresseux : nom → (module relatif, attribut)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Authentification
    "afficher_formulaire_connexion": (".authentification", "afficher_formulaire_connexion"),
    "afficher_menu_utilisateur": (".authentification", "afficher_menu_utilisateur"),
    "afficher_parametres_profil": (".authentification", "afficher_parametres_profil"),
    "require_authenticated": (".authentification", "require_authenticated"),
    "require_role": (".authentification", "require_role"),
    # Historique
    "afficher_activite_utilisateur": (".historique", "afficher_activite_utilisateur"),
    "afficher_statistiques_activite": (".historique", "afficher_statistiques_activite"),
    "afficher_timeline_activite": (".historique", "afficher_timeline_activite"),
    # Import recettes
    "afficher_import_recette": (".import_recettes", "afficher_import_recette"),
    # Jeux
    "afficher_badge_notifications_jeux": (".jeux", "afficher_badge_notifications_jeux"),
    "afficher_liste_notifications_jeux": (".jeux", "afficher_liste_notifications_jeux"),
    "afficher_notification_jeux": (".jeux", "afficher_notification_jeux"),
    # Météo
    "afficher_meteo_jardin": (".meteo", "afficher_meteo_jardin"),
    # Notifications
    "afficher_demande_permission_push": (".notifications", "afficher_demande_permission_push"),
    "afficher_preferences_notification": (".notifications", "afficher_preferences_notification"),
    # PWA
    "afficher_invite_installation_pwa": (".pwa", "afficher_invite_installation_pwa"),
    "injecter_meta_pwa": (".pwa", "injecter_meta_pwa"),
    # Sauvegarde
    "afficher_sauvegarde": (".sauvegarde", "afficher_sauvegarde"),
    # Synchronisation
    "afficher_indicateur_frappe": (".synchronisation", "afficher_indicateur_frappe"),
    "afficher_indicateur_presence": (".synchronisation", "afficher_indicateur_presence"),
    "afficher_statut_synchronisation": (".synchronisation", "afficher_statut_synchronisation"),
}


def __getattr__(name: str) -> Any:
    """PEP 562 — import paresseux à la première utilisation."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
