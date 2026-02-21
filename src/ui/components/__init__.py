"""
UI Components - Point d'entrée
Composants UI réutilisables organisés par thème
"""

# Alertes
from .alertes import alerte_stock

# Atoms
from .atoms import badge, boite_info, boule_loto, carte_metrique, etat_vide, separateur

# Charts (graphiques Plotly)
from .charts import (
    graphique_inventaire_categories,
    graphique_repartition_repas,
)

# Data
from .data import (
    barre_progression,
    boutons_export,
    ligne_metriques,
    pagination,
    tableau_donnees,
)

# Dynamic
from .dynamic import Modale

# Filters (nouveau - composants de filtrage réutilisables)
from .filters import (
    FilterConfig,
    afficher_barre_filtres,
    afficher_filtres_rapides,
    afficher_recherche,
    appliquer_filtres,
    appliquer_recherche,
)

# Forms
from .forms import (
    ConfigChamp,
    TypeChamp,
    barre_recherche,
    champ_formulaire,
    filtres_rapides,
    panneau_filtres,
)

# Layouts
from .layouts import (
    carte_item,
    disposition_grille,
)

# Metrics (cartes métriques avancées)
from .metrics import carte_metrique_avancee, widget_jules_apercu, widget_meteo_jour

# Metrics Row (nouveau - lignes de métriques réutilisables)
from .metrics_row import (
    MetricConfig,
    afficher_kpi_banner,
    afficher_metriques_row,
    afficher_progress_metrics,
    afficher_stats_cards,
)

# Streaming (réponses IA progressives)
from .streaming import (
    StreamingContainer,
    safe_write_stream,
    streaming_placeholder,
    streaming_response,
    streaming_section,
)

# System (santé système, timeline)
from .system import afficher_sante_systeme, afficher_timeline_activites, indicateur_sante_systeme

__all__ = [
    # Alertes
    "alerte_stock",
    # Atoms
    "badge",
    "etat_vide",
    "carte_metrique",
    "separateur",
    "boite_info",
    # Charts
    "graphique_repartition_repas",
    "graphique_inventaire_categories",
    # Filters (nouveau)
    "FilterConfig",
    "afficher_barre_filtres",
    "afficher_recherche",
    "afficher_filtres_rapides",
    "appliquer_filtres",
    "appliquer_recherche",
    # Forms
    "champ_formulaire",
    "barre_recherche",
    "panneau_filtres",
    "filtres_rapides",
    "ConfigChamp",
    "TypeChamp",
    # Data
    "pagination",
    "ligne_metriques",
    "boutons_export",
    "tableau_donnees",
    "barre_progression",
    # Layouts
    "disposition_grille",
    "carte_item",
    # Dynamic
    "Modale",
    # Metrics
    "carte_metrique_avancee",
    "widget_jules_apercu",
    "widget_meteo_jour",
    # Metrics Row (nouveau)
    "MetricConfig",
    "afficher_metriques_row",
    "afficher_stats_cards",
    "afficher_kpi_banner",
    "afficher_progress_metrics",
    # System
    "indicateur_sante_systeme",
    "afficher_sante_systeme",
    "afficher_timeline_activites",
    # Streaming
    "StreamingContainer",
    "streaming_response",
    "streaming_section",
    "streaming_placeholder",
    "safe_write_stream",
]
