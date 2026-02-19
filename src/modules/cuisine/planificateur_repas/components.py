"""
Module Planificateur de Repas - Composants UI
"""

from ._common import PROTEINES, ROBOTS_CUISINE, TEMPS_CATEGORIES, PreferencesUtilisateur, date, st
from .preferences import (
    ajouter_feedback,
    charger_feedbacks,
    charger_preferences,
    sauvegarder_preferences,
)


def afficher_configuration_preferences():
    """Affiche le formulaire de configuration des préférences."""

    prefs = charger_preferences()

    st.subheader("⚙️ Mes Préférences Alimentaires")

    with st.form("form_preferences"):
        # Famille
        st.markdown("##### 👨‍👩‍👦 Ma famille")
        col1, col2, col3 = st.columns(3)

        with col1:
            nb_adultes = st.number_input("Adultes", 1, 6, prefs.nb_adultes)
        with col2:
            jules_present = st.checkbox("Jules mange avec nous", value=prefs.jules_present)
        with col3:
            jules_age = st.number_input("Âge Jules (mois)", 6, 36, prefs.jules_age_mois)

        st.markdown("##### ⏱️ Temps de cuisine")
        col1, col2 = st.columns(2)

        with col1:
            temps_semaine = st.selectbox(
                "En semaine",
                options=list(TEMPS_CATEGORIES.keys()),
                format_func=lambda x: TEMPS_CATEGORIES[x]["label"],
                index=list(TEMPS_CATEGORIES.keys()).index(prefs.temps_semaine),
            )
        with col2:
            temps_weekend = st.selectbox(
                "Le weekend",
                options=list(TEMPS_CATEGORIES.keys()),
                format_func=lambda x: TEMPS_CATEGORIES[x]["label"],
                index=list(TEMPS_CATEGORIES.keys()).index(prefs.temps_weekend),
            )

        st.markdown("##### 🚫 Aliments à éviter")
        exclus = st.text_input(
            "Séparés par des virgules",
            value=", ".join(prefs.aliments_exclus),
            placeholder="Ex: fruits de mer, abats, coriandre",
        )

        st.markdown("##### ❤️ Vos basiques adorés")
        favoris = st.text_input(
            "Séparés par des virgules",
            value=", ".join(prefs.aliments_favoris),
            placeholder="Ex: pâtes, poulet, gratins",
        )

        st.markdown("##### ⚖️ Équilibre souhaité par semaine")
        col1, col2, col3 = st.columns(3)

        with col1:
            poisson = st.number_input("🐟 Poisson", 0, 7, prefs.poisson_par_semaine)
        with col2:
            vege = st.number_input("🥬 Végétarien", 0, 7, prefs.vegetarien_par_semaine)
        with col3:
            viande_rouge = st.number_input("🥩 Viande rouge max", 0, 7, prefs.viande_rouge_max)

        st.markdown("##### 🤖 Mes robots cuisine")
        robots_selected = []
        cols = st.columns(3)
        for i, (robot_id, robot_info) in enumerate(ROBOTS_CUISINE.items()):
            with cols[i % 3]:
                if st.checkbox(
                    f"{robot_info['emoji']} {robot_info['label']}",
                    value=robot_id in prefs.robots,
                    key=f"robot_pref_{robot_id}",
                ):
                    robots_selected.append(robot_id)

        # Soumettre
        if st.form_submit_button("💾 Sauvegarder", type="primary"):
            new_prefs = PreferencesUtilisateur(
                nb_adultes=nb_adultes,
                jules_present=jules_present,
                jules_age_mois=jules_age,
                temps_semaine=temps_semaine,
                temps_weekend=temps_weekend,
                aliments_exclus=[x.strip() for x in exclus.split(",") if x.strip()],
                aliments_favoris=[x.strip() for x in favoris.split(",") if x.strip()],
                poisson_par_semaine=poisson,
                vegetarien_par_semaine=vege,
                viande_rouge_max=viande_rouge,
                robots=robots_selected,
                magasins_preferes=prefs.magasins_preferes,
            )
            sauvegarder_preferences(new_prefs)
            st.success("✅ Préférences sauvegardées!")
            st.rerun()


