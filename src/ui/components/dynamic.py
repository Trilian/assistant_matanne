"""
UI Components - Dynamic
Listes dynamiques, modals
"""

import streamlit as st

from src.ui.components.forms import champ_formulaire


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


class ListeDynamique:
    """
    Liste dynamique (ajouter/supprimer items)

    Usage:
        dynamic_list = ListeDynamique(
            "ingredients",
            fields=[
                {"name": "nom", "label": "Nom", "type": "text"},
                {"name": "quantite", "label": "Quantité", "type": "number"}
            ]
        )

        items = dynamic_list.render()
    """

    def __init__(self, key: str, fields: list[dict], initial_items: list[dict] | None = None):
        self.key = key
        self.fields = fields

        if f"{key}_items" not in st.session_state:
            st.session_state[f"{key}_items"] = initial_items or []

    def render(self) -> list[dict]:
        """
        Render liste dynamique

        Returns:
            Liste des items
        """
        items = st.session_state[f"{self.key}_items"]

        # Formulaire ajout
        with st.expander("➕ Ajouter", expanded=len(items) == 0):
            cols = st.columns(len(self.fields) + 1)
            form_data = {}

            for i, field in enumerate(self.fields):
                with cols[i]:
                    form_data[field["name"]] = champ_formulaire(field, f"add_{self.key}")

            with cols[-1]:
                st.write("")
                st.write("")
                if st.button("➕", key=f"{self.key}_add"):
                    st.session_state[f"{self.key}_items"].append(form_data)
                    st.rerun()

        # Liste items
        if items:
            for idx, item in enumerate(items):
                col1, col2 = st.columns([5, 1])

                with col1:
                    display = " • ".join([f"{item.get(f['name'], '—')}" for f in self.fields[:3]])
                    st.write(display)

                with col2:
                    if st.button("🗑️", key=f"{self.key}_del_{idx}"):
                        st.session_state[f"{self.key}_items"].pop(idx)
                        st.rerun()
        else:
            st.info("Aucun élément")

        return items

    def get_items(self) -> list[dict]:
        """Récupère items"""
        return st.session_state[f"{self.key}_items"]

    def clear(self):
        """Vide liste"""
        st.session_state[f"{self.key}_items"] = []

    def add_item(self, item: dict):
        """Ajoute item programmatiquement"""
        st.session_state[f"{self.key}_items"].append(item)


class AssistantEtapes:
    """
    Stepper (wizard multi-étapes)

    Usage:
        stepper = AssistantEtapes("wizard", ["Étape 1", "Étape 2", "Étape 3"])

        current = stepper.render()

        if current == 0:
            st.write("Contenu étape 1")
            if st.button("Suivant"):
                stepper.next()
    """

    def __init__(self, key: str, steps: list[str]):
        self.key = key
        self.steps = steps

        if f"{key}_step" not in st.session_state:
            st.session_state[f"{key}_step"] = 0

    def render(self) -> int:
        """
        Render stepper

        Returns:
            Index étape courante
        """
        current = st.session_state[f"{self.key}_step"]

        # Progress bar
        progress = (current + 1) / len(self.steps)
        st.progress(progress)

        # Étapes
        cols = st.columns(len(self.steps))

        for idx, step in enumerate(self.steps):
            with cols[idx]:
                if idx < current:
                    st.markdown(f"✅ **{step}**")
                elif idx == current:
                    st.markdown(f"🔵 **{step}**")
                else:
                    st.markdown(f"⚪ {step}")

        st.markdown("---")

        return current

    def next(self):
        """Étape suivante"""
        current = st.session_state[f"{self.key}_step"]
        if current < len(self.steps) - 1:
            st.session_state[f"{self.key}_step"] = current + 1
            st.rerun()

    def previous(self):
        """Étape précédente"""
        current = st.session_state[f"{self.key}_step"]
        if current > 0:
            st.session_state[f"{self.key}_step"] = current - 1
            st.rerun()

    def reset(self):
        """Reset stepper"""
        st.session_state[f"{self.key}_step"] = 0

    def is_last_step(self) -> bool:
        """Dernière étape ?"""
        return st.session_state[f"{self.key}_step"] == len(self.steps) - 1
