"""
Historique d'actions Undo - Bouton annuler dernière action.

Utilise ActionHistoryService (624 LOC) pour restaurer les états précédents.
Affichage via st.popover pour un accès rapide.

Usage:
    from src.ui.components import afficher_bouton_undo, afficher_historique_actions

    afficher_bouton_undo()  # En header
    afficher_historique_actions()  # Panel complet
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.state import naviguer, rerun
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("historique_undo")


# ═══════════════════════════════════════════════════════════
# COMPOSANT BOUTON UNDO
# ═══════════════════════════════════════════════════════════


@composant_ui("historique", tags=("ui", "undo", "actions"))
def afficher_bouton_undo(max_actions: int = 5) -> None:
    """
    Affiche un bouton "Annuler" avec popover listant les dernières actions.

    Args:
        max_actions: Nombre max d'actions à afficher
    """
    try:
        from src.services.core.utilisateur import (
            ActionHistoryService,
            get_action_history_service,
        )

        service = get_action_history_service()
        actions = service.get_recent_actions(limit=max_actions)

        # Compter les actions annulables
        annulables = [a for a in actions if service.can_undo(a.id) if a.id]
        nb_annulables = len(annulables)

        # Bouton avec popover
        with st.popover(f"↩️ ({nb_annulables})" if nb_annulables else "↩️", use_container_width=True):
            st.markdown("### Dernières actions")

            if not actions:
                st.caption("Aucune action récente")
                return

            for action in actions:
                col1, col2 = st.columns([0.8, 0.2])

                with col1:
                    # Icône selon type
                    icone = _get_action_icone(
                        action.action_type.value
                        if hasattr(action.action_type, "value")
                        else str(action.action_type)
                    )
                    temps = _format_temps_relatif(action.timestamp)

                    st.markdown(
                        f"**{icone} {action.description}**  \n"
                        f"<small style='color: {Sem.ON_SURFACE_SECONDARY};'>{temps}</small>",
                        unsafe_allow_html=True,
                    )

                with col2:
                    if action.id and service.can_undo(action.id):
                        if st.button("↩️", key=_keys(f"undo_{action.id}"), help="Annuler"):
                            if service.undo_action(action.id):
                                st.success("Action annulée!")
                                rerun()
                            else:
                                st.error("Impossible d'annuler")
                    else:
                        st.caption("—")

                st.divider()

            # Lien vers historique complet
            if st.button("📜 Voir tout l'historique", key=_keys("voir_tout")):
                naviguer("parametres")

    except Exception as e:
        logger.debug(f"Historique undo non disponible: {e}")
        # Fallback: bouton désactivé
        st.button("↩️ Annuler", disabled=True, help="Historique non disponible")


@composant_ui("historique", tags=("ui", "timeline", "actions"))
def afficher_historique_actions(
    jours: int = 7, limit: int = 50, filtrer_utilisateur: bool = False
) -> None:
    """
    Affiche la timeline complète des actions.

    Args:
        jours: Période à afficher
        limit: Nombre max d'actions
        filtrer_utilisateur: Si True, filtre sur l'utilisateur courant
    """
    try:
        from src.services.core.utilisateur import (
            ActionFilter,
            ActionHistoryService,
            get_action_history_service,
        )

        service = get_action_history_service()

        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            jours_filtre = st.selectbox(
                "Période",
                options=[1, 7, 30, 90],
                format_func=lambda x: f"{x} jour(s)",
                index=1,
                key=_keys("filtre_jours"),
            )
        with col2:
            type_filtre = st.selectbox(
                "Type",
                options=["Tous", "Recettes", "Inventaire", "Courses", "Planning", "Système"],
                key=_keys("filtre_type"),
            )
        with col3:
            limite_filtre = st.number_input(
                "Max",
                min_value=10,
                max_value=200,
                value=limit,
                key=_keys("filtre_limite"),
            )

        # Construire le filtre
        from datetime import timedelta

        entity_type = None
        if type_filtre != "Tous":
            entity_type = type_filtre.lower()

        filtre = ActionFilter(
            entity_type=entity_type,
            date_from=datetime.now() - timedelta(days=jours_filtre),
            limit=limite_filtre,
        )

        actions = service.get_history(filtre)

        if not actions:
            st.info("Aucune action dans cette période")
            return

        # Statistiques
        stats = service.get_stats(days=jours_filtre)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", stats.total_actions)
        with col2:
            st.metric("Aujourd'hui", stats.actions_today)
        with col3:
            st.metric("Cette semaine", stats.actions_this_week)

        st.divider()

        # Timeline
        st.markdown("### 📜 Timeline")

        for action in actions:
            icone = _get_action_icone(
                action.action_type.value
                if hasattr(action.action_type, "value")
                else str(action.action_type)
            )
            temps = _format_temps_relatif(action.timestamp)
            utilisateur = action.user_name or "Anonyme"

            with st.container():
                col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

                with col1:
                    st.markdown(
                        f"<div style='font-size: 1.5rem;'>{icone}</div>", unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(f"**{action.description}**")
                    st.caption(f"{utilisateur} • {temps}")

                with col3:
                    if action.id and service.can_undo(action.id):
                        if st.button("↩️", key=_keys(f"timeline_undo_{action.id}")):
                            if service.undo_action(action.id):
                                st.success("Annulé!")
                                rerun()

            st.divider()

    except Exception as e:
        logger.error(f"Erreur historique: {e}")
        st.error("Impossible de charger l'historique")


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _get_action_icone(action_type: str) -> str:
    """Retourne l'icône pour un type d'action."""
    icones = {
        "recette_created": "🍳",
        "recette_updated": "✏️",
        "recette_deleted": "🗑️",
        "recette_favorited": "⭐",
        "inventaire_added": "📦",
        "inventaire_updated": "📝",
        "inventaire_consumed": "🍽️",
        "courses_item_checked": "✅",
        "courses_list_created": "🛒",
        "planning_repas_added": "📅",
        "planning_repas_deleted": "❌",
        "system_login": "🔓",
        "system_logout": "🔒",
        "system_settings": "⚙️",
    }
    return icones.get(action_type.lower(), "📝")


def _format_temps_relatif(dt: datetime) -> str:
    """Formate un datetime en temps relatif."""
    if dt is None:
        return "?"

    now = datetime.now()
    delta = now - dt

    if delta.days > 30:
        return dt.strftime("%d/%m/%Y")
    elif delta.days > 0:
        return f"il y a {delta.days} jour(s)"
    elif delta.seconds > 3600:
        heures = delta.seconds // 3600
        return f"il y a {heures}h"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"il y a {minutes} min"
    else:
        return "À l'instant"


__all__ = [
    "afficher_bouton_undo",
    "afficher_historique_actions",
]