def afficher_apprentissage_ia():
    """Affiche ce que l'IA a appris des goûts."""

    feedbacks = charger_feedbacks()

    if not feedbacks:
        st.info("🧠 L'IA n'a pas encore appris vos goûts. Notez les recettes avec 👍/👎 !")
        return

    st.markdown("##### 🧠 L'IA a appris que vous...")

    likes = [f.recette_nom for f in feedbacks if f.feedback == "like"]
    dislikes = [f.recette_nom for f in feedbacks if f.feedback == "dislike"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👍 Aimez:**")
        if likes:
            for nom in likes[-5:]:
                st.caption(f"• {nom}")
        else:
            st.caption("Pas encore de données")

    with col2:
        st.markdown("**👎 N'aimez pas:**")
        if dislikes:
            for nom in dislikes[-5:]:
                st.caption(f"• {nom}")
        else:
            st.caption("Pas encore de données")


def afficher_carte_recette_suggestion(
    suggestion: dict,
    jour: str,
    type_repas: str,
    key_prefix: str,
):
    """Affiche une carte de recette avec feedback."""

    with st.container():
        col_info, col_actions = st.columns([4, 1])

        with col_info:
            st.markdown(f"**{suggestion.get('nom', 'Recette')}**")

            # Tags
            tags = []
            if suggestion.get("temps_minutes"):
                tags.append(f"â±ï¸ {suggestion['temps_minutes']} min")
            if suggestion.get("proteine"):
                prot_info = PROTEINES.get(suggestion["proteine"], {})
                tags.append(
                    f"{prot_info.get('emoji', '')} {prot_info.get('label', suggestion['proteine'])}"
                )
            if suggestion.get("robot"):
                robot_info = ROBOTS_CUISINE.get(suggestion["robot"], {})
                tags.append(f"{robot_info.get('emoji', '')} {robot_info.get('label', '')}")

            st.caption(" â”‚ ".join(tags))

            # Version Jules
            if suggestion.get("jules_adaptation"):
                with st.expander("👶 Instructions Jules", expanded=False):
                    st.markdown(suggestion["jules_adaptation"])

        with col_actions:
            # Feedback
            col_like, col_dislike = st.columns(2)
            with col_like:
                if st.button("👍", key=f"{key_prefix}_like", help="J'aime"):
                    ajouter_feedback(
                        recette_id=hash(suggestion.get("nom", "")),
                        recette_nom=suggestion.get("nom", ""),
                        feedback="like",
                    )
                    st.toast("👍 Noté!")
            with col_dislike:
                if st.button("👎", key=f"{key_prefix}_dislike", help="Je n'aime pas"):
                    ajouter_feedback(
                        recette_id=hash(suggestion.get("nom", "")),
                        recette_nom=suggestion.get("nom", ""),
                        feedback="dislike",
                    )
                    st.toast("👎 Noté!")

            # Changer
            if st.button("🔄", key=f"{key_prefix}_change", help="Autre suggestion"):
                st.session_state[f"show_alternatives_{key_prefix}"] = True
                st.rerun()


def afficher_jour_planning(
    jour: str,
    jour_date: date,
    repas_jour: dict,
    key_prefix: str,
):
    """Affiche un jour du planning avec ses repas."""

    with st.expander(f"📅 **{jour}** {jour_date.strftime('%d/%m')}", expanded=True):
        # Midi
        st.markdown("##### 🌞 Midi")
        midi = repas_jour.get("midi")
        if midi:
            afficher_carte_recette_suggestion(midi, jour, "midi", f"{key_prefix}_midi")
        else:
            st.info("Pas encore planifié")
            if st.button("➕ Ajouter midi", key=f"{key_prefix}_add_midi"):
                st.session_state[f"add_repas_{key_prefix}_midi"] = True

        st.divider()

        # Soir
        st.markdown("##### 🌙 Soir")
        soir = repas_jour.get("soir")
        if soir:
            afficher_carte_recette_suggestion(soir, jour, "soir", f"{key_prefix}_soir")
        else:
            st.info("Pas encore planifié")
            if st.button("➕ Ajouter soir", key=f"{key_prefix}_add_soir"):
                st.session_state[f"add_repas_{key_prefix}_soir"] = True

        # Goûter (optionnel)
        gouter = repas_jour.get("gouter")
        if gouter:
            st.divider()
            st.markdown("##### 🍰 Goûter")
            afficher_carte_recette_suggestion(gouter, jour, "gouter", f"{key_prefix}_gouter")


def afficher_resume_equilibre(planning_data: dict):
    """Affiche le résumé de l'équilibre nutritionnel."""

    # Compter les types de protéines
    equilibre = {
        "poisson": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
    }

    for jour, repas in planning_data.items():
        for type_repas in ["midi", "soir"]:
            if repas.get(type_repas) and repas[type_repas].get("proteine"):
                prot = repas[type_repas]["proteine"]
                if prot in PROTEINES:
                    cat = PROTEINES[prot]["categorie"]
                    if cat in equilibre:
                        equilibre[cat] += 1
                    elif cat in ("viande", "volaille"):
                        equilibre["volaille"] += 1

    prefs = charger_preferences()

    st.markdown("##### 📊 Équilibre de la semaine")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta = equilibre["poisson"] - prefs.poisson_par_semaine
        st.metric("🐟 Poisson", equilibre["poisson"], delta=f"{delta:+d}" if delta else None)

    with col2:
        delta = equilibre["vegetarien"] - prefs.vegetarien_par_semaine
        st.metric("🥬 Végé", equilibre["vegetarien"], delta=f"{delta:+d}" if delta else None)

    with col3:
        st.metric("🐔 Volaille", equilibre["volaille"])

    with col4:
        delta = equilibre["viande_rouge"] - prefs.viande_rouge_max
        color = "inverse" if delta > 0 else "normal"
        st.metric(
            "🥩 Rouge",
            equilibre["viande_rouge"],
            delta=f"{delta:+d}" if delta else None,
            delta_color=color,
        )
