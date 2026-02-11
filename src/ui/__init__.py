"""
UI - Point d'entrée unifié optimisé
Architecture claire : core/ components/ feedback/
"""

# Core (modules, forms, io)
# Components - Atoms
# Components - Forms
# Components - Data
# Components - Layouts
# Components - Dynamic
# Components - Alertes
from .components import (
    AssistantEtapes,
    ListeDynamique,
    Modale,
    alerte_stock,
    badge,
    barre_progression,
    boite_info,
    boutons_export,
    carte_item,
    carte_metrique,
    champ_formulaire,
    conteneur_carte,
    disposition_grille,
    disposition_onglets,
    etat_vide,
    filtres_rapides,
    indicateur_statut,
    ligne_metriques,
    notification,
    pagination,
    panneau_filtres,
    barre_recherche,
    section_pliable,
    separateur,
    tableau_donnees,
)
from .core import (
    # Nouveaux noms français
    ConfigurationIO,
    ConfigurationModule,
    ConstructeurFormulaire,
    ModuleUIBase,
    ServiceIOBase,
    creer_module_ui,
    creer_service_io,
    # Alias compatibilité
    BaseIOService,
    BaseModuleUI,
    FormBuilder,
    IOConfig,
    ModuleConfig,
    create_io_service,
    create_module_ui,
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
]
