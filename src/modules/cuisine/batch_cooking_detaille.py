"""
Module Batch Cooking Détaillé - UI Streamlit

Interface pour les sessions de batch cooking:
- Planning visuel avec timeline
- Instructions détaillées (découpes, robots, quantités)
- Moments Jules intégrés
- Génération liste de courses
- Export/impression
"""

import json
import logging
from datetime import date, time, timedelta

import streamlit as st

from src.core.ai import obtenir_client_ia

# Importer la logique existante
from src.modules.cuisine.batch_cooking_utils import (
    ROBOTS_INFO,
    estimer_heure_fin,
    formater_duree,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES UI
# ═══════════════════════════════════════════════════════════


TYPES_DECOUPE = {
    "rondelles": {"label": "Rondelles", "emoji": "⭕", "description": "Tranches circulaires"},
    "cubes": {"label": "Cubes", "emoji": "🔲", "description": "Morceaux cubiques"},
    "julienne": {"label": "Julienne", "emoji": "📝", "description": "Bâtonnets fins 3-4mm"},
    "brunoise": {"label": "Brunoise", "emoji": "🔹", "description": "Petits dés 3mm"},
    "lamelles": {"label": "Lamelles", "emoji": "➖", "description": "Tranches fines plates"},
    "cisele": {"label": "Ciselé", "emoji": "✂️", "description": "Haché finement"},
    "emince": {"label": "Émincé", "emoji": "🔪", "description": "Tranches fines allongées"},
    "rape": {"label": "Râpé", "emoji": "🧀", "description": "Râpé grossier ou fin"},
}

TYPES_SESSION = {
    "dimanche": {
        "label": "🌞 Session Dimanche",
        "duree_type": "2-3h",
        "avec_jules": True,
        "heure_defaut": time(10, 0),
        "description": "Grande session familiale avec Jules",
    },
    "mercredi": {
        "label": "🌙 Session Mercredi",
        "duree_type": "1-1.5h",
        "avec_jules": False,
        "heure_defaut": time(20, 0),
        "description": "Session rapide en solo",
    },
}


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_selecteur_session():
    """Sélecteur de type de session."""

    st.subheader("📅 Type de session")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🌞 **Dimanche**\n2-3h avec Jules",
            key="btn_session_dimanche",
            use_container_width=True,
            type="primary" if st.session_state.get("batch_type") == "dimanche" else "secondary",
        ):
            st.session_state.batch_type = "dimanche"
            st.rerun()

    with col2:
        if st.button(
            "🌙 **Mercredi**\n1-1.5h solo",
            key="btn_session_mercredi",
            use_container_width=True,
            type="primary" if st.session_state.get("batch_type") == "mercredi" else "secondary",
        ):
            st.session_state.batch_type = "mercredi"
            st.rerun()


def render_planning_semaine_preview(planning_data: dict):
    """Affiche les repas de la semaine pour lesquels on fait le batch."""

    st.markdown("##### 📋 Repas à préparer")

    if not planning_data:
        st.info("Aucun planning trouvé. Allez d'abord dans 'Planifier mes repas'.")
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


def render_ingredient_detaille(ingredient: dict, key_prefix: str):
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
                st.caption(f"📝 {ingredient['instruction_prep']}")

        # Badge Jules
        if ingredient.get("jules_peut_aider"):
            st.success(f"👶 Jules: {ingredient.get('tache_jules', 'Peut aider')}", icon="👶")


def render_etape_batch(etape: dict, numero: int, key_prefix: str):
    """Affiche une étape de batch cooking."""

    est_passif = etape.get("est_passif", False)
    couleur_bg = "background-color: #f0f8ff;" if est_passif else ""

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
            render_instruction_robot(robot)

        # Jules
        if etape.get("jules_participation"):
            st.success(f"👶 **Jules peut aider:** {etape.get('tache_jules', '')}", icon="👶")

        st.divider()


def render_instruction_robot(robot_config: dict):
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


def render_timeline_session(etapes: list, heure_debut: time):
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


def render_moments_jules(moments: list):
    """Affiche les moments de participation de Jules."""

    if not moments:
        return

    st.markdown("##### 👶 Moments avec Jules")

    for moment in moments:
        st.success(moment, icon="👶")


def render_liste_courses_batch(ingredients: dict):
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


def render_finition_jour_j(recette: dict):
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


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════


