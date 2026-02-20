"""Composants UI pour le module Batch Cooking Détaillé."""

from datetime import time

import streamlit as st

from src.core.session_keys import SK
from src.modules.cuisine.batch_cooking_utils import ROBOTS_INFO
from src.ui import etat_vide

from .constants import TYPES_DECOUPE


def afficher_selecteur_session():
    """Sélecteur de type de session."""

    st.subheader("📅 Type de session")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🌞 **Dimanche**\n2-3h avec Jules",
            key="btn_session_dimanche",
            use_container_width=True,
            type="primary" if st.session_state.get(SK.BATCH_TYPE) == "dimanche" else "secondary",
        ):
            st.session_state.batch_type = "dimanche"
            st.rerun()

    with col2:
        if st.button(
            "🌙 **Mercredi**\n1-1.5h solo",
            key="btn_session_mercredi",
            use_container_width=True,
            type="primary" if st.session_state.get(SK.BATCH_TYPE) == "mercredi" else "secondary",
        ):
            st.session_state.batch_type = "mercredi"
            st.rerun()


def afficher_planning_semaine_preview(planning_data: dict):
    """Affiche les repas de la semaine pour lesquels on fait le batch."""

    st.markdown("##### 📋 Repas à préparer")

    if not planning_data:
        etat_vide("Aucun planning trouvé", "📋", "Allez d'abord dans 'Planifier mes repas'")
        return

    # Afficher en tableau compact
    for jour, repas in planning_data.items():
        with st.container():
            st.markdown(f"**{jour}**")
            cols = st.columns(2)

            with cols[0]:
                midi = repas.get("midi", {})
                if midi:
                    st.caption(f"🌞 {midi.get('nom', 'Non défini')}")
                else:
                    st.caption("🌞 -")

            with cols[1]:
                soir = repas.get("soir", {})
                if soir:
                    st.caption(f"🌙 {soir.get('nom', 'Non défini')}")
                else:
                    st.caption("🌙 -")


def afficher_ingredient_detaille(ingredient: dict, key_prefix: str):
    """Affiche un ingrédient avec tous ses détails."""

    with st.container():
        # Ligne principale
        col_qty, col_nom, col_prep = st.columns([1, 2, 2])

        with col_qty:
            qty = ingredient.get("quantite", 0)
            unite = ingredient.get("unite", "")
            poids = ingredient.get("poids_g", "")

            qty_str = f"{int(qty) if qty == int(qty) else qty} {unite}"
            if poids:
                qty_str += f"\n(~{poids}g)"

            st.markdown(f"**{qty_str}**")

        with col_nom:
            st.markdown(f"**{ingredient.get('nom', '')}**")
            if ingredient.get("description"):
                st.caption(ingredient["description"])

        with col_prep:
            if ingredient.get("decoupe"):
                decoupe_info = TYPES_DECOUPE.get(ingredient["decoupe"], {})
                taille = ingredient.get("taille_decoupe", "")

                st.markdown(
                    f"{decoupe_info.get('emoji', '🔪')} **{decoupe_info.get('label', 'Découpe')}**"
                )
                if taille:
                    st.caption(f"Taille: {taille}")

            if ingredient.get("instruction_prep"):
                st.caption(f"📝 {ingredient['instruction_prep']}")

        # Badge Jules
        if ingredient.get("jules_peut_aider"):
            st.success(f"👶 Jules: {ingredient.get('tache_jules', 'Peut aider')}", icon="👶")


def afficher_etape_batch(etape: dict, numero: int, key_prefix: str):
    """Affiche une étape de batch cooking."""

    est_passif = etape.get("est_passif", False)

    with st.container():
        # Header
        col_num, col_titre, col_duree = st.columns([1, 5, 1])

        with col_num:
            st.markdown(f"### {numero}")

        with col_titre:
            titre = etape.get("titre", "Étape")
            emoji = "⏳" if est_passif else "👩‍🍳"
            st.markdown(f"**{emoji} {titre}**")

        with col_duree:
            duree = etape.get("duree_minutes", 0)
            st.markdown(f"**{duree} min**")

        # Description
        if etape.get("description"):
            st.markdown(etape["description"])

        # Robot
        robot = etape.get("robot")
        if robot:
            afficher_instruction_robot(robot)

        # Jules
        if etape.get("jules_participation"):
            st.success(f"👶 **Jules peut aider:** {etape.get('tache_jules', '')}", icon="👶")

        st.divider()


