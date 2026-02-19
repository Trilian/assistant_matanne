"""
Interface UI pour l'historique d'activité.

Note: Ce fichier a été extrait depuis src/services/utilisateur/historique.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.core.utilisateur.historique import get_action_history_service


def afficher_timeline_activite(limit: int = 10):
    """Affiche la timeline d'activité récente."""
    service = get_action_history_service()
    actions = service.get_recent_actions(limit=limit)

    if not actions:
        st.info("Aucune activité récente")
        return

    st.markdown("### 📋 Activité récente")

    for action in actions:
        col1, col2 = st.columns([1, 4])

        with col1:
            # Icône selon le type
            icons = {
                "recette": "🍳",
                "inventaire": "📦",
                "courses": "🛒",
                "planning": "📅",
                "famille": "👨‍👩‍👧",
                "system": "⚙️",
            }
            icon = icons.get(action.entity_type, "📝")
            st.markdown(f"### {icon}")

        with col2:
            st.markdown(f"**{action.description}**")
            st.caption(f"{action.user_name} à {action.created_at.strftime('%d/%m %H:%M')}")

        st.markdown("---")


def afficher_activite_utilisateur(user_id: str):
    """Affiche l'activité d'un utilisateur spécifique."""
    service = get_action_history_service()
    actions = service.get_user_history(user_id, limit=20)

    st.markdown("### 👤 Activité de l'utilisateur")

    if not actions:
        st.info("Aucune activité enregistrée")
        return

    for action in actions:
        with st.expander(
            f"{action.description} - {action.created_at.strftime('%d/%m %H:%M')}",
            expanded=False,
        ):
            st.json(action.details)


def afficher_statistiques_activite():
    """Affiche les statistiques d'activité."""
    service = get_action_history_service()
    stats = service.get_stats()

    st.markdown("### 📊 Statistiques")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total actions", stats.total_actions)
    with col2:
        st.metric("Aujourd'hui", stats.actions_today)
    with col3:
        st.metric("Cette semaine", stats.actions_this_week)

    if stats.most_active_users:
        st.markdown("**🏆 Utilisateurs les plus actifs:**")
        for user in stats.most_active_users[:3]:
            st.write(f"• {user['name']}: {user['count']} actions")


# Alias rétrocompatibilité
render_activity_timeline = afficher_timeline_activite
render_user_activity = afficher_activite_utilisateur
render_activity_stats = afficher_statistiques_activite


__all__ = [
    "afficher_timeline_activite",
    "afficher_activite_utilisateur",
    "afficher_statistiques_activite",
    # Alias rétrocompatibilité
    "render_activity_timeline",
    "render_user_activity",
    "render_activity_stats",
]
