"""
UI Components - Point d'entrée
Composants UI réutilisables organisés par thème
"""

# Alertes
from .alertes import alerte_stock

# Atoms
from .atoms import badge, boite_info, carte_metrique, etat_vide, notification, separateur

# Data
from .data import (
    barre_progression,
    boutons_export,
    indicateur_statut,
    ligne_metriques,
    pagination,
    tableau_donnees,
)

# Dynamic
from .dynamic import AssistantEtapes, ListeDynamique, Modale

# Forms
from .forms import barre_recherche, champ_formulaire, filtres_rapides, panneau_filtres

# Layouts
from .layouts import (
    carte_item,
    conteneur_carte,
    disposition_grille,
    disposition_onglets,
    section_pliable,
)

__all__ = [
    # Alertes
    "alerte_stock",
    # Atoms
    "badge",
    "etat_vide",
    "carte_metrique",
    "notification",
    "separateur",
    "boite_info",
    # Forms
    "champ_formulaire",
    "barre_recherche",
    "panneau_filtres",
    "filtres_rapides",
    # Data
    "pagination",
    "ligne_metriques",
    "boutons_export",
    "tableau_donnees",
    "barre_progression",
    "indicateur_statut",
    # Layouts
    "disposition_grille",
    "carte_item",
    "section_pliable",
    "disposition_onglets",
    "conteneur_carte",
    # Dynamic
    "Modale",
    "ListeDynamique",
    "AssistantEtapes",
]
