"""
Composants Calendrier - Vues semaine

Composants UI pour l'affichage hebdomadaire : grille, liste, stats, actions rapides, impression.
"""

import streamlit as st

from src.core.session_keys import SK

from .utils import SemaineCalendrier, generer_texte_semaine_pour_impression


def afficher_vue_semaine_grille(semaine: SemaineCalendrier):
    """Affiche la semaine en grille 7 colonnes."""
    from .components_jour import afficher_cellule_jour

    # En-têtes des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            prefix = "🔵 " if jour.est_aujourdhui else ""
            col.markdown(f"**{prefix}{jour.jour_semaine_court}**")

    st.divider()

    # Contenu des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            afficher_cellule_jour(jour)


def afficher_vue_semaine_liste(semaine: SemaineCalendrier):
    """Affiche la semaine en liste (plus détaillée)."""
    from .components_jour import afficher_jour_calendrier

    for jour in semaine.jours:
        expanded = jour.est_aujourdhui

        # Construire le titre avec indicateurs
        indicateurs = []
        if jour.repas_midi or jour.repas_soir:
            indicateurs.append("🍽️")
        if jour.batch_cooking:
            indicateurs.append("🍳")
        if jour.courses:
            indicateurs.append("🛒")
        if jour.rdv:
            indicateurs.append("🏥")
        if jour.activites:
            indicateurs.append("🎨")

        marqueur = "⭐ " if jour.est_aujourdhui else ""
        indicateurs_str = " ".join(indicateurs) if indicateurs else "—"

        with st.expander(
            f"{marqueur}**{jour.jour_semaine}** {jour.date_jour.strftime('%d/%m')} │ {indicateurs_str}",
            expanded=expanded,
        ):
            afficher_jour_calendrier(jour)


def afficher_stats_semaine(semaine: SemaineCalendrier):
    """Affiche les statistiques de la semaine."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🍽️ Repas planifiés", f"{semaine.nb_repas_planifies}/14")

    with col2:
        st.metric("🍳 Batch cooking", semaine.nb_sessions_batch)

    with col3:
        st.metric("🛒 Courses", semaine.nb_courses)

    with col4:
        st.metric("🎨 Activités", semaine.nb_activites)


def afficher_actions_rapides(semaine: SemaineCalendrier):
    """Affiche les boutons d'actions rapides."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🍽️ Planifier repas", use_container_width=True, type="primary"):
            # Naviguer vers le planificateur
            from src.core.state import GestionnaireEtat, rerun

            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            rerun()

    with col2:
        if st.button("🍳 Nouveau batch", use_container_width=True):
            from src.core.state import GestionnaireEtat, rerun

            GestionnaireEtat.naviguer_vers("cuisine.batch_cooking")
            rerun()

    with col3:
        if st.button("🛒 Mes courses", use_container_width=True):
            from src.core.state import GestionnaireEtat, rerun

            GestionnaireEtat.naviguer_vers("cuisine.courses")
            rerun()

    with col4:
        if st.button("🖨️ Imprimer", use_container_width=True):
            _dialog_impression(semaine)


@st.dialog("🖨️ Imprimer le planning")
def _dialog_impression(semaine: SemaineCalendrier):
    """Dialog natif pour l'impression du planning."""
    from src.core.state import rerun

    texte = generer_texte_semaine_pour_impression(semaine)

    st.text_area(
        "Aperçu (copier-coller pour imprimer)",
        value=texte,
        height=400,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Télécharger .txt",
            data=texte,
            file_name=f"planning_{semaine.date_debut.strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )
    with col2:
        if st.button("Fermer", use_container_width=True):
            rerun()


def afficher_modal_impression(semaine: SemaineCalendrier):
    """Affiche le modal d'impression.

    DÉPRÉCIÉ — Utiliser _dialog_impression() via le bouton Imprimer.
    Conservé pour compatibilité arrière.
    """
    if st.session_state.get(SK.SHOW_PRINT_MODAL):
        _dialog_impression(semaine)
