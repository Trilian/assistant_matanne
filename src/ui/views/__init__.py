"""
Views - Vues UI extraites des services.

Ce package contient les fonctions d'affichage (render_*, afficher_*)
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

from .authentification import (
    afficher_formulaire_connexion,
    afficher_menu_utilisateur,
    afficher_parametres_profil,
    require_authenticated,
    require_role,
)
from .historique import (
    afficher_activite_utilisateur,
    afficher_statistiques_activite,
    afficher_timeline_activite,
)
from .import_recettes import (
    afficher_import_recette,
)
from .jeux import (
    afficher_badge_notifications_jeux,
    afficher_liste_notifications_jeux,
    afficher_notification_jeux,
)
from .meteo import (
    afficher_meteo_jardin,
)
from .notifications import (
    afficher_demande_permission_push,
    afficher_preferences_notification,
)
from .sauvegarde import (
    afficher_sauvegarde,
)
from .synchronisation import (
    afficher_indicateur_frappe,
    afficher_indicateur_presence,
    afficher_invite_installation_pwa,
    afficher_statut_synchronisation,
)

__all__ = [
    # Notifications
    "afficher_demande_permission_push",
    "afficher_preferences_notification",
    # Météo
    "afficher_meteo_jardin",
    # Sauvegarde
    "afficher_sauvegarde",
    # Authentification
    "afficher_formulaire_connexion",
    "afficher_menu_utilisateur",
    "afficher_parametres_profil",
    "require_authenticated",
    "require_role",
    # Historique
    "afficher_timeline_activite",
    "afficher_activite_utilisateur",
    "afficher_statistiques_activite",
    # Import recettes
    "afficher_import_recette",
    # Synchronisation
    "afficher_indicateur_presence",
    "afficher_indicateur_frappe",
    "afficher_statut_synchronisation",
    "afficher_invite_installation_pwa",
    # Jeux
    "afficher_badge_notifications_jeux",
    "afficher_notification_jeux",
    "afficher_liste_notifications_jeux",
]
