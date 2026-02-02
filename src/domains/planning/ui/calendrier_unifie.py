"""
Module Calendrier Familial Unifié - Vue centrale de TOUT

Affiche dans une seule vue:
- 🍽️ Repas (midi, soir, goûters)
- 🍳 Sessions batch cooking
- 🛒 Courses planifiées
- 🎨 Activités famille
- 🏥 RDV médicaux
- 📅 Événements divers

Fonctionnalités:
- Vue semaine avec impression
- Ajout rapide d'événements
- Navigation semaine par semaine
- Export pour le frigo
"""

import streamlit as st
from datetime import date, datetime, time, timedelta
import logging

from src.core.database import obtenir_contexte_db
from src.core.models import (
    Planning, Repas, Recette,
    SessionBatchCooking,
    FamilyActivity,
    CalendarEvent,
)

# Logique métier pure
from src.domains.planning.logic.calendrier_unifie_logic import (
    TypeEvenement,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    JOURS_SEMAINE,
    EMOJI_TYPE,
    COULEUR_TYPE,
    get_debut_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
    construire_semaine_calendrier,
    generer_texte_semaine_pour_impression,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DES DONNÉES
# ═══════════════════════════════════════════════════════════


def charger_donnees_semaine(date_debut: date) -> dict:
    """
    Charge toutes les données nécessaires pour une semaine.
    
    Returns:
        Dict avec repas, sessions_batch, activites, events
    """
    lundi = get_debut_semaine(date_debut)
    dimanche = lundi + timedelta(days=6)
    
    donnees = {
        "repas": [],
        "sessions_batch": [],
        "activites": [],
        "events": [],
        "courses_planifiees": [],
    }
    
    try:
        with obtenir_contexte_db() as db:
            # Charger le planning actif et ses repas
            planning = db.query(Planning).filter(
                Planning.semaine_debut <= dimanche,
                Planning.semaine_fin >= lundi
            ).first()
            
            if planning:
                repas = db.query(Repas).filter(
                    Repas.planning_id == planning.id,
                    Repas.date_repas >= lundi,
                    Repas.date_repas <= dimanche
                ).all()
                
                # Charger les recettes associées
                for r in repas:
                    if r.recette_id:
                        r.recette = db.query(Recette).filter_by(id=r.recette_id).first()
                
                donnees["repas"] = repas
            
            # Sessions batch cooking
            sessions = db.query(SessionBatchCooking).filter(
                SessionBatchCooking.date_session >= lundi,
                SessionBatchCooking.date_session <= dimanche
            ).all()
            donnees["sessions_batch"] = sessions
            
            # Activités famille
            activites = db.query(FamilyActivity).filter(
                FamilyActivity.date_prevue >= lundi,
                FamilyActivity.date_prevue <= dimanche
            ).all()
            donnees["activites"] = activites
            
            # Événements calendrier
            events = db.query(CalendarEvent).filter(
                CalendarEvent.date_debut >= datetime.combine(lundi, time.min),
                CalendarEvent.date_debut <= datetime.combine(dimanche, time.max)
            ).all()
            donnees["events"] = events
            
    except Exception as e:
        logger.error(f"Erreur chargement données semaine: {e}")
    
    return donnees


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_navigation_semaine():
    """Affiche la navigation entre semaines."""
    if "cal_semaine_debut" not in st.session_state:
        st.session_state.cal_semaine_debut = get_debut_semaine(date.today())
    
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    
    with col1:
        if st.button("◀ Précédente", use_container_width=True):
            st.session_state.cal_semaine_debut = get_semaine_precedente(
                st.session_state.cal_semaine_debut
            )
            st.rerun()
    
    with col2:
        semaine_debut = st.session_state.cal_semaine_debut
        semaine_fin = semaine_debut + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center; margin: 0;'>"
            f"📅 {semaine_debut.strftime('%d/%m')} — {semaine_fin.strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Suivante ▶", use_container_width=True):
            st.session_state.cal_semaine_debut = get_semaine_suivante(
                st.session_state.cal_semaine_debut
            )
            st.rerun()
    
    with col4:
        if st.button("📅 Aujourd'hui", use_container_width=True):
            st.session_state.cal_semaine_debut = get_debut_semaine(date.today())
            st.rerun()


def render_jour_calendrier(jour: JourCalendrier):
    """Affiche un jour du calendrier dans une carte."""
    
    # Style du conteneur
    bg_color = "#e3f2fd" if jour.est_aujourdhui else "#ffffff"
    border = "3px solid #1976d2" if jour.est_aujourdhui else "1px solid #e0e0e0"
    
    with st.container():
        # Header du jour
        col_titre, col_actions = st.columns([4, 1])
        
        with col_titre:
            marqueur = "⭐ " if jour.est_aujourdhui else ""
            st.markdown(
                f"**{marqueur}{jour.jour_semaine}** {jour.date_jour.strftime('%d/%m')}"
            )
        
        with col_actions:
            if st.button("➕", key=f"add_{jour.date_jour}", help="Ajouter"):
                st.session_state.ajouter_event_date = jour.date_jour
        
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
        
        # Autres événements
        for evt in jour.autres_evenements:
            st.caption(f"{evt.emoji} {evt.titre}")


def render_vue_semaine_grille(semaine: SemaineCalendrier):
    """Affiche la semaine en grille 7 colonnes."""
    
    # En-têtes des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            bg = "🔵" if jour.est_aujourdhui else ""
            col.markdown(f"**{bg} {jour.jour_semaine_court}**")
    
    st.divider()
    
    # Contenu des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            render_cellule_jour(jour)


