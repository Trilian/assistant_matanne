"""
Module Sorties Weekend - Composants UI
"""

from src.core.async_utils import executer_async
from src.core.session_keys import SK
from src.services.famille.weekend import obtenir_service_weekend
from src.ui import etat_vide

from .ai_service import WeekendAIService
from .utils import (
    METEO_OPTIONS,
    TYPES_ACTIVITES,
    WeekendActivity,
    date,
    get_age_jules_mois,
    get_budget_weekend,
    get_lieux_testes,
    get_next_weekend,
    get_weekend_activities,
    mark_activity_done,
    st,
)


def afficher_planning():
    """Affiche le planning du weekend"""
    saturday, sunday = get_next_weekend()
    activities = get_weekend_activities(saturday, sunday)

    st.subheader("📅 Ce Weekend")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**🗓️ Samedi {saturday.strftime('%d/%m')}**")
        afficher_day_activities(saturday, activities["saturday"])

    with col2:
        st.markdown(f"**🗓️ Dimanche {sunday.strftime('%d/%m')}**")
        afficher_day_activities(sunday, activities["sunday"])

    # Budget
    budget = get_budget_weekend(saturday, sunday)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Budget estime", f"{budget['estime']:.0f}€")
    with col2:
        st.metric("💸 Depense", f"{budget['reel']:.0f}€")


def afficher_day_activities(day: date, activities: list):
    """Affiche les activites d'un jour"""
    if not activities:
        st.caption("Rien de prevu")
        if st.button("➕ Ajouter", key=f"add_{day}"):
            st.session_state[SK.WEEKEND_ADD_DATE] = day
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
                if act.statut == "planifie":
                    if st.button("✅", key=f"done_{act.id}", help="Marquer fait"):
                        mark_activity_done(act.id)
                        st.rerun()
                elif act.statut == "termine":
                    if act.note_lieu:
                        st.write("⭐" * act.note_lieu)
                    else:
                        st.caption("✅ Fait")


def afficher_suggestions():
    """Affiche les suggestions IA"""
    st.subheader("💡 Suggestions IA")

    col1, col2, col3 = st.columns(3)

    with col1:
        meteo = st.selectbox("🌤️ Meteo", METEO_OPTIONS)

    with col2:
        budget = st.slider("💰 Budget max", 0, 200, 50, step=10)

    with col3:
        region = st.text_input("📍 Region", "Île-de-France")

    age_jules = get_age_jules_mois()
    st.caption(f"👶 Jules: {age_jules} mois")

    if st.button("🤖 Generer des idees", type="primary"):
        with st.spinner("Reflexion en cours..."):
            try:
                service = WeekendAIService()
                result = executer_async(
                    service.suggerer_activites(
                        meteo=meteo, age_enfant_mois=age_jules, budget=budget, region=region
                    )
                )
                st.markdown(result)

                # Bouton pour ajouter
                st.markdown("---")
                st.info("💡 Pour ajouter une suggestion au planning, utilisez l'onglet 'Ajouter'")

            except Exception as e:
                st.error(f"Erreur IA: {e}")


def afficher_lieux_testes():
    """Affiche les lieux dejà testes"""
    st.subheader("🗺️ Lieux testes")

    lieux = get_lieux_testes()

    if not lieux:
        etat_vide("Aucun lieu noté", "📍", "Notez vos sorties pour les retrouver ici !")
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


def afficher_add_activity():
    """Formulaire d'ajout d'activite"""
    st.subheader("➕ Ajouter une activite")

    saturday, sunday = get_next_weekend()

    # Preremplir avec la date si selectionnee
    default_date = st.session_state.get(SK.WEEKEND_ADD_DATE, saturday)

    with st.form("add_weekend_activity"):
        titre = st.text_input("Titre *", placeholder="Ex: Parc de la Villette")

        col1, col2 = st.columns(2)

        with col1:
            type_activite = st.selectbox(
                "Type *",
                list(TYPES_ACTIVITES.keys()),
                format_func=lambda x: (
                    f"{TYPES_ACTIVITES[x]['emoji']} {TYPES_ACTIVITES[x]['label']}"
                ),
            )

        with col2:
            date_prevue = st.date_input("Date *", value=default_date)

        col3, col4 = st.columns(2)

        with col3:
            heure = st.time_input("Heure", value=None)

        with col4:
            duree = st.number_input(
                "Duree (heures)", min_value=0.5, max_value=8.0, value=2.0, step=0.5
            )

        lieu = st.text_input("Lieu / Adresse", placeholder="Ex: 211 Av. Jean Jaurès, Paris")

        col5, col6 = st.columns(2)

        with col5:
            cout = st.number_input("Coût estime (€)", min_value=0.0, step=5.0)

        with col6:
            meteo = st.selectbox("Meteo requise", ["", "ensoleille", "couvert", "interieur"])

        description = st.text_area("Notes", height=80)

        adapte_jules = st.checkbox("Adapte à Jules", value=True)

        if st.form_submit_button("✅ Ajouter", type="primary"):
            if not titre:
                st.error("Titre requis")
            else:
                try:
                    obtenir_service_weekend().ajouter_activite(
                        titre=titre,
                        type_activite=type_activite,
                        date_prevue=date_prevue,
                        heure=heure.strftime("%H:%M") if heure else None,
                        duree=duree,
                        lieu=lieu or None,
                        cout_estime=cout if cout > 0 else None,
                        meteo_requise=meteo or None,
                        description=description or None,
                        adapte_jules=adapte_jules,
                    )
                    st.success(f"\u2705 {titre} ajoute!")
                    st.session_state.pop(SK.WEEKEND_ADD_DATE, None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def afficher_noter_sortie():
    """Permet de noter une sortie terminee"""
    st.subheader("⭐ Noter une sortie")

    try:
        service = obtenir_service_weekend()
        activities = service.get_activites_non_notees()

        if not activities:
            etat_vide("Aucune sortie à noter", "⭐", "Les sorties terminées apparaîtront ici")
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
                    cout_reel = st.number_input(
                        "Coût reel (€)", min_value=0.0, key=f"cout_{act.id}"
                    )
                    commentaire = st.text_input("Commentaire", key=f"comm_{act.id}")

                if st.button("💾 Sauvegarder", key=f"save_{act.id}"):
                    service.noter_sortie(
                        activity_id=act.id,
                        note=note,
                        a_refaire=a_refaire,
                        cout_reel=cout_reel if cout_reel > 0 else None,
                        commentaire=commentaire or None,
                    )
                    st.success("✅ Note!")
                    st.rerun()

    except Exception as e:
        st.error(f"Erreur: {e}")