def afficher_instruction_robot(robot_config: dict):
    """Affiche les instructions détaillées pour un robot."""

    robot_type = robot_config.get("type", "")
    robot_info = ROBOTS_INFO.get(robot_type, {})

    emoji = robot_info.get("emoji", "🤖")
    nom = robot_info.get("nom", robot_type.title())

    # Construire l'instruction
    parts = [f"**{emoji} {nom.upper()}**"]

    # Paramètres spécifiques
    if robot_type == "monsieur_cuisine":
        if robot_config.get("vitesse"):
            parts.append(f"Vitesse **{robot_config['vitesse']}**")
        if robot_config.get("duree_secondes"):
            secs = robot_config["duree_secondes"]
            if secs >= 60:
                mins = secs // 60
                rest = secs % 60
                duree_str = f"{mins}min{rest:02d}" if rest else f"{mins}min"
            else:
                duree_str = f"{secs}sec"
            parts.append(f"Durée **{duree_str}**")
        if robot_config.get("temperature"):
            parts.append(f"Temp **{robot_config['temperature']}°C**")

    elif robot_type == "cookeo":
        if robot_config.get("programme"):
            parts.append(f"Programme: **{robot_config['programme']}**")
        if robot_config.get("duree_secondes"):
            mins = robot_config["duree_secondes"] // 60
            parts.append(f"Durée: **{mins}min**")

    elif robot_type == "four":
        if robot_config.get("mode"):
            parts.append(f"Mode: {robot_config['mode']}")
        if robot_config.get("temperature"):
            parts.append(f"**{robot_config['temperature']}°C**")
        if robot_config.get("duree_secondes"):
            mins = robot_config["duree_secondes"] // 60
            parts.append(f"**{mins}min**")

    st.info(" │ ".join(parts))


def afficher_timeline_session(etapes: list, heure_debut: time):
    """Affiche une timeline visuelle de la session."""

    st.markdown("##### ⏱️ Timeline")

    temps_courant = 0

    for i, etape in enumerate(etapes):
        duree = etape.get("duree_minutes", 0)
        debut_h = (heure_debut.hour * 60 + heure_debut.minute + temps_courant) // 60
        debut_m = (heure_debut.hour * 60 + heure_debut.minute + temps_courant) % 60

        est_passif = etape.get("est_passif", False)
        emoji = "⏳" if est_passif else "👩‍🍳"

        # Afficher la barre
        with st.container():
            col_time, col_bar = st.columns([1, 4])

            with col_time:
                st.markdown(f"**{debut_h:02d}:{debut_m:02d}**")

            with col_bar:
                titre = etape.get("titre", "Étape")[:30]

                # Couleur selon type
                if est_passif:
                    st.info(f"{emoji} {titre} ({duree}min)")
                else:
                    st.success(f"{emoji} {titre} ({duree}min)")

        if not est_passif:
            temps_courant += duree


def afficher_moments_jules(moments: list):
    """Affiche les moments de participation de Jules."""

    if not moments:
        return

    st.markdown("##### 👶 Moments avec Jules")

    for moment in moments:
        st.success(moment, icon="👶")


def afficher_liste_courses_batch(ingredients: dict):
    """Affiche la liste de courses groupée par rayon."""

    st.markdown("##### 🛒 Liste de courses")

    rayons_labels = {
        "fruits_legumes": "🥬 Fruits & Légumes",
        "viandes": "🥩 Boucherie",
        "poissons": "🐟 Poissonnerie",
        "cremerie": "🧀 Crèmerie",
        "epicerie": "🍝 Épicerie",
        "surgeles": "❄️ Surgelés",
        "bio": "🌿 Bio",
        "autres": "📦 Autres",
    }

    for rayon_key, label in rayons_labels.items():
        items = ingredients.get(rayon_key, [])
        if items:
            with st.expander(f"{label} ({len(items)})"):
                for item in items:
                    qty = item.get("quantite", "")
                    unite = item.get("unite", "")
                    nom = item.get("nom", "")
                    poids = item.get("poids_g", "")

                    ligne = f"☐ {qty} {unite} {nom}"
                    if poids:
                        ligne += f" (~{poids}g)"

                    st.checkbox(ligne, key=f"course_{rayon_key}_{nom}")


def afficher_finition_jour_j(recette: dict):
    """Affiche les instructions de finition pour le jour J."""

    st.markdown(f"##### 🍽️ {recette.get('nom', 'Recette')}")

    # Temps de finition
    temps = recette.get("temps_finition_minutes", 10)
    st.caption(f"⏱️ Temps de finition: {temps} min")

    # Étapes
    etapes = recette.get("instructions_finition", [])
    for i, etape in enumerate(etapes, 1):
        st.markdown(f"{i}. {etape}")

    # Notes Jules
    if recette.get("version_jules"):
        st.info(f"👶 Jules: {recette['version_jules']}", icon="👶")
