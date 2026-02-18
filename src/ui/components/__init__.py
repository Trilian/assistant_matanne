"""
UI Components - Point d'entrée
Composants UI réutilisables organisés par thème
"""

# Alertes
from .alertes import alerte_stock

# Atoms
from .atoms import badge, boite_info, carte_metrique, etat_vide, notification, separateur

# Charts (graphiques Plotly)
from .charts import (
    graphique_activite_semaine,
    graphique_inventaire_categories,
    graphique_progression_objectifs,
    graphique_repartition_repas,
)

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

# Metrics (cartes métriques avancées)
from .metrics import carte_metrique_avancee, widget_jules_apercu, widget_meteo_jour

# System (santé système, timeline)
from .system import afficher_sante_systeme, afficher_timeline_activites, indicateur_sante_systeme

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
    # Charts
    "graphique_repartition_repas",
    "graphique_inventaire_categories",
    "graphique_activite_semaine",
    "graphique_progression_objectifs",
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
    # Metrics
    "carte_metrique_avancee",
    "widget_jules_apercu",
    "widget_meteo_jour",
    # System
    "indicateur_sante_systeme",
    "afficher_sante_systeme",
    "afficher_timeline_activites",
]
