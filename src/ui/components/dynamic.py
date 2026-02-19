"""
UI Components - Dynamic
Modales et composants interactifs
"""

import streamlit as st


class Modale:
    """
    Modal simple

    Usage:
        modal = Modale("delete_confirm")

        if modal.is_showing():
            st.warning("Confirmer suppression ?")
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
        """Affiche modal"""
        st.session_state[self.key] = True

    def close(self):
        """Ferme modal"""
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        """Modal visible ?"""
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        """Bouton confirmer"""
        return st.button(label, key=f"{self.key}_yes", type="primary", use_container_width=True)

    def cancel(self, label: str = "❌ Annuler"):
        """Bouton annuler"""
        if st.button(label, key=f"{self.key}_no", use_container_width=True):
            self.close()

    # Alias français
    afficher = show
    fermer = close
    est_affichee = is_showing
    confirmer = confirm
    annuler = cancel
