"""
UI - Point d'entrée unifié optimisé
Architecture claire : core/ components/ feedback/ layout/ tablet/ integrations/
Design system : tokens/ html_builder/ theme/ registry/
"""

# Design System primitives
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
from .a11y import A11y
from .animations import Animation, animer, injecter_animations
from .components import (
    ConfigChamp,
    Modale,
    TypeChamp,
    afficher_sante_systeme,
    afficher_timeline_activites,
    alerte_stock,
    badge,
    barre_progression,
    barre_recherche,
    boite_info,
    boule_loto,
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

# UI 3.0 - Hooks avancés
from .hooks_v2 import (
    FormState,
    QueryResult,
    QueryStatus,
    State,
    use_counter,
    use_form,
    use_list,
    use_mutation,
    use_query,
    use_state,
    use_toggle,
)

# Hooks désactivés (module vide) - utiliser hooks_v2 pour les nouvelles implémentations
# from .hooks import (
#     use_confirmation,
#     use_filtres,
#     use_onglets,
#     use_pagination,
#     use_recherche,
#     use_tri,
# )
from .html_builder import HtmlBuilder, render_html

# Integrations (Google Calendar, etc.)
from .integrations import (
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL,
    afficher_bouton_sync_rapide,
    afficher_config_google_calendar,
    afficher_statut_sync_google,
    verifier_config_google,
)

# UI 3.0 - Primitives (Box, Stack, Text)
from .primitives import Box, BoxProps, HStack, Stack, Text, TextProps, VStack
from .registry import ComponentMeta, composant_ui, obtenir_catalogue, rechercher_composants

# UI 3.0 - Système de variants CVA
from .system import (
    BADGE_VARIANTS,
    BUTTON_VARIANTS,
    CARD_SLOTS,
    StyleSheet,
    VariantConfig,
    cva,
    slot,
    styled,
    tv,
)

# Tablet mode
from .tablet import (
    CSS_MODE_CUISINE,
    CSS_TABLETTE,
    ModeTablette,
    TimerCuisine,
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

# UI 3.0 - Tests visuels
from .testing import (
    ComponentSnapshot,
    SnapshotTester,
    assert_html_contains,
    assert_html_not_contains,
)
from .theme import ModeTheme, Theme, appliquer_theme, obtenir_theme
from .tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Transition,
    Typographie,
    Variante,
    ZIndex,
    obtenir_couleurs_variante,
)
from .tokens_semantic import Sem, injecter_tokens_semantiques

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
    # Design System
    "Couleur",
    "Espacement",
    "Rayon",
    "Typographie",
    "Ombre",
    "Transition",
    "ZIndex",
    "Variante",
    "obtenir_couleurs_variante",
    "Sem",
    "injecter_tokens_semantiques",
    "HtmlBuilder",
    "render_html",
    "A11y",
    "Animation",
    "animer",
    "injecter_animations",
    # Hooks (désactivés - utiliser hooks_v2)
    # "use_pagination",
    # "use_recherche",
    # "use_filtres",
    # "use_confirmation",
    # "use_tri",
    # "use_onglets",
    "ModeTheme",
    "Theme",
    "obtenir_theme",
    "appliquer_theme",
    "ComponentMeta",
    "composant_ui",
    "obtenir_catalogue",
    "rechercher_composants",
    # Components - Atoms
    "alerte_stock",
    "badge",
    "etat_vide",
    "carte_metrique",
    "separateur",
    "boite_info",
    # Components - Forms
    "champ_formulaire",
    "barre_recherche",
    "panneau_filtres",
    "filtres_rapides",
    "ConfigChamp",
    "TypeChamp",
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
    "TimerCuisine",
    # Integrations
    "GOOGLE_SCOPES",
    "REDIRECT_URI_LOCAL",
    "verifier_config_google",
    "afficher_config_google_calendar",
    "afficher_statut_sync_google",
    "afficher_bouton_sync_rapide",
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
    # UI 3.0 - System (CVA variants)
    "cva",
    "tv",
    "slot",
    "VariantConfig",
    "BADGE_VARIANTS",
    "BUTTON_VARIANTS",
    "CARD_SLOTS",
    "StyleSheet",
    "styled",
    # UI 3.0 - Primitives
    "Box",
    "BoxProps",
    "Stack",
    "HStack",
    "VStack",
    "Text",
    "TextProps",
    # UI 3.0 - Hooks v2
    "use_state",
    "use_toggle",
    "use_counter",
    "use_list",
    "use_query",
    "use_mutation",
    "use_form",
    "State",
    "QueryResult",
    "QueryStatus",
    "FormState",
    # UI 3.0 - Testing
    "SnapshotTester",
    "ComponentSnapshot",
    "assert_html_contains",
    "assert_html_not_contains",
]
