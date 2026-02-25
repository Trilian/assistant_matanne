"""
UI Components - Point d'entrée
Composants UI réutilisables organisés par thème.

Utilise le chargement différé (__getattr__) pour éviter l'import eager
de tous les sous-modules au moment de ``import src.ui.components``.
"""

from __future__ import annotations

from typing import Any

# ═══════════════════════════════════════════════════════════
# LAZY LOADING MAP : nom_public → (module_relatif, nom_dans_module)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Alertes
    "alerte_stock": (".alertes", "alerte_stock"),
    # Atoms
    "badge": (".atoms", "badge"),
    "badge_html": (".atoms", "badge_html"),
    "boite_info": (".atoms", "boite_info"),
    "boite_info_html": (".atoms", "boite_info_html"),
    "boule_loto": (".atoms", "boule_loto"),
    "boule_loto_html": (".atoms", "boule_loto_html"),
    "carte_metrique": (".atoms", "carte_metrique"),
    "etat_vide": (".atoms", "etat_vide"),
    "separateur": (".atoms", "separateur"),
    # Charts
    "graphique_inventaire_categories": (".charts", "graphique_inventaire_categories"),
    "graphique_repartition_repas": (".charts", "graphique_repartition_repas"),
    # Chat contextuel
    "ChatContextuelService": (".chat_contextuel", "ChatContextuelService"),
    "afficher_chat_contextuel": (".chat_contextuel", "afficher_chat_contextuel"),
    # Chat global (Phase D.1)
    "afficher_chat_global": (".chat_global", "afficher_chat_global"),
    # Data
    "barre_progression": (".data", "barre_progression"),
    "boutons_export": (".data", "boutons_export"),
    "ligne_metriques": (".data", "ligne_metriques"),
    "pagination": (".data", "pagination"),
    "tableau_donnees": (".data", "tableau_donnees"),
    # Data Editors
    "editeur_budget": (".data_editors", "editeur_budget"),
    "editeur_budgets_mensuels": (".data_editors", "editeur_budgets_mensuels"),
    "editeur_courses": (".data_editors", "editeur_courses"),
    "editeur_inventaire": (".data_editors", "editeur_inventaire"),
    # Dynamic
    "confirm_dialog": (".dynamic", "confirm_dialog"),
    # Filters
    "FilterConfig": (".filters", "FilterConfig"),
    "afficher_barre_filtres": (".filters", "afficher_barre_filtres"),
    "afficher_filtres_rapides": (".filters", "afficher_filtres_rapides"),
    "afficher_recherche": (".filters", "afficher_recherche"),
    "appliquer_filtres": (".filters", "appliquer_filtres"),
    "appliquer_recherche": (".filters", "appliquer_recherche"),
    # Forms
    "ConfigChamp": (".forms", "ConfigChamp"),
    "TypeChamp": (".forms", "TypeChamp"),
    "barre_recherche": (".forms", "barre_recherche"),
    "champ_formulaire": (".forms", "champ_formulaire"),
    "filtres_rapides": (".forms", "filtres_rapides"),
    "panneau_filtres": (".forms", "panneau_filtres"),
    # Gamification widget (Phase D.4)
    "afficher_badges_complets": (".gamification_widget", "afficher_badges_complets"),
    "afficher_gamification_sidebar": (".gamification_widget", "afficher_gamification_sidebar"),
    "toast_badge": (".gamification_widget", "toast_badge"),
    # Historique Undo
    "afficher_bouton_undo": (".historique_undo", "afficher_bouton_undo"),
    "afficher_historique_actions": (".historique_undo", "afficher_historique_actions"),
    # Jules aujourd'hui
    "carte_resume_jules": (".jules_aujourdhui", "carte_resume_jules"),
    "generer_resume_jules": (".jules_aujourdhui", "generer_resume_jules"),
    "widget_jules_aujourdhui": (".jules_aujourdhui", "widget_jules_aujourdhui"),
    "widget_jules_resume_compact": (".jules_aujourdhui", "widget_jules_resume_compact"),
    # Layouts
    "carte_item": (".layouts", "carte_item"),
    "disposition_grille": (".layouts", "disposition_grille"),
    # Metrics
    "carte_metrique_avancee": (".metrics", "carte_metrique_avancee"),
    "widget_jules_apercu": (".metrics", "widget_jules_apercu"),
    "widget_meteo_jour": (".metrics", "widget_meteo_jour"),
    # Metrics Row
    "MetricConfig": (".metrics_row", "MetricConfig"),
    "afficher_kpi_banner": (".metrics_row", "afficher_kpi_banner"),
    "afficher_metriques_row": (".metrics_row", "afficher_metriques_row"),
    "afficher_progress_metrics": (".metrics_row", "afficher_progress_metrics"),
    "afficher_stats_cards": (".metrics_row", "afficher_stats_cards"),
    # Mode Focus / Zen
    "focus_exit_button": (".mode_focus", "focus_exit_button"),
    "injecter_css_mode_focus": (".mode_focus", "injecter_css_mode_focus"),
    "is_mode_focus": (".mode_focus", "is_mode_focus"),
    "mode_focus_fab": (".mode_focus", "mode_focus_fab"),
    "mode_focus_toggle": (".mode_focus", "mode_focus_toggle"),
    # Notifications live (Phase D.2)
    "widget_notifications_live": (".notifications_live", "widget_notifications_live"),
    # Charts Drill-down
    "graphique_activites_heatmap": (".plotly_drilldown", "graphique_activites_heatmap"),
    "graphique_budget_drilldown": (".plotly_drilldown", "graphique_budget_drilldown"),
    "graphique_inventaire_drilldown": (".plotly_drilldown", "graphique_inventaire_drilldown"),
    "graphique_recettes_drilldown": (".plotly_drilldown", "graphique_recettes_drilldown"),
    # Progressive Loading
    "EtapeChargement": (".progressive_loading", "EtapeChargement"),
    "ProgressiveLoader": (".progressive_loading", "ProgressiveLoader"),
    "charger_avec_progression": (".progressive_loading", "charger_avec_progression"),
    "progressive_loader": (".progressive_loading", "progressive_loader"),
    "skeleton_loading": (".progressive_loading", "skeleton_loading"),
    "status_chargement": (".progressive_loading", "status_chargement"),
    # Qu'est-ce qu'on mange ?
    "widget_qcom_compact": (".quest_ce_quon_mange", "widget_qcom_compact"),
    "widget_quest_ce_quon_mange": (".quest_ce_quon_mange", "widget_quest_ce_quon_mange"),
    # Recherche globale ⌘K
    "RechercheGlobaleService": (".recherche_globale", "RechercheGlobaleService"),
    "afficher_recherche_globale": (".recherche_globale", "afficher_recherche_globale"),
    "afficher_recherche_globale_popover": (
        ".recherche_globale",
        "afficher_recherche_globale_popover",
    ),
    "get_recherche_globale_service": (".recherche_globale", "get_recherche_globale_service"),
    "injecter_raccourcis_clavier": (".recherche_globale", "injecter_raccourcis_clavier"),
    # Streaming
    "StreamingContainer": (".streaming", "StreamingContainer"),
    "safe_write_stream": (".streaming", "safe_write_stream"),
    "streaming_placeholder": (".streaming", "streaming_placeholder"),
    "streaming_response": (".streaming", "streaming_response"),
    "streaming_section": (".streaming", "streaming_section"),
    # System
    "afficher_sante_systeme": (".system", "afficher_sante_systeme"),
    "afficher_timeline_activites": (".system", "afficher_timeline_activites"),
    "indicateur_sante_systeme": (".system", "indicateur_sante_systeme"),
}


def __getattr__(name: str) -> Any:
    """Charge les composants à la demande uniquement."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib

        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        # Cache dans le namespace du module pour les accès suivants
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
