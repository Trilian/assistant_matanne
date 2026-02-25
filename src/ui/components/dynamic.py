"""
UI Components - Dynamic

Dialog helpers basés sur @st.dialog natif.

Usage::

    # Créer un dialog personnalisé (recommandé)
    @st.dialog("Confirmer suppression")
    def dialog_supprimer(item_id: int):
        st.warning("Êtes-vous sûr ?")
        if st.button("Supprimer", type="primary"):
            delete(item_id)
            st.rerun()
        if st.button("Annuler"):
            st.rerun()

    # Appeler le dialog
    if st.button("🗑️ Supprimer"):
        dialog_supprimer(item_id=42)

    # Ou utiliser le helper confirm_dialog()
    if st.button("🗑️ Supprimer"):
        confirm_dialog("Confirmer", "Supprimer cet élément ?", on_confirm=lambda: delete(42))
"""

from collections.abc import Callable

import streamlit as st

from src.core.state import rerun
from src.ui.registry import composant_ui

# ═══════════════════════════════════════════════════════════
# HELPER DIALOG MODERNE — @st.dialog
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "forms",
    exemple='confirm_dialog("Confirmer", "Supprimer ?", on_confirm=lambda: delete())',
    tags=("dialog", "confirm", "modal"),
)
def confirm_dialog(
    titre: str = "Confirmer",
    message: str = "Êtes-vous sûr ?",
    *,
    on_confirm: Callable[[], None] | None = None,
    confirm_label: str = "✅ Confirmer",
    cancel_label: str = "❌ Annuler",
):
    """Ouvre un @st.dialog de confirmation.

    Args:
        titre: Titre du dialog
        message: Message affiché
        on_confirm: Callback exécuté si l'utilisateur confirme
        confirm_label: Texte du bouton confirmer
        cancel_label: Texte du bouton annuler
    """

    @st.dialog(titre)
    def _dlg():
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(confirm_label, type="primary", use_container_width=True):
                if on_confirm:
                    on_confirm()
                rerun()
        with col2:
            if st.button(cancel_label, use_container_width=True):
                rerun()

    _dlg()


__all__ = ["confirm_dialog"]