def render_cellule_jour(jour: JourCalendrier):
    """Affiche une cellule de jour dans la grille."""
    
    # Container stylisé
    style = "background: #e3f2fd; border-radius: 8px; padding: 5px;" if jour.est_aujourdhui else ""
    
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
        st.info(f"🛒", icon="🛒")
    
    for rdv in jour.rdv[:1]:
        st.warning(f"🏥", icon="🏥")
    
    # Indicateur si plus d'événements
    nb_autres = len(jour.activites) + len(jour.autres_evenements)
    if nb_autres > 0:
        st.caption(f"+{nb_autres} autres")


def render_vue_semaine_liste(semaine: SemaineCalendrier):
    """Affiche la semaine en liste (plus détaillée)."""
    
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
            expanded=expanded
        ):
            render_jour_calendrier(jour)


def render_stats_semaine(semaine: SemaineCalendrier):
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


def render_actions_rapides(semaine: SemaineCalendrier):
    """Affiche les boutons d'actions rapides."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🍽️ Planifier repas", use_container_width=True, type="primary"):
            # Naviguer vers le planificateur
            from src.core.state import GestionnaireEtat
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            st.rerun()
    
    with col2:
        if st.button("🍳 Nouveau batch", use_container_width=True):
            from src.core.state import GestionnaireEtat
            GestionnaireEtat.naviguer_vers("cuisine.batch_cooking")
            st.rerun()
    
    with col3:
        if st.button("🛒 Mes courses", use_container_width=True):
            from src.core.state import GestionnaireEtat
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            st.rerun()
    
    with col4:
        if st.button("🖨️ Imprimer", use_container_width=True):
            st.session_state.show_print_modal = True


def render_modal_impression(semaine: SemaineCalendrier):
    """Affiche le modal d'impression."""
    
    if st.session_state.get("show_print_modal"):
        with st.container():
            st.subheader("🖨️ Imprimer le planning")
            
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
                if st.button("Fermer"):
                    st.session_state.show_print_modal = False
                    st.rerun()


def render_formulaire_ajout_event():
    """Affiche le formulaire d'ajout d'événement."""
    
    if "ajouter_event_date" in st.session_state:
        date_selectionnee = st.session_state.ajouter_event_date
        
        with st.container():
            st.subheader(f"➕ Ajouter un événement - {date_selectionnee.strftime('%d/%m/%Y')}")
            
            with st.form("form_ajout_event"):
                type_event = st.selectbox(
                    "Type",
                    options=[
                        ("🏥 RDV Médical", "rdv_medical"),
                        ("📅 RDV Autre", "rdv_autre"),
                        ("🎨 Activité", "activite"),
                        ("🛒 Courses", "courses"),
                        ("📌 Autre", "autre"),
                    ],
                    format_func=lambda x: x[0],
                )
                
                titre = st.text_input("Titre *", placeholder="Ex: Pédiatre Jules")
                
                col1, col2 = st.columns(2)
                with col1:
                    heure = st.time_input("Heure", value=time(10, 0))
                with col2:
                    lieu = st.text_input("Lieu", placeholder="Ex: Cabinet Dr Martin")
                
                notes = st.text_area("Notes", placeholder="Informations supplémentaires...")
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    submitted = st.form_submit_button("✅ Créer", type="primary")
                
                with col_cancel:
                    if st.form_submit_button("❌ Annuler"):
                        del st.session_state.ajouter_event_date
                        st.rerun()
                
                if submitted and titre:
                    # Créer l'événement
                    try:
                        with obtenir_contexte_db() as db:
                            if type_event[1] == "activite":
                                evt = FamilyActivity(
                                    titre=titre,
                                    date_prevue=date_selectionnee,
                                    heure_debut=heure,
                                    lieu=lieu,
                                    notes=notes,
                                    type_activite="famille",
                                    statut="planifié",
                                )
                            else:
                                evt = CalendarEvent(
                                    titre=titre,
                                    date_debut=datetime.combine(date_selectionnee, heure),
                                    type_event=type_event[1],
                                    lieu=lieu,
                                    description=notes,
                                )
                            db.add(evt)
                            db.commit()
                        
                        st.success(f"✅ {titre} ajouté!")
                        del st.session_state.ajouter_event_date
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Calendrier Familial Unifié."""
    
    st.title("📅 Calendrier Familial")
    st.caption("Vue unifiée de toute votre semaine: repas, batch, courses, activités, RDV")
    
    # Navigation
    render_navigation_semaine()
    
    st.divider()
    
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
        ["📋 Liste détaillée", "📊 Grille"],
        horizontal=True,
        label_visibility="collapsed",
    )
    
    # Affichage principal
    if mode == "📋 Liste détaillée":
        render_vue_semaine_liste(semaine)
    else:
        render_vue_semaine_grille(semaine)
    
    # Modals
    render_modal_impression(semaine)
    render_formulaire_ajout_event()
    
    # Légende
    with st.expander("📖 Légende"):
        cols = st.columns(5)
        legendes = [
            ("🌞 Midi", "🌙 Soir", "🍰 Goûter"),
            ("🍳 Batch", "🛒 Courses"),
            ("🎨 Activité", "🏥 RDV médical"),
            ("📅 RDV", "👶 Pour Jules"),
            ("⭐ Aujourd'hui",),
        ]
        for i, col in enumerate(cols):
            with col:
                for item in legendes[i]:
                    st.caption(item)
