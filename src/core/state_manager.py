"""
State Manager - Gestion centralisée de l'état de l'application
Remplace l'utilisation dispersée de st.session_state
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import streamlit as st
import logging

logger = logging.getLogger(__name__)


# ===================================
# DATACLASS ÉTAT GLOBAL
# ===================================

@dataclass
class AppState:
    """
    État global de l'application
    Tous les states importants centralisés ici
    """

    # Navigation
    current_module: str = "accueil"
    previous_module: Optional[str] = None
    navigation_history: List[str] = field(default_factory=list)

    # Utilisateur
    user_id: Optional[int] = None
    user_name: Optional[str] = "Anne"

    # Agent IA
    agent_ia: Optional[Any] = None
    chat_history: List[Dict] = field(default_factory=list)

    # ===================================
    # ÉTAT TEMPORAIRE - RECETTES
    # ===================================

    # Édition/Affichage
    viewing_recipe_id: Optional[int] = None
    editing_recipe_id: Optional[int] = None

    # Génération IA
    generated_recipes: List[Dict] = field(default_factory=list)
    generation_in_progress: bool = False

    # Filtres actifs
    recipe_filters: Dict[str, Any] = field(default_factory=dict)
    recipe_search: str = ""
    recipe_sort: str = "nom"  # nom, date, temps

    # ===================================
    # ÉTAT TEMPORAIRE - INVENTAIRE
    # ===================================

    inventory_cache: Optional[Any] = None  # DataFrame
    inventory_cache_time: Optional[datetime] = None
    inventory_filters: Dict[str, Any] = field(default_factory=dict)

    confirming_purchase: Dict[int, bool] = field(default_factory=dict)

    # ===================================
    # ÉTAT TEMPORAIRE - COURSES
    # ===================================

    liste_ia_generee: Optional[Dict] = None
    magasin_actif: str = "Cora"
    budget_prefere: float = 100.0

    # ===================================
    # ÉTAT TEMPORAIRE - PLANNING
    # ===================================

    semaine_actuelle: Optional[date] = None
    planning_actif_id: Optional[int] = None
    editing_repas_id: Optional[int] = None

    # ===================================
    # NOTIFICATIONS
    # ===================================

    notifications: List[Dict] = field(default_factory=list)
    unread_notifications: int = 0

    # ===================================
    # CACHE GLOBAL
    # ===================================

    cache: Dict[str, Any] = field(default_factory=dict)
    cache_timestamps: Dict[str, datetime] = field(default_factory=dict)

    # ===================================
    # FLAGS
    # ===================================

    debug_mode: bool = False
    show_ai_stats: bool = False

    def __post_init__(self):
        """Post-initialisation"""
        if not self.navigation_history:
            self.navigation_history = [self.current_module]


# ===================================
# GESTIONNAIRE DE STATE
# ===================================

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

    # ===================================
    # NAVIGATION
    # ===================================

    @staticmethod
    def navigate_to(module: str):
        """
        Navigue vers un module

        Args:
            module: Nom du module (ex: "cuisine.recettes")
        """
        state = StateManager.get()

        # Sauvegarder l'historique
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
            # Revenir au module d'avant
            state.navigation_history.pop()  # Retirer actuel
            previous = state.navigation_history[-1]
            StateManager.navigate_to(previous)

    @staticmethod
    def get_navigation_breadcrumb() -> List[str]:
        """Retourne le fil d'Ariane"""
        state = StateManager.get()
        return state.navigation_history[-5:]  # 5 derniers

    # ===================================
    # CACHE
    # ===================================

    @staticmethod
    def cache_get(key: str, ttl: int = 300) -> Optional[Any]:
        """
        Récupère du cache avec TTL

        Args:
            key: Clé du cache
            ttl: Time to live en secondes

        Returns:
            Valeur ou None si expiré
        """
        state = StateManager.get()

        if key not in state.cache:
            return None

        # Vérifier expiration
        if key in state.cache_timestamps:
            age = (datetime.now() - state.cache_timestamps[key]).seconds
            if age > ttl:
                # Expiré
                del state.cache[key]
                del state.cache_timestamps[key]
                return None

        return state.cache[key]

    @staticmethod
    def cache_set(key: str, value: Any):
        """Sauvegarde en cache"""
        state = StateManager.get()
        state.cache[key] = value
        state.cache_timestamps[key] = datetime.now()
        logger.debug(f"Cache SET: {key}")

    @staticmethod
    def cache_clear(pattern: Optional[str] = None):
        """
        Vide le cache

        Args:
            pattern: Si fourni, supprime seulement les clés contenant ce pattern
        """
        state = StateManager.get()

        if pattern:
            to_remove = [k for k in state.cache.keys() if pattern in k]
            for key in to_remove:
                del state.cache[key]
                if key in state.cache_timestamps:
                    del state.cache_timestamps[key]
            logger.info(f"Cache cleared: {len(to_remove)} clés avec pattern '{pattern}'")
        else:
            state.cache = {}
            state.cache_timestamps = {}
            logger.info("Cache cleared: tout")

    # ===================================
    # NOTIFICATIONS
    # ===================================

    @staticmethod
    def add_notification(
            message: str,
            type: str = "info",
            module: Optional[str] = None,
            action_link: Optional[str] = None
    ):
        """
        Ajoute une notification

        Args:
            message: Message
            type: info/success/warning/error
            module: Module source
            action_link: Lien d'action (module à ouvrir)
        """
        state = StateManager.get()

        notif = {
            "id": len(state.notifications) + 1,
            "message": message,
            "type": type,
            "module": module,
            "action_link": action_link,
            "timestamp": datetime.now(),
            "read": False
        }

        state.notifications.append(notif)
        state.unread_notifications += 1

        logger.info(f"Notification: {message}")

    @staticmethod
    def mark_notification_read(notif_id: int):
        """Marque une notification comme lue"""
        state = StateManager.get()

        for notif in state.notifications:
            if notif["id"] == notif_id and not notif["read"]:
                notif["read"] = True
                state.unread_notifications = max(0, state.unread_notifications - 1)
                break

    @staticmethod
    def get_unread_notifications() -> List[Dict]:
        """Récupère les notifications non lues"""
        state = StateManager.get()
        return [n for n in state.notifications if not n["read"]]

    @staticmethod
    def clear_notifications():
        """Supprime toutes les notifications"""
        state = StateManager.get()
        state.notifications = []
        state.unread_notifications = 0

    # ===================================
    # RECETTES
    # ===================================

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

    # ===================================
    # INVENTAIRE
    # ===================================

    @staticmethod
    def cache_inventory(df: Any):
        """Cache l'inventaire"""
        state = StateManager.get()
        state.inventory_cache = df
        state.inventory_cache_time = datetime.now()

    @staticmethod
    def get_cached_inventory(max_age: int = 60) -> Optional[Any]:
        """
        Récupère l'inventaire du cache

        Args:
            max_age: Âge max en secondes
        """
        state = StateManager.get()

        if state.inventory_cache is None:
            return None

        if state.inventory_cache_time:
            age = (datetime.now() - state.inventory_cache_time).seconds
            if age > max_age:
                return None

        return state.inventory_cache

    # ===================================
    # HELPERS
    # ===================================

    @staticmethod
    def get_state_summary() -> Dict[str, Any]:
        """Résumé du state pour debug"""
        state = StateManager.get()

        return {
            "current_module": state.current_module,
            "user": state.user_name,
            "cache_size": len(state.cache),
            "notifications": state.unread_notifications,
            "generated_recipes": len(state.generated_recipes),
            "navigation_depth": len(state.navigation_history)
        }


