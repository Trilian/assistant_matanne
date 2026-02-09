"""
Module Sorties Weekend - Composants UI
"""

from ._common import (
    st, date,
    get_db_context, WeekendActivity,
    TYPES_ACTIVITES, METEO_OPTIONS
)
from .helpers import (
    get_next_weekend, get_weekend_activities, get_budget_weekend,
    get_lieux_testes, get_age_jules_mois, mark_activity_done
)
from .ai_service import WeekendAIService


def render_planning():
    """Affiche le planning du weekend"""
    saturday, sunday = get_next_weekend()
    activities = get_weekend_activities(saturday, sunday)
    
    st.subheader("📅 Ce Weekend")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**🗓️ Samedi {saturday.strftime('%d/%m')}**")
        render_day_activities(saturday, activities["saturday"])
    
    with col2:
        st.markdown(f"**🗓️ Dimanche {sunday.strftime('%d/%m')}**")
        render_day_activities(sunday, activities["sunday"])
    
    # Budget
    budget = get_budget_weekend(saturday, sunday)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Budget estimé", f"{budget['estime']:.0f}€")
    with col2:
        st.metric("💸 Dépensé", f"{budget['reel']:.0f}€")


def render_day_activities(day: date, activities: list):
    """Affiche les activités d'un jour"""
    if not activities:
        st.caption("Rien de prévu")
        if st.button(f"➕ Ajouter", key=f"add_{day}"):
            st.session_state["weekend_add_date"] = day
            st.session_state["weekend_tab"] = "add"
            st.rerun()
        return
    
    for act in activities:
        type_info = TYPES_ACTIVITES.get(act.type_activite, TYPES_ACTIVITES["autre"])
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                heure = act.heure_debut or "?"
                st.markdown(f"**{type_info['emoji']} {heure} - {act.titre}**")
                if act.lieu:
                    st.caption(f"📍 {act.lieu}")
                if act.cout_estime:
                    st.caption(f"💰 ~{act.cout_estime:.0f}€")
            
            with col2:
                if act.statut == "planifié":
                    if st.button("✅", key=f"done_{act.id}", help="Marquer fait"):
                        mark_activity_done(act.id)
                        st.rerun()
                elif act.statut == "terminé":
                    if act.note_lieu:
                        st.write("⭐" * act.note_lieu)
                    else:
                        st.caption("✅ Fait")


def render_suggestions():
    """Affiche les suggestions IA"""
    st.subheader("💡 Suggestions IA")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        meteo = st.selectbox("🌤️ Météo", METEO_OPTIONS)
    
    with col2:
        budget = st.slider("💰 Budget max", 0, 200, 50, step=10)
    
    with col3:
        region = st.text_input("📍 Région", "Île-de-France")
    
    age_jules = get_age_jules_mois()
    st.caption(f"👶 Jules: {age_jules} mois")
    
    if st.button("🤖 Générer des idées", type="primary"):
        with st.spinner("Réflexion en cours..."):
            try:
                import asyncio
                service = WeekendAIService()
                result = asyncio.run(service.suggerer_activites(
                    meteo=meteo,
                    age_enfant_mois=age_jules,
                    budget=budget,
                    region=region
                ))
                st.markdown(result)
                
                # Bouton pour ajouter
                st.markdown("---")
                st.info("💡 Pour ajouter une suggestion au planning, utilisez l'onglet 'Ajouter'")
                
            except Exception as e:
                st.error(f"Erreur IA: {e}")


def render_lieux_testes():
    """Affiche les lieux déjà testés"""
    st.subheader("🗺️ Lieux testés")
    
    lieux = get_lieux_testes()
    
    if not lieux:
        st.info("Aucun lieu noté pour l'instant. Notez vos sorties pour les retrouver ici!")
        return
    
    # Filtres
    types_presents = list(set(l.type_activite for l in lieux))
    filtre_type = st.selectbox("Filtrer par type", ["Tous"] + types_presents)
    
    for lieu in lieux:
        if filtre_type != "Tous" and lieu.type_activite != filtre_type:
            continue
        
        type_info = TYPES_ACTIVITES.get(lieu.type_activite, TYPES_ACTIVITES["autre"])
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{type_info['emoji']} {lieu.titre}**")
                if lieu.lieu:
                    st.caption(f"📍 {lieu.lieu}")
                if lieu.commentaire:
                    st.write(lieu.commentaire)
            
            with col2:
                st.write("⭐" * (lieu.note_lieu or 0))
                if lieu.a_refaire is not None:
                    st.write("🔄 À refaire" if lieu.a_refaire else "❌ Non")
            
            with col3:
                if lieu.cout_reel:
                    st.write(f"💰 {lieu.cout_reel:.0f}€")
                st.caption(lieu.date_prevue.strftime("%d/%m/%Y"))


