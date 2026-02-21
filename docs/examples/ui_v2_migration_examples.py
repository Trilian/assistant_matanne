"""
Exemples de migration vers UI v2.0.

Ce fichier démontre comment migrer le code existant vers les nouveaux patterns.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════
# EXEMPLE 1: Migration st.rerun() → @ui_fragment
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_backup_list():
    import streamlit as st

    backups = get_backups()
    for backup in backups:
        with st.expander(backup.id):
            if st.button("Supprimer", key=f"del_{backup.id}"):
                delete_backup(backup.id)
                st.rerun()  # ⚠️ Recharge TOUTE la page


# --- APRÈS ---
def _new_backup_list():
    import streamlit as st

    from src.ui import ui_fragment

    @ui_fragment
    def backup_section():
        """Fragment isolé - ne recharge que cette section."""
        backups = get_backups()
        for backup in backups:
            with st.expander(backup.id):
                if st.button("Supprimer", key=f"del_{backup.id}"):
                    delete_backup(backup.id)
                    # Pas besoin de st.rerun() ! Le fragment se recharge seul

    backup_section()


# ═══════════════════════════════════════════════════════════
# EXEMPLE 2: Migration st.columns() → Row
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_backup_page():
    import streamlit as st

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Créer")
        if st.button("Créer backup"):
            create_backup()
    with col2:
        st.markdown("### Liste")
        show_backups()


# --- APRÈS ---
def _new_backup_page():
    import streamlit as st

    from src.ui import Row

    with Row(2, gap="medium") as row:
        with row.col(0):
            st.markdown("### Créer")
            if st.button("Créer backup"):
                create_backup()
        with row.col(1):
            st.markdown("### Liste")
            show_backups()


# ═══════════════════════════════════════════════════════════
# EXEMPLE 3: Migration forms → FormBuilder
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_contact_form():
    import streamlit as st

    with st.form("contact"):
        nom = st.text_input("Nom")
        email = st.text_input("Email")
        message = st.text_area("Message")
        submit = st.form_submit_button("Envoyer")

        if submit:
            errors = []
            if not nom:
                errors.append("Nom requis")
            if not email or "@" not in email:
                errors.append("Email invalide")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                send_message(nom, email, message)
                st.success("Envoyé!")


# --- APRÈS ---
def _new_contact_form():
    import streamlit as st

    from src.ui import FormBuilder

    result = (
        FormBuilder("contact", submit_label="✉️ Envoyer")
        .text("nom", label="Nom", required=True)
        .text("email", label="Email", required=True, pattern=r".+@.+\..+")
        .textarea("message", label="Message", max_length=500)
        .render()
    )

    if result.is_valid:
        send_message(**result.data)
        st.success("Envoyé!")


# ═══════════════════════════════════════════════════════════
# EXEMPLE 4: URL State pour deep linking
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_tabs_page():
    import streamlit as st

    # État perdu au refresh
    tab = st.selectbox("Section", ["Aperçu", "Détails", "Stats"])
    if tab == "Aperçu":
        show_overview()
    elif tab == "Détails":
        show_details()


# --- APRÈS ---
def _new_tabs_page():
    from src.ui import tabs_with_url

    # URL: /app?tab=Details -> section=Détails
    tab = tabs_with_url(["Aperçu", "Détails", "Stats"], param="tab")
    if tab == "Aperçu":
        show_overview()
    elif tab == "Détails":
        show_details()


# ═══════════════════════════════════════════════════════════
# EXEMPLE 5: Auto-refresh pour données temps réel
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_metrics_dashboard():
    import time

    import streamlit as st

    placeholder = st.empty()

    while True:
        with placeholder.container():
            data = get_metrics()
            st.metric("CPU", f"{data['cpu']}%")
            st.metric("RAM", f"{data['ram']}%")
        time.sleep(30)  # ⚠️ Bloque le thread


# --- APRÈS ---
def _new_metrics_dashboard():
    import streamlit as st

    from src.ui import auto_refresh

    @auto_refresh(seconds=30)
    def live_metrics():
        """Refresh automatique toutes les 30s."""
        data = get_metrics()
        st.metric("CPU", f"{data['cpu']}%")
        st.metric("RAM", f"{data['ram']}%")

    live_metrics()


# ═══════════════════════════════════════════════════════════
# EXEMPLE 6: Grid pour cartes
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_recipe_grid():
    import streamlit as st

    recipes = get_recipes()

    # Création manuelle de grille 4 colonnes
    for i in range(0, len(recipes), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(recipes):
                with col:
                    st.image(recipes[idx].image)
                    st.caption(recipes[idx].name)


# --- APRÈS ---
def _new_recipe_grid():
    import streamlit as st

    from src.ui import Grid

    recipes = get_recipes()

    with Grid(cols=4, gap="medium") as grid:
        for recipe in recipes:
            with grid.cell():
                st.image(recipe.image)
                st.caption(recipe.name)


# ═══════════════════════════════════════════════════════════
# EXEMPLE 7: Dialogue de confirmation
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_delete_with_confirm():
    import streamlit as st

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if st.button("Supprimer"):
        st.session_state.confirm_delete = True

    if st.session_state.confirm_delete:
        st.warning("Êtes-vous sûr ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Oui, supprimer"):
                delete_item()
                st.session_state.confirm_delete = False
                st.rerun()
        with col2:
            if st.button("Annuler"):
                st.session_state.confirm_delete = False
                st.rerun()


# --- APRÈS ---
def _new_delete_with_confirm():
    import streamlit as st

    from src.ui import confirm_dialog, ouvrir_dialog

    if st.button("Supprimer"):
        ouvrir_dialog("delete_confirm")

    if confirm_dialog(
        "delete_confirm",
        titre="Confirmer la suppression",
        message="Cette action est irréversible.",
        on_confirm=delete_item,
    ):
        st.success("Élément supprimé")


# ═══════════════════════════════════════════════════════════
# EXEMPLE 8: Progress avec st.status()
# ═══════════════════════════════════════════════════════════


# --- AVANT ---
def _old_import_progress():
    import streamlit as st

    from src.ui.feedback import SuiviProgression

    items = get_items_to_import()
    progression = SuiviProgression("Import", total=len(items))

    for i, item in enumerate(items):
        process(item)
        progression.mettre_a_jour(i + 1, f"Import: {item.name}")

    progression.terminer()


# --- APRÈS ---
def _new_import_progress():
    from src.ui.feedback import SuiviProgressionV2

    items = get_items_to_import()

    # Context manager - se termine automatiquement
    with SuiviProgressionV2("Import", total=len(items)) as progression:
        for i, item in enumerate(items):
            process(item)
            progression.update(i + 1, f"Import: {item.name}")
    # Terminé automatiquement


# ═══════════════════════════════════════════════════════════
# Helpers fictifs pour les exemples
# ═══════════════════════════════════════════════════════════


def get_backups():
    return []


def delete_backup(id):
    pass


def create_backup():
    pass


def show_backups():
    pass


def send_message(*args, **kwargs):
    pass


def show_overview():
    pass


def show_details():
    pass


def get_metrics():
    return {"cpu": 0, "ram": 0}


def get_recipes():
    return []


def delete_item():
    pass


def get_items_to_import():
    return []


def process(item):
    pass