# ===================================
# HELPERS RACCOURCIS
# ===================================

def get_state() -> AppState:
    """Raccourci pour récupérer le state"""
    return StateManager.get()


def navigate(module: str):
    """Raccourci pour naviguer"""
    StateManager.navigate_to(module)
    st.rerun()


def notify(message: str, type: str = "info", action: Optional[str] = None):
    """Raccourci pour notifier"""
    StateManager.add_notification(message, type, action_link=action)


# ===================================
# DÉCORATEUR POUR MODULES
# ===================================

def require_state(func):
    """
    Décorateur pour garantir que le state est initialisé

    Usage:
        @require_state
        def app():
            state = get_state()
            ...
    """
    def wrapper(*args, **kwargs):
        StateManager.init()
        return func(*args, **kwargs)
    return wrapper


# ===================================
# WIDGET DEBUG (optionnel)
# ===================================

def render_state_debug():
    """Widget de debug pour afficher le state (dev uniquement)"""
    import streamlit as st

    state = StateManager.get()

    if not state.debug_mode:
        return

    with st.sidebar.expander("🐛 State Debug", expanded=False):
        summary = StateManager.get_state_summary()

        st.json(summary)

        if st.button("🔄 Reset State"):
            StateManager.reset()
            st.rerun()

        if st.button("🗑️ Clear Cache"):
            StateManager.cache_clear()
            st.success("Cache vidé")