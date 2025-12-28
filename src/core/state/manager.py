"""
State Manager Simplifié
Garde uniquement l'essentiel du state_manager.py original
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import streamlit as st
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

    # Agent IA
    agent_ia: Optional[Any] = None

    # Recettes
    viewing_recipe_id: Optional[int] = None
    editing_recipe_id: Optional[int] = None
    generated_recipes: List[Dict] = field(default_factory=list)

    # Inventaire
    inventory_cache_time: Optional[datetime] = None

    # Planning
    semaine_actuelle: Optional[Any] = None
    planning_actif_id: Optional[int] = None

    # Notifications
    unread_notifications: int = 0

    # Flags
    debug_mode: bool = False

    def __post_init__(self):
        if not self.navigation_history:
            self.navigation_history = [self.current_module]


class StateManager:
    """Gestionnaire centralisé du state"""

    STATE_KEY = "app_state"

    @staticmethod
    def init():
        """Initialise le state si nécessaire"""
        if StateManager.STATE_KEY not in st.session_state:
            st.session_state[StateManager.STATE_KEY] = AppState()
            logger.info("✅ AppState initialisé")

    @staticmethod
    def get() -> AppState:
        """Récupère le state global"""
        StateManager.init()
        return st.session_state[StateManager.STATE_KEY]

    @staticmethod
    def reset():
        """Reset complet du state"""
        st.session_state[StateManager.STATE_KEY] = AppState()
        logger.warning("⚠️ AppState reset")

    # ═══════════════════════════════════════════════════════════
    # NAVIGATION
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def navigate_to(module: str):
        """Navigue vers un module"""
        state = StateManager.get()

        if state.current_module != module:
            state.previous_module = state.current_module
            state.navigation_history.append(module)

            # Limiter historique à 50
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
        """Retourne le fil d'Ariane"""
        state = StateManager.get()
        return state.navigation_history[-5:]

    # ═══════════════════════════════════════════════════════════
    # RECETTES
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def set_viewing_recipe(recipe_id: Optional[int]):
        """Définit la recette en cours de visualisation"""
        state = StateManager.get()
        state.viewing_recipe_id = recipe_id

    @staticmethod
    def set_editing_recipe(recipe_id: Optional[int]):
        """Définit la recette en cours d'édition"""
        state = StateManager.get()
        state.editing_recipe_id = recipe_id

    @staticmethod
    def save_generated_recipes(recipes: List[Dict]):
        """Sauvegarde les recettes générées par IA"""
        state = StateManager.get()
        state.generated_recipes = recipes

    @staticmethod
    def clear_generated_recipes():
        """Vide les recettes générées"""
        state = StateManager.get()
        state.generated_recipes = []

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def get_state_summary() -> Dict[str, Any]:
        """Résumé du state pour debug"""
        state = StateManager.get()

        return {
            "current_module": state.current_module,
            "user": state.user_name,
            "generated_recipes": len(state.generated_recipes),
            "navigation_depth": len(state.navigation_history),
        }


def get_state() -> AppState:
    """Raccourci pour récupérer le state"""
    return StateManager.get()


def navigate(module: str):
    """Raccourci pour naviguer"""
    StateManager.navigate_to(module)
    st.rerun()