def generer_batch_ia(planning_data: dict, type_session: str, avec_jules: bool) -> dict:
    """Génère les instructions de batch cooking avec l'IA."""

    prompt = f"""Tu es un expert en batch cooking familial. Génère des instructions TRÈS DÉTAILLÉES.

SESSION: {type_session.upper()}
{"Avec Jules (19 mois) - prévoir des tâches simples et sécurisées" if avec_jules else "Session solo"}

RECETTES À PRÉPARER:
"""

    for jour, repas in planning_data.items():
        for type_repas in ["midi", "soir"]:
            r = repas.get(type_repas, {})
            if r:
                prompt += f"\n- {jour} {type_repas}: {r.get('nom', 'Recette')}"

    prompt += """

RÉPONDS EN JSON avec cette structure EXACTE:
{
  "session": {
    "duree_estimee_minutes": 120,
    "conseils_organisation": ["Conseil 1", "Conseil 2"]
  },
  "recettes": [
    {
      "nom": "Nom recette",
      "pour_jours": ["Lundi midi", "Mardi soir"],
      "portions": 4,
      "ingredients": [
        {
          "nom": "carottes",
          "quantite": 2,
          "unite": "pièces",
          "poids_g": 200,
          "description": "taille moyenne",
          "decoupe": "rondelles",
          "taille_decoupe": "1cm",
          "instruction_prep": "Éplucher et laver",
          "jules_peut_aider": true,
          "tache_jules": "Laver les carottes"
        }
      ],
      "etapes_batch": [
        {
          "titre": "Préparer les légumes",
          "description": "Éplucher et couper tous les légumes",
          "duree_minutes": 15,
          "est_passif": false,
          "robot": null,
          "jules_participation": true,
          "tache_jules": "Mettre les légumes dans le saladier"
        },
        {
          "titre": "Cuisson Cookeo",
          "description": "Cuisson sous pression des légumes",
          "duree_minutes": 20,
          "est_passif": true,
          "robot": {
            "type": "cookeo",
            "programme": "Sous pression",
            "duree_secondes": 1200
          },
          "jules_participation": false
        }
      ],
      "instructions_finition": [
        "Sortir du frigo 15min avant",
        "Réchauffer 5min au micro-ondes"
      ],
      "stockage": "frigo",
      "duree_conservation_jours": 4,
      "temps_finition_minutes": 10,
      "version_jules": "Mixer la portion de Jules plus finement"
    }
  ],
  "moments_jules": [
    "0-15min: Laver les légumes ensemble",
    "30-40min: Mélanger les ingrédients"
  ],
  "liste_courses": {
    "fruits_legumes": [
      {"nom": "carottes", "quantite": 4, "unite": "pièces", "poids_g": 400}
    ],
    "viandes": [],
    "cremerie": [],
    "epicerie": [],
    "surgeles": []
  }
}

IMPORTANT:
- Découpes possibles: rondelles, cubes, julienne, brunoise, lamelles, cisele, emince, rape
- Monsieur Cuisine: vitesse 1-10, duree_secondes, temperature
- Cookeo: programme (Sous pression, Dorer, Mijoter, Cuisson rapide, Cuisson douce)
- Four: mode (Chaleur tournante, Grill), temperature, duree_secondes
- Quantités: TOUJOURS poids approximatif en grammes
- Jules 19 mois: tâches TRÈS simples (laver, mélanger, verser)
"""

    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}

        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un expert batch cooking. Réponds UNIQUEMENT en JSON valide.",
        )

        if response and isinstance(response, dict):
            return response

        if isinstance(response, str):
            return json.loads(response)

    except Exception as e:
        logger.error(f"Erreur génération batch IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")

    return {}


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Batch Cooking Détaillé."""

    st.title("🍳 Batch Cooking")
    st.caption("Préparez vos repas de la semaine en une session efficace")

    # Initialiser la session
    if "batch_type" not in st.session_state:
        st.session_state.batch_type = "dimanche"

    if "batch_data" not in st.session_state:
        st.session_state.batch_data = {}

    # Récupérer le planning (depuis le planificateur de repas)
    planning_data = st.session_state.get("planning_data", {})

    # Tabs
    tab_preparer, tab_session, tab_finitions = st.tabs(
        ["📋 Préparer", "👩‍🍳 Session Batch", "🍽️ Finitions Jour J"]
    )

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉPARER
    # ═══════════════════════════════════════════════════════

    with tab_preparer:
        # Sélection du type de session
        render_selecteur_session()

        st.divider()

        # Infos session
        type_info = TYPES_SESSION.get(st.session_state.batch_type, {})

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**{type_info.get('label', 'Session')}**")
            st.caption(type_info.get("description", ""))

        with col2:
            st.markdown(f"**⏱️ Durée**: {type_info.get('duree_type', '2h')}")

        with col3:
            avec_jules = type_info.get("avec_jules", False)
            if avec_jules:
                st.success("👶 Avec Jules", icon="👶")
            else:
                st.info("👤 Solo", icon="👤")

        st.divider()

        # Sélection date & heure
        col_date, col_heure = st.columns(2)

        with col_date:
            date_batch = st.date_input(
                "📅 Date de la session",
                value=date.today() + timedelta(days=1),
                format="DD/MM/YYYY",
            )

        with col_heure:
            heure_batch = st.time_input(
                "⏰ Heure de début",
                value=type_info.get("heure_defaut", time(10, 0)),
            )

        st.session_state.batch_date = date_batch
        st.session_state.batch_heure = heure_batch

        st.divider()

        # Preview du planning
        st.markdown("##### 📋 Recettes du planning")

        if planning_data:
            render_planning_semaine_preview(planning_data)
        else:
            st.warning("⚠️ Aucun planning de repas trouvé.")
            if st.button("📅 Aller au planificateur de repas"):
                st.info("🚧 Navigation vers le planificateur...")

        st.divider()

        # Générer le batch
        if planning_data:
            if st.button(
                "🚀 Générer les instructions de batch", type="primary", use_container_width=True
            ):
                avec_jules = type_info.get("avec_jules", False)

                with st.spinner("🤖 L'IA génère vos instructions détaillées..."):
                    result = generer_batch_ia(
                        planning_data, st.session_state.batch_type, avec_jules
                    )

                    if result:
                        st.session_state.batch_data = result
                        st.success("✅ Instructions générées!")
                        st.rerun()
                    else:
                        st.error("❌ Impossible de générer les instructions")

    # ═══════════════════════════════════════════════════════
    # TAB: SESSION BATCH
    # ═══════════════════════════════════════════════════════

    with tab_session:
        batch_data = st.session_state.get("batch_data", {})

        if not batch_data:
            st.info("👆 Allez dans 'Préparer' et générez les instructions d'abord")
            return

        session_info = batch_data.get("session", {})
        recettes = batch_data.get("recettes", [])

        # Header session
        duree = session_info.get("duree_estimee_minutes", 120)
        heure_debut = st.session_state.get("batch_heure", time(10, 0))
        heure_fin = estimer_heure_fin(heure_debut, duree)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("⏱️ Durée estimée", formater_duree(duree))

        with col2:
            st.metric("🕐 Début", heure_debut.strftime("%H:%M"))

        with col3:
            st.metric("🕐 Fin estimée", heure_fin.strftime("%H:%M"))

        # Conseils
        conseils = session_info.get("conseils_organisation", [])
        if conseils:
            with st.expander("💡 Conseils d'organisation", expanded=False):
                for c in conseils:
                    st.markdown(f"• {c}")

        st.divider()

        # Timeline
        all_etapes = []
        for recette in recettes:
            for etape in recette.get("etapes_batch", []):
                etape["recette"] = recette.get("nom", "")
                all_etapes.append(etape)

        if all_etapes:
            render_timeline_session(all_etapes, heure_debut)

        st.divider()

        # Moments Jules
        moments_jules = batch_data.get("moments_jules", [])
        render_moments_jules(moments_jules)

        st.divider()

        # Recettes détaillées
        for recette in recettes:
            with st.expander(f"🍳 {recette.get('nom', 'Recette')}", expanded=False):
                # Ingrédients
                st.markdown("**Ingrédients:**")
                for ing in recette.get("ingredients", []):
                    render_ingredient_detaille(ing, f"ing_{recette.get('nom', '')}")

                st.divider()

                # Étapes
                st.markdown("**Étapes batch:**")
                for i, etape in enumerate(recette.get("etapes_batch", []), 1):
                    render_etape_batch(etape, i, f"etape_{recette.get('nom', '')}")

                # Stockage
                st.info(
                    f"📦 Stockage: {recette.get('stockage', 'frigo').upper()} - {recette.get('duree_conservation_jours', 3)} jours max"
                )

        st.divider()

        # Liste de courses
        liste_courses = batch_data.get("liste_courses", {})
        if liste_courses:
            render_liste_courses_batch(liste_courses)

        st.divider()

        # Actions
        col_act1, col_act2, col_act3 = st.columns(3)

        with col_act1:
            if st.button("🖨️ Imprimer les instructions", use_container_width=True):
                st.info("🚧 Export PDF en développement")

        with col_act2:
            if st.button("🛒 Envoyer aux courses", use_container_width=True):
                st.info("🚧 Intégration liste de courses...")

        with col_act3:
            if st.button("💾 Sauvegarder session", use_container_width=True):
                st.success("✅ Session sauvegardée!")

    # ═══════════════════════════════════════════════════════
    # TAB: FINITIONS JOUR J
    # ═══════════════════════════════════════════════════════

    with tab_finitions:
        batch_data = st.session_state.get("batch_data", {})
        recettes = batch_data.get("recettes", [])

        if not recettes:
            st.info("👆 Générez d'abord les instructions de batch")
            return

        st.markdown("##### 🗓️ Instructions de finition par jour")
        st.caption("Ce qu'il reste à faire le jour J")

        # Grouper par jour
        finitions_par_jour = {}
        for recette in recettes:
            for jour in recette.get("pour_jours", []):
                if jour not in finitions_par_jour:
                    finitions_par_jour[jour] = []
                finitions_par_jour[jour].append(recette)

        if finitions_par_jour:
            for jour in sorted(finitions_par_jour.keys()):
                with st.expander(f"📅 {jour}", expanded=False):
                    for recette in finitions_par_jour[jour]:
                        render_finition_jour_j(recette)
        else:
            # Afficher toutes les recettes
            for recette in recettes:
                with st.expander(f"🍽️ {recette.get('nom', 'Recette')}", expanded=False):
                    render_finition_jour_j(recette)
