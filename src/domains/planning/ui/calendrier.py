"""
Module Calendrier Unifié - Vue détaillée du calendrier familial

Affiche tous les événements calendrier avec interface interactive
Utilise PlanningAIService pour agrégation optimisée
"""

import calendar
from datetime import date, datetime, timedelta

import streamlit as st

from src.services.planning_unified import get_planning_service

# Logique métier pure
from src.domains.planning.logic.calendrier_logic import (
    get_jours_mois,
    filtrer_evenements_jour,
    grouper_evenements_par_jour
)

logger = __import__("logging").getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS UI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def afficher_jour_expandable(jour: date, jour_complet: dict, jour_nom: str) -> None:
    """Affiche un jour avec tous ses événements en expandable"""
    is_today = jour == date.today()

    # Header avec badge charge
    charge_emoji = {
        "faible": "🔔,
        "normal": "💰,
        "intense": "❌",
    }.get(jour_complet.get("charge", "normal"), "âšª")

    header = f"{charge_emoji} {jour_nom} {jour.strftime('%d/%m')}"
    if is_today:
        header = f"📥 {header}"

    with st.expander(header, expanded=is_today):
        # Colonnes pour meilleure organisation
        if jour_complet.get("repas"):
            st.markdown("##### 📷 Repas")
            for repas in jour_complet["repas"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{repas['type'].capitalize()}**: {repas['recette']}")
                with col2:
                    st.caption(f"{repas['portions']} portions")

        if jour_complet.get("activites"):
            st.markdown("##### 🎨 Activités")
            for act in jour_complet["activites"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    label = "👶 if act.get("pour_jules") else "📅€🧹€💡
                    st.write(f"{label} **{act['titre']}** ({act['type']})")
                with col2:
                    if act.get("budget"):
                        st.caption(f"{act['budget']:.0f}€")

        if jour_complet.get("projets"):
            st.markdown("##### 🗑️ Projets")
            for proj in jour_complet["projets"]:
                priorite_color = {
                    "basse": "🔔,
                    "moyenne": "💰,
                    "haute": "❌",
                }.get(proj.get("priorite", "moyenne"), "âšª")
                st.write(f"{priorite_color} **{proj['nom']}** - {proj['statut']}")

        if jour_complet.get("events"):
            st.markdown("##### 📋… Événements")
            for event in jour_complet["events"]:
                debut = event["debut"].strftime("%H:%M") if isinstance(event["debut"], datetime) else "â€”"
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"â° **{event['titre']}**")
                    if event.get("lieu"):
                        st.caption(f"📋 {event['lieu']}")
                with col2:
                    st.caption(debut)

        if jour_complet.get("routines"):
            st.markdown("##### â° Routines")
            for routine in jour_complet["routines"]:
                heure = routine.get("heure", "â€”")
                status = "✅" if routine.get("fait") else "◯"
                st.write(f"{status} **{routine['nom']}** ({heure})")

        # Alertes du jour
        if jour_complet.get("alertes"):
            st.markdown("##### âš ï¸ Alertes")
            for alerte in jour_complet["alertes"]:
                st.warning(alerte, icon="âš ï¸")

        # Si vide
        if not any(
            [
                jour_complet.get("repas"),
                jour_complet.get("activites"),
                jour_complet.get("projets"),
                jour_complet.get("events"),
                jour_complet.get("routines"),
            ]
        ):
            st.caption("Aucun événement prévu ce jour")

        # Charge visuelle
        charge = jour_complet.get("charge_score", 0)
        st.markdown(f"**Charge du jour**: {charge}/100")
        st.progress(min(charge / 100, 1.0))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Module Calendrier unifié"""

    st.title("📋… Calendrier Familial")
    st.caption("Vue intégrée de tous les événements familiaux")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # NAVIGATION SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    if "planning_week_start" not in st.session_state:
        today = date.today()
        st.session_state.planning_week_start = today - timedelta(days=today.weekday())

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

    with col_nav1:
        if st.button("â¬…ï¸ Semaine précédente", use_container_width=True):
            st.session_state.planning_week_start -= timedelta(days=7)
            st.rerun()

    with col_nav2:
        week_start = st.session_state.planning_week_start
        week_end = week_start + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center;'>{week_start.strftime('%d/%m')} â€” {week_end.strftime('%d/%m/%Y')}</h3>",
            unsafe_allow_html=True,
        )

    with col_nav3:
        if st.button("Semaine suivante âž¡ï¸", use_container_width=True):
            st.session_state.planning_week_start += timedelta(days=7)
            st.rerun()

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CHARGEMENT DONNÉES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    service = get_planning_service()
    semaine = service.get_semaine_complete(st.session_state.planning_week_start)

    if not semaine:
        st.error("❌ Erreur lors du chargement de la semaine")
        return

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STATS SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    st.markdown("### [CHART] Résumé de la semaine")

    cols_stats = st.columns(5)

    stats = semaine.stats_semaine
    with cols_stats[0]:
        st.metric("📷 Repas", stats.get("total_repas", 0))

    with cols_stats[1]:
        st.metric("🎨 Activités", stats.get("total_activites", 0))

    with cols_stats[2]:
        st.metric("🍽️ Pour Jules", stats.get("activites_jules", 0))

    with cols_stats[3]:
        st.metric("🗑️ Projets", stats.get("total_projets", 0))

    with cols_stats[4]:
        budget = stats.get("budget_total", 0)
        st.metric(f"📱 Budget", f"{budget:.0f}€")

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALERTES SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    if semaine.alertes_semaine:
        st.markdown("### âš ï¸ Alertes Semaine")
        for alerte in semaine.alertes_semaine:
            st.warning(alerte, icon="âš ï¸")
        st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CHARGE GLOBALE SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    charge_color = {
        "faible": "🔔,
        "normal": "💰,
        "intense": "❌",
    }
    charge_emoji = charge_color.get(semaine.charge_globale, "âšª")

    st.markdown(f"### {charge_emoji} Charge semaine globale: **{semaine.charge_globale.upper()}**")
    st.progress(min(stats.get("charge_moyenne", 50) / 100, 1.0))

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # VUE JOURS DÉTAILLÉE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    st.markdown("### 📋… Détail par jour")

    jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    for i in range(7):
        jour = st.session_state.planning_week_start + timedelta(days=i)
        jour_str = jour.isoformat()
        jour_complet = semaine.jours.get(jour_str)

        if jour_complet:
            afficher_jour_expandable(jour, jour_complet.dict(), jours_semaine[i].capitalize())

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ONGLETS ACTIONS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    tab1, tab2, tab3 = st.tabs(["âž• Nouvel événement", "– Générer avec IA", "📋… Vue mois"])

    with tab1:
        st.subheader("âž• Ajouter un événement")

        with st.form("form_event_planning"):
            titre = st.text_input("Titre *", placeholder="Ex: RDV médecin, Sortie parc...")
            type_event = st.selectbox(
                "Type d'événement",
                ["famille", "santé", "loisirs", "social", "travail", "autre"],
            )

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                date_event = st.date_input("Date *", value=date.today())
                heure = st.time_input("Heure", value=datetime.now().time())

            with col_e2:
                lieu = st.text_input("Lieu", placeholder="Ex: Parc du château")
                couleur = st.selectbox("Couleur", ["bleu", "rouge", "vert", "jaune", "violet"])

            description = st.text_area("Description (optionnel)")

            submitted = st.form_submit_button("🎯 Créer l'événement", type="primary")

            if submitted:
                if not titre:
                    st.error("Le titre est obligatoire")
                else:
                    debut = datetime.combine(date_event, heure)
                    service.creer_event(
                        titre=titre,
                        date_debut=debut,
                        type_event=type_event,
                        description=description,
                        lieu=lieu,
                        couleur=couleur,
                    )
                    st.success(f"✅ Événement '{titre}' créé!")
                    st.balloons()
                    st.rerun()

    with tab2:
        st.subheader("– Générer semaine avec IA")

        st.info(
            "🚀 L'IA peut générer une semaine complète équilibrée basée sur vos contraintes et objectifs familiaux"
        )

        with st.form("form_gen_ia"):
            budget = st.slider("Budget semaine (€)", 100, 1000, 400)
            energie = st.selectbox("Niveau d'énergie famille", ["faible", "normal", "élevé"])
            objectifs = st.multiselect(
                "Objectifs santé",
                ["Cardio", "Yoga", "Detente", "Temps en famille", "Sommeil"],
            )

            gen_submitted = st.form_submit_button("📤 Générer une semaine équilibrée", type="primary")

            if gen_submitted:
                with st.spinner("– L'IA réfléchit..."):
                    result = service.generer_semaine_ia(
                        date_debut=st.session_state.planning_week_start,
                        contraintes={"budget": budget, "energie": energie},
                        contexte={"objectifs_sante": objectifs, "jules_age_mois": 19},
                    )

                    if result:
                        st.success("✅ Semaine générée!")
                        st.markdown(f"**Harmonie**: {result.harmonie_description}")
                        with st.expander("Raisons de cette proposition"):
                            for raison in result.raisons:
                                st.write(f"• {raison}")
                    else:
                        st.error("❌ Erreur lors de la génération")

    with tab3:
        st.subheader("📋… Vue mensuelle")

        col_m1, col_m2 = st.columns([2, 1])

        with col_m1:
            today = date.today()
            mois_select = st.selectbox("Mois", list(calendar.month_name)[1:], index=today.month - 1)
            mois_num = list(calendar.month_name).index(mois_select)

        with col_m2:
            annee = st.number_input("Année", 2020, 2030, today.year)

        st.markdown(f"### {mois_select} {annee}")

        # Calendrier minimal
        cal = calendar.monthcalendar(annee, mois_num)

        cols_jours = st.columns(7)
        jours_semaine_abbr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

        for i, col in enumerate(cols_jours):
            col.markdown(f"**{jours_semaine_abbr[i]}**")

        for semaine_cal in cal:
            cols = st.columns(7)
            for i, jour in enumerate(semaine_cal):
                if jour == 0:
                    cols[i].write("")
                else:
                    date_jour = date(annee, mois_num, jour)
                    is_today = date_jour == date.today()

                    style = "👧 if is_today else ""
                    cols[i].write(f"{style} **{jour}**")

        st.caption("📥 = Aujourd'hui")

