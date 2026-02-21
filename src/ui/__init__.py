"""
UI - Point d'entrée unifié optimisé (PEP 562 lazy imports).

Architecture claire : core/ components/ feedback/ layout/ tablet/ integrations/
Design system : tokens/ theme/ registry/ hooks_v2/ primitives/ system/

Tous les symboles sont importés paresseusement via ``__getattr__``.
Seul le dictionnaire ``_LAZY_IMPORTS`` est chargé à l'import du package.
"""

from __future__ import annotations

import importlib
from typing import Any

# ═══════════════════════════════════════════════════════════
# Mapping paresseux : nom → (module relatif, attribut)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ── Design Tokens ──────────────────────────────────
    "Couleur": (".tokens", "Couleur"),
    "Espacement": (".tokens", "Espacement"),
    "Rayon": (".tokens", "Rayon"),
    "Typographie": (".tokens", "Typographie"),
    "Ombre": (".tokens", "Ombre"),
    "Transition": (".tokens", "Transition"),
    "ZIndex": (".tokens", "ZIndex"),
    "Variante": (".tokens", "Variante"),
    "obtenir_couleurs_variante": (".tokens", "obtenir_couleurs_variante"),
    # ── Semantic Tokens ────────────────────────────────
    "Sem": (".tokens_semantic", "Sem"),
    "injecter_tokens_semantiques": (".tokens_semantic", "injecter_tokens_semantiques"),
    # ── Accessibility ──────────────────────────────────
    "A11y": (".a11y", "A11y"),
    # ── Animations ─────────────────────────────────────
    "Animation": (".animations", "Animation"),
    "animer": (".animations", "animer"),
    "injecter_animations": (".animations", "injecter_animations"),
    # ── Theme ──────────────────────────────────────────
    "ModeTheme": (".theme", "ModeTheme"),
    "Theme": (".theme", "Theme"),
    "obtenir_theme": (".theme", "obtenir_theme"),
    "appliquer_theme": (".theme", "appliquer_theme"),
    # ── Registry ───────────────────────────────────────
    "ComponentMeta": (".registry", "ComponentMeta"),
    "composant_ui": (".registry", "composant_ui"),
    "obtenir_catalogue": (".registry", "obtenir_catalogue"),
    "rechercher_composants": (".registry", "rechercher_composants"),
    # ── Primitives (Box, Stack, Text) ──────────────────
    "Box": (".primitives", "Box"),
    "BoxProps": (".primitives", "BoxProps"),
    "Stack": (".primitives", "Stack"),
    "HStack": (".primitives", "HStack"),
    "VStack": (".primitives", "VStack"),
    "Text": (".primitives", "Text"),
    "TextProps": (".primitives", "TextProps"),
    # ── System (CVA / TV / StyleSheet) ─────────────────
    "cva": (".system", "cva"),
    "tv": (".system", "tv"),
    "slot": (".system", "slot"),
    "styled": (".system", "styled"),
    "VariantConfig": (".system", "VariantConfig"),
    "BADGE_VARIANTS": (".system", "BADGE_VARIANTS"),
    "BUTTON_VARIANTS": (".system", "BUTTON_VARIANTS"),
    "CARD_SLOTS": (".system", "CARD_SLOTS"),
    "StyleSheet": (".system", "StyleSheet"),
    # ── Components – Atoms ─────────────────────────────
    "alerte_stock": (".components", "alerte_stock"),
    "badge": (".components", "badge"),
    "etat_vide": (".components", "etat_vide"),
    "carte_metrique": (".components", "carte_metrique"),
    "separateur": (".components", "separateur"),
    "boite_info": (".components", "boite_info"),
    "boule_loto": (".components", "boule_loto"),
    # ── Components – Filters ───────────────────────────
    "FilterConfig": (".components", "FilterConfig"),
    "afficher_barre_filtres": (".components", "afficher_barre_filtres"),
    "afficher_recherche": (".components", "afficher_recherche"),
    "afficher_filtres_rapides": (".components", "afficher_filtres_rapides"),
    "appliquer_filtres": (".components", "appliquer_filtres"),
    "appliquer_recherche": (".components", "appliquer_recherche"),
    # ── Components – Forms ─────────────────────────────
    "champ_formulaire": (".components", "champ_formulaire"),
    "barre_recherche": (".components", "barre_recherche"),
    "panneau_filtres": (".components", "panneau_filtres"),
    "filtres_rapides": (".components", "filtres_rapides"),
    "ConfigChamp": (".components", "ConfigChamp"),
    "TypeChamp": (".components", "TypeChamp"),
    # ── Components – Data ──────────────────────────────
    "pagination": (".components", "pagination"),
    "ligne_metriques": (".components", "ligne_metriques"),
    "boutons_export": (".components", "boutons_export"),
    "tableau_donnees": (".components", "tableau_donnees"),
    "barre_progression": (".components", "barre_progression"),
    # ── Components – Layouts ───────────────────────────
    "disposition_grille": (".components", "disposition_grille"),
    "carte_item": (".components", "carte_item"),
    # ── Components – Dynamic ───────────────────────────
    "Modale": (".components", "Modale"),
    # ── Components – Charts ────────────────────────────
    "graphique_repartition_repas": (".components", "graphique_repartition_repas"),
    "graphique_inventaire_categories": (".components", "graphique_inventaire_categories"),
    # ── Components – Metrics ───────────────────────────
    "carte_metrique_avancee": (".components", "carte_metrique_avancee"),
    "widget_jules_apercu": (".components", "widget_jules_apercu"),
    "widget_meteo_jour": (".components", "widget_meteo_jour"),
    "MetricConfig": (".components", "MetricConfig"),
    "afficher_metriques_row": (".components", "afficher_metriques_row"),
    "afficher_stats_cards": (".components", "afficher_stats_cards"),
    "afficher_kpi_banner": (".components", "afficher_kpi_banner"),
    "afficher_progress_metrics": (".components", "afficher_progress_metrics"),
    # ── Components – System ────────────────────────────
    "indicateur_sante_systeme": (".components", "indicateur_sante_systeme"),
    "afficher_sante_systeme": (".components", "afficher_sante_systeme"),
    "afficher_timeline_activites": (".components", "afficher_timeline_activites"),
    # ── Feedback ───────────────────────────────────────
    "spinner_intelligent": (".feedback", "spinner_intelligent"),
    "indicateur_chargement": (".feedback", "indicateur_chargement"),
    "chargeur_squelette": (".feedback", "chargeur_squelette"),
    "SuiviProgression": (".feedback", "SuiviProgression"),
    "EtatChargement": (".feedback", "EtatChargement"),
    "GestionnaireNotifications": (".feedback", "GestionnaireNotifications"),
    "afficher_succes": (".feedback", "afficher_succes"),
    "afficher_erreur": (".feedback", "afficher_erreur"),
    "afficher_avertissement": (".feedback", "afficher_avertissement"),
    "afficher_info": (".feedback", "afficher_info"),
    "afficher_resultat": (".feedback", "afficher_resultat"),
    "afficher_resultat_toast": (".feedback", "afficher_resultat_toast"),
    # ── Hooks v2 ───────────────────────────────────────
    "use_state": (".hooks_v2", "use_state"),
    "use_toggle": (".hooks_v2", "use_toggle"),
    "use_counter": (".hooks_v2", "use_counter"),
    "use_list": (".hooks_v2", "use_list"),
    "use_query": (".hooks_v2", "use_query"),
    "use_mutation": (".hooks_v2", "use_mutation"),
    "use_form": (".hooks_v2", "use_form"),
    "use_service": (".hooks_v2", "use_service"),
    "use_memo": (".hooks_v2", "use_memo"),
    "use_effect": (".hooks_v2", "use_effect"),
    "use_callback": (".hooks_v2", "use_callback"),
    "use_previous": (".hooks_v2", "use_previous"),
    "State": (".hooks_v2", "State"),
    "CounterState": (".hooks_v2", "CounterState"),
    "ToggleState": (".hooks_v2", "ToggleState"),
    "ListState": (".hooks_v2", "ListState"),
    "MutationState": (".hooks_v2", "MutationState"),
    "QueryResult": (".hooks_v2", "QueryResult"),
    "QueryStatus": (".hooks_v2", "QueryStatus"),
    "FormState": (".hooks_v2", "FormState"),
    # ── Integrations ───────────────────────────────────
    "GOOGLE_SCOPES": (".integrations", "GOOGLE_SCOPES"),
    "REDIRECT_URI_LOCAL": (".integrations", "REDIRECT_URI_LOCAL"),
    "verifier_config_google": (".integrations", "verifier_config_google"),
    "afficher_config_google_calendar": (".integrations", "afficher_config_google_calendar"),
    "afficher_statut_sync_google": (".integrations", "afficher_statut_sync_google"),
    "afficher_bouton_sync_rapide": (".integrations", "afficher_bouton_sync_rapide"),
    # ── Tablet ─────────────────────────────────────────
    "ModeTablette": (".tablet", "ModeTablette"),
    "obtenir_mode_tablette": (".tablet", "obtenir_mode_tablette"),
    "definir_mode_tablette": (".tablet", "definir_mode_tablette"),
    "CSS_TABLETTE": (".tablet", "CSS_TABLETTE"),
    "CSS_MODE_CUISINE": (".tablet", "CSS_MODE_CUISINE"),
    "appliquer_mode_tablette": (".tablet", "appliquer_mode_tablette"),
    "fermer_mode_tablette": (".tablet", "fermer_mode_tablette"),
    "bouton_tablette": (".tablet", "bouton_tablette"),
    "grille_selection_tablette": (".tablet", "grille_selection_tablette"),
    "saisie_nombre_tablette": (".tablet", "saisie_nombre_tablette"),
    "liste_cases_tablette": (".tablet", "liste_cases_tablette"),
    "afficher_vue_recette_cuisine": (".tablet", "afficher_vue_recette_cuisine"),
    "afficher_selecteur_mode": (".tablet", "afficher_selecteur_mode"),
    "TimerCuisine": (".tablet", "TimerCuisine"),
    # ── Views ──────────────────────────────────────────
    "afficher_demande_permission_push": (".views", "afficher_demande_permission_push"),
    "afficher_preferences_notification": (".views", "afficher_preferences_notification"),
    "afficher_meteo_jardin": (".views", "afficher_meteo_jardin"),
    "afficher_sauvegarde": (".views", "afficher_sauvegarde"),
    "afficher_formulaire_connexion": (".views", "afficher_formulaire_connexion"),
    "afficher_menu_utilisateur": (".views", "afficher_menu_utilisateur"),
    "afficher_parametres_profil": (".views", "afficher_parametres_profil"),
    "require_authenticated": (".views", "require_authenticated"),
    "require_role": (".views", "require_role"),
    "afficher_timeline_activite": (".views", "afficher_timeline_activite"),
    "afficher_activite_utilisateur": (".views", "afficher_activite_utilisateur"),
    "afficher_statistiques_activite": (".views", "afficher_statistiques_activite"),
    "afficher_import_recette": (".views", "afficher_import_recette"),
    "afficher_indicateur_presence": (".views", "afficher_indicateur_presence"),
    "afficher_indicateur_frappe": (".views", "afficher_indicateur_frappe"),
    "afficher_statut_synchronisation": (".views", "afficher_statut_synchronisation"),
    "afficher_invite_installation_pwa": (".views", "afficher_invite_installation_pwa"),
    "injecter_meta_pwa": (".views", "injecter_meta_pwa"),
    "afficher_badge_notifications_jeux": (".views", "afficher_badge_notifications_jeux"),
    "afficher_notification_jeux": (".views", "afficher_notification_jeux"),
    "afficher_liste_notifications_jeux": (".views", "afficher_liste_notifications_jeux"),
    # ── Testing ────────────────────────────────────────
    "SnapshotTester": (".testing", "SnapshotTester"),
    "ComponentSnapshot": (".testing", "ComponentSnapshot"),
    "assert_html_contains": (".testing", "assert_html_contains"),
    "assert_html_not_contains": (".testing", "assert_html_not_contains"),
}


def __getattr__(name: str) -> Any:
    """PEP 562 — import paresseux à la première utilisation."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        # Cache dans le module dict pour les accès futurs
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
