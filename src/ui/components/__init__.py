"""
UI Components - Point d'entrée
Composants UI réutilisables organisés par thème
"""

# Alertes
from .alertes import alerte_stock

# Atoms
from .atoms import (
    badge,
    badge_html,
    boite_info,
    boite_info_html,
    boule_loto,
    boule_loto_html,
    carte_metrique,
    etat_vide,
    separateur,
)

# Charts (graphiques Plotly)
from .charts import (
    graphique_inventaire_categories,
    graphique_repartition_repas,
)

# Chat contextuel (assistant IA intégré par module)
from .chat_contextuel import ChatContextuelService, afficher_chat_contextuel

# Data
from .data import (
    barre_progression,
    boutons_export,
    ligne_metriques,
    pagination,
    tableau_donnees,
)

# Data Editors (édition inline via st.data_editor)
from .data_editors import (
    editeur_budget,
    editeur_budgets_mensuels,
    editeur_courses,
    editeur_inventaire,
)

# Dynamic
from .dynamic import Modale, confirm_dialog

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

# Charts Drill-down (graphiques interactifs avec on_select)
from .plotly_drilldown import (
    graphique_activites_heatmap,
    graphique_budget_drilldown,
    graphique_inventaire_drilldown,
    graphique_recettes_drilldown,
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
    # Charts Drill-down
    "graphique_budget_drilldown",
    "graphique_recettes_drilldown",
    "graphique_activites_heatmap",
    "graphique_inventaire_drilldown",
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
    # Data Editors
    "editeur_inventaire",
    "editeur_courses",
    "editeur_budget",
    "editeur_budgets_mensuels",
    # Layouts
    "disposition_grille",
    "carte_item",
    # Dynamic
    "Modale",
    "confirm_dialog",
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
    # Chat contextuel
    "afficher_chat_contextuel",
    "ChatContextuelService",
]
