"""
UI Components - Dynamic

Composant Modale **DÉPRÉCIÉ** — migré vers @st.dialog natif.

Usage moderne::

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

Voir docs/MIGRATION_UI_V2.md pour le guide complet.
"""

import warnings
from collections.abc import Callable

import streamlit as st

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
                st.rerun()
        with col2:
            if st.button(cancel_label, use_container_width=True):
                st.rerun()

    _dlg()


# ═══════════════════════════════════════════════════════════
# MODALE LEGACY — DÉPRÉCIÉ
# ═══════════════════════════════════════════════════════════


class Modale:
    """
    **DÉPRÉCIÉ** — Utiliser @st.dialog ou confirm_dialog() à la place.

    Cette classe reste fonctionnelle mais émet un DeprecationWarning.
    Voir docs/MIGRATION_UI_V2.md pour migrer.

    Usage legacy:
        modal = Modale("delete_confirm")

        if modal.is_showing():
            st.warning("Confirmer suppression ?")
            if modal.confirm():
                delete_item()
                modal.close()
            modal.cancel()
    """

    def __init__(self, key: str):
        warnings.warn(
            "Modale est déprécié. Utiliser @st.dialog ou confirm_dialog(). "
            "Voir docs/MIGRATION_UI_V2.md",
            DeprecationWarning,
            stacklevel=2,
        )
        self.key = f"modal_{key}"
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self):
        """Affiche modal"""
        st.session_state[self.key] = True

    def close(self):
        """Ferme modal"""
        st.session_state[self.key] = False

    def is_showing(self) -> bool:
        """Modal visible ?"""
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        """Bouton confirmer"""
        return st.button(label, key=f"{self.key}_yes", type="primary", use_container_width=True)

    def cancel(self, label: str = "❌ Annuler"):
        """Bouton annuler — ferme la modal si cliqué"""
        if st.button(label, key=f"{self.key}_no", use_container_width=True):
            self.close()

    # Alias français
    afficher = show
    fermer = close
    est_affichee = is_showing
    confirmer = confirm
    annuler = cancel


__all__ = ["Modale", "confirm_dialog"]
