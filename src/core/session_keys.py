"""
Constantes nommées pour les clés st.session_state.

Registre centralisé de toutes les clés de session Streamlit utilisées
dans l'application. Élimine les chaînes magiques et prévient les collisions.

Deux mécanismes coexistent:
- **SK** (ci-dessous): Clés statiques centralisées pour l'état global/partagé.
- **KeyNamespace** (``src/ui/keys.py``): Clés dynamiques préfixées par module
  (ex: ``charges__mode_ajout``). Utilisées pour l'état local d'un module.

Règle: Utiliser **SK** pour l'état partagé inter-modules,
**KeyNamespace** pour l'état local d'un module.

Usage:
    from src.core.session_keys import SK
    if SK.BATCH_TYPE not in st.session_state:
        st.session_state[SK.BATCH_TYPE] = "dimanche"

    # Audit des clés en session
    from src.core.session_keys import auditer_session_keys
    rapport = auditer_session_keys()
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# REGISTRE DYNAMIQUE DES CLÉS DE SESSION
# ═══════════════════════════════════════════════════════════


class _SessionKeyRegistry:
    """Registre centralisé qui trace TOUTES les clés de session state.

    Trace les clés statiques (SK.*) et les clés dynamiques (_keys()).
    Permet l'audit, la détection de collisions et le nettoyage.
    """

    def __init__(self) -> None:
        self._static_keys: dict[str, str] = {}  # key → description/source
        self._dynamic_namespaces: dict[str, set[str]] = {}  # prefix → {key_names}
        self._lock = threading.Lock()

    def enregistrer_statique(self, key: str, source: str = "SK") -> None:
        """Enregistre une clé statique."""
        with self._lock:
            self._static_keys[key] = source

    def enregistrer_dynamique(self, namespace: str, key_name: str) -> None:
        """Enregistre une clé dynamique générée par KeyNamespace."""
        with self._lock:
            if namespace not in self._dynamic_namespaces:
                self._dynamic_namespaces[namespace] = set()
            self._dynamic_namespaces[namespace].add(key_name)

    def obtenir_toutes_cles(self) -> dict[str, str]:
        """Retourne toutes les clés connues (statiques + dynamiques)."""
        with self._lock:
            result = dict(self._static_keys)
            for ns, keys in self._dynamic_namespaces.items():
                for k in keys:
                    full_key = f"{ns}__{k}"
                    result[full_key] = f"KeyNamespace({ns})"
            return result

    def detecter_collisions(self) -> list[tuple[str, str, str]]:
        """Détecte les collisions entre clés statiques et dynamiques."""
        collisions: list[tuple[str, str, str]] = []
        with self._lock:
            dynamic_full = {}
            for ns, keys in self._dynamic_namespaces.items():
                for k in keys:
                    full_key = f"{ns}__{k}"
                    dynamic_full[full_key] = f"KeyNamespace({ns})"

            for key in self._static_keys:
                if key in dynamic_full:
                    collisions.append((key, self._static_keys[key], dynamic_full[key]))
        return collisions

    def rapport(self) -> str:
        """Génère un rapport d'audit des clés de session."""
        with self._lock:
            nb_static = len(self._static_keys)
            nb_dynamic_ns = len(self._dynamic_namespaces)
            nb_dynamic_keys = sum(len(v) for v in self._dynamic_namespaces.values())

        collisions = self.detecter_collisions()
        lines = [
            "📊 Audit Session Keys",
            f"  Clés statiques (SK): {nb_static}",
            f"  Namespaces dynamiques: {nb_dynamic_ns}",
            f"  Clés dynamiques totales: {nb_dynamic_keys}",
            f"  Total: {nb_static + nb_dynamic_keys}",
        ]

        if collisions:
            lines.append(f"\n⚠️ {len(collisions)} collision(s):")
            for key, src1, src2 in collisions:
                lines.append(f"  • '{key}': {src1} ↔ {src2}")
        else:
            lines.append("  ✅ Aucune collision")

        if self._dynamic_namespaces:
            lines.append("\n📦 Namespaces actifs:")
            for ns, keys in sorted(self._dynamic_namespaces.items()):
                lines.append(f"  • {ns}: {len(keys)} clés")

        return "\n".join(lines)


# Singleton thread-safe
_registry_lock = threading.Lock()
_registry_instance: _SessionKeyRegistry | None = None


def obtenir_registre_session_keys() -> _SessionKeyRegistry:
    """Obtient l'instance singleton du registre de clés."""
    global _registry_instance
    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = _SessionKeyRegistry()
    return _registry_instance


def auditer_session_keys() -> str:
    """Audit rapide des clés de session — retourne un rapport texte."""
    return obtenir_registre_session_keys().rapport()


# ═══════════════════════════════════════════════════════════
# SESSION KEYS — Clés statiques globales
# ═══════════════════════════════════════════════════════════


