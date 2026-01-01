"""
State Unifié - StateManager Complet
Corrigé avec toutes les méthodes manquantes
"""
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    """État global de l'application"""
    # Navigation
    current_module: str = "accueil"
    previous_module: Optional[str] = None
    navigation_history: List[str] = field(default_factory=list)

    # Utilisateur
    user_name: str = "Anne"
    unread_notifications: int = 0

    # Agent IA
    agent_ia: Optional[Any] = None

    # Recettes
    viewing_recipe_id: Optional[int] = None
    editing_recipe_id: Optional[int] = None
    adapt_baby_recipe_id: Optional[int] = None

    # Inventaire
    viewing_article_id: Optional[int] = None
    editing_article_id: Optional[int] = None

    # Planning
    viewing_planning_id: Optional[int] = None
    semaine_actuelle: Optional[Any] = None
    adding_repas_planning_id: Optional[int] = None
    adding_repas_jour: Optional[int] = None
    adding_repas_date: Optional[Any] = None
    editing_repas_id: Optional[int] = None

    # UI States
    show_add_form: bool = False
    show_ia_generation: bool = False
    show_clear_confirm: bool = False
    show_notifications: bool = False
    show_add_repas_form: bool = False
    active_tab: Optional[str] = None

    # Flags
    debug_mode: bool = False
    cache_enabled: bool = True

    def __post_init__(self):
        if not self.navigation_history:
            self.navigation_history = [self.current_module]


