"""
Module Planning - Gestion du planning hebdomadaire
 Fonctionnalités complètes:
- Vue semaine avec édition en ligne
- Génération IA planning
- Historique et gestion plannings
- Activités weekend intégrées
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import logging

from src.services.planning import get_planning_service
from src.services.recettes import get_recette_service
from src.core.database import obtenir_contexte_db
from src.core.errors_base import ErreurValidation

# Logique métier pure
from src.domains.cuisine.logic.planning_logic import (
    get_debut_semaine,
    valider_planning,
    calculer_statistiques_planning
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_EMOJI = ["🟡", "🟠", "🟣", "🟢", "⚫", "🔴", "🟢"]
TYPES_REPAS = ["déjeuner", "dîner"]
REGIMES = ["Omnivore", "Végétarien", "Végan", "Sans gluten"]
TEMPS_CUISINE = ["Rapide (< 30 min)", "Moyen (30-60 min)", "Long (> 60 min)"]
BUDGETS = ["Bas (< 20€)", "Moyen (20-40€)", "Haut (> 40€)"]

TYPES_ACTIVITES_WEEKEND = {
    "parc": {"emoji": "🌳", "label": "Parc / Nature"},
    "musee": {"emoji": "🏛️", "label": "Musée / Expo"},
    "piscine": {"emoji": "🏊", "label": "Piscine"},
    "zoo": {"emoji": "🦁", "label": "Zoo / Ferme"},
    "restaurant": {"emoji": "🍽️", "label": "Restaurant"},
    "famille": {"emoji": "👨‍👩‍👧", "label": "Visite famille"},
    "maison": {"emoji": "🏠", "label": "Maison"},
    "autre": {"emoji": "✨", "label": "Autre"},
}


def app():
    """Point d'entrée module planning"""
    st.title("📅 Planning Hebdomadaire")
    
    tabs = st.tabs(["🍽️ Planning Actif", "🛒 Courses", "🎉 Weekend", "👶 Jules", "🤖 Générer avec IA", "⚖️ Créateur Équilibré", "📚 Historique"])
    
    with tabs[0]:
        render_planning()
    
    with tabs[1]:
        render_courses_aggregees()
    
    with tabs[2]:
        render_weekend_activities()
    
    with tabs[3]:
        render_versions_jules()
    
    with tabs[4]:
        render_generer()
    
    with tabs[5]:
        render_createur_equilibre()
    
    with tabs[6]:
        render_historique()