class _SessionKeys:
    """Namespace pour les clés de session state GLOBALES/PARTAGÉES.

    Pour l'état local d'un module, utiliser ``KeyNamespace`` à la place.
    """

    __slots__ = ()

    # ─── Core ─────────────────────────────────────────
    ETAT_APP = "etat_app"
    DEBUG_MODE = "debug_mode"

    # ─── Core / IA Rate Limiting ──────────────────────
    RATE_LIMIT_IA = "rate_limit_ia"

    # ─── Core / Cache ─────────────────────────────────
    CACHE_DONNEES = "cache_donnees"
    CACHE_TIMESTAMPS = "cache_timestamps"
    CACHE_DEPENDANCES = "cache_dependances"
    CACHE_STATISTIQUES = "cache_statistiques"
    CACHE_L2_DATA = "_cache_l2_data"

    # ─── UI / Layout ──────────────────────────────────
    SHOW_NOTIFICATIONS = "show_notifications"
    SHOW_LOGIN = "show_login"
    MODE_TABLETTE = "mode_tablette"
    GOOGLE_CALENDAR_CONFIG = "google_calendar_config"

    # ─── Cuisine / Recettes ───────────────────────────
    DETAIL_RECETTE_ID = "detail_recette_id"
    RECETTES_PAGE = "recettes_page"
    RECETTES_PAGE_SIZE = "recettes_page_size"
    FORM_NUM_INGREDIENTS = "form_num_ingredients"
    FORM_NUM_ETAPES = "form_num_etapes"

    # ─── Cuisine / Import Recettes ────────────────────
    EXTRACTED_RECIPE = "extracted_recipe"
    LAST_IMPORTED_RECIPE_NAME = "last_imported_recipe_name"

    # ─── Cuisine / Planificateur Repas ────────────────
    PLANNING_DATA = "planning_data"
    PLANNING_DATE_DEBUT = "planning_date_debut"
    PLANNING_CONSEILS = "planning_conseils"
    PLANNING_SUGGESTIONS_BIO = "planning_suggestions_bio"
    USER_PREFERENCES = "preferences_utilisateurs"
    RECIPE_FEEDBACKS = "retours_recettes"

    # ─── Cuisine / Courses ────────────────────────────
    COURSES_REFRESH = "courses_refresh"
    NEW_ARTICLE_MODE = "new_article_mode"
    EDIT_ARTICLE_ID = "edit_article_id"
    COURSES_PLANNING_RESULTAT = "courses_planning_resultat"
    CURRENT_PAGE = "current_page"
    REALTIME_INITIALIZED = "realtime_initialized"
    USER_ID = "user_id"
    USER_NAME = "user_name"
    LISTE_ACTIVE_ID = "liste_active_id"

    # ─── Cuisine / Inventaire ─────────────────────────
    SHOW_FORM = "show_form"
    REFRESH_COUNTER = "refresh_counter"
    PREDICTIONS_GENERATED = "predictions_generated"
    PREDICTIONS_DATA = "predictions_data"
    SUGGESTIONS_DATA = "suggestions_data"

    # ─── Cuisine / Batch Cooking ──────────────────────
    BATCH_TYPE = "batch_type"
    BATCH_DATA = "batch_data"
    BATCH_DATE = "batch_date"
    BATCH_HEURE = "batch_heure"
    COURSES_DEPUIS_BATCH = "courses_depuis_batch"

    # ─── Cuisine / Planificateur → Courses ────────────
    COURSES_DEPUIS_PLANNING = "courses_depuis_planning"
    PLANNING_STOCK_CONTEXT = "planning_stock_context"

    # ─── Famille / Hub ────────────────────────────────
    FAMILLE_PAGE = "famille_page"

    # ─── Famille / Jules ──────────────────────────────
    JULES_SHOW_AI_ACTIVITIES = "jules_show_ai_activities"
    JULES_CONSEIL_THEME = "jules_conseil_theme"
    JULES_ACTIVITES_FAITES = "jules_activites_faites"

    # ─── Famille / Routines ───────────────────────────
    ADDING_TASK_TO = "adding_task_to"
    RAPPELS_IA = "rappels_ia"
    AGENT_IA = "agent_ia"

    # ─── Famille / Weekend ────────────────────────────
    WEEKEND_ADD_DATE = "weekend_add_date"

    # ─── Famille / Suivi Personnel ────────────────────
    SUIVI_USER = "suivi_user"
    GARMIN_AUTH_USER = "garmin_auth_user"
    GARMIN_REQUEST_TOKEN = "garmin_request_token"

    # ─── Maison / Entretien ───────────────────────────
    MES_OBJETS_ENTRETIEN = "mes_objets_entretien"
    HISTORIQUE_ENTRETIEN = "historique_entretien"
    ENTRETIEN_MODE_AJOUT = "entretien_mode_ajout"
    PIECE_SELECTIONNEE = "piece_selectionnee"

    # ─── Maison / Jardin ──────────────────────────────
    MES_PLANTES_JARDIN = "mes_plantes_jardin"
    RECOLTES_JARDIN = "recoltes_jardin"
    HISTORIQUE_JARDIN = "historique_jardin"
    JARDIN_MODE_AJOUT = "jardin_mode_ajout"
    JARDIN_PLANTE_SELECTIONNEE = "jardin_plante_selectionnee"
    MES_PLANTES = "mes_plantes"

    # ─── Maison / Charges ─────────────────────────────
    FACTURES_CHARGES = "factures_charges"
    BADGES_VUS = "badges_vus"
    PREV_ECO_SCORE = "prev_eco_score"
    CHARGES_MODE_AJOUT = "charges_mode_ajout"

    # ─── Maison / Dépenses ────────────────────────────
    EDIT_DEPENSE_ID = "edit_depense_id"

    # ─── Planning / Calendrier ────────────────────────
    CAL_SEMAINE_DEBUT = "cal_semaine_debut"
    AJOUTER_EVENT_DATE = "ajouter_event_date"
    SHOW_PRINT_MODAL = "show_print_modal"

    # ─── Paramètres ───────────────────────────────────
    DISPLAY_MODE_SELECTION = "display_mode_selection"
    DISPLAY_MODE_KEY = "display_mode_key"
    FOYER_CONFIG = "foyer_config"
    SHOW_MIGRATIONS_HISTORY = "show_migrations_history"
    CACHE_DATA = "cache_data"
    CACHE_STATS = "cache_stats"
    RATE_LIMIT = "rate_limit"

    # ─── Utilitaires / Barcode ────────────────────────
    BARCODE_SERVICE = "barcode_service"
    LAST_WEBRTC_SCAN = "last_webrtc_scan"

    # ─── Utilitaires / Rapports PDF ───────────────────
    RAPPORTS_SERVICE = "rapports_service"
    PREVIEW_STOCKS = "preview_stocks"
    DOWNLOAD_STOCKS = "download_stocks"
    PREVIEW_BUDGET = "preview_budget"
    DOWNLOAD_BUDGET = "download_budget"
    PREVIEW_GASPILLAGE = "preview_gaspillage"
    DOWNLOAD_GASPILLAGE = "download_gaspillage"

    # ─── Utilitaires / Notifications Push ─────────────
    NOTIF_CONFIG = "notif_config"
    NOTIF_DEMO_HISTORY = "notif_demo_history"
    NOTIF_MODE_DEMO = "notif_mode_demo"
    SHOW_NOTIF_HELP = "show_notif_help"

    # ─── Utilitaires / Scan Factures ──────────────────
    HISTORIQUE_FACTURES = "historique_factures"

    # ─── Utilitaires / Recherche Produits ─────────────
    PRODUITS_FAVORIS = "produits_favoris"

    # ─── Templates de clés dynamiques ─────────────────
    # Usage: SK.generated_image(recette_id)
    @staticmethod
    def generated_image(recette_id: int) -> str:
        """Clé pour l'image générée d'une recette."""
        return f"generated_image_{recette_id}"

    @staticmethod
    def show_alternatives(key_prefix: str) -> str:
        """Clé pour afficher les alternatives d'un repas."""
        return f"show_alternatives_{key_prefix}"

    @staticmethod
    def add_repas_midi(key_prefix: str) -> str:
        """Clé pour ajouter un repas du midi."""
        return f"add_repas_{key_prefix}_midi"

    @staticmethod
    def add_repas_soir(key_prefix: str) -> str:
        """Clé pour ajouter un repas du soir."""
        return f"add_repas_{key_prefix}_soir"

    @staticmethod
    def show_details_match(match_id: str) -> str:
        """Clé pour afficher les détails d'un match."""
        return f"show_details_{match_id}"

    @staticmethod
    def page_key(prefix: str) -> str:
        """Clé de pagination."""
        return f"{prefix}_page"

    @staticmethod
    def week_start(prefix: str) -> str:
        """Clé de début de semaine pour le navigateur."""
        return f"{prefix}_start"

    @staticmethod
    def barcode_detected(key: str) -> str:
        """Clé pour les barcodes détectés."""
        return f"{key}_detected"


# Singleton — usage: from src.core.session_keys import SK
SK = _SessionKeys()


# ═══════════════════════════════════════════════════════════
# AUTO-ENREGISTREMENT des clés statiques
# ═══════════════════════════════════════════════════════════


def _enregistrer_cles_statiques() -> None:
    """Enregistre toutes les constantes de SK dans le registre global."""
    registry = obtenir_registre_session_keys()
    for attr in dir(SK):
        if attr.startswith("_") or callable(getattr(SK, attr)):
            continue
        value = getattr(SK, attr)
        if isinstance(value, str):
            registry.enregistrer_statique(value, f"SK.{attr}")


_enregistrer_cles_statiques()


__all__ = [
    "SK",
    "auditer_session_keys",
    "obtenir_registre_session_keys",
]
