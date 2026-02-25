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

# Chat global (assistant IA flottant persistant — Phase D.1)
from .chat_global import afficher_chat_global

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

# Gamification widget (Phase D.4)
from .gamification_widget import (
    afficher_badges_complets,
    afficher_gamification_sidebar,
    toast_badge,
)

# Historique Undo
from .historique_undo import (
    afficher_bouton_undo,
    afficher_historique_actions,
)

# Jules aujourd'hui
from .jules_aujourdhui import (
    carte_resume_jules,
    generer_resume_jules,
    widget_jules_aujourdhui,
    widget_jules_resume_compact,
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

# Mode Focus / Zen
from .mode_focus import (
    focus_exit_button,
    injecter_css_mode_focus,
    is_mode_focus,
    mode_focus_fab,
    mode_focus_toggle,
)

# Notifications live (temps réel — Phase D.2)
from .notifications_live import widget_notifications_live

# Charts Drill-down (graphiques interactifs avec on_select)
from .plotly_drilldown import (
    graphique_activites_heatmap,
    graphique_budget_drilldown,
    graphique_inventaire_drilldown,
    graphique_recettes_drilldown,
)

# Progressive Loading
from .progressive_loading import (
    EtapeChargement,
    ProgressiveLoader,
    charger_avec_progression,
    progressive_loader,
    skeleton_loading,
    status_chargement,
)

# Widget "Qu'est-ce qu'on mange ?"
from .quest_ce_quon_mange import (
    widget_qcom_compact,
    widget_quest_ce_quon_mange,
)

# ═══════════════════════════════════════════════════════════
# INNOVATIONS 10.x (Rapport d'audit)
# ═══════════════════════════════════════════════════════════
# Recherche globale ⌘K
from .recherche_globale import (
    RechercheGlobaleService,
    afficher_recherche_globale,
    afficher_recherche_globale_popover,
    get_recherche_globale_service,
    injecter_raccourcis_clavier,
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
    # ── Innovations 10.x ──
    # Recherche globale ⌘K
    "afficher_recherche_globale",
    "afficher_recherche_globale_popover",
    "injecter_raccourcis_clavier",
    "RechercheGlobaleService",
    "get_recherche_globale_service",
    # Mode Focus / Zen
    "is_mode_focus",
    "mode_focus_toggle",
    "mode_focus_fab",
    "injecter_css_mode_focus",
    "focus_exit_button",
    # Historique Undo
    "afficher_bouton_undo",
    "afficher_historique_actions",
    # Qu'est-ce qu'on mange ?
    "widget_quest_ce_quon_mange",
    "widget_qcom_compact",
    # Jules aujourd'hui
    "widget_jules_aujourdhui",
    "widget_jules_resume_compact",
    "carte_resume_jules",
    "generer_resume_jules",
    # Progressive Loading
    "ProgressiveLoader",
    "progressive_loader",
    "EtapeChargement",
    "charger_avec_progression",
    "skeleton_loading",
    "status_chargement",
    # Chat global (Phase D.1)
    "afficher_chat_global",
    # Notifications live (Phase D.2)
    "widget_notifications_live",
    # Gamification (Phase D.4)
    "afficher_gamification_sidebar",
    "afficher_badges_complets",
    "toast_badge",
]
