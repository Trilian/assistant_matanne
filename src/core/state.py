"""
State Unifié - State Manager Simplifié
Fusionne core/state/manager.py
"""
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, List, Any
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
        if StateManager.STATE_KEY not in st.session_state:
            st.session_state[StateManager.STATE_KEY] = AppState()
            logger.info("✅ AppState initialisé")

    @staticmethod
    def get() -> AppState:
        StateManager.init()
        return st.session_state[StateManager.STATE_KEY]

    @staticmethod
    def navigate_to(module: str):
        state = StateManager.get()
        if state.current_module != module:
            state.previous_module = state.current_module
            state.navigation_history.append(module)
            if len(state.navigation_history) > 50:
                state.navigation_history = state.navigation_history[-50:]
        state.current_module = module
        logger.info(f"Navigation: {module}")

    @staticmethod
    def go_back():
        state = StateManager.get()
        if state.previous_module:
            StateManager.navigate_to(state.previous_module)
        elif len(state.navigation_history) > 1:
            state.navigation_history.pop()
            previous = state.navigation_history[-1]
            StateManager.navigate_to(previous)


def get_state() -> AppState:
    """Raccourci pour récupérer le state"""
    return StateManager.get()


def navigate(module: str):
    """Raccourci pour naviguer"""
    StateManager.navigate_to(module)
    st.rerun()