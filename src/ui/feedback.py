"""
Composants Feedback
Toasts, modals, confirmations, notifications
"""
import streamlit as st
from typing import Optional, Callable


# ═══════════════════════════════════════════════════════════════
# TOASTS & NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

def toast(message: str, type: str = "success", duration: int = 3):
    """
    Toast notification

    Args:
        message: Message à afficher
        type: "success" | "error" | "warning" | "info"
        duration: Durée (non utilisé avec Streamlit standard)
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def notification_banner(
        message: str,
        type: str = "info",
        dismissible: bool = True,
        key: str = "notif"
):
    """
    Bannière de notification (reste affichée)

    Args:
        message: Message
        type: Type de notification
        dismissible: Peut être fermée
        key: Clé unique
    """
    if st.session_state.get(f"{key}_dismissed"):
        return

    col1, col2 = st.columns([10, 1]) if dismissible else (st.container(), None)

    with col1:
        if type == "success":
            st.success(message)
        elif type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        else:
            st.info(message)

    if dismissible and col2:
        with col2:
            st.write("")
            if st.button("✕", key=f"{key}_close"):
                st.session_state[f"{key}_dismissed"] = True
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# MODALS & DIALOGUES
# ═══════════════════════════════════════════════════════════════

class Modal:
    """
    Modal simple (utilise expander + état)

    Usage:
        modal = Modal("delete_confirm")

        if st.button("Supprimer"):
            modal.show()

        if modal.is_showing():
            st.warning("Confirmer la suppression ?")
            if modal.confirm():
                delete_item()
                modal.close()
            modal.cancel()
    """

    def __init__(self, key: str):
        self.key = f"modal_{key}"
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self):
        """Affiche le modal"""
        st.session_state[self.key] = True

    def close(self):
        """Ferme le modal"""
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        """Vérifie si le modal est affiché"""
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        """Bouton de confirmation"""
        return st.button(label, key=f"{self.key}_yes", type="primary", use_container_width=True)

    def cancel(self, label: str = "❌ Annuler"):
        """Bouton d'annulation"""
        if st.button(label, key=f"{self.key}_no", use_container_width=True):
            self.close()


def confirmation_dialog(
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_label: str = "✅ Confirmer",
        cancel_label: str = "❌ Annuler",
        key: str = "confirm"
) -> bool:
    """
    Dialogue de confirmation simple

    Args:
        message: Message de confirmation
        on_confirm: Callback si confirmé
        on_cancel: Callback si annulé (optionnel)
        confirm_label: Label bouton confirmation
        cancel_label: Label bouton annulation
        key: Clé unique

    Returns:
        True si confirmé

    Usage:
        if confirmation_dialog(
            "Supprimer cet élément ?",
            on_confirm=lambda: delete(id)
        ):
            st.success("Supprimé !")
    """
    st.warning(message)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(confirm_label, key=f"{key}_yes", type="primary", use_container_width=True):
            on_confirm()
            return True

    with col2:
        if st.button(cancel_label, key=f"{key}_no", use_container_width=True):
            if on_cancel:
                on_cancel()
            return False

    return False


def alert_box(
        title: str,
        message: str,
        type: str = "warning",
        icon: Optional[str] = None,
        actions: Optional[list] = None,
        key: str = "alert"
):
    """
    Boîte d'alerte avec actions

    Args:
        title: Titre
        message: Message
        type: "info" | "success" | "warning" | "error"
        icon: Icône personnalisée
        actions: [{"label": str, "callback": Callable, "type": str}]
        key: Clé unique
    """
    icon_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }

    display_icon = icon or icon_map.get(type, "ℹ️")

    # Conteneur selon le type
    container_func = {
        "success": st.success,
        "warning": st.warning,
        "error": st.error,
        "info": st.info
    }.get(type, st.info)

    with container_func(f"{display_icon} **{title}**"):
        st.write(message)

        if actions:
            cols = st.columns(len(actions))
            for idx, action in enumerate(actions):
                with cols[idx]:
                    action_type = action.get("type", "secondary")
                    if st.button(
                            action["label"],
                            key=f"{key}_action_{idx}",
                            type=action_type,
                            use_container_width=True
                    ):
                        action["callback"]()


