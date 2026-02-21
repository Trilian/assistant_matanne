"""
UI Components - Dynamic

Composant Modale **DÉPRÉCIÉ** — migrer vers DialogBuilder.

Migration recommandée::

    # Ancien code (déprécié)
    from src.ui import Modale
    modal = Modale("delete")
    if modal.is_showing():
        if modal.confirm():
            delete()
            modal.close()

    # Nouveau code
    from src.ui import confirm_dialog, ouvrir_dialog
    if st.button("Supprimer"):
        ouvrir_dialog("delete")
    if confirm_dialog("delete", titre="Confirmer ?", on_confirm=delete):
        st.success("Supprimé")

Voir docs/MIGRATION_UI_V2.md pour le guide complet.
"""

import warnings

import streamlit as st


class Modale:
    """
    **DÉPRÉCIÉ** — Utiliser DialogBuilder ou confirm_dialog à la place.

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
            "Modale est déprécié. Utiliser DialogBuilder ou confirm_dialog. "
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


__all__ = ["Modale"]