def render_planning():
    """Affiche et édite le planning actuel"""
    service = get_planning_service()
    recette_service = get_recette_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    try:
        # Récupérer planning actif AVEC eager loading des repas et recettes
        # ✅ FIX: get_planning() charge maintenant les repas avec joinedload
        planning = service.get_planning()
        
        if not planning:
            st.warning("⚠️ Aucun planning actif pour cette semaine")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Créer nouveau planning", use_container_width=True, type="primary"):
                    st.session_state.go_to_generer = True
                    st.rerun()
            return
        
        # Afficher infos planning
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📅 Semaine du", planning.semaine_debut.strftime("%d/%m"))
        with col2:
            # ✅ FIX: planning.repas est maintenant accessible (eager loaded)
            st.metric("📊 Repas planifiés", len(planning.repas) if planning.repas else 0)
        with col3:
            genere_ia = "🤖 IA" if planning.genere_par_ia else "✏️ Manuel"
            st.metric("Créé par", genere_ia)
        
        st.divider()
        
        # ✅ FIX: Récupérer recettes dans son propre contexte BD
        from src.core.models import Recette
        with obtenir_contexte_db() as db:
            recettes = db.query(Recette).all()
            recettes_dict = {r.nom: r.id for r in recettes}
        
        # Organiser repas par jour (les repas sont déjà chargés par eager loading du service)
        repas_par_jour = {}
        if planning.repas:
            for repas in planning.repas:
                jour_key = repas.date_repas.strftime("%Y-%m-%d")
                if jour_key not in repas_par_jour:
                    repas_par_jour[jour_key] = []
                repas_par_jour[jour_key].append(repas)
        
        # Afficher 7 jours
        for idx, jour_offset in enumerate(range(7)):
            jour_date = planning.semaine_debut + timedelta(days=jour_offset)
            jour_key = jour_date.strftime("%Y-%m-%d")
            jour_name = JOURS_SEMAINE[idx]
            emoji = JOURS_EMOJI[idx]
            
            with st.expander(f"{emoji} {jour_name} - {jour_date.strftime('%d/%m')}", expanded=(idx == 0)):
                repas_jour = repas_par_jour.get(jour_key, [])
                
                if not repas_jour:
                    st.info(f"Aucun repas planifié ce jour")
                    continue
                
                for repas in repas_jour:
                    col1, col2, col3, col4 = st.columns([1.5, 2, 1.5, 1])
                    
                    with col1:
                        type_emoji = "🍽️" if repas.type_repas == "dîner" else "☕"
                        st.write(f"**{type_emoji} {repas.type_repas.capitalize()}**")
                    
                    with col2:
                        # Selectbox recette
                        recette_options = ["-- Aucune --"] + list(recettes_dict.keys())
                        # ✅ FIX: repas.recette est accessible (eager loaded)
                        recette_current = repas.recette.nom if repas.recette else "-- Aucune --"
                        
                        new_recette = st.selectbox(
                            "Recette",
                            recette_options,
                            index=recette_options.index(recette_current) if recette_current in recette_options else 0,
                            key=f"recette_{repas.id}",
                            label_visibility="collapsed"
                        )
                        
                        # Mettre à jour si changement
                        if new_recette != "-- Aucune --" and new_recette != recette_current:
                            try:
                                # ✅ FIX: Chaque modification usa son propre contexte BD
                                from src.core.models import Repas as RepasModel
                                with obtenir_contexte_db() as db:
                                    repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                    if repas_db:
                                        repas_db.recette_id = recettes_dict[new_recette]
                                        db.commit()
                                        st.session_state['planning_updated'] = True  # Flag sans rerun
                                st.success(f"✨ Recette mise à jour")
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
                    
                    with col3:
                        # Toggle "Préparé"
                        prepared = st.checkbox(
                            "Préparé",
                            value=repas.prepare,
                            key=f"prepared_{repas.id}"
                        )
                        if prepared != repas.prepare:
                            try:
                                from src.core.models import Repas as RepasModel
                                with obtenir_contexte_db() as db:
                                    repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                    if repas_db:
                                        repas_db.prepare = prepared
                                        db.commit()
                                        st.session_state['planning_updated'] = True  # Flag sans rerun
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
                    
                    with col4:
                        if st.button("🖊️", key=f"edit_notes_{repas.id}", help="Éditer notes"):
                            st.session_state[f"editing_notes_{repas.id}"] = True
                    
                    # Notes editor
                    if st.session_state.get(f"editing_notes_{repas.id}"):
                        notes = st.text_area(
                            "Notes",
                            value=repas.notes or "",
                            key=f"notes_{repas.id}",
                            height=80
                        )
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✨ Sauvegarder", key=f"save_notes_{repas.id}"):
                                try:
                                    from src.core.models import Repas as RepasModel
                                    with obtenir_contexte_db() as db:
                                        repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                        if repas_db:
                                            repas_db.notes = notes if notes else None
                                            db.commit()
                                    st.session_state[f"editing_notes_{repas.id}"] = False
                                    st.session_state['planning_updated'] = True
                                    st.success("✨ Notes sauvegardées")
                                    st.rerun()  # ← Rerun uniquement après sauvegarde
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                        with col_b:
                            if st.button("❌ Annuler", key=f"cancel_notes_{repas.id}"):
                                st.session_state[f"editing_notes_{repas.id}"] = False
                                st.rerun()
        
        st.divider()
        
        # Actions de masse
        st.subheader("⚙️ Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✨ Marquer tout préparé", width='stretch'):
                try:
                    from src.core.models import Repas as RepasModel
                    with obtenir_contexte_db() as db:
                        db.query(RepasModel).filter_by(planning_id=planning.id).update({"prepare": True})
                        db.commit()
                    st.success("✨ Tous les repas marqués comme préparés")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        with col2:
            if st.button("🔄 Dupliquer (semaine suiv.)", width='stretch'):
                try:
                    from src.core.models import Planning as PlanningModel, Repas as RepasModel
                    
                    with obtenir_contexte_db() as db:
                        # Créer nouveau planning
                        semaine_suivante = planning.semaine_debut + timedelta(days=7)
                        semaine_fin = planning.semaine_fin + timedelta(days=7)
                        
                        nouveau = PlanningModel(
                            nom=f"Planning {semaine_suivante.strftime('%d/%m/%Y')}",
                            semaine_debut=semaine_suivante,
                            semaine_fin=semaine_fin,
                            actif=False,
                            genere_par_ia=planning.genere_par_ia
                        )
                        db.add(nouveau)
                        db.flush()
                        
                        # Dupliquer repas
                        for repas in planning.repas:
                            nouveau_repas = RepasModel(
                                planning_id=nouveau.id,
                                recette_id=repas.recette_id,
                                date_repas=repas.date_repas + timedelta(days=7),
                                type_repas=repas.type_repas,
                                portion_ajustee=repas.portion_ajustee,
                                notes=repas.notes
                            )
                            db.add(nouveau_repas)
                        
                        db.commit()
                    st.success("✨ Planning dupliqué pour la semaine suivante")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        with col3:
            if st.button("📦 Archiver planning", use_container_width=True):
                try:
                    from src.core.models import Planning as PlanningModel
                    with obtenir_contexte_db() as db:
                        planning_db = db.query(PlanningModel).filter_by(id=planning.id).first()
                        if planning_db:
                            planning_db.actif = False
                            db.commit()
                    st.success("✨ Planning archivé")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_planning: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2: COURSES AGRÉGÉES
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_courses_aggregees():
    """Affiche et gère la liste de courses agrégée du planning actif"""
    service = get_planning_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    st.subheader("🛒 Liste de Courses - Agrégée")
    st.markdown("Ingrédients de tous les repas de la semaine, regroupés par rayon.")
    
    try:
        # Récupérer planning actif
        planning = service.get_planning()
        
        if not planning:
            st.warning("⚠️ Aucun planning actif pour cette semaine")
            return
        
        st.info(f"📅 Courses pour la semaine du **{planning.semaine_debut.strftime('%d/%m')}**")
        
        # Agréger les courses
        with st.spinner("📦 Agrégation des ingrédients..."):
            courses = service.agréger_courses_pour_planning(planning_id=planning.id)
        
        if not courses:
            st.info("ℹ️ Aucun ingrédient à acheter (planning vide ou sans recettes)")
            return
        
        # Afficher par rayon
        rayons = {}
        for course in courses:
            rayon = course["rayon"]
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(course)
        
        # Créer un dataframe pour affichage
        st.markdown("---")
        
        # Checkboxes pour sélectionner
        st.markdown("#### 📋 Ingrédients à acheter")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Tout cocher", use_container_width=True):
                if "courses_selection" not in st.session_state:
                    st.session_state.courses_selection = {}
                for course in courses:
                    st.session_state.courses_selection[f"course_{course['nom']}"] = True
                st.rerun()
        
        with col2:
            if st.button("☐ Tout décocher", use_container_width=True):
                if "courses_selection" not in st.session_state:
                    st.session_state.courses_selection = {}
                for course in courses:
                    st.session_state.courses_selection[f"course_{course['nom']}"] = False
                st.rerun()
        
        with col3:
            format_export = st.radio("Exporter en:", ["PDF", "CSV", "Texte"], horizontal=True)
        
        st.markdown("---")
        
        # Afficher par rayon avec checkboxes
        for rayon in sorted(rayons.keys()):
            articles = rayons[rayon]
            
            with st.expander(f"🏪 {rayon.capitalize()} ({len(articles)} article{'s' if len(articles) > 1 else ''})"):
                for course in articles:
                    col1, col2, col3, col4 = st.columns([0.5, 2, 1, 0.5])
                    
                    with col1:
                        checked = st.checkbox(
                            "✓",
                            value=st.session_state.get(f"course_{course['nom']}", False),
                            key=f"course_{course['nom']}",
                            label_visibility="collapsed"
                        )
                    
                    with col2:
                        article_text = f"🛒 **{course['nom']}**"
                        if checked:
                            article_text = f"~~{article_text}~~"
                        st.markdown(article_text)
                    
                    with col3:
                        quantite_text = f"{course['quantite']:.1f} {course['unite']}"
                        st.caption(quantite_text)
                    
                    with col4:
                        st.caption(f"×{course.get('repas_count', 1)}")
        
        st.markdown("---")
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total articles", len(courses))
        with col2:
            st.metric("🏪 Rayons", len(rayons))
        with col3:
            selected_count = sum(1 for c in courses if st.session_state.get(f"course_{c['nom']}", False))
            st.metric("✅ Cochés", selected_count)
        
        st.markdown("---")
        
        # Export
        if st.button("📥 Exporter liste", use_container_width=True, type="primary"):
            if format_export == "PDF":
                st.info("💡 Export PDF: À implémenter")
            elif format_export == "CSV":
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Rayon", "Article", "Quantité", "Unité", "Repas"])
                
                for course in courses:
                    writer.writerow([
                        course["rayon"],
                        course["nom"],
                        course["quantite"],
                        course["unite"],
                        course.get("repas_count", 1)
                    ])
                
                st.download_button(
                    label="Télécharger CSV",
                    data=output.getvalue(),
                    file_name=f"courses_{planning.semaine_debut.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:  # Texte
                texte = "📋 LISTE DE COURSES\n"
                texte += f"Semaine du {planning.semaine_debut.strftime('%d/%m/%Y')}\n\n"
                
                for rayon in sorted(rayons.keys()):
                    texte += f"🏪 {rayon.upper()}\n"
                    for course in rayons[rayon]:
                        texte += f"  ☐ {course['nom']} ({course['quantite']:.1f} {course['unite']})\n"
                    texte += "\n"
                
                st.text_area("Copier-coller:", value=texte, height=400)
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_courses: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3: ACTIVITÉS WEEKEND
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_weekend_activities():
    """Affiche et gère les activités du weekend dans le planning global"""
    st.subheader("🎉 Activités Weekend")
    st.markdown("Planifiez vos sorties et activités du weekend.")
    
    try:
        # Import du modèle WeekendActivity
        from src.core.models import WeekendActivity
        
        # Calculer les dates du weekend actuel
        today = date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0 and today.weekday() != 5:
            days_until_saturday = 7
        samedi = today + timedelta(days=days_until_saturday)
        dimanche = samedi + timedelta(days=1)
        
        st.info(f"📅 Weekend du **{samedi.strftime('%d/%m')}** au **{dimanche.strftime('%d/%m')}**")
        
        # Récupérer activités weekend
        with obtenir_contexte_db() as db:
            activites_samedi = db.query(WeekendActivity).filter(
                WeekendActivity.activity_date == samedi
            ).order_by(WeekendActivity.time_slot).all()
            
            activites_dimanche = db.query(WeekendActivity).filter(
                WeekendActivity.activity_date == dimanche
            ).order_by(WeekendActivity.time_slot).all()
        
        # Layout 2 colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🔴 Samedi {samedi.strftime('%d/%m')}")
            if activites_samedi:
                for act in activites_samedi:
                    type_info = TYPES_ACTIVITES_WEEKEND.get(act.activity_type, {"emoji": "✨", "label": act.activity_type})
                    with st.container(border=True):
                        st.markdown(f"**{type_info['emoji']} {act.title}**")
                        if act.location:
                            st.caption(f"📍 {act.location}")
                        if act.estimated_cost and act.estimated_cost > 0:
                            st.caption(f"💰 ~{act.estimated_cost:.0f}€")
                        if act.adapte_jules:
                            st.caption("👶 Adapté Jules")
            else:
                st.info("Pas d'activité planifiée")
        
        with col2:
            st.markdown(f"### 🟢 Dimanche {dimanche.strftime('%d/%m')}")
            if activites_dimanche:
                for act in activites_dimanche:
                    type_info = TYPES_ACTIVITES_WEEKEND.get(act.activity_type, {"emoji": "✨", "label": act.activity_type})
                    with st.container(border=True):
                        st.markdown(f"**{type_info['emoji']} {act.title}**")
                        if act.location:
                            st.caption(f"📍 {act.location}")
                        if act.estimated_cost and act.estimated_cost > 0:
                            st.caption(f"💰 ~{act.estimated_cost:.0f}€")
                        if act.adapte_jules:
                            st.caption("👶 Adapté Jules")
            else:
                st.info("Pas d'activité planifiée")
        
        st.divider()
        
        # Formulaire ajout rapide
        with st.expander("➕ Ajouter une activité"):
            with st.form("form_weekend_activity"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    titre = st.text_input("Titre*")
                    type_act = st.selectbox("Type", list(TYPES_ACTIVITES_WEEKEND.keys()), 
                                           format_func=lambda x: f"{TYPES_ACTIVITES_WEEKEND[x]['emoji']} {TYPES_ACTIVITES_WEEKEND[x]['label']}")
                    jour = st.selectbox("Jour", ["Samedi", "Dimanche"])
                
                with col_b:
                    lieu = st.text_input("Lieu")
                    cout = st.number_input("Coût estimé (€)", 0.0, 500.0, 0.0, step=5.0)
                    adapte_jules = st.checkbox("Adapté à Jules", value=True)
                
                if st.form_submit_button("✅ Ajouter", use_container_width=True):
                    if titre:
                        try:
                            with obtenir_contexte_db() as db:
                                nouvelle = WeekendActivity(
                                    activity_date=samedi if jour == "Samedi" else dimanche,
                                    activity_type=type_act,
                                    title=titre,
                                    location=lieu if lieu else None,
                                    estimated_cost=cout if cout > 0 else None,
                                    adapte_jules=adapte_jules,
                                    time_slot="matin",
                                    source="manuel"
                                )
                                db.add(nouvelle)
                                db.commit()
                            st.success(f"✅ '{titre}' ajouté!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
                    else:
                        st.warning("⚠️ Titre requis")
        
        # Lien vers module weekend complet
        st.markdown("---")
        st.markdown("🔗 Pour plus d'options (suggestions IA, lieux testés...), allez dans **Famille > Weekend**")
    
    except ImportError:
        st.warning("⚠️ Module WeekendActivity non disponible. Exécutez la migration SQL.")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_weekend_activities: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: VERSIONS JULES (19 MOIS)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_versions_jules():
    """Affiche et gère les versions adaptées pour Jules (19 mois)"""
    service = get_planning_service()
    recette_service = get_recette_service()
    
    if service is None or recette_service is None:
        st.error("❌ Services indisponibles")
        return
    
    st.subheader("👶 Repas Adaptés pour Jules (19 mois)")
    st.markdown("Versions des recettes adaptées à l'âge de Jules: moins salé, textures appropriées, allergènes évitées.")
    
    try:
        # Récupérer planning actif
        planning = service.get_planning()
        
        if not planning:
            st.warning("⚠️ Aucun planning actif pour cette semaine")
            return
        
        if not planning.repas:
            st.info("ℹ️ Planning sans repas")
            return
        
        st.info(f"📅 Semaine du **{planning.semaine_debut.strftime('%d/%m')}**")
        st.markdown("---")
        
        # Afficher une version Jules par jour
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        for idx, jour_offset in enumerate(range(7)):
            jour_date = planning.semaine_debut + timedelta(days=jour_offset)
            jour_name = jours_semaine[idx]
            jour_key = jour_date.strftime("%Y-%m-%d")
            
            # Récupérer repas du jour
            repas_jour = [r for r in planning.repas if r.date_repas.strftime("%Y-%m-%d") == jour_key]
            
            if not repas_jour:
                st.info(f"**{jour_name} ({jour_date.strftime('%d/%m')})** - Pas de repas planifiés")
                continue
            
            with st.expander(f"👶 **{jour_name}** - {jour_date.strftime('%d/%m')}", expanded=(idx == 0)):
                for repas in repas_jour:
                    if not repas.recette_id:
                        st.info(f"{repas.type_repas}: Repas non défini")
                        continue
                    
                    recette = repas.recette
                    if not recette:
                        st.warning(f"{repas.type_repas}: Recette non trouvée")
                        continue
                    
                    st.markdown(f"#### 🍽️ {recette.nom}")
                    
                    # Vérifier si version Jules existe
                    has_version = recette.versions and any(v.type_version == "bebe" for v in recette.versions)
                    
                    if has_version:
                        version = next(v for v in recette.versions if v.type_version == "bebe")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Modifications Jules:**")
                            modifications = version.notes_bebe or "Pas de modifications spécifiées"
                            st.write(modifications)
                        
                        with col2:
                            st.markdown("**Conseils:**")
                            st.info("""
                            ✅ À 19 mois:
                            - Sans sel ou très peu
                            - Textures molles, faciles à mâcher
                            - Morceaux petits (risque d'étouffement)
                            - Pas d'allergènes courants
                            """)
                    
                    else:
                        # Proposer de générer une version
                        st.warning(f"⚠️ Pas de version Jules pour '{recette.nom}'")
                        
                        if st.button(f"🤖 Générer version Jules", key=f"gen_jules_{repas.id}"):
                            with st.spinner("Génération en cours..."):
                                try:
                                    version_bebe = recette_service.generer_version_bebe(
                                        recette_id=recette.id
                                    )
                                    if version_bebe:
                                        st.success(f"✅ Version Jules générée pour '{recette.nom}'")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erreur lors de la génération")
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                                    logger.error(f"Erreur genération version Jules: {e}")
                        
                        # Afficher les conseils génériques
                        with st.expander("📖 Conseils génériques pour Jules"):
                            st.markdown("""
                            ### Adaptation pour bébé 19 mois:
                            
                            **Sécurité:**
                            - Éviter: Sel, sucre, miel (botulisme), épices fortes
                            - Couper en petits morceaux pour éviter l'étouffement
                            
                            **Texture:**
                            - Molles et facilement écrasables
                            - Plutôt mixées ou très cuites
                            
                            **Portions:**
                            - 1/3 à 1/2 des portions adulte
                            
                            **Protéines:**
                            - Viandes cuites et hachées
                            - Poisson sans arêtes
                            - Œufs bien cuits
                            """)
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_versions_jules: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: GÉNÉRER PLANNING AVEC IA
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_generer():
    """Générer un planning hebdomadaire avec IA"""
    service = get_planning_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    st.subheader("🤖 Générer Planning Hebdomadaire")
    
    try:
        # Date de début (défaut lundi prochain)
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        default_start = today + timedelta(days=days_until_monday)
        
        col1, col2 = st.columns(2)
        
        with col1:
            semaine_debut = st.date_input(
                "📅 Semaine à partir du",
                value=default_start,
                format="YYYY-MM-DD"
            )
        
        with col2:
            # Vérifier que c'est un lundi
            if semaine_debut.weekday() != 0:
                st.warning("[!] Veuillez sélectionner un lundi")
                semaine_debut = semaine_debut - timedelta(days=semaine_debut.weekday())
        
        st.divider()
        st.subheader("🍽️ Préférences")
        
        col1, col2 = st.columns(2)
        with col1:
            regime = st.radio("Régime alimentaire", REGIMES, index=0)
        with col2:
            temps = st.radio("Temps de cuisine", TEMPS_CUISINE, index=1)
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.radio("Budget", BUDGETS, index=1)
        with col2:
            allergies = st.multiselect("Allergies à éviter", [
                "Arachides", "Noix", "Lait", "Gluten", "Œufs", "Fruits de mer"
            ])
        
        notes_prefs = st.text_area(
            "Notes additionnelles",
            placeholder="Ex: pas de viande rouge, préférez les pâtes...",
            height=60
        )
        
        st.divider()
        
        if st.button("🚀 Générer Planning avec IA", use_container_width=True, type="primary"):
            try:
                with st.spinner("🤖 Génération en cours..."):
                    # Préparer préférences
                    preferences = {
                        "regime": regime,
                        "temps_cuisine": temps,
                        "budget": budget,
                        "allergies": allergies,
                        "notes": notes_prefs
                    }
                    
                    # Générer planning
                    planning = service.generer_planning_ia(
                        semaine_debut=semaine_debut,
                        preferences=preferences
                    )
                    
                    if planning:
                        st.success("✨ Planning généré avec succès!")
                        
                        # Afficher preview
                        st.subheader("📋 Aperçu du planning")
                        
                        # Récupérer planning complet
                        planning_complet = service.get_planning_complet(planning.id)
                        
                        if planning_complet:
                            # Créer tableau
                            data = []
                            for jour_offset in range(7):
                                jour_date = semaine_debut + timedelta(days=jour_offset)
                                jour_key = jour_date.strftime("%Y-%m-%d")
                                jour_name = JOURS_SEMAINE[jour_offset]
                                
                                repas_jour = planning_complet.get("repas_par_jour", {}).get(jour_key, [])
                                
                                for repas in repas_jour:
                                    # Afficher recette ou notes
                                    display_text = repas.get("recette_nom") or repas.get("notes") or "À remplir"
                                    data.append({
                                        "Jour": jour_name,
                                        "Date": jour_date.strftime("%d/%m"),
                                        "Type": repas["type_repas"].capitalize(),
                                        "Recette/Notes": display_text
                                    })
                            
                            if data:
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                        
                        st.divider()
                        st.info("✨ Planning sauvegardé en BD et prêt à utiliser!")
                        
                        if st.button("📋 Voir planning", use_container_width=True):
                            st.session_state.go_to_planning = True
                            st.rerun()
                    else:
                        st.error("❌ Erreur lors de la génération")
            
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur generer_planning_ia: {e}")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_generer: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5: CRÉATEUR ÉQUILIBRÉ - CHOIX INTELLIGENT DE RECETTES
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_createur_equilibre():
    """Workflow progressif: paramètres → suggestions → validation"""
    service = get_planning_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    st.subheader("⚖️ Créateur Équilibré - Avec Suggestions Intelligentes")
    st.markdown("""
    Construis une semaine équilibrée en poisson, viande, végé et féculents.
    Tu choisis les recettes entre nos suggestions.
    """)
    
    # Initialiser session state
    if "equilibre_step" not in st.session_state:
        st.session_state.equilibre_step = 1
        st.session_state.equilibre_params = {
            "poisson_jours": ["lundi", "jeudi"],
            "viande_rouge_jours": ["mardi"],
            "vegetarien_jours": ["mercredi"],
            "pates_riz_count": 3,
            "ingredients_exclus": [],
        }
        st.session_state.equilibre_recettes_selection = {}
        st.session_state.equilibre_suggestions = []
        st.session_state.equilibre_semaine_debut = date.today() + timedelta(days=(7 - date.today().weekday()) % 7)
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ÉTAPE 1: PARAMÈTRES D'ÉQUILIBRE
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    if st.session_state.equilibre_step == 1:
        st.markdown("### 📋 Étape 1: Paramètres d'Équilibre")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🐟 Protéines par jour")
            
            poisson_jours = st.multiselect(
                "Jours avec du poisson",
                ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
                default=st.session_state.equilibre_params["poisson_jours"],
                key="ms_poisson_eq",
            )
            st.session_state.equilibre_params["poisson_jours"] = poisson_jours
            
            viande_jours = st.multiselect(
                "Jours avec viande rouge",
                ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
                default=st.session_state.equilibre_params["viande_rouge_jours"],
                key="ms_viande_eq",
            )
            st.session_state.equilibre_params["viande_rouge_jours"] = viande_jours
            
            vege_jours = st.multiselect(
                "Jours végétariens",
                ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
                default=st.session_state.equilibre_params["vegetarien_jours"],
                key="ms_vege_eq",
            )
            st.session_state.equilibre_params["vegetarien_jours"] = vege_jours
        
        with col2:
            st.markdown("#### 🍝 Féculents & Restrictions")
            
            pates_count = st.slider(
                "Nombre de fois pâtes/riz par semaine",
                1, 6, 
                value=st.session_state.equilibre_params["pates_riz_count"],
                key="slider_pates_eq",
            )
            st.session_state.equilibre_params["pates_riz_count"] = pates_count
            
            ingredients_txt = st.text_area(
                "Ingrédients à éviter (allergies)",
                value=", ".join(st.session_state.equilibre_params["ingredients_exclus"]),
                height=60,
                placeholder="Ex: miel, cacahuète, ail",
                key="ta_exclus_eq",
            )
            st.session_state.equilibre_params["ingredients_exclus"] = [
                i.strip() for i in ingredients_txt.split(",") if i.strip()
            ]
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            semaine_debut = st.date_input(
                "Semaine à partir du (doit être un lundi)",
                value=st.session_state.equilibre_semaine_debut,
                key="di_semaine_eq",
            )
            if semaine_debut.weekday() != 0:
                st.warning("⚠️ Veuillez sélectionner un lundi")
                semaine_debut = semaine_debut - timedelta(days=semaine_debut.weekday())
            st.session_state.equilibre_semaine_debut = semaine_debut
        
        # Vérifier équilibre
        st.markdown("---")
        st.markdown("#### 📊 Récapitulatif")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🐟 Poisson", len(poisson_jours) if poisson_jours else "—")
        with col2:
            st.metric("🥩 Viande rouge", len(viande_jours) if viande_jours else "—")
        with col3:
            st.metric("🥬 Végétarien", len(vege_jours) if vege_jours else "—")
        with col4:
            st.metric("🍝 Pâtes/Riz", f"{pates_count}×")
        
        if st.button("📊 Voir suggestions", use_container_width=True, type="primary"):
            st.session_state.equilibre_step = 2
            st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ÉTAPE 2: REVIEW DES SUGGESTIONS
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    elif st.session_state.equilibre_step == 2:
        st.markdown("### 🍽️ Étape 2: Choisir les Recettes")
        st.markdown("Sélectionne une recette pour chaque jour parmi nos suggestions équilibrées.")
        
        # Charger les suggestions si pas déjà fait
        if not st.session_state.equilibre_suggestions:
            with st.spinner("🤖 Génération des suggestions..."):
                try:
                    from src.services.planning import ParametresEquilibre
                    
                    params = ParametresEquilibre(
                        poisson_jours=st.session_state.equilibre_params["poisson_jours"],
                        viande_rouge_jours=st.session_state.equilibre_params["viande_rouge_jours"],
                        vegetarien_jours=st.session_state.equilibre_params["vegetarien_jours"],
                        pates_riz_count=st.session_state.equilibre_params["pates_riz_count"],
                        ingredients_exclus=st.session_state.equilibre_params["ingredients_exclus"],
                    )
                    
                    suggestions = service.suggerer_recettes_equilibrees(
                        semaine_debut=st.session_state.equilibre_semaine_debut,
                        parametres=params,
                    )
                    st.session_state.equilibre_suggestions = suggestions or []
                    
                    if not suggestions:
                        st.error("❌ Pas de suggestions générées")
                        return
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
                    logger.error(f"Erreur suggestions: {e}")
                    return
        
        # Afficher statut équilibre
        if st.session_state.equilibre_suggestions:
            stats = {
                "🐟 Poisson": 0,
                "🥩 Viande rouge": 0,
                "🍗 Volaille": 0,
                "🥬 Végétarien": 0,
            }
            
            for jour_info in st.session_state.equilibre_suggestions:
                raison = jour_info.get("raison_jour", "")
                if "poisson" in raison.lower():
                    stats["🐟 Poisson"] += 1
                elif "viande" in raison.lower():
                    stats["🥩 Viande rouge"] += 1
                elif "végé" in raison.lower():
                    stats["🥬 Végétarien"] += 1
                else:
                    stats["🍗 Volaille"] += 1
            
            cols = st.columns(4)
            for idx, (label, count) in enumerate(stats.items()):
                with cols[idx]:
                    st.metric(label, f"{count}×" if count > 0 else "—")
        
        st.markdown("---")
        
        # Afficher chaque jour avec ses suggestions
        for jour_info in st.session_state.equilibre_suggestions:
            jour_name = jour_info["jour"]
            jour_idx = jour_info["jour_index"]
            raison = jour_info["raison_jour"]
            suggestions_jour = jour_info["suggestions"]
            
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"### {jour_name}")
                with col2:
                    st.markdown(f"**{raison}** · {jour_info['date']}")
                
                if suggestions_jour:
                    jour_key = f"jour_{jour_idx}"
                    
                    # Créer les radio buttons
                    options_text = []
                    options_ids = []
                    
                    for sugg in suggestions_jour:
                        texte = f"🍽️ **{sugg['nom']}** ({sugg['temps_total']}min)"
                        options_text.append(texte)
                        options_ids.append(sugg["id"])
                    
                    # Radio buttons
                    choix_idx = st.radio(
                        "Choisir une recette:",
                        range(len(options_text)),
                        format_func=lambda i: options_text[i],
                        key=f"radio_{jour_key}",
                        horizontal=False,
                    )
                    
                    st.session_state.equilibre_recettes_selection[jour_key] = options_ids[choix_idx]
                    
                    # Afficher description
                    recette_sel = suggestions_jour[choix_idx]
                    with st.expander(f"📖 Détails"):
                        st.write(recette_sel["description"])
                        st.caption(f"🥘 Type: {recette_sel.get('type_proteines', 'mixte')} · ⏱️ {recette_sel['temps_total']} min")
                else:
                    st.warning(f"❌ Pas de suggestions pour {jour_name}")
        
        st.markdown("---")
        
        # Boutons navigation
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("◀️ Retour", key="btn_etape1_back", use_container_width=True):
                st.session_state.equilibre_step = 1
                st.rerun()
        
        with col3:
            if len(st.session_state.equilibre_recettes_selection) == 7:
                if st.button("✅ Récapitulatif", key="btn_etape3", use_container_width=True, type="primary"):
                    st.session_state.equilibre_step = 3
                    st.rerun()
            else:
                st.button(f"⏳ Choisir une recette par jour ({len(st.session_state.equilibre_recettes_selection)}/7)", 
                         key="btn_etape3_disabled", disabled=True, use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ÉTAPE 3: RÉCAPITULATIF & VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    elif st.session_state.equilibre_step == 3:
        st.markdown("### ✨ Étape 3: Récapitulatif & Validation")
        
        # Créer le planning avec les choix
        with st.spinner("💾 Création du planning..."):
            try:
                planning = service.creer_planning_avec_choix(
                    semaine_debut=st.session_state.equilibre_semaine_debut,
                    recettes_selection=st.session_state.equilibre_recettes_selection,
                )
                
                if planning:
                    st.success(f"✅ Planning créé: **{planning.nom}**")
                else:
                    st.error("❌ Erreur lors de la création du planning")
                    return
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur création planning: {e}")
                return
        
        # Afficher le planning créé
        st.markdown("#### 📅 Votre Semaine Équilibrée")
        
        for jour_info in st.session_state.equilibre_suggestions:
            jour_name = jour_info["jour"]
            jour_idx = jour_info["jour_index"]
            jour_key = f"jour_{jour_idx}"
            raison = jour_info["raison_jour"]
            
            recette_id = st.session_state.equilibre_recettes_selection.get(jour_key)
            if recette_id:
                for sugg in jour_info["suggestions"]:
                    if sugg["id"] == recette_id:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{jour_name}** · {raison} · 🍽️ {sugg['nom']}")
                        with col2:
                            st.caption(f"⏱️ {sugg['temps_total']}min")
                        break
        
        st.markdown("---")
        st.success("🎉 Planning sauvegardé! Retrouvez-le dans l'onglet 'Planning Actif'")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("◀️ Retour", use_container_width=True):
                st.session_state.equilibre_step = 2
                st.rerun()
        with col2:
            if st.button("➕ Créer un autre planning", use_container_width=True, type="primary"):
                # Reset
                st.session_state.equilibre_step = 1
                st.session_state.equilibre_recettes_selection = {}
                st.session_state.equilibre_suggestions = []
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6: HISTORIQUE PLANNINGS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def render_historique():
    """Affiche historique des plannings"""
    service = get_planning_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    st.subheader("📚 Historique des Plannings")
    
    try:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_debut = st.date_input("Du", value=date.today() - timedelta(days=90))
        with col2:
            date_fin = st.date_input("Au", value=date.today() + timedelta(days=30))
        with col3:
            filter_ia = st.checkbox("Générés par IA seulement")
        
        st.divider()
        
        # Récupérer tous plannings
        from src.core.models import Planning as PlanningModel
        from sqlalchemy.orm import joinedload
        
        with obtenir_contexte_db() as db:
            query = db.query(PlanningModel)
            query = query.options(joinedload(PlanningModel.repas))
            query = query.filter(PlanningModel.semaine_debut >= date_debut)
            query = query.filter(PlanningModel.semaine_debut <= date_fin)
            
            if filter_ia:
                query = query.filter(PlanningModel.genere_par_ia == True)
            
            plannings = query.order_by(PlanningModel.semaine_debut.desc()).all()
        
        if not plannings:
            st.info("Aucun planning trouvé")
            return
        
        st.metric("📊 Total plannings", len(plannings))
        
        st.divider()
        
        # Tableau plannings
        for planning in plannings:
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 0.8, 0.8])
            
            with col1:
                genere_icon = "🤖" if planning.genere_par_ia else "✏️"
                actif_icon = "✅" if planning.actif else "⚫"
                st.write(f"**{genere_icon} {planning.nom}** {actif_icon}")
                st.caption(f"📅 {planning.semaine_debut.strftime('%d/%m')} → {planning.semaine_fin.strftime('%d/%m')}")
            
            with col2:
                repas_count = len(planning.repas) if planning.repas else 0
                st.metric("🍽️ Repas", repas_count)
            
            with col3:
                created = planning.cree_le.strftime("%d/%m/%y") if planning.cree_le else "N/A"
                st.caption(f"Créé: {created}")
            
            with col4:
                if st.button("📂", key=f"load_{planning.id}", help="Charger ce planning"):
                    try:
                        with obtenir_contexte_db() as db:
                            # Désactiver tous les autres
                            db.query(PlanningModel).filter(PlanningModel.actif == True).update({"actif": False})
                            # Activer celui-ci
                            planning_db = db.query(PlanningModel).filter_by(id=planning.id).first()
                            if planning_db:
                                planning_db.actif = True
                                db.commit()
                        st.success("✨ Planning chargé")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
            
            with col5:
                if st.button("🗑️", key=f"delete_{planning.id}", help="Supprimer ce planning"):
                    try:
                        with obtenir_contexte_db() as db:
                            db.query(PlanningModel).filter_by(id=planning.id).delete()
                            db.commit()
                        st.success("✨ Planning supprimé")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
            
            st.divider()

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_historique: {e}")
