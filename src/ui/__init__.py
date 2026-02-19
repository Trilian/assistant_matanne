"""
UI - Point d'entrée unifié optimisé
Architecture claire : core/ components/ feedback/ layout/ tablet/ integrations/
"""

# Core (modules, forms, io)
# Components - Atoms
# Components - Forms
# Components - Data
# Components - Layouts
# Components - Dynamic
# Components - Alertes
# Components - Charts
# Components - Metrics
# Components - System
from .components import (
    Modale,
    afficher_sante_systeme,
    afficher_timeline_activites,
    alerte_stock,
    badge,
    barre_progression,
    barre_recherche,
    boite_info,
    boutons_export,
    carte_item,
    carte_metrique,
    carte_metrique_avancee,
    champ_formulaire,
    disposition_grille,
    etat_vide,
    filtres_rapides,
    graphique_inventaire_categories,
    graphique_repartition_repas,
    indicateur_sante_systeme,
    ligne_metriques,
    notification,
    pagination,
    panneau_filtres,
    separateur,
    tableau_donnees,
    widget_jules_apercu,
    widget_meteo_jour,
)

# Feedback
from .feedback import (
    EtatChargement,
    GestionnaireNotifications,
    SuiviProgression,
    afficher_avertissement,
    afficher_erreur,
    afficher_info,
    afficher_succes,
    chargeur_squelette,
    indicateur_chargement,
    spinner_intelligent,
)

# Integrations (Google Calendar, etc.)
from .integrations import (
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL,
    render_google_calendar_config,
    render_quick_sync_button,
    render_sync_status,
    verifier_config_google,
)

# Tablet mode
from .tablet import (
    CSS_MODE_CUISINE,
    CSS_TABLETTE,
    ModeTablette,
    afficher_selecteur_mode,
    afficher_vue_recette_cuisine,
    appliquer_mode_tablette,
    bouton_tablette,
    definir_mode_tablette,
    fermer_mode_tablette,
    grille_selection_tablette,
    liste_cases_tablette,
    obtenir_mode_tablette,
    saisie_nombre_tablette,
)

# Views (vues UI extraites des services)
from .views import (
    afficher_activite_utilisateur,
    afficher_badge_notifications_jeux,
    afficher_demande_permission_push,
    afficher_formulaire_connexion,
    afficher_import_recette,
    afficher_indicateur_frappe,
    afficher_indicateur_presence,
    afficher_invite_installation_pwa,
    afficher_liste_notifications_jeux,
    afficher_menu_utilisateur,
    afficher_meteo_jardin,
    afficher_notification_jeux,
    afficher_parametres_profil,
    afficher_preferences_notification,
    afficher_sauvegarde,
    afficher_statistiques_activite,
    afficher_statut_synchronisation,
    afficher_timeline_activite,
    injecter_meta_pwa,
    require_authenticated,
    require_role,
)

__all__ = [
    # Components - Atoms
    "alerte_stock",
    "badge",
    "etat_vide",
    "carte_metrique",
    "notification",
    "separateur",
    "boite_info",
    # Components - Forms
    "champ_formulaire",
    "barre_recherche",
    "panneau_filtres",
    "filtres_rapides",
    # Components - Data
    "pagination",
    "ligne_metriques",
    "boutons_export",
    "tableau_donnees",
    "barre_progression",
    # Components - Layouts
    "disposition_grille",
    "carte_item",
    # Components - Dynamic
    "Modale",
    # Components - Charts
    "graphique_repartition_repas",
    "graphique_inventaire_categories",
    # Components - Metrics
    "carte_metrique_avancee",
    "widget_jules_apercu",
    "widget_meteo_jour",
    # Components - System
    "indicateur_sante_systeme",
    "afficher_sante_systeme",
    "afficher_timeline_activites",
    # Feedback
    "spinner_intelligent",
    "indicateur_chargement",
    "chargeur_squelette",
    "SuiviProgression",
    "EtatChargement",
    "GestionnaireNotifications",
    "afficher_succes",
    "afficher_erreur",
    "afficher_avertissement",
    "afficher_info",
    # Tablet
    "ModeTablette",
    "obtenir_mode_tablette",
    "definir_mode_tablette",
    "CSS_TABLETTE",
    "CSS_MODE_CUISINE",
    "appliquer_mode_tablette",
    "fermer_mode_tablette",
    "bouton_tablette",
    "grille_selection_tablette",
    "saisie_nombre_tablette",
    "liste_cases_tablette",
    "afficher_vue_recette_cuisine",
    "afficher_selecteur_mode",
    # Integrations
    "GOOGLE_SCOPES",
    "REDIRECT_URI_LOCAL",
    "verifier_config_google",
    "render_google_calendar_config",
    "render_sync_status",
    "render_quick_sync_button",
    # Views
    "afficher_demande_permission_push",
    "afficher_preferences_notification",
    "afficher_meteo_jardin",
    "afficher_sauvegarde",
    "afficher_formulaire_connexion",
    "afficher_menu_utilisateur",
    "afficher_parametres_profil",
    "require_authenticated",
    "require_role",
    "afficher_timeline_activite",
    "afficher_activite_utilisateur",
    "afficher_statistiques_activite",
    "afficher_import_recette",
    "afficher_indicateur_presence",
    "afficher_indicateur_frappe",
    "afficher_statut_synchronisation",
    "afficher_invite_installation_pwa",
    "injecter_meta_pwa",
    "afficher_badge_notifications_jeux",
    "afficher_notification_jeux",
    "afficher_liste_notifications_jeux",
]
