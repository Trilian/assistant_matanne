"""
Synchronisation temps réel pour les courses.
"""

from ._common import st, logger, get_realtime_sync_service


def _init_realtime_sync():
    """Initialise la synchronisation temps réel."""
    if "realtime_initialized" not in st.session_state:
        st.session_state.realtime_initialized = False
    
    try:
        sync_service = get_realtime_sync_service()
        
        if sync_service.is_configured and not st.session_state.realtime_initialized:
            # Récupérer l'utilisateur courant
            user_id = st.session_state.get("user_id", "anonymous")
            user_name = st.session_state.get("user_name", "Utilisateur")
            
            # Rejoindre le canal de synchronisation (liste par défaut = 1)
            liste_id = st.session_state.get("liste_active_id", 1)
            
            if sync_service.join_list(liste_id, user_id, user_name):
                st.session_state.realtime_initialized = True
                logger.info(f"Sync temps réel initialisée pour liste {liste_id}")
        
    except Exception as e:
        logger.warning(f"Sync temps réel non disponible: {e}")


def render_realtime_status():
    """Affiche le statut de synchronisation temps réel."""
    try:
        sync_service = get_realtime_sync_service()
        
        if not sync_service.is_configured:
            return
        
        from src.services.realtime_sync import (
            render_presence_indicator,
            render_typing_indicator,
            render_sync_status,
        )
        
        # Statut dans la sidebar
        with st.sidebar:
            st.divider()
            st.markdown("### 📄 Synchronisation")
            
            render_sync_status()
            render_presence_indicator()
            
            # Afficher qui tape
            if sync_service.state.users_present:
                typing_users = [
                    u for u in sync_service.state.users_present.values()
                    if u.is_typing
                ]
                if typing_users:
                    render_typing_indicator()
    
    except Exception as e:
        logger.debug(f"Statut realtime non affiché: {e}")


def _broadcast_article_change(event_type: str, article_data: dict):
    """Diffuse un changement d'article aux autres utilisateurs."""
    try:
        sync_service = get_realtime_sync_service()
        
        if not sync_service.is_configured or not sync_service.state.connected:
            return
        
        liste_id = st.session_state.get("liste_active_id", 1)
        
        if event_type == "added":
            sync_service.broadcast_item_added(liste_id, article_data)
        elif event_type == "checked":
            sync_service.broadcast_item_checked(
                liste_id,
                article_data.get("id"),
                article_data.get("achete", False)
            )
        elif event_type == "deleted":
            sync_service.broadcast_item_deleted(liste_id, article_data.get("id"))
    
    except Exception as e:
        logger.debug(f"Broadcast non envoyé: {e}")


__all__ = [
    "_init_realtime_sync",
    "render_realtime_status",
    "_broadcast_article_change",
]
