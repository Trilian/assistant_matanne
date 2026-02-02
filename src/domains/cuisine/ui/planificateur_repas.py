"""
Module Planificateur de Repas Intelligent - UI Streamlit

Interface style Jow:
- Générateur IA de menus équilibrés
- Apprentissage des goûts (👍/👎) persistant en DB
- Versions Jules intégrées
- Suggestions alternatives
- Validation équilibre nutritionnel
"""

import streamlit as st
from datetime import date, datetime, time, timedelta
from io import BytesIO
import logging
import json

from src.core.database import obtenir_contexte_db
from src.core.models import (
    Recette, Planning, Repas,
    SessionBatchCooking,
)
from src.core.ai import obtenir_client_ia
from src.services.recettes import get_recette_service
from src.services.planning import get_planning_service
from src.services.user_preferences import get_user_preference_service

# Logique métier pure
from src.domains.cuisine.logic.planificateur_repas_logic import (
    JOURS_SEMAINE,
    PROTEINES,
    ROBOTS_CUISINE,
    TEMPS_CATEGORIES,
    PreferencesUtilisateur,
    FeedbackRecette,
    RecetteSuggestion,
    RepasPlannifie,
    PlanningSemaine,
    calculer_score_recette,
    filtrer_recettes_eligibles,
    generer_suggestions_alternatives,
    generer_prompt_semaine,
    generer_prompt_alternative,
    valider_equilibre_semaine,
    suggerer_ajustements_equilibre,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION PDF PLANNING
# ═══════════════════════════════════════════════════════════


def generer_pdf_planning_session(
    planning_data: dict,
    date_debut: date,
    conseils: str = "",
    suggestions_bio: list = None
) -> BytesIO | None:
    """
    Génère un PDF du planning depuis les données en session.
    
    Args:
        planning_data: Données du planning {jour: {midi, soir, gouter}}
        date_debut: Date de début du planning
        conseils: Conseils batch cooking
        suggestions_bio: Liste de suggestions bio/local
        
    Returns:
        BytesIO contenant le PDF ou None en cas d'erreur
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'PlanningTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#4CAF50'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'PlanningSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        day_style = ParagraphStyle(
            'DayHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=8,
            spaceBefore=15
        )
        
        elements = []
        
        # En-tête
        date_fin = date_debut + timedelta(days=len(planning_data) - 1)
        elements.append(Paragraph(
            "🍽️ Planning Repas Famille Matanne",
            title_style
        ))
        elements.append(Paragraph(
            f"Du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}",
            subtitle_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Table repas par jour
        type_repas_emoji = {
            "midi": "☀️",
            "soir": "🌙",
            "gouter": "🍪",
        }
        
        for i, (jour, repas) in enumerate(planning_data.items()):
            jour_date = date_debut + timedelta(days=i)
            
            # Tableau pour ce jour
            day_data = [[f"📆 {jour} {jour_date.strftime('%d/%m')}", "Repas"]]
            
            for type_repas in ["midi", "soir", "gouter"]:
                if type_repas in repas and repas[type_repas]:
                    recette_nom = repas[type_repas]
                    if isinstance(recette_nom, dict):
                        recette_nom = recette_nom.get("nom", str(recette_nom))
                    emoji = type_repas_emoji.get(type_repas, "🍴")
                    label = {"midi": "Déjeuner", "soir": "Dîner", "gouter": "Goûter"}.get(type_repas, type_repas)
                    day_data.append([
                        f"{emoji} {label}",
                        str(recette_nom)[:40]
                    ])
            
            day_table = Table(day_data, colWidths=[2.5*inch, 4*inch])
            day_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E3F2FD')])
            ]))
            elements.append(day_table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Conseils batch cooking
        if conseils:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("🍳 Conseils Batch Cooking", day_style))
            elements.append(Paragraph(conseils, styles['Normal']))
        
        # Suggestions bio
        if suggestions_bio:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("🌿 Suggestions Bio/Local", day_style))
            for sug in suggestions_bio:
                elements.append(Paragraph(f"• {sug}", styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} • Assistant Matanne 🏠",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"❌ Erreur génération PDF planning: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# GESTION DES PRÉFÉRENCES (PERSISTÉES EN DB)
# ═══════════════════════════════════════════════════════════


def charger_preferences() -> PreferencesUtilisateur:
    """
    Charge les préférences depuis la DB.
    
    Utilise un cache session_state pour éviter les requêtes répétées
    pendant la même session Streamlit.
    """
    # Cache en session pour éviter requêtes DB répétées
    if "user_preferences" in st.session_state:
        return st.session_state.user_preferences
    
    # Charger depuis DB
    try:
        service = get_user_preference_service()
        prefs = service.charger_preferences()
        st.session_state.user_preferences = prefs
        logger.info("✅ Préférences chargées depuis DB")
        return prefs
    except Exception as e:
        logger.error(f"❌ Erreur chargement préférences: {e}")
        # Fallback sur valeurs par défaut
        prefs = PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            jules_age_mois=19,
            temps_semaine="normal",
            temps_weekend="long",
            aliments_exclus=[],
            aliments_favoris=["poulet", "pâtes", "gratins", "soupes"],
            poisson_par_semaine=2,
            vegetarien_par_semaine=1,
            viande_rouge_max=2,
            robots=["monsieur_cuisine", "cookeo", "four"],
            magasins_preferes=["Carrefour Drive", "Bio Coop", "Grand Frais", "Thiriet"],
        )
        st.session_state.user_preferences = prefs
        return prefs


def sauvegarder_preferences(prefs: PreferencesUtilisateur) -> bool:
    """
    Sauvegarde les préférences en DB.
    
    Args:
        prefs: Préférences à sauvegarder
        
    Returns:
        True si succès
    """
    try:
        service = get_user_preference_service()
        success = service.sauvegarder_preferences(prefs)
        
        if success:
            # Mettre à jour le cache session
            st.session_state.user_preferences = prefs
            logger.info("✅ Préférences sauvegardées en DB")
        
        return success
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde préférences: {e}")
        # Fallback: sauvegarder en session seulement
        st.session_state.user_preferences = prefs
        return False


def charger_feedbacks() -> list[FeedbackRecette]:
    """
    Charge l'historique des feedbacks depuis la DB.
    
    Utilise un cache session pour les performances.
    """
    # Cache en session
    if "recipe_feedbacks" in st.session_state:
        return st.session_state.recipe_feedbacks
    
    try:
        service = get_user_preference_service()
        feedbacks = service.charger_feedbacks()
        st.session_state.recipe_feedbacks = feedbacks
        logger.debug(f"Chargé {len(feedbacks)} feedbacks depuis DB")
        return feedbacks
    except Exception as e:
        logger.error(f"❌ Erreur chargement feedbacks: {e}")
        st.session_state.recipe_feedbacks = []
        return []


def ajouter_feedback(recette_id: int, recette_nom: str, feedback: str, contexte: str = None):
    """
    Ajoute un feedback sur une recette en DB.
    
    Args:
        recette_id: ID de la recette
        recette_nom: Nom de la recette
        feedback: "like", "dislike", ou "neutral"
        contexte: Contexte optionnel
    """
    try:
        service = get_user_preference_service()
        success = service.ajouter_feedback(
            recette_id=recette_id,
            recette_nom=recette_nom,
            feedback=feedback,
            contexte=contexte
        )
        
        if success:
            # Mettre à jour le cache session
            fb = FeedbackRecette(
                recette_id=recette_id,
                recette_nom=recette_nom,
                feedback=feedback,
                contexte=contexte,
            )
            
            if "recipe_feedbacks" not in st.session_state:
                st.session_state.recipe_feedbacks = []
            
            # Remplacer si feedback existant
            st.session_state.recipe_feedbacks = [
                f for f in st.session_state.recipe_feedbacks if f.recette_id != recette_id
            ]
            st.session_state.recipe_feedbacks.append(fb)
            
            logger.info(f"✅ Feedback ajouté: {recette_nom} → {feedback}")
            
    except Exception as e:
        logger.error(f"❌ Erreur ajout feedback: {e}")
        # Fallback: sauvegarder en session seulement
        fb = FeedbackRecette(
            recette_id=recette_id,
            recette_nom=recette_nom,
            feedback=feedback,
            contexte=contexte,
        )
        if "recipe_feedbacks" not in st.session_state:
            st.session_state.recipe_feedbacks = []
        st.session_state.recipe_feedbacks = [
            f for f in st.session_state.recipe_feedbacks if f.recette_id != recette_id
        ]
        st.session_state.recipe_feedbacks.append(fb)


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_configuration_preferences():
    """Affiche le formulaire de configuration des préférences."""
    
    prefs = charger_preferences()
    
    st.subheader("⚙️ Mes Préférences Alimentaires")
    
    with st.form("form_preferences"):
        # Famille
        st.markdown("##### 👨‍👩‍👧 Ma famille")
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
            placeholder="Ex: fruits de mer, abats, coriandre"
        )
        
        st.markdown("##### ❤️ Vos basiques adorés")
        favoris = st.text_input(
            "Séparés par des virgules",
            value=", ".join(prefs.aliments_favoris),
            placeholder="Ex: pâtes, poulet, gratins"
        )
        
        st.markdown("##### ⚖️ Équilibre souhaité par semaine")
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
                    key=f"robot_pref_{robot_id}"
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


def render_apprentissage_ia():
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


def render_carte_recette_suggestion(
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
            if suggestion.get('temps_minutes'):
                tags.append(f"⏱️ {suggestion['temps_minutes']} min")
            if suggestion.get('proteine'):
                prot_info = PROTEINES.get(suggestion['proteine'], {})
                tags.append(f"{prot_info.get('emoji', '')} {prot_info.get('label', suggestion['proteine'])}")
            if suggestion.get('robot'):
                robot_info = ROBOTS_CUISINE.get(suggestion['robot'], {})
                tags.append(f"{robot_info.get('emoji', '')} {robot_info.get('label', '')}")
            
            st.caption(" │ ".join(tags))
            
            # Version Jules
            if suggestion.get('jules_adaptation'):
                with st.expander("👶 Instructions Jules", expanded=False):
                    st.markdown(suggestion['jules_adaptation'])
        
        with col_actions:
            # Feedback
            col_like, col_dislike = st.columns(2)
            with col_like:
                if st.button("👍", key=f"{key_prefix}_like", help="J'aime"):
                    ajouter_feedback(
                        recette_id=hash(suggestion.get('nom', '')),
                        recette_nom=suggestion.get('nom', ''),
                        feedback="like"
                    )
                    st.toast("👍 Noté!")
            with col_dislike:
                if st.button("👎", key=f"{key_prefix}_dislike", help="Je n'aime pas"):
                    ajouter_feedback(
                        recette_id=hash(suggestion.get('nom', '')),
                        recette_nom=suggestion.get('nom', ''),
                        feedback="dislike"
                    )
                    st.toast("👎 Noté!")
            
            # Changer
            if st.button("🔄", key=f"{key_prefix}_change", help="Autre suggestion"):
                st.session_state[f"show_alternatives_{key_prefix}"] = True
                st.rerun()


def render_jour_planning(
    jour: str,
    jour_date: date,
    repas_jour: dict,
    key_prefix: str,
):
    """Affiche un jour du planning avec ses repas."""
    
    est_weekend = jour_date.weekday() >= 5
    
    with st.expander(f"📅 **{jour}** {jour_date.strftime('%d/%m')}", expanded=True):
        
        # Midi
        st.markdown("##### 🌞 Midi")
        midi = repas_jour.get("midi")
        if midi:
            render_carte_recette_suggestion(midi, jour, "midi", f"{key_prefix}_midi")
        else:
            st.info("Pas encore planifié")
            if st.button("➕ Ajouter midi", key=f"{key_prefix}_add_midi"):
                st.session_state[f"add_repas_{key_prefix}_midi"] = True
        
        st.divider()
        
        # Soir
        st.markdown("##### 🌙 Soir")
        soir = repas_jour.get("soir")
        if soir:
            render_carte_recette_suggestion(soir, jour, "soir", f"{key_prefix}_soir")
        else:
            st.info("Pas encore planifié")
            if st.button("➕ Ajouter soir", key=f"{key_prefix}_add_soir"):
                st.session_state[f"add_repas_{key_prefix}_soir"] = True
        
        # Goûter (optionnel)
        gouter = repas_jour.get("gouter")
        if gouter:
            st.divider()
            st.markdown("##### 🍰 Goûter")
            render_carte_recette_suggestion(gouter, jour, "gouter", f"{key_prefix}_gouter")


def render_resume_equilibre(planning_data: dict):
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
        st.metric("🥩 Rouge", equilibre["viande_rouge"], delta=f"{delta:+d}" if delta else None, delta_color=color)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════


def generer_semaine_ia(date_debut: date) -> dict:
    """Génère une semaine complète avec l'IA."""
    
    prefs = charger_preferences()
    feedbacks = charger_feedbacks()
    
    prompt = generer_prompt_semaine(prefs, feedbacks, date_debut)
    
    try:
        client = obtenir_client_ia()
        if not client:
            st.error("❌ Client IA non disponible")
            return {}
        
        response = client.generer_json(
            prompt=prompt,
            system_prompt="Tu es un assistant culinaire familial. Réponds UNIQUEMENT en JSON valide.",
        )
        
        if response and isinstance(response, dict):
            return response
        
        # Tenter de parser si c'est une string
        if isinstance(response, str):
            return json.loads(response)
        
    except Exception as e:
        logger.error(f"Erreur génération IA: {e}")
        st.error(f"❌ Erreur IA: {str(e)}")
    
    return {}


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Planificateur de Repas."""
    
    st.title("🍽️ Planifier mes repas")
    st.caption("Générateur intelligent de menus équilibrés avec adaptation pour Jules")
    
    # Initialiser la session
    if "planning_data" not in st.session_state:
        st.session_state.planning_data = {}
    
    if "planning_date_debut" not in st.session_state:
        # Par défaut: mercredi prochain
        today = date.today()
        days_until_wednesday = (2 - today.weekday()) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7
        st.session_state.planning_date_debut = today + timedelta(days=days_until_wednesday)
    
    # Tabs
    tab_planifier, tab_preferences, tab_historique = st.tabs([
        "📅 Planifier",
        "⚙️ Préférences",
        "📚 Historique"
    ])
    
    # ═══════════════════════════════════════════════════════
    # TAB: PLANIFIER
    # ═══════════════════════════════════════════════════════
    
    with tab_planifier:
        # Sélection période
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            date_debut = st.date_input(
                "📅 Début de la semaine",
                value=st.session_state.planning_date_debut,
                format="DD/MM/YYYY",
            )
            st.session_state.planning_date_debut = date_debut
        
        with col2:
            date_fin = date_debut + timedelta(days=9)  # Mer → Ven suivant = 10 jours
            st.markdown(f"**→** Vendredi {date_fin.strftime('%d/%m/%Y')}")
        
        with col3:
            st.write("")  # Spacer
        
        st.divider()
        
        # Apprentissage IA
        with st.expander("🧠 Ce que l'IA a appris", expanded=False):
            render_apprentissage_ia()
        
        st.divider()
        
        # Bouton génération
        col_gen1, col_gen2, col_gen3 = st.columns([2, 2, 1])
        
        with col_gen1:
            if st.button("🎲 Générer une semaine", type="primary", use_container_width=True):
                with st.spinner("🤖 L'IA réfléchit à vos menus..."):
                    result = generer_semaine_ia(date_debut)
                    
                    if result and result.get("semaine"):
                        # Convertir en format interne
                        planning = {}
                        for jour_data in result["semaine"]:
                            jour = jour_data.get("jour", "")
                            planning[jour] = {
                                "midi": jour_data.get("midi"),
                                "soir": jour_data.get("soir"),
                                "gouter": jour_data.get("gouter"),
                            }
                        
                        st.session_state.planning_data = planning
                        st.session_state.planning_conseils = result.get("conseils_batch", "")
                        st.session_state.planning_suggestions_bio = result.get("suggestions_bio", [])
                        
                        st.success("✅ Semaine générée!")
                        st.rerun()
                    else:
                        st.error("❌ Impossible de générer la semaine")
        
        with col_gen2:
            if st.button("📦 Utiliser mon stock", use_container_width=True):
                st.info("🚧 Fonctionnalité en développement")
        
        with col_gen3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.planning_data = {}
                st.rerun()
        
        st.divider()
        
        # Afficher le planning
        if st.session_state.planning_data:
            # Résumé équilibre
            render_resume_equilibre(st.session_state.planning_data)
            
            st.divider()
            
            # Afficher par jour
            for i, (jour, repas) in enumerate(st.session_state.planning_data.items()):
                jour_date = date_debut + timedelta(days=i)
                render_jour_planning(jour, jour_date, repas, f"jour_{i}")
            
            st.divider()
            
            # Conseils batch
            if st.session_state.get("planning_conseils"):
                st.markdown("##### 🍳 Conseils Batch Cooking")
                st.info(st.session_state.planning_conseils)
            
            # Suggestions bio
            if st.session_state.get("planning_suggestions_bio"):
                st.markdown("##### 🌿 Suggestions bio/local")
                for sug in st.session_state.planning_suggestions_bio:
                    st.caption(f"• {sug}")
            
            st.divider()
            
            # Actions finales
            col_val1, col_val2, col_val3 = st.columns(3)
            
            with col_val1:
                if st.button("💚 Valider ce planning", type="primary", use_container_width=True):
                    st.success("✅ Planning validé! Redirection vers les courses...")
                    # TODO: Créer le planning en DB et générer la liste de courses
            
            with col_val2:
                if st.button("🛒 Générer courses", use_container_width=True):
                    st.info("🚧 Génération de la liste de courses...")
            
            with col_val3:
                # Export PDF du planning
                if st.session_state.planning_data:
                    pdf_buffer = generer_pdf_planning_session(
                        planning_data=st.session_state.planning_data,
                        date_debut=date_debut,
                        conseils=st.session_state.get("planning_conseils", ""),
                        suggestions_bio=st.session_state.get("planning_suggestions_bio", [])
                    )
                    if pdf_buffer:
                        st.download_button(
                            label="🖨️ Télécharger PDF",
                            data=pdf_buffer,
                            file_name=f"planning_{date_debut.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.button("🖨️ Imprimer", disabled=True, use_container_width=True)
        
        else:
            st.info("👆 Cliquez sur 'Générer une semaine' pour commencer")
    
    # ═══════════════════════════════════════════════════════
    # TAB: PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════
    
    with tab_preferences:
        render_configuration_preferences()
    
    # ═══════════════════════════════════════════════════════
    # TAB: HISTORIQUE
    # ═══════════════════════════════════════════════════════
    
    with tab_historique:
        st.subheader("📚 Historique des plannings")
        
        # TODO: Charger l'historique depuis la DB
        st.info("🚧 Historique des plannings passés à venir")
        
        st.markdown("##### 🧠 Vos feedbacks")
        feedbacks = charger_feedbacks()
        
        if feedbacks:
            for fb in feedbacks[-10:]:
                emoji = "👍" if fb.feedback == "like" else "👎" if fb.feedback == "dislike" else "😐"
                st.caption(f"{emoji} {fb.recette_nom} ({fb.date_feedback.strftime('%d/%m')})")
        else:
            st.caption("Pas encore de feedbacks")