class StateManager:
    """Gestionnaire centralisé du state"""
    STATE_KEY = "app_state"

    @staticmethod
    def init():
        """Initialise le state si pas déjà fait"""
        if StateManager.STATE_KEY not in st.session_state:
            st.session_state[StateManager.STATE_KEY] = AppState()
            logger.info("✅ AppState initialisé")

    @staticmethod
    def get() -> AppState:
        """Récupère le state actuel"""
        StateManager.init()
        return st.session_state[StateManager.STATE_KEY]

    @staticmethod
    def navigate_to(module: str):
        """
        Navigue vers un module

        Args:
            module: Nom du module (ex: "cuisine.recettes")
        """
        state = StateManager.get()

        if state.current_module != module:
            state.previous_module = state.current_module
            state.navigation_history.append(module)

            # Limiter taille historique
            if len(state.navigation_history) > 50:
                state.navigation_history = state.navigation_history[-50:]

        state.current_module = module
        logger.info(f"Navigation: {module}")

    @staticmethod
    def go_back():
        """Retourne au module précédent"""
        state = StateManager.get()

        if state.previous_module:
            StateManager.navigate_to(state.previous_module)
        elif len(state.navigation_history) > 1:
            state.navigation_history.pop()
            previous = state.navigation_history[-1]
            StateManager.navigate_to(previous)

    @staticmethod
    def get_navigation_breadcrumb() -> List[str]:
        """
        Retourne le fil d'Ariane de navigation

        Returns:
            Liste des modules parcourus (ex: ["Accueil", "Cuisine", "Recettes"])
        """
        state = StateManager.get()

        if not state.navigation_history:
            return ["Accueil"]

        # Convertir chemins modules en labels
        breadcrumb = []
        for module in state.navigation_history[-5:]:  # 5 derniers
            label = StateManager._module_to_label(module)
            breadcrumb.append(label)

        return breadcrumb

    @staticmethod
    def _module_to_label(module: str) -> str:
        """
        Convertit nom module en label lisible

        Args:
            module: "cuisine.recettes" -> "Recettes"
        """
        label_map = {
            "accueil": "Accueil",
            "cuisine.recettes": "Recettes",
            "cuisine.inventaire": "Inventaire",
            "cuisine.planning_semaine": "Planning",
            "cuisine.courses": "Courses",
            "famille.suivi_jules": "Suivi Jules",
            "famille.bien_etre": "Bien-être",
            "famille.routines": "Routines",
            "maison.projets": "Projets",
            "maison.jardin": "Jardin",
            "maison.entretien": "Entretien",
            "planning.calendrier": "Calendrier",
            "planning.vue_ensemble": "Vue d'ensemble",
            "parametres": "Paramètres",
        }

        return label_map.get(module, module.split(".")[-1].capitalize())

    @staticmethod
    def reset():
        """Réinitialise complètement le state"""
        if StateManager.STATE_KEY in st.session_state:
            del st.session_state[StateManager.STATE_KEY]

        StateManager.init()
        logger.info("🔄 State réinitialisé")

    @staticmethod
    def get_state_summary() -> Dict:
        """
        Retourne résumé du state pour debug

        Returns:
            Dict avec infos clés du state
        """
        state = StateManager.get()

        return {
            "current_module": state.current_module,
            "previous_module": state.previous_module,
            "navigation_history": state.navigation_history[-10:],  # 10 derniers
            "user_name": state.user_name,
            "debug_mode": state.debug_mode,
            "cache_enabled": state.cache_enabled,
            "ai_available": state.agent_ia is not None,
            "viewing_recipe": state.viewing_recipe_id,
            "viewing_planning": state.viewing_planning_id,
            "unread_notifications": state.unread_notifications,
        }

    @staticmethod
    def clear_ui_states():
        """Nettoie les états UI temporaires"""
        state = StateManager.get()

        # Réinitialiser états UI
        state.show_add_form = False
        state.show_ia_generation = False
        state.show_clear_confirm = False
        state.show_notifications = False
        state.show_add_repas_form = False
        state.active_tab = None

        logger.debug("🧹 États UI nettoyés")

    @staticmethod
    def set_viewing_recipe(recipe_id: Optional[int]):
        """Définit recette en cours de visualisation"""
        state = StateManager.get()
        state.viewing_recipe_id = recipe_id

        if recipe_id:
            logger.debug(f"👁️ Visualisation recette {recipe_id}")

    @staticmethod
    def set_editing_recipe(recipe_id: Optional[int]):
        """Définit recette en cours d'édition"""
        state = StateManager.get()
        state.editing_recipe_id = recipe_id

        if recipe_id:
            logger.debug(f"✏️ Édition recette {recipe_id}")

    @staticmethod
    def set_viewing_planning(planning_id: Optional[int]):
        """Définit planning en cours de visualisation"""
        state = StateManager.get()
        state.viewing_planning_id = planning_id

        if planning_id:
            logger.debug(f"👁️ Visualisation planning {planning_id}")

    @staticmethod
    def increment_notifications():
        """Incrémente compteur notifications"""
        state = StateManager.get()
        state.unread_notifications += 1

    @staticmethod
    def clear_notifications():
        """Réinitialise notifications"""
        state = StateManager.get()
        state.unread_notifications = 0

    @staticmethod
    def toggle_debug_mode():
        """Active/désactive mode debug"""
        state = StateManager.get()
        state.debug_mode = not state.debug_mode
        logger.info(f"🐛 Debug mode: {'ON' if state.debug_mode else 'OFF'}")

    @staticmethod
    def is_in_module(module_prefix: str) -> bool:
        """
        Vérifie si on est dans un module spécifique

        Args:
            module_prefix: Préfixe module (ex: "cuisine")

        Returns:
            True si module courant commence par préfixe
        """
        state = StateManager.get()
        return state.current_module.startswith(module_prefix)

    @staticmethod
    def get_module_context() -> Dict[str, Any]:
        """
        Retourne contexte du module actuel

        Returns:
            Dict avec infos contextuelles du module
        """
        state = StateManager.get()

        context = {
            "module": state.current_module,
            "breadcrumb": StateManager.get_navigation_breadcrumb(),
        }

        # Ajouter contexte spécifique selon module
        if state.current_module.startswith("cuisine.recettes"):
            context["viewing_recipe"] = state.viewing_recipe_id
            context["editing_recipe"] = state.editing_recipe_id

        elif state.current_module.startswith("cuisine.planning"):
            context["viewing_planning"] = state.viewing_planning_id
            context["semaine"] = state.semaine_actuelle

        elif state.current_module.startswith("cuisine.inventaire"):
            context["viewing_article"] = state.viewing_article_id

        return context


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════

def get_state() -> AppState:
    """Raccourci pour récupérer le state"""
    return StateManager.get()


def navigate(module: str):
    """Raccourci pour naviguer"""
    StateManager.navigate_to(module)
    st.rerun()


def go_back():
    """Raccourci pour revenir en arrière"""
    StateManager.go_back()
    st.rerun()


def get_breadcrumb() -> List[str]:
    """Raccourci pour fil d'Ariane"""
    return StateManager.get_navigation_breadcrumb()


def is_debug_mode() -> bool:
    """Raccourci pour vérifier mode debug"""
    state = get_state()
    return state.debug_mode


def clear_ui_states():
    """Raccourci pour nettoyer états UI"""
    StateManager.clear_ui_states()