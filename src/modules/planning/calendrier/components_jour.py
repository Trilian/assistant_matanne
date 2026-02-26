"""
Composants Calendrier - Affichage d'un jour

Composants UI pour l'affichage des jours du calendrier.
"""

import streamlit as st

from src.ui.keys import KeyNamespace

from .types import JourCalendrier, TypeEvenement

# Drag & drop (graceful fallback si pas installé)
try:
    from streamlit_sortables import sort_items

    HAS_SORTABLES = True
except ImportError:
    HAS_SORTABLES = False

_keys = KeyNamespace("calendrier")


def afficher_jour_calendrier(jour: JourCalendrier):
    """Affiche un jour du calendrier dans une carte."""

    with st.container():
        # Header du jour
        col_titre, col_actions = st.columns([4, 1])

        with col_titre:
            marqueur = "⭐ " if jour.est_aujourdhui else ""
            st.markdown(f"**{marqueur}{jour.jour_semaine}** {jour.date_jour.strftime('%d/%m')}")

        with col_actions:
            if st.button("➕", key=f"add_{jour.date_jour}", help="Ajouter"):
                st.session_state[_keys("event_date")] = jour.date_jour

        # Grille des repas
        col_midi, col_soir = st.columns(2)

        with col_midi:
            if jour.repas_midi:
                st.markdown(f"🌞 **{jour.repas_midi.titre}**")
                if jour.repas_midi.version_jules:
                    st.caption(f"👶 {jour.repas_midi.version_jules[:40]}...")
            else:
                st.markdown("🌞 *Midi: —*")

        with col_soir:
            if jour.repas_soir:
                st.markdown(f"🌙 **{jour.repas_soir.titre}**")
                if jour.repas_soir.version_jules:
                    st.caption(f"👶 {jour.repas_soir.version_jules[:40]}...")
            else:
                st.markdown("🌙 *Soir: —*")

        # Goûter si présent
        if jour.gouter:
            st.markdown(f"🍰 {jour.gouter.titre}")

        # Batch cooking
        if jour.batch_cooking:
            st.success(f"🍳 **BATCH COOKING** {jour.batch_cooking.heure_str}")

        # Courses
        for courses in jour.courses:
            st.info(f"🛒 {courses.magasin} {courses.heure_str}")

        # Activités
        for act in jour.activites:
            emoji = "👶" if act.pour_jules else "🎨"
            st.markdown(f"{emoji} {act.titre} {act.heure_str}")

        # RDV
        for rdv in jour.rdv:
            emoji = "🏥" if rdv.type == TypeEvenement.RDV_MEDICAL else "📅"
            lieu_str = f" @ {rdv.lieu}" if rdv.lieu else ""
            st.warning(f"{emoji} {rdv.titre} {rdv.heure_str}{lieu_str}")

        # Tâches ménage
        for tache in jour.taches_menage:
            en_retard = "⚠️ " if tache.notes and "RETARD" in tache.notes else ""
            duree_str = f" ({tache.description.split('•')[0].strip()})" if tache.description else ""
            st.markdown(f"{tache.emoji} {en_retard}{tache.titre}{duree_str}")

        # Autres événements
        for evt in jour.autres_evenements:
            st.caption(f"{evt.emoji} {evt.titre}")


def afficher_jour_sortable(jour: JourCalendrier):
    """Affiche les événements d'un jour avec réordonnancement drag & drop.

    Utilise streamlit-sortables pour permettre le réordonnancement
    visuel des activités et événements. Fallback sur l'affichage
    classique si le package n'est pas installé.
    """
    if not HAS_SORTABLES or not (jour.activites or jour.autres_evenements):
        # Fallback classique
        afficher_jour_calendrier(jour)
        return

    # Construire les labels pour les événements triables
    items = []
    for act in jour.activites:
        emoji = "👶" if act.pour_jules else "🎨"
        items.append(f"{emoji} {act.titre} {act.heure_str}")

    for evt in jour.autres_evenements:
        items.append(f"{evt.emoji} {evt.titre}")

    if items:
        st.caption("↕️ Glissez pour réorganiser")
        sorted_items = sort_items(items, key=f"sort_{jour.date_jour}")

        # Afficher dans le nouvel ordre
        for item in sorted_items:
            st.markdown(f"• {item}")


def afficher_cellule_jour(jour: JourCalendrier):
    """Affiche une cellule de jour dans la grille."""

    # Date
    st.markdown(f"**{jour.date_jour.strftime('%d')}**")

    # Repas
    if jour.repas_midi:
        st.caption(f"🌞 {jour.repas_midi.titre[:15]}...")
    if jour.repas_soir:
        st.caption(f"🌙 {jour.repas_soir.titre[:15]}...")

    # Événements importants
    if jour.batch_cooking:
        st.success("🍳 Batch", icon="🍳")

    for c in jour.courses[:1]:  # Max 1 pour la place
        st.info("🛒", icon="🛒")

    for rdv in jour.rdv[:1]:
        st.warning("🏥", icon="🏥")

    # Indicateur si plus d'événements
    nb_autres = len(jour.activites) + len(jour.autres_evenements)
    if nb_autres > 0:
        st.caption(f"+{nb_autres} autres")