# ═══════════════════════════════════════════════════════════════
# LOADING & PROGRESS
# ═══════════════════════════════════════════════════════════════

def loading_message(message: str = "Chargement...", icon: str = "⏳"):
    """
    Message de chargement simple
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem; color: #6c757d;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="margin-top: 1rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def progress_tracker(
        current: int,
        total: int,
        label: str = "Progression",
        show_percentage: bool = True
):
    """
    Suivi de progression avec étapes

    Args:
        current: Étape actuelle
        total: Total d'étapes
        label: Label
        show_percentage: Afficher le %
    """
    percentage = (current / total) * 100

    st.caption(f"{label}: Étape {current}/{total}")
    st.progress(percentage / 100)

    if show_percentage:
        st.caption(f"{percentage:.0f}% complété")


def step_indicator(
        steps: list[str],
        current_step: int,
        key: str = "steps"
):
    """
    Indicateur d'étapes

    Args:
        steps: ["Étape 1", "Étape 2", "Étape 3"]
        current_step: Index de l'étape actuelle (0-based)
        key: Clé unique
    """
    cols = st.columns(len(steps))

    for idx, step in enumerate(steps):
        with cols[idx]:
            if idx < current_step:
                # Complétée
                st.markdown(
                    f'<div style="text-align: center; color: #4CAF50;">'
                    f'<div style="font-size: 2rem;">✅</div>'
                    f'<div style="font-size: 0.875rem;">{step}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif idx == current_step:
                # En cours
                st.markdown(
                    f'<div style="text-align: center; color: #2196F3;">'
                    f'<div style="font-size: 2rem;">🔵</div>'
                    f'<div style="font-size: 0.875rem; font-weight: 600;">{step}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                # À venir
                st.markdown(
                    f'<div style="text-align: center; color: #9e9e9e;">'
                    f'<div style="font-size: 2rem;">⚪</div>'
                    f'<div style="font-size: 0.875rem;">{step}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ═══════════════════════════════════════════════════════════════
# VALIDATION & ERREURS
# ═══════════════════════════════════════════════════════════════

def validation_error(field_name: str, error_message: str):
    """
    Erreur de validation pour un champ
    """
    st.error(f"❌ **{field_name}**: {error_message}")


def success_message(message: str, details: Optional[str] = None):
    """
    Message de succès avec détails optionnels
    """
    st.success(f"✅ {message}")
    if details:
        st.caption(details)


def error_message(message: str, details: Optional[str] = None, show_trace: bool = False):
    """
    Message d'erreur avec détails

    Args:
        message: Message principal
        details: Détails (optionnel)
        show_trace: Afficher la trace (debug)
    """
    st.error(f"❌ {message}")

    if details:
        with st.expander("Détails"):
            st.code(details)

    if show_trace and st.session_state.get("debug_mode"):
        import traceback
        with st.expander("🐛 Stack Trace (debug)"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def info_tooltip(text: str, tooltip: str, key: str = "tooltip"):
    """
    Texte avec tooltip (via expander)

    Args:
        text: Texte principal
        tooltip: Contenu du tooltip
        key: Clé unique
    """
    col1, col2 = st.columns([10, 1])

    with col1:
        st.write(text)

    with col2:
        with st.expander("ℹ️"):
            st.caption(tooltip)


def status_badge(status: str, color_map: Optional[dict] = None):
    """
    Badge de statut coloré

    Args:
        status: Statut à afficher
        color_map: {"ok": "#4CAF50", "error": "#f44336"}
    """
    default_colors = {
        "ok": "#4CAF50",
        "success": "#4CAF50",
        "warning": "#FFC107",
        "error": "#f44336",
        "pending": "#2196F3",
        "info": "#2196F3"
    }

    colors = color_map or default_colors
    color = colors.get(status.lower(), "#9e9e9e")

    st.markdown(
        f'<span style="background: {color}; color: white; '
        f'padding: 0.25rem 0.75rem; border-radius: 12px; '
        f'font-size: 0.875rem; font-weight: 600;">{status}</span>',
        unsafe_allow_html=True
    )