def render_add_activity():
    """Formulaire d'ajout d'activité"""
    st.subheader("➕ Ajouter une activité")
    
    saturday, sunday = get_next_weekend()
    
    # Préremplir avec la date si sélectionnée
    default_date = st.session_state.get("weekend_add_date", saturday)
    
    with st.form("add_weekend_activity"):
        titre = st.text_input("Titre *", placeholder="Ex: Parc de la Villette")
        
        col1, col2 = st.columns(2)
        
        with col1:
            type_activite = st.selectbox(
                "Type *",
                list(TYPES_ACTIVITES.keys()),
                format_func=lambda x: f"{TYPES_ACTIVITES[x]['emoji']} {TYPES_ACTIVITES[x]['label']}"
            )
        
        with col2:
            date_prevue = st.date_input("Date *", value=default_date)
        
        col3, col4 = st.columns(2)
        
        with col3:
            heure = st.time_input("Heure", value=None)
        
        with col4:
            duree = st.number_input("Durée (heures)", min_value=0.5, max_value=8.0, value=2.0, step=0.5)
        
        lieu = st.text_input("Lieu / Adresse", placeholder="Ex: 211 Av. Jean Jaurès, Paris")
        
        col5, col6 = st.columns(2)
        
        with col5:
            cout = st.number_input("Coût estimé (€)", min_value=0.0, step=5.0)
        
        with col6:
            meteo = st.selectbox("Météo requise", ["", "ensoleillé", "couvert", "intérieur"])
        
        description = st.text_area("Notes", height=80)
        
        adapte_jules = st.checkbox("Adapté à Jules", value=True)
        
        if st.form_submit_button("✅ Ajouter", type="primary"):
            if not titre:
                st.error("Titre requis")
            else:
                try:
                    with get_db_context() as db:
                        activity = WeekendActivity(
                            titre=titre,
                            type_activite=type_activite,
                            date_prevue=date_prevue,
                            heure_debut=heure.strftime("%H:%M") if heure else None,
                            duree_estimee_h=duree,
                            lieu=lieu or None,
                            cout_estime=cout if cout > 0 else None,
                            meteo_requise=meteo or None,
                            description=description or None,
                            adapte_jules=adapte_jules,
                            statut="planifié",
                            participants=["Anne", "Mathieu", "Jules"]
                        )
                        db.add(activity)
                        db.commit()
                        st.success(f"✅ {titre} ajouté!")
                        st.session_state.pop("weekend_add_date", None)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def render_noter_sortie():
    """Permet de noter une sortie terminée"""
    st.subheader("⭐ Noter une sortie")
    
    try:
        with get_db_context() as db:
            # Activités terminées non notées
            activities = db.query(WeekendActivity).filter(
                WeekendActivity.statut == "terminé",
                WeekendActivity.note_lieu.is_(None)
            ).all()
            
            if not activities:
                st.info("Aucune sortie à noter")
                return
            
            for act in activities:
                type_info = TYPES_ACTIVITES.get(act.type_activite, TYPES_ACTIVITES["autre"])
                
                with st.container(border=True):
                    st.markdown(f"**{type_info['emoji']} {act.titre}**")
                    st.caption(f"📅 {act.date_prevue.strftime('%d/%m/%Y')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        note = st.slider("Note", 1, 5, 3, key=f"note_{act.id}")
                        a_refaire = st.checkbox("À refaire ?", key=f"refaire_{act.id}")
                    
                    with col2:
                        cout_reel = st.number_input("Coût réel (€)", min_value=0.0, key=f"cout_{act.id}")
                        commentaire = st.text_input("Commentaire", key=f"comm_{act.id}")
                    
                    if st.button("💾 Sauvegarder", key=f"save_{act.id}"):
                        act.note_lieu = note
                        act.a_refaire = a_refaire
                        act.cout_reel = cout_reel if cout_reel > 0 else None
                        act.commentaire = commentaire or None
                        db.commit()
                        st.success("✅ Noté!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"Erreur: {e}")
