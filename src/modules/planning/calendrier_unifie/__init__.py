"""
Module Calendrier Familial Unifié - Vue centrale de TOUT

Affiche dans une seule vue:
- ðŸ½ï¸ Repas (midi, soir, goûters)
- ðŸ³ Sessions batch cooking
- ðŸ›’ Courses planifiées
- ðŸŽ¨ Activités famille
- ðŸ¥ RDV médicaux
- ðŸ“… Événements divers

Fonctionnalités:
- Vue semaine avec impression
- Ajout rapide d'événements
- Navigation semaine par semaine
- Export pour le frigo
"""

from ._common import construire_semaine_calendrier, date, get_debut_semaine, st
from .components import (
    render_actions_rapides,
    render_cellule_jour,
    render_formulaire_ajout_event,
    render_jour_calendrier,
    render_legende,
    render_modal_impression,
    render_navigation_semaine,
    render_stats_semaine,
    render_vue_semaine_grille,
    render_vue_semaine_liste,
)

# Import des fonctions pour exposer l'API publique
from .data import charger_donnees_semaine


def app():
    """Point d'entrée du module Calendrier Familial Unifié."""

    st.title("ðŸ“… Calendrier Familial")
    st.caption("Vue unifiée de toute votre semaine: repas, batch, courses, activités, ménage, RDV")

    # Navigation
    render_navigation_semaine()

    st.divider()

    # Init state
    if "cal_semaine_debut" not in st.session_state:
        st.session_state.cal_semaine_debut = get_debut_semaine(date.today())

    # Charger les données
    with st.spinner("Chargement..."):
        donnees = charger_donnees_semaine(st.session_state.cal_semaine_debut)

        semaine = construire_semaine_calendrier(
            date_debut=st.session_state.cal_semaine_debut,
            repas=donnees["repas"],
            sessions_batch=donnees["sessions_batch"],
            activites=donnees["activites"],
            events=donnees["events"],
            courses_planifiees=donnees["courses_planifiees"],
            taches_menage=donnees["taches_menage"],  # Intégration ménage
        )

    # Stats en haut
    render_stats_semaine(semaine)

    st.divider()

    # Actions rapides
    render_actions_rapides(semaine)

    st.divider()

    # Mode d'affichage
    mode = st.radio(
        "Vue",
        ["ðŸ“‹ Liste détaillée", "ðŸ“Š Grille"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # Affichage principal
    if mode == "ðŸ“‹ Liste détaillée":
        render_vue_semaine_liste(semaine)
    else:
        render_vue_semaine_grille(semaine)

    # Modals
    render_modal_impression(semaine)
    render_formulaire_ajout_event()

    # Légende
    render_legende()


__all__ = [
    # Entry point
    "app",
    # Data
    "charger_donnees_semaine",
    # UI
    "render_navigation_semaine",
    "render_jour_calendrier",
    "render_vue_semaine_grille",
    "render_cellule_jour",
    "render_vue_semaine_liste",
    "render_stats_semaine",
    "render_actions_rapides",
    "render_modal_impression",
    "render_formulaire_ajout_event",
    "render_legende",
]
