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
    AssistantEtapes,
    ListeDynamique,
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
    conteneur_carte,
    disposition_grille,
    disposition_onglets,
    etat_vide,
    filtres_rapides,
    graphique_activite_semaine,
    graphique_inventaire_categories,
    graphique_progression_objectifs,
    graphique_repartition_repas,
    indicateur_sante_systeme,
    indicateur_statut,
    ligne_metriques,
    notification,
    pagination,
    panneau_filtres,
    section_pliable,
    separateur,
    tableau_donnees,
    widget_jules_apercu,
    widget_meteo_jour,
)
from .core import (
    # Alias compatibilité
    BaseIOService,
    BaseModuleUI,
    # Nouveaux noms français
    ConfigurationIO,
    ConfigurationModule,
    ConstructeurFormulaire,
    FormBuilder,
    IOConfig,
    ModuleConfig,
    ModuleUIBase,
    ServiceIOBase,
    create_io_service,
    create_module_ui,
    creer_module_ui,
    creer_service_io,
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
    KITCHEN_MODE_CSS,
    TABLET_CSS,
    TabletMode,
    apply_tablet_mode,
    close_tablet_mode,
    get_tablet_mode,
    render_kitchen_recipe_view,
    render_mode_selector,
    set_tablet_mode,
    tablet_button,
    tablet_checklist,
    tablet_number_input,
    tablet_select_grid,
)

__all__ = [
    # Core - Nouveaux noms français
    "ConfigurationModule",
    "ModuleUIBase",
    "creer_module_ui",
    "ConstructeurFormulaire",
    "ConfigurationIO",
    "ServiceIOBase",
    "creer_service_io",
    # Core - Alias compatibilité
    "BaseModuleUI",
    "ModuleConfig",
    "create_module_ui",
    "FormBuilder",
    "BaseIOService",
    "IOConfig",
    "create_io_service",
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
    "indicateur_statut",
    # Components - Layouts
    "disposition_grille",
    "carte_item",
    "section_pliable",
    "disposition_onglets",
    "conteneur_carte",
    # Components - Dynamic
    "Modale",
    "ListeDynamique",
    "AssistantEtapes",
    # Components - Charts
    "graphique_repartition_repas",
    "graphique_inventaire_categories",
    "graphique_activite_semaine",
    "graphique_progression_objectifs",
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
    "TabletMode",
    "get_tablet_mode",
    "set_tablet_mode",
    "TABLET_CSS",
    "KITCHEN_MODE_CSS",
    "apply_tablet_mode",
    "close_tablet_mode",
    "tablet_button",
    "tablet_select_grid",
    "tablet_number_input",
    "tablet_checklist",
    "render_kitchen_recipe_view",
    "render_mode_selector",
    # Integrations
    "GOOGLE_SCOPES",
    "REDIRECT_URI_LOCAL",
    "verifier_config_google",
    "render_google_calendar_config",
    "render_sync_status",
    "render_quick_sync_button",
